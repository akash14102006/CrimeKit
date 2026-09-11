import logging
import os
import re
import struct
from datetime import datetime
from typing import Any, Dict, FrozenSet, List, Optional

from ...forensic_engine.base import BaseProcessor
from ...forensic_engine.schemas import (
    EvidenceSchema,
    EvidenceCategory,
    ForensicProcessorConfig,
    ProcessorPriority,
)

logger = logging.getLogger(__name__)

# Windows kernel structure constants (NT 10.0 / Win10)
_EPROCESS_SIZE = 0x7F0
_ACTIVE_PROCESS_LINKS_OFFSET = 0x2F0
_UNIQUE_PROCESS_ID_OFFSET = 0x2E0
_IMAGE_FILE_NAME_OFFSET = 0x450
_CREATE_TIME_OFFSET = 0x2D8
_PEB_OFFSET = 0x3F8
_VADROOT_OFFSET = 0x510

_OBJECT_HEADER_SIZE = 0x30
_OBJECT_TYPE_OFFSET = 0x18

# Memory section protection constants
_MEM_EXECUTE = 0x20
_MEM_READ = 0x04
_MEM_WRITE = 0x08
_MEM_RWX = _MEM_READ | _MEM_WRITE | _MEM_EXECUTE

# Known magic signatures
_HIBERFIL_MAGIC = b"hibr"
_CRASHDUMP_MAGIC_PAGE = b"PAGE"
_CRASHDUMP_SIGNATURE = b"\x45\x47\x44\x44"  # EGDD
_NTFS_MFT_MAGIC = b"FILE"
_EXT4_SUPER_MAGIC = 0xEF53
_FAT_BOOT_MAGIC = b"\x55\xaa"

# Registry hive signature
_HIVE_SIGNATURE = b"regf"

# LSASS-related process names
_LSASS_NAMES = {"lsass.exe", "lsass"}


class MemoryForensicsProcessor(BaseProcessor):
    """Memory dump analysis with struct-based parsing for standalone operation."""

    name = "memory_forensics"
    description = (
        "Memory dump analysis: process enumeration, DLL analysis, network connections, "
        "injected code detection, credential harvesting, registry analysis"
    )
    supported_categories: FrozenSet[EvidenceCategory] = frozenset(
        {EvidenceCategory.MEMORY_DUMP, EvidenceCategory.UNKNOWN}
    )
    priority = ProcessorPriority.DEEP_ANALYSIS

    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        try:
            fmt = self._detect_memory_format(evidence)
            evidence.metadata["memory_format"] = fmt

            self._extract_strings(evidence)
            self._extract_network_connections(evidence)
            self._extract_dlls(evidence)
            self._extract_registry_hives(evidence)
            self._extract_processes(evidence)
            self._build_process_tree(evidence)
            self._detect_injected_code(evidence)
            self._extract_credentials_metadata(evidence)
            self._analyze_memory_sections(evidence)
            evidence.add_tag("memory_forensics")
        except Exception as exc:
            evidence.add_error(self.name, f"Memory analysis failed: {exc}")
            logger.exception("MemoryForensicsProcessor failed on %s", evidence.filename)
        return evidence

    # ------------------------------------------------------------------
    # Format detection
    # ------------------------------------------------------------------

    def _detect_memory_format(self, evidence: EvidenceSchema) -> str:
        try:
            with open(evidence.storage_path, "rb") as fh:
                header = fh.read(4096)
        except Exception as exc:
            evidence.add_error(self.name, f"Cannot read memory dump header: {exc}")
            return "unknown"

        if len(header) < 4:
            return "unknown"

        if header[:4] == _HIBERFIL_MAGIC:
            evidence.add_tag("hibernation_file")
            return "hiberfil.sys"

        if header[:4] == _CRASHDUMP_MAGIC_PAGE:
            evidence.add_tag("crash_dump")
            return "crash_dump"

        if header[:4] == _CRASHDUMP_SIGNATURE:
            evidence.add_tag("crash_dump")
            return "crash_dump_extended"

        # Check for full memory dump: look for PE headers or known structures
        if b"MZ" == header[:2]:
            evidence.add_tag("raw_memory")
            return "raw_memory"

        # Heuristic: if file is very large and has no recognized header, treat as raw
        try:
            file_size = os.path.getsize(evidence.storage_path)
            if file_size > 100 * 1024 * 1024:
                evidence.add_tag("raw_memory")
                return "raw_memory"
        except Exception:
            pass

        return "unknown"

    # ------------------------------------------------------------------
    # Process extraction (Windows EPROCESS walking)
    # ------------------------------------------------------------------

    def _extract_processes(self, evidence: EvidenceSchema) -> List[Dict[str, Any]]:
        processes: List[Dict[str, Any]] = []

        try:
            data = self._read_full_or_sample(evidence)
            if not data:
                return processes

            # Scan for EPROCESS patterns: unique PID values in expected range
            # and adjacent valid pointers
            pid_pattern = struct.pack("<I", 4)  # System PID is usually 4
            search_offset = 0
            found_pids: set = set()

            while search_offset < len(data) - _EPROCESS_SIZE:
                # Look for potential EPROCESS: PID at known offset should be reasonable
                pid_offset = search_offset + _UNIQUE_PROCESS_ID_OFFSET
                if pid_offset + 4 > len(data):
                    break

                pid = struct.unpack_from("<I", data, pid_offset)[0]
                if pid == 0 or pid > 0xFFFF or pid in found_pids:
                    search_offset += 0x1000
                    continue

                # Validate active process links (forward and back pointers should be aligned)
                links_offset = search_offset + _ACTIVE_PROCESS_LINKS_OFFSET
                if links_offset + 8 > len(data):
                    break
                fwd_ptr = struct.unpack_from("<Q", data, links_offset)[0]
                bwd_ptr = struct.unpack_from("<Q", data, links_offset + 8)[0]

                # Pointers should be in reasonable kernel range (high canonical on x64)
                if not (0xFFFF000000000000 <= fwd_ptr <= 0xFFFFFFFFFFFFFFFF):
                    search_offset += 0x1000
                    continue
                if not (0xFFFF000000000000 <= bwd_ptr <= 0xFFFFFFFFFFFFFFFF):
                    search_offset += 0x1000
                    continue

                # Extract image name
                name_offset = search_offset + _IMAGE_FILE_NAME_OFFSET
                if name_offset + 16 > len(data):
                    search_offset += 0x1000
                    continue
                raw_name = data[name_offset : name_offset + 16]
                try:
                    proc_name = raw_name.split(b"\x00", 1)[0].decode("ascii", errors="ignore")
                except Exception:
                    proc_name = f"pid_{pid}"

                # Extract creation time (Windows FILETIME)
                create_offset = search_offset + _CREATE_TIME_OFFSET
                create_time_str = ""
                if create_offset + 8 <= len(data):
                    filetime = struct.unpack_from("<Q", data, create_offset)[0]
                    create_time_str = self._filetime_to_iso(filetime)

                # PEB address
                peb_offset_addr = search_offset + _PEB_OFFSET
                peb_val = 0
                if peb_offset_addr + 8 <= len(data):
                    peb_val = struct.unpack_from("<Q", data, peb_offset_addr)[0]

                process = {
                    "pid": pid,
                    "name": proc_name,
                    "create_time": create_time_str,
                    "peb_address": f"0x{peb_val:x}" if peb_val else None,
                    "eprocess_address": f"0x{search_offset:x}",
                }
                processes.append(process)
                found_pids.add(pid)

                evidence.add_entity(
                    name=proc_name,
                    entity_type="process",
                    properties=process,
                )
                evidence.add_tag("process")

                if create_time_str:
                    evidence.add_timeline_event(
                        create_time_str,
                        f"Process created: {proc_name} (PID {pid})",
                        self.name,
                    )

                search_offset += 0x1000
                if len(processes) >= 500:
                    break

        except Exception as exc:
            evidence.add_error(self.name, f"Process extraction failed: {exc}")

        evidence.metadata["processes"] = processes
        return processes

    # ------------------------------------------------------------------
    # Network connection extraction
    # ------------------------------------------------------------------

    def _extract_network_connections(self, evidence: EvidenceSchema) -> List[Dict[str, Any]]:
        connections: List[Dict[str, Any]] = []

        try:
            data = self._read_full_or_sample(evidence)
            if not data:
                return connections

            # Scan for TCP/UDP endpoint structures by looking for:
            # - Local address port (uint16 in network byte order)
            # - Remote address in reasonable IPv4 range
            # - State field in valid range
            offset = 0
            scan_limit = min(len(data) - 128, 512 * 1024)
            while offset < scan_limit:
                # Try to find port values in common ranges
                local_port = struct.unpack_from(">H", data, offset)[0]
                if 0 < local_port <= 65535 and local_port != 0:
                    remote_port = struct.unpack_from(">H", data, offset + 4)[0]
                    local_ip_raw = struct.unpack_from("<I", data, offset + 8)[0] if offset + 12 <= len(data) else 0
                    remote_ip_raw = struct.unpack_from("<I", data, offset + 12)[0] if offset + 16 <= len(data) else 0

                    # Validate: IPs should be non-zero and not broadcast
                    if (local_ip_raw and remote_ip_raw
                            and local_ip_raw != 0xFFFFFFFF
                            and remote_ip_raw != 0xFFFFFFFF):
                        conn = {
                            "local_ip": self._ip_to_str(local_ip_raw),
                            "local_port": local_port,
                            "remote_ip": self._ip_to_str(remote_ip_raw),
                            "remote_port": remote_port,
                            "protocol": "TCP",
                        }
                        connections.append(conn)
                        evidence.add_entity(
                            name=f"{conn['local_ip']}:{conn['local_port']} -> {conn['remote_ip']}:{conn['remote_port']}",
                            entity_type="network_connection",
                            properties=conn,
                        )
                        evidence.add_tag("network_connection")

                offset += 16
                if len(connections) >= 200:
                    break

        except Exception as exc:
            evidence.add_error(self.name, f"Network connection extraction failed: {exc}")

        evidence.metadata["network_connections"] = connections
        return connections

    # ------------------------------------------------------------------
    # DLL extraction
    # ------------------------------------------------------------------

    def _extract_dlls(self, evidence: EvidenceSchema) -> List[Dict[str, Any]]:
        dlls: List[Dict[str, Any]] = []

        try:
            data = self._read_full_or_sample(evidence)
            if not data:
                return dlls

            # Scan for PE headers (MZ + PE\0\0) followed by module name strings
            mz_offsets: List[int] = []
            search_offset = 0
            while search_offset < len(data) - 0x40:
                if data[search_offset : search_offset + 2] == b"MZ":
                    # Check for PE signature at e_lfanew
                    if search_offset + 0x40 <= len(data):
                        e_lfanew = struct.unpack_from("<I", data, search_offset + 0x3C)[0]
                        pe_offset = search_offset + e_lfanew
                        if pe_offset + 4 <= len(data):
                            pe_sig = data[pe_offset : pe_offset + 4]
                            if pe_sig == b"PE\x00\x00":
                                mz_offsets.append(search_offset)
                                if len(mz_offsets) >= 300:
                                    break
                search_offset += 0x1000

            # Try to extract module name from PE export table or filename
            for mz_off in mz_offsets:
                try:
                    e_lfanew = struct.unpack_from("<I", data, mz_off + 0x3C)[0]
                    pe_off = mz_off + e_lfanew
                    if pe_off + 0x18 > len(data):
                        continue

                    # Optional header magic
                    opt_magic = struct.unpack_from("<H", data, pe_off + 0x18)[0]
                    is_pe32_plus = opt_magic == 0x20b

                    # Export directory RVA
                    export_rva_off = pe_off + 0x18 + (0x70 if is_pe32_plus else 0x60)
                    if export_rva_off + 8 > len(data):
                        continue
                    export_rva = struct.unpack_from("<I", data, export_rva_off)[0]
                    export_size = struct.unpack_from("<I", data, export_rva_off + 4)[0]

                    if export_rva > 0 and export_size > 0:
                        # Attempt to find the DLL name string nearby
                        dll_name = self._find_pe_module_name(data, mz_off)
                        if dll_name:
                            dlls.append({
                                "base_address": f"0x{mz_off:x}",
                                "name": dll_name,
                                "pe_offset": f"0x{pe_off:x}",
                            })
                            evidence.add_entity(
                                name=dll_name,
                                entity_type="dll",
                                properties={"base_address": f"0x{mz_off:x}"},
                            )
                            evidence.add_relationship(
                                source="system",
                                target=dll_name,
                                rel_type="loaded_module",
                            )
                            evidence.add_tag("dll")
                except Exception:
                    continue

                if len(dlls) >= 200:
                    break

        except Exception as exc:
            evidence.add_error(self.name, f"DLL extraction failed: {exc}")

        evidence.metadata["loaded_dlls"] = dlls
        return dlls

    def _find_pe_module_name(self, data: bytes, mz_offset: int) -> Optional[str]:
        # Heuristic: look for a .dll or .exe string in a 4KB window after PE header
        window = data[mz_offset : mz_offset + 0x2000]
        for match in re.finditer(rb"([A-Za-z0-9_\-]{2,60}\.(dll|exe|sys))\x00", window):
            return match.group(1).decode("ascii", errors="ignore")
        return None

    # ------------------------------------------------------------------
    # Registry hive extraction
    # ------------------------------------------------------------------

    def _extract_registry_hives(self, evidence: EvidenceSchema) -> List[Dict[str, Any]]:
        hives: List[Dict[str, Any]] = []

        try:
            data = self._read_full_or_sample(evidence)
            if not data:
                return hives

            search_offset = 0
            while search_offset < len(data) - 4096:
                pos = data.find(_HIVE_SIGNATURE, search_offset)
                if pos == -1:
                    break

                # Validate regf header structure
                if pos + 4096 > len(data):
                    break

                hive = self._parse_regf_header(data, pos)
                if hive:
                    hives.append(hive)
                    evidence.add_entity(
                        name=hive.get("hive_name", f"registry_hive_0x{pos:x}"),
                        entity_type="registry_hive",
                        properties=hive,
                    )
                    evidence.add_tag("registry_hive")

                search_offset = pos + 4096
                if len(hives) >= 50:
                    break

        except Exception as exc:
            evidence.add_error(self.name, f"Registry hive extraction failed: {exc}")

        evidence.metadata["registry_hives"] = hives
        return hives

    def _parse_regf_header(self, data: bytes, offset: int) -> Optional[Dict[str, Any]]:
        try:
            sig = data[offset : offset + 4]
            if sig != _HIVE_SIGNATURE:
                return None

            seq1 = struct.unpack_from("<I", data, offset + 4)[0]
            seq2 = struct.unpack_from("<I", data, offset + 8)[0]

            # File name at offset + 48, 64 bytes UTF-16LE
            fname_raw = data[offset + 48 : offset + 48 + 64]
            try:
                fname = fname_raw.decode("utf-16-le").rstrip("\x00")
            except Exception:
                fname = ""

            return {
                "hive_name": fname or f"regf_0x{offset:x}",
                "sequence1": seq1,
                "sequence2": seq2,
                "consistent": seq1 == seq2,
                "offset_in_memory": f"0x{offset:x}",
            }
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Injected code detection
    # ------------------------------------------------------------------

    def _detect_injected_code(self, evidence: EvidenceSchema) -> List[Dict[str, Any]]:
        injections: List[Dict[str, Any]] = []

        try:
            data = self._read_full_or_sample(evidence)
            if not data:
                return injections

            shellcode_signatures = [
                b"\xfc\xe8",           # CLD; CALL rel32
                b"\x60\x8d\x3c\x24",   # PUSHAD; LEA EDI, [ESP]
                b"\x64\x8b\x35",       # MOV ESI, FS:[0x30] (PEB access)
                b"\x48\x89\xe5",       # MOV RBP, RSP (x64 prologue)
                b"\xe8\x00\x00\x00\x00",  # CALL $+5 (position independent)
            ]

            xor_patterns = [
                b"\x30",  # XOR AL, ...
                b"\x31",  # XOR r/m32, r32
                b"\x33",  # XOR r32, r/m32
            ]

            seen_offsets: set = set()

            for sig in shellcode_signatures:
                pos = 0
                while True:
                    idx = data.find(sig, pos)
                    if idx == -1:
                        break
                    if idx not in seen_offsets:
                        seen_offsets.add(idx)
                        injections.append({
                            "offset": f"0x{idx:x}",
                            "type": "potential_shellcode",
                            "signature": sig.hex(),
                        })
                        evidence.add_entity(
                            name=f"shellcode_0x{idx:x}",
                            entity_type="injected_code",
                            properties={"offset": f"0x{idx:x}", "signature": sig.hex()},
                        )
                        evidence.add_tag("injected_code")
                    pos = idx + len(sig)
                    if len(injections) >= 100:
                        break
                if len(injections) >= 100:
                    break

            # Check for XOR decoding loops followed by API calls (sample up to 1MB)
            sample_data = data[:1024 * 1024]
            for xor_sig in xor_patterns:
                pos = 0
                while len(injections) < 100:
                    idx = sample_data.find(xor_sig, pos)
                    if idx == -1:
                        break
                    window = sample_data[idx : idx + 32]
                    if b"\xe8" in window[2:] or b"\xe9" in window[2:]:
                        if idx not in seen_offsets:
                            seen_offsets.add(idx)
                            injections.append({
                                "offset": f"0x{idx:x}",
                                "type": "xor_decode_loop",
                            })
                            evidence.add_entity(
                                name=f"xor_decode_0x{idx:x}",
                                entity_type="injected_code",
                                properties={"offset": f"0x{idx:x}"},
                            )
                            evidence.add_tag("injected_code")
                    pos = idx + len(xor_sig)

        except Exception as exc:
            evidence.add_error(self.name, f"Injected code detection failed: {exc}")

        evidence.metadata["injected_code_detections"] = injections
        if injections:
            evidence.add_timeline_event(
                datetime.utcnow().isoformat(),
                f"Detected {len(injections)} potential injected code region(s)",
                self.name,
            )
        return injections

    # ------------------------------------------------------------------
    # String extraction
    # ------------------------------------------------------------------

    def _extract_strings(self, evidence: EvidenceSchema) -> Dict[str, Any]:
        results: Dict[str, Any] = {
            "ascii_count": 0,
            "unicode_count": 0,
            "ascii_sample": [],
            "unicode_sample": [],
        }

        min_len = 6
        ascii_strings: List[str] = []
        unicode_strings: List[str] = []

        try:
            file_size = os.path.getsize(evidence.storage_path)
            scan_limit = min(file_size, 4 * 1024 * 1024)
            with open(evidence.storage_path, "rb") as fh:
                chunk_size = 1024 * 1024
                offset = 0
                while offset < scan_limit:
                    chunk = fh.read(min(chunk_size, scan_limit - offset))
                    if not chunk:
                        break

                    # ASCII
                    for s in self._find_ascii(chunk, min_len):
                        ascii_strings.append(s)
                        if len(ascii_strings) >= 10000:
                            break

                    # Unicode UTF-16LE
                    for s in self._find_unicode(chunk, min_len):
                        unicode_strings.append(s)
                        if len(unicode_strings) >= 10000:
                            break

                    offset += len(chunk)
                    if len(ascii_strings) >= 10000:
                        break
        except Exception as exc:
            evidence.add_error(self.name, f"String extraction failed: {exc}")

        results["ascii_count"] = len(ascii_strings)
        results["unicode_count"] = len(unicode_strings)
        results["ascii_sample"] = ascii_strings[:500]
        results["unicode_sample"] = unicode_strings[:500]

        # Search for interesting strings (URLs, IPs, file paths, credentials)
        interesting = self._find_interesting_strings(ascii_strings + unicode_strings)
        results["interesting_strings"] = interesting

        evidence.metadata["memory_strings"] = results
        if interesting:
            evidence.add_tag("interesting_strings_found")

        # Build extracted text summary (only if no text yet)
        if (ascii_strings or unicode_strings) and not evidence.extracted_text:
            evidence.extracted_text = "\n".join(
                ascii_strings[:200] + unicode_strings[:200]
            )

        return results

    @staticmethod
    def _find_ascii(data: bytes, min_len: int = 6) -> List[str]:
        pattern = re.compile(rb"[\x20-\x7e]{" + str(min_len).encode() + rb",}")
        return [m.decode("ascii", errors="ignore") for m in pattern.findall(data)]

    @staticmethod
    def _find_unicode(data: bytes, min_len: int = 6) -> List[str]:
        pattern = re.compile(rb"(?:[\x20-\x7e]\x00){" + str(min_len).encode() + rb",}")
        return [m.decode("utf-16-le", errors="ignore") for m in pattern.findall(data)]

    def _find_interesting_strings(self, strings: List[str]) -> List[Dict[str, Any]]:
        interesting: List[Dict[str, Any]] = []
        patterns = {
            "url": re.compile(r"https?://[^\s\"'<>]{5,200}"),
            "ip_address": re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"),
            "file_path": re.compile(r"[A-Za-z]:\\[\w\\.\-]{5,200}"),
            "credential_hint": re.compile(
                r"(?i)(password|passwd|pwd|secret|token|api[_\-]?key|auth[_\-]?token)\s*[=:]\s*\S{3,100}"
            ),
            "email": re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),
        }
        for s in strings:
            for category, regex in patterns.items():
                for match in regex.finditer(s):
                    interesting.append({
                        "category": category,
                        "value": match.group()[:200],
                    })
                    if len(interesting) >= 500:
                        return interesting
        return interesting

    # ------------------------------------------------------------------
    # Credential metadata extraction (metadata only, not actual passwords)
    # ------------------------------------------------------------------

    def _extract_credentials_metadata(self, evidence: EvidenceSchema) -> List[Dict[str, Any]]:
        credentials: List[Dict[str, Any]] = []

        try:
            data = self._read_full_or_sample(evidence)
            if not data:
                return credentials

            # Search for DPAPI blob signatures
            dpapi_magic = b"\x01\x00\x00\x00"
            search_offset = 0
            while search_offset < len(data) - 64:
                pos = data.find(dpapi_magic, search_offset)
                if pos == -1:
                    break
                credentials.append({
                    "type": "dpapi_blob",
                    "offset": f"0x{pos:x}",
                })
                evidence.add_tag("dpapi_blob")
                search_offset = pos + 64
                if len(credentials) >= 50:
                    break

            # Search for NTLM hash patterns (32-byte hex in SAM/SECURITY hives)
            ntlm_pattern = re.compile(rb"([0-9a-fA-F]{32})")
            search_offset = 0
            while search_offset < len(data) - 1024:
                chunk = data[search_offset : search_offset + 1024 * 64]
                for match in ntlm_pattern.finditer(chunk):
                    val = match.group(1).decode("ascii")
                    # Skip obviously non-hash strings (all zeros, etc.)
                    if val == "0" * 32 or val == "f" * 32:
                        continue
                    credentials.append({
                        "type": "potential_ntlm_hash",
                        "value": val,
                        "offset": f"0x{search_offset + match.start():x}",
                    })
                    evidence.add_tag("credential_metadata")
                    if len(credentials) >= 20:
                        break
                search_offset += 1024 * 64
                if len(credentials) >= 20:
                    break

            # Check for LSASS process presence
            lsass_found = False
            for proc in evidence.metadata.get("processes", []):
                if proc.get("name", "").lower() in _LSASS_NAMES:
                    lsass_found = True
                    credentials.append({
                        "type": "lsass_process",
                        "pid": proc.get("pid"),
                        "offset": proc.get("eprocess_address"),
                    })
                    evidence.add_entity(
                        name="lsass.exe",
                        entity_type="credential_store",
                        properties=proc,
                    )
                    evidence.add_tag("lsass_found")
                    break

            if not lsass_found:
                # Scan raw for LSASS string
                lsass_bytes = b"lsass.exe"
                if data.find(lsass_bytes) != -1:
                    credentials.append({"type": "lsass_process_string_found"})
                    evidence.add_tag("lsass_found")

        except Exception as exc:
            evidence.add_error(self.name, f"Credential metadata extraction failed: {exc}")

        evidence.metadata["credential_metadata"] = credentials
        return credentials

    # ------------------------------------------------------------------
    # Process tree construction
    # ------------------------------------------------------------------

    def _build_process_tree(self, evidence: EvidenceSchema) -> Dict[int, List[int]]:
        tree: Dict[int, List[int]] = {}

        try:
            processes = evidence.metadata.get("processes", [])
            pid_to_proc = {p["pid"]: p for p in processes if "pid" in p}

            # Build parent-child relationships by scanning for parent PID patterns
            data = self._read_full_or_sample(evidence)
            if not data:
                return tree

            for proc in processes:
                pid = proc.get("pid")
                eprocess_addr = proc.get("eprocess_address")
                if not eprocess_addr:
                    continue
                try:
                    addr = int(eprocess_addr, 16)
                except (ValueError, TypeError):
                    continue

                # In EPROCESS, InheritedProcessId is typically at offset +0x290
                inherit_pid_off = addr + 0x290
                if inherit_pid_off + 4 <= len(data):
                    parent_pid = struct.unpack_from("<I", data, inherit_pid_off)[0]
                    if parent_pid in pid_to_proc and parent_pid != pid:
                        tree.setdefault(parent_pid, []).append(pid)
                        evidence.add_relationship(
                            source=pid_to_proc[parent_pid].get("name", str(parent_pid)),
                            target=proc.get("name", str(pid)),
                            rel_type="parent_child",
                        )
        except Exception as exc:
            evidence.add_error(self.name, f"Process tree construction failed: {exc}")

        evidence.metadata["process_tree"] = tree
        return tree

    # ------------------------------------------------------------------
    # Memory section analysis (RWX detection)
    # ------------------------------------------------------------------

    def _analyze_memory_sections(self, evidence: EvidenceSchema) -> List[Dict[str, Any]]:
        sections: List[Dict[str, Any]] = []

        try:
            data = self._read_full_or_sample(evidence)
            if not data:
                return sections

            # Scan for VirtualAddress / RegionSize / Protect patterns
            # Common VAD or VMA structures contain protection flags
            offset = 0
            while offset < len(data) - 32:
                # Look for section protection flags in kernel memory structures
                protect_val = struct.unpack_from("<I", data, offset)[0]

                # RWX protection: 0x40 (PAGE_EXECUTE_READWRITE) or masked flags
                if protect_val in (0x40, _MEM_RWX, 0x60):  # RWX variants
                    # Validate region size looks reasonable
                    region_size = struct.unpack_from("<Q", data, offset + 8)[0] if offset + 16 <= len(data) else 0
                    if 0x1000 <= region_size <= 0x10000000:
                        sections.append({
                            "offset": f"0x{offset:x}",
                            "protection": f"0x{protect_val:x}",
                            "region_size": region_size,
                            "flag": "RWX",
                        })
                        evidence.add_entity(
                            name=f"rwx_section_0x{offset:x}",
                            entity_type="memory_section",
                            properties={"protection": hex(protect_val), "size": region_size},
                        )
                        evidence.add_tag("rwx_memory_section")

                offset += 0x1000
                if len(sections) >= 100:
                    break

        except Exception as exc:
            evidence.add_error(self.name, f"Memory section analysis failed: {exc}")

        evidence.metadata["memory_sections"] = sections
        if sections:
            evidence.add_timeline_event(
                datetime.utcnow().isoformat(),
                f"Identified {len(sections)} RWX memory section(s) (potential injection)",
                self.name,
            )
        return sections

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _read_full_or_sample(self, evidence: EvidenceSchema, max_bytes: int = 16 * 1024 * 1024) -> Optional[bytes]:
        """Read the memory dump, capped at max_bytes to avoid OOM and excessive scanning time."""
        try:
            file_size = os.path.getsize(evidence.storage_path)
            with open(evidence.storage_path, "rb") as fh:
                return fh.read(min(file_size, max_bytes))
        except Exception as exc:
            evidence.add_error(self.name, f"Failed to read memory dump: {exc}")
            return None

    @staticmethod
    def _filetime_to_iso(filetime: int) -> str:
        """Convert Windows FILETIME to ISO 8601 string."""
        if filetime <= 0 or filetime > 0x7FFFFFFFFFFFFFFF:
            return ""
        try:
            # FILETIME: 100-ns intervals since 1601-01-01
            epoch_diff = 116444736000000000
            ts = (filetime - epoch_diff) / 10000000
            dt = datetime.utcfromtimestamp(ts)
            if dt.year < 1990 or dt.year > 2100:
                return ""
            return dt.isoformat()
        except (ValueError, OSError, OverflowError):
            return ""

    @staticmethod
    def _ip_to_str(ip_int: int) -> str:
        """Convert a 32-bit integer to dotted-quad IP string."""
        return f"{ip_int & 0xFF}.{(ip_int >> 8) & 0xFF}.{(ip_int >> 16) & 0xFF}.{(ip_int >> 24) & 0xFF}"
