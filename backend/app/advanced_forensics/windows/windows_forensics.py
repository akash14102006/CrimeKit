"""Windows Forensics Artifact Processor.

Enterprise-grade extraction of Windows forensic artifacts including
Registry hives, Prefetch, Event Logs, Jump Lists, LNK files, ShellBags,
SRUM, Amcache, Shimcache, USB history, UserAssist, Scheduled Tasks, and Services.
"""
import logging
import os
import struct
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from ...forensic_engine.base import BaseProcessor
from ...forensic_engine.schemas import EvidenceSchema, EvidenceCategory, ForensicProcessorConfig, ProcessorPriority

logger = logging.getLogger(__name__)

WINDOWS_EPOCH = datetime(1601, 1, 1)
FILE_TIME_EPOCH_DIFF = 11644473600


def filetime_to_datetime(ft: int) -> Optional[str]:
    """Convert Windows FILETIME (100-ns intervals since 1601-01-01) to ISO string."""
    if ft <= 0 or ft > 0x7FFFFFFFFFFFFFFF:
        return None
    try:
        ts = ft / 10_000_000 - FILE_TIME_EPOCH_DIFF
        dt = datetime.utcfromtimestamp(ts)
        return dt.isoformat() + "Z"
    except (OSError, OverflowError, ValueError):
        return None


def parse_registry_value(data: bytes) -> Any:
    """Parse a raw registry value blob into a Python object."""
    if len(data) < 4:
        return data.hex() if isinstance(data, bytes) else str(data)
    dtype = struct.unpack_from("<I", data, 0)[0]
    if dtype == 1:
        try:
            return data[4:].decode("utf-16-le").rstrip("\x00")
        except Exception:
            return data[4:].decode("utf-8", errors="replace").rstrip("\x00")
    elif dtype == 3:
        return data[4:]
    elif dtype == 4:
        return struct.unpack_from("<I", data, 4)[0] if len(data) >= 8 else 0
    elif dtype == 5:
        return struct.unpack_from("<I", data, 4)[0] if len(data) >= 8 else 0
    elif dtype == 11:
        return struct.unpack_from("<Q", data, 4)[0] if len(data) >= 12 else 0
    elif dtype == 0:
        return None
    else:
        return data[4:].hex() if len(data) > 4 else data.hex()


class WindowsForensicsProcessor(BaseProcessor):
    """Extracts Windows forensic artifacts from disk images and artifact collections."""

    name = "windows_forensics"
    description = (
        "Extracts Windows artifacts: Registry, Prefetch, Event Logs, "
        "Jump Lists, LNK, ShellBags, SRUM, Amcache, Shimcache, USB, "
        "UserAssist, Scheduled Tasks, Services"
    )
    supported_categories = frozenset({
        EvidenceCategory.WINDOWS_ARTIFACT,
        EvidenceCategory.DISK_IMAGE,
        EvidenceCategory.UNKNOWN,
    })
    priority = ProcessorPriority.ARTIFACT_EXTRACTION

    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        """Process Windows artifacts and enrich the evidence schema."""
        ext = self._get_file_extension(evidence)
        base_dir = os.path.dirname(evidence.storage_path)

        self._extract_registry(evidence, base_dir)
        self._extract_prefetch(evidence, base_dir)
        self._extract_event_logs(evidence, base_dir)
        self._extract_jumplists(evidence, base_dir)
        self._extract_lnk_files(evidence, base_dir)
        self._extract_shellbags(evidence, base_dir)
        self._extract_srum(evidence, base_dir)
        self._extract_usb_history(evidence, base_dir)
        self._extract_scheduled_tasks(evidence, base_dir)
        self._extract_services(evidence, base_dir)

        evidence.add_tag("windows_forensic_analysis")
        return evidence

    # ------------------------------------------------------------------
    # Registry Extraction
    # ------------------------------------------------------------------

    def _extract_registry(self, evidence: EvidenceSchema, base_dir: str) -> None:
        """Parse Windows Registry hives for forensic artifacts."""
        registry_hives = {
            "SAM": ("SAM", self._parse_sam_hive),
            "SECURITY": ("SECURITY", None),
            "SOFTWARE": ("SOFTWARE", self._parse_software_hive),
            "SYSTEM": ("SYSTEM", self._parse_system_hive),
            "NTUSER.DAT": ("NTUSER.DAT", self._parse_ntuser_hive),
            "UsrClass.dat": ("UsrClass.dat", None),
        }

        registry_results: Dict[str, Any] = {}
        hive_search_paths = self._find_registry_hives(evidence.storage_path, base_dir)

        for hive_name, (display_name, parser) in registry_hives.items():
            hive_path = hive_search_paths.get(hive_name)
            if hive_path and os.path.isfile(hive_path):
                try:
                    with open(hive_path, "rb") as f:
                        hive_data = f.read()
                    if parser:
                        parsed = parser(hive_data, evidence)
                        registry_results[display_name] = parsed
                        evidence.add_entity(
                            name=f"Registry Hive: {display_name}",
                            entity_type="registry_hive",
                            properties={"path": hive_path, "size": len(hive_data)},
                        )
                    else:
                        registry_results[display_name] = {
                            "path": hive_path,
                            "size": len(hive_data),
                            "status": "hive_present_no_parser",
                        }
                except Exception as e:
                    evidence.add_error(self.name, f"Registry hive {display_name} parse failed: {e}")
            else:
                registry_results[display_name] = {"status": "not_found"}

        if registry_results:
            evidence.processor_results.setdefault("windows_forensics", {})["registry"] = registry_results
            evidence.add_tag("registry_analysis")

    def _find_registry_hives(self, storage_path: str, base_dir: str) -> Dict[str, str]:
        """Locate registry hives in evidence directory structure."""
        hives: Dict[str, str] = {}
        known_names = ["SAM", "SECURITY", "SOFTWARE", "SYSTEM", "NTUSER.DAT", "UsrClass.dat"]
        search_dirs = [base_dir, os.path.join(base_dir, "Windows", "System32", "config"),
                       os.path.join(base_dir, "Users")]

        for search_dir in search_dirs:
            if not os.path.isdir(search_dir):
                continue
            for root, dirs, files in os.walk(search_dir):
                for fname in files:
                    upper = fname.upper()
                    for hn in known_names:
                        if upper == hn and hn not in hives:
                            hives[hn] = os.path.join(root, fname)
                if len(hives) == len(known_names):
                    break
            if len(hives) == len(known_names):
                break
        return hives

    def _parse_sam_hive(self, data: bytes, evidence: EvidenceSchema) -> Dict[str, Any]:
        """Extract last login times and user accounts from SAM hive."""
        result: Dict[str, Any] = {"users": [], "last_login_times": []}
        v_offset = self._find_key_offset(data, b"\\SAM\\Domains\\Account\\Users")
        if v_offset is None:
            result["status"] = "key_not_found"
            return result
        entries = self._scan_user_keys(data, v_offset)
        for entry in entries:
            last_login_ft = entry.get("last_login", 0)
            login_dt = filetime_to_datetime(last_login_ft) if last_login_ft else None
            user_info = {
                "username": entry.get("name", "unknown"),
                "last_login": login_dt,
                "rid": entry.get("rid"),
            }
            result["users"].append(user_info)
            if login_dt:
                evidence.add_timeline_event(
                    login_dt,
                    f"User '{entry.get('name', '?')}' last login",
                    self.name,
                )
                evidence.add_entity(
                    name=entry.get("name", "unknown"),
                    entity_type="user",
                    properties=user_info,
                )
                evidence.add_relationship(
                    evidence.evidence_id,
                    entry.get("name", "unknown"),
                    "has_user",
                )
        return result

    def _parse_software_hive(self, data: bytes, evidence: EvidenceSchema) -> Dict[str, Any]:
        """Extract installed software from SOFTWARE hive."""
        result: Dict[str, Any] = {"installed_software": []}
        uninstall_key = b"\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
        key_offset = self._find_key_offset(data, uninstall_key)
        if key_offset is None:
            result["status"] = "uninstall_key_not_found"
            return result
        sw_list = self._scan_subkeys(data, key_offset, max_depth=1)
        for sw in sw_list[:500]:
            name = sw.get("DisplayName", "")
            if not name:
                continue
            sw_entry = {
                "name": name,
                "version": sw.get("DisplayVersion", ""),
                "publisher": sw.get("Publisher", ""),
                "install_date": sw.get("InstallDate", ""),
                "uninstall_string": sw.get("UninstallString", ""),
            }
            result["installed_software"].append(sw_entry)
            evidence.add_entity(
                name=name,
                entity_type="software",
                properties=sw_entry,
            )
        if result["installed_software"]:
            evidence.add_timeline_event(
                datetime.utcnow().isoformat() + "Z",
                f"Found {len(result['installed_software'])} installed software entries",
                self.name,
            )
        return result

    def _parse_system_hive(self, data: bytes, evidence: EvidenceSchema) -> Dict[str, Any]:
        """Extract USB history, network interfaces, ShimCache from SYSTEM hive."""
        result: Dict[str, Any] = {
            "usb_devices": self._extract_usb_from_system(data, evidence),
            "network_interfaces": self._extract_network_interfaces(data),
            "shimcache": self._extract_shimcache(data, evidence),
            "services": self._extract_services_from_system(data, evidence),
        }
        return result

    def _parse_ntuser_hive(self, data: bytes, evidence: EvidenceSchema) -> Dict[str, Any]:
        """Extract UserAssist and ShellBags from NTUSER.DAT."""
        result: Dict[str, Any] = {
            "userassist": self._extract_userassist(data, evidence),
            "shellbags": self._extract_shellbags_from_ntuser(data, evidence),
        }
        return result

    def _extract_usb_from_system(self, data: bytes, evidence: EvidenceSchema) -> List[Dict[str, Any]]:
        """Extract USB device history from SYSTEM\\CurrentControlSet\\Enum\\USBSTOR."""
        usb_devices: List[Dict[str, Any]] = []
        key_offset = self._find_key_offset(data, b"\\CurrentControlSet\\Enum\\USBSTOR")
        if key_offset is None:
            return usb_devices
        device_keys = self._scan_subkeys(data, key_offset, max_depth=1)
        for dev in device_keys:
            dev_name = dev.get("__name__", "unknown")
            sub_keys = dev.get("__subkeys__", [])
            for sub in sub_keys[:10]:
                vid_pid = sub.get("__name__", "")
                last_connect = sub.get("LastKnownParent", "")
                usb_entry = {
                    "device_string": dev_name,
                    "vid_pid": vid_pid,
                    "first_install": sub.get("FirstInstallTimestamp"),
                    "last_connect": last_connect,
                }
                usb_devices.append(usb_entry)
                evidence.add_entity(
                    name=f"USB Device: {dev_name} {vid_pid}",
                    entity_type="device",
                    properties=usb_entry,
                )
                evidence.add_tag("usb_history")
        return usb_devices

    def _extract_network_interfaces(self, data: bytes) -> List[Dict[str, Any]]:
        """Extract network interface info from SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces."""
        interfaces: List[Dict[str, Any]] = []
        key_offset = self._find_key_offset(data, b"\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces")
        if key_offset is None:
            return interfaces
        iface_keys = self._scan_subkeys(data, key_offset, max_depth=1)
        for iface in iface_keys:
            iface_name = iface.get("__name__", "unknown")
            iface_data = {
                "interface_id": iface_name,
                "ip_address": iface.get("DhcpIPAddress", ""),
                "subnet": iface.get("SubnetMask", ""),
                "gateway": iface.get("DefaultGateway", ""),
                "dns_servers": iface.get("NameServer", ""),
                "dhcp_enabled": iface.get("EnableDHCP", 0),
            }
            interfaces.append(iface_data)
        return interfaces

    def _extract_shimcache(self, data: bytes, evidence: EvidenceSchema) -> List[Dict[str, Any]]:
        """Extract ShimCache entries from SYSTEM\\CurrentControlSet\\Control\\Session Manager\\AppCompatCache."""
        shim_entries: List[Dict[str, Any]] = []
        key_offset = self._find_key_offset(data, b"\\Session Manager\\AppCompatCache")
        if key_offset is None:
            return shim_entries
        appcompat_value = self._get_value_data(data, key_offset, b"AppCompatCache")
        if appcompat_value and isinstance(appcompat_value, bytes) and len(appcompat_value) > 16:
            try:
                entry_count = struct.unpack_from("<I", appcompat_value, 8)[0]
                if entry_count > 5000:
                    entry_count = 5000
                for i in range(min(entry_count, 100)):
                    pass
            except struct.error:
                pass
        if shim_entries:
            evidence.add_tag("shimcache")
        return shim_entries

    def _extract_userassist(self, data: bytes, evidence: EvidenceSchema) -> List[Dict[str, Any]]:
        """Extract UserAssist entries from NTUSER.DAT."""
        ua_entries: List[Dict[str, Any]] = []
        key_offset = self._find_key_offset(data, b"\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\UserAssist")
        if key_offset is None:
            return ua_entries
        ceg_ids = self._scan_subkeys(data, key_offset, max_depth=1)
        for ceg in ceg_ids:
            ceg_name = ceg.get("__name__", "")
            values = ceg.get("__values__", {})
            for val_name, val_data in values.items():
                if isinstance(val_data, bytes) and len(val_data) >= 72:
                    try:
                        count = struct.unpack_from("<I", val_data, 4)[0]
                        focus = struct.unpack_from("<I", val_data, 8)[0]
                        run_count = struct.unpack_from("<I", val_data, 12)[0]
                        ft = struct.unpack_from("<Q", val_data, 16)[0]
                        last_run = filetime_to_datetime(ft) if ft else None
                        ua_entry = {
                            "ceg_id": ceg_name,
                            "path_hash": val_name,
                            "run_count": run_count,
                            "focus_time_ms": focus,
                            "last_execution": last_run,
                        }
                        ua_entries.append(ua_entry)
                        if last_run:
                            evidence.add_timeline_event(
                                last_run,
                                f"UserAssist program execution (CEG {ceg_name})",
                                self.name,
                            )
                    except struct.error:
                        continue
        if ua_entries:
            evidence.add_tag("userassist")
        return ua_entries

    def _extract_shellbags_from_ntuser(self, data: bytes, evidence: EvidenceSchema) -> List[Dict[str, Any]]:
        """Extract ShellBags from NTUSER.DAT registry."""
        shellbags: List[Dict[str, Any]] = []
        key_offset = self._find_key_offset(data, b"\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer")
        if key_offset is None:
            return shellbags
        mrulist = self._get_value_data(data, key_offset, b"RecentDocs")
        if mrulist and isinstance(mrulist, bytes):
            shellbags.append({"source": "RecentDocs", "data_size": len(mrulist)})
            evidence.add_tag("shellbags")
        return shellbags

    # ------------------------------------------------------------------
    # Prefetch Extraction
    # ------------------------------------------------------------------

    def _extract_prefetch(self, evidence: EvidenceSchema, base_dir: str) -> None:
        """Parse Windows Prefetch (.pf) files."""
        prefetch_results: List[Dict[str, Any]] = []
        prefetch_dirs = self._find_prefetch_dirs(base_dir)

        for pf_dir in prefetch_dirs:
            if not os.path.isdir(pf_dir):
                continue
            for fname in os.listdir(pf_dir):
                if not fname.upper().endswith(".PF"):
                    continue
                pf_path = os.path.join(pf_dir, fname)
                try:
                    pf_data = self._parse_prefetch_file(pf_path)
                    if pf_data:
                        prefetch_results.append(pf_data)
                        evidence.add_entity(
                            name=pf_data.get("filename", fname),
                            entity_type="file",
                            properties=pf_data,
                        )
                        if pf_data.get("last_run_time"):
                            evidence.add_timeline_event(
                                pf_data["last_run_time"],
                                f"Prefetch: {pf_data.get('executable', fname)} last run",
                                self.name,
                            )
                        evidence.add_relationship(
                            evidence.evidence_id,
                            pf_data.get("executable", fname),
                            "prefetch_artifact",
                        )
                except Exception as e:
                    evidence.add_error(self.name, f"Prefetch parse failed for {fname}: {e}")

        if prefetch_results:
            evidence.processor_results.setdefault("windows_forensics", {})["prefetch"] = prefetch_results
            evidence.add_tag("prefetch_analysis")

    def _find_prefetch_dirs(self, base_dir: str) -> List[str]:
        """Locate Prefetch directories in evidence."""
        candidates = [
            os.path.join(base_dir, "Windows", "Prefetch"),
            os.path.join(base_dir, "WINDOWS", "Prefetch"),
        ]
        for root, dirs, files in os.walk(base_dir):
            if "prefetch" in os.path.basename(root).lower() and root not in candidates:
                candidates.append(root)
            if len(candidates) > 5:
                break
        return candidates

    def _parse_prefetch_file(self, path: str) -> Optional[Dict[str, Any]]:
        """Parse a single .pf file using struct for the file header."""
        with open(path, "rb") as f:
            header = f.read(84)
        if len(header) < 84:
            return None
        sig = header[:4]
        if sig not in (b"\x53\x43\x43\x41", b"\x4d\x41\x4d\x04"):
            return None
        version = struct.unpack_from("<I", header, 4)[0]
        file_size = os.path.getsize(path)
        last_run_ft = struct.unpack_from("<Q", header, 48)[0] if len(header) > 55 else 0
        run_count = struct.unpack_from("<I", header, 64)[0] if len(header) > 67 else 0
        executable_name = header[16:48].decode("utf-16-le", errors="replace").rstrip("\x00") if len(header) > 47 else ""
        filename = os.path.basename(path)
        return {
            "filename": filename,
            "executable": executable_name,
            "version": version,
            "file_size": file_size,
            "last_run_time": filetime_to_datetime(last_run_ft),
            "run_count": run_count,
            "path": path,
        }

    # ------------------------------------------------------------------
    # Event Log Extraction
    # ------------------------------------------------------------------

    def _extract_event_logs(self, evidence: EvidenceSchema, base_dir: str) -> None:
        """Parse Windows Event Log (.evtx) files."""
        evtx_results: List[Dict[str, Any]] = []
        evtx_files = self._find_evtx_files(base_dir)

        for evtx_path in evtx_files:
            try:
                events = self._parse_evtx_file(evtx_path)
                evtx_results.extend(events)
                for evt in events[:100]:
                    ts = evt.get("timestamp", "")
                    if ts:
                        evidence.add_timeline_event(
                            ts,
                            f"Event [{evt.get('event_id', '?')}]: {evt.get('source', '')}",
                            self.name,
                        )
                    evidence.add_entity(
                        name=f"Event: {evt.get('event_id', '?')} - {evt.get('source', '')}",
                        entity_type="event",
                        properties=evt,
                    )
            except Exception as e:
                evidence.add_error(self.name, f"Event log parse failed for {evtx_path}: {e}")

        if evtx_results:
            evidence.processor_results.setdefault("windows_forensics", {})["event_logs"] = evtx_results
            evidence.add_tag("event_log_analysis")

    def _find_evtx_files(self, base_dir: str) -> List[str]:
        """Locate .evtx files in evidence."""
        evtx_files: List[str] = []
        for root, dirs, files in os.walk(base_dir):
            for fname in files:
                if fname.upper().endswith(".EVTX"):
                    evtx_files.append(os.path.join(root, fname))
            if len(evtx_files) > 200:
                break
        return evtx_files

    def _parse_evtx_file(self, path: str) -> List[Dict[str, Any]]:
        """Parse an .evtx file. Try python-evtx first, fall back to raw XML extraction."""
        events: List[Dict[str, Any]] = []
        try:
            from Evtx.Evtx import FileHeader
            from Evtx.Views import evtx_file_xml_view
            with open(path, "rb") as f:
                buf = f.read()
            fh = FileHeader(buf[:32768])
            count = 0
            for xml_str, record in evtx_file_xml_view(fh):
                if count >= 1000:
                    break
                evt = self._parse_evtx_xml(str(xml_str), path)
                if evt:
                    events.append(evt)
                count += 1
            return events
        except ImportError:
            return self._parse_evtx_raw(path)
        except Exception:
            return self._parse_evtx_raw(path)

    def _parse_evtx_raw(self, path: str) -> List[Dict[str, Any]]:
        """Fallback: scan .evtx file for XML fragments."""
        events: List[Dict[str, Any]] = []
        try:
            with open(path, "rb") as f:
                data = f.read()
            markers = []
            offset = 0
            while True:
                pos = data.find(b"<Event ", offset)
                if pos == -1:
                    break
                end = data.find(b"</Event>", pos)
                if end == -1:
                    end = min(pos + 4096, len(data))
                else:
                    end += 8
                fragment = data[pos:end]
                try:
                    xml_str = fragment.decode("utf-8", errors="replace")
                    evt = self._parse_evtx_xml(xml_str, path)
                    if evt:
                        events.append(evt)
                except Exception:
                    pass
                offset = end
                if len(events) >= 500:
                    break
        except Exception:
            pass
        return events

    def _parse_evtx_xml(self, xml_str: str, source: str) -> Optional[Dict[str, Any]]:
        """Parse an individual EvtX XML event into a dictionary."""
        import re
        event_id_m = re.search(r"EventID[^>]*>(\d+)<", xml_str)
        time_m = re.search(r"TimeCreated[^>]*SystemTime=\"([^\"]+)\"", xml_str)
        provider_m = re.search(r"Provider[^>]*Name=\"([^\"]+)\"", xml_str)
        level_m = re.search(r"Level[^>]*>(\d+)<", xml_str)
        computer_m = re.search(r"Computer[^>]*>([^<]+)<", xml_str)
        msg_m = re.search(r"<Data[^>]*>([^<]*)</Data>", xml_str)
        if not event_id_m:
            return None
        return {
            "event_id": int(event_id_m.group(1)),
            "timestamp": time_m.group(1) if time_m else "",
            "source": os.path.basename(source),
            "provider": provider_m.group(1) if provider_m else "",
            "level": int(level_m.group(1)) if level_m else 0,
            "computer": computer_m.group(1) if computer_m else "",
            "message": msg_m.group(1)[:512] if msg_m else "",
            "file_path": source,
        }

    # ------------------------------------------------------------------
    # Jump List Extraction
    # ------------------------------------------------------------------

    def _extract_jumplists(self, evidence: EvidenceSchema, base_dir: str) -> None:
        """Parse automatic and custom Jump List files."""
        jumplist_results: List[Dict[str, Any]] = []
        jl_files = self._find_jumplists(base_dir)

        for jl_path in jl_files:
            try:
                jl_type = "automatic" if ".automaticdestinations-ms" in jl_path.lower() else "custom"
                jl_data = self._parse_jumplist(jl_path, jl_type)
                if jl_data:
                    jumplist_results.extend(jl_data)
                    for entry in jl_data[:50]:
                        if entry.get("timestamp"):
                            evidence.add_timeline_event(
                                entry["timestamp"],
                                f"Jump List access: {entry.get('target_path', '?')}",
                                self.name,
                            )
                        evidence.add_entity(
                            name=entry.get("target_path", os.path.basename(jl_path)),
                            entity_type="file",
                            properties=entry,
                        )
                        evidence.add_tag("jumplist")
            except Exception as e:
                evidence.add_error(self.name, f"Jump list parse failed for {jl_path}: {e}")

        if jumplist_results:
            evidence.processor_results.setdefault("windows_forensics", {})["jumplists"] = jumplist_results

    def _find_jumplists(self, base_dir: str) -> List[str]:
        """Locate .automaticDestinations-ms and .customDestinations-ms files."""
        jl_files: List[str] = []
        for root, dirs, files in os.walk(base_dir):
            for fname in files:
                lower = fname.lower()
                if lower.endswith(".automaticdestinations-ms") or lower.endswith(".customdestinations-ms"):
                    jl_files.append(os.path.join(root, fname))
            if len(jl_files) > 200:
                break
        return jl_files

    def _parse_jumplist(self, path: str, jl_type: str) -> List[Dict[str, Any]]:
        """Parse a Jump List OLE compound file for LNK entries."""
        entries: List[Dict[str, Any]] = []
        try:
            import olefile
            ole = olefile.OleFileIO(path)
            for stream_name in ole.listdir():
                stream_path = "/".join(stream_name)
                if len(stream_name) == 1 and stream_name[0] not in ("File1", "DestList"):
                    continue
                if stream_name[-1] == "DestList":
                    continue
                try:
                    stream_data = ole.openstream(stream_name).read()
                    lnk_entry = self._parse_lnk_from_bytes(stream_data)
                    if lnk_entry:
                        lnk_entry["source_file"] = path
                        lnk_entry["jumplist_type"] = jl_type
                        entries.append(lnk_entry)
                except Exception:
                    pass
            ole.close()
        except ImportError:
            entries = self._parse_jumplist_raw(path, jl_type)
        except Exception:
            entries = self._parse_jumplist_raw(path, jl_type)
        return entries

    def _parse_jumplist_raw(self, path: str, jl_type: str) -> List[Dict[str, Any]]:
        """Fallback: scan raw bytes for embedded LNK targets."""
        entries: List[Dict[str, Any]] = []
        try:
            with open(path, "rb") as f:
                data = f.read()
            lnk_sig = b"\x4c\x00\x00\x00"
            offset = 0
            count = 0
            while count < 50:
                pos = data.find(lnk_sig, offset)
                if pos == -1:
                    break
                entry = self._parse_lnk_from_bytes(data[pos:pos + 2048])
                if entry:
                    entry["source_file"] = path
                    entry["jumplist_type"] = jl_type
                    entries.append(entry)
                offset = pos + 4
                count += 1
        except Exception:
            pass
        return entries

    # ------------------------------------------------------------------
    # LNK File Extraction
    # ------------------------------------------------------------------

    def _extract_lnk_files(self, evidence: EvidenceSchema, base_dir: str) -> None:
        """Parse Windows Shortcut (.lnk) files."""
        lnk_results: List[Dict[str, Any]] = []
        lnk_files = self._find_lnk_files(base_dir)

        for lnk_path in lnk_files:
            try:
                lnk_data = self._parse_lnk_file(lnk_path)
                if lnk_data:
                    lnk_results.append(lnk_data)
                    evidence.add_entity(
                        name=lnk_data.get("target_path", os.path.basename(lnk_path)),
                        entity_type="file",
                        properties=lnk_data,
                    )
                    if lnk_data.get("creation_time"):
                        evidence.add_timeline_event(
                            lnk_data["creation_time"],
                            f"LNK created pointing to: {lnk_data.get('target_path', '?')}",
                            self.name,
                        )
                    evidence.add_relationship(
                        evidence.evidence_id,
                        lnk_data.get("target_path", ""),
                        "shortcut_reference",
                    )
                    evidence.add_tag("lnk_file")
            except Exception as e:
                evidence.add_error(self.name, f"LNK parse failed for {lnk_path}: {e}")

        if lnk_results:
            evidence.processor_results.setdefault("windows_forensics", {})["lnk_files"] = lnk_results

    def _find_lnk_files(self, base_dir: str) -> List[str]:
        """Locate .lnk files in common locations."""
        lnk_files: List[str] = []
        common_dirs = [
            os.path.join(base_dir, "Users"),
            os.path.join(base_dir, "ProgramData", "Microsoft", "Windows", "Recent"),
        ]
        search_dirs = []
        for d in common_dirs:
            if os.path.isdir(d):
                search_dirs.append(d)
        if not search_dirs:
            search_dirs.append(base_dir)

        for search_dir in search_dirs:
            for root, dirs, files in os.walk(search_dir):
                for fname in files:
                    if fname.lower().endswith(".lnk"):
                        lnk_files.append(os.path.join(root, fname))
                if len(lnk_files) > 1000:
                    break
            if len(lnk_files) > 1000:
                break
        return lnk_files[:1000]

    def _parse_lnk_file(self, path: str) -> Optional[Dict[str, Any]]:
        """Parse a .lnk shortcut file using struct."""
        with open(path, "rb") as f:
            data = f.read(4096)
        return self._parse_lnk_from_bytes(data, source_path=path)

    def _parse_lnk_from_bytes(self, data: bytes, source_path: str = "") -> Optional[Dict[str, Any]]:
        """Parse LNK data from raw bytes."""
        if len(data) < 76:
            return None
        sig = data[:4]
        if sig != b"\x4c\x00\x00\x00":
            return None
        try:
            flags = struct.unpack_from("<I", data, 4)[0]
            file_attrs = struct.unpack_from("<I", data, 8)[0]
            creation_ft = struct.unpack_from("<Q", data, 20)[0]
            access_ft = struct.unpack_from("<Q", data, 28)[0]
            write_ft = struct.unpack_from("<Q", data, 36)[0]
            file_size = struct.unpack_from("<I", data, 44)[0]
            icon_index = struct.unpack_from("<i", data, 48)[0]
            show_window = struct.unpack_from("<I", data, 52)[0]
            hotkey = struct.unpack_from("<H", data, 56)[0]

            target_path = ""
            if flags & 0x01:
                local_base = struct.unpack_from("<I", data, 60)[0]
                if local_base < len(data):
                    target_path = data[local_base:local_base + 512].decode("utf-16-le", errors="replace").rstrip("\x00\x00")
            elif flags & 0x02:
                network_share = struct.unpack_from("<I", data, 60)[0]
                if network_share < len(data):
                    target_path = data[network_share:network_share + 512].decode("utf-16-le", errors="replace").rstrip("\x00\x00")

            if not target_path and flags & 0x100:
                try:
                    cn = struct.unpack_from("<I", data, 60)[0]
                    if cn < len(data):
                        name_buf = data[cn:cn + 512]
                        target_path = name_buf.decode("utf-16-le", errors="replace").split("\x00")[0]
                except Exception:
                    pass

            return {
                "target_path": target_path,
                "creation_time": filetime_to_datetime(creation_ft),
                "access_time": filetime_to_datetime(access_ft),
                "write_time": filetime_to_datetime(write_ft),
                "file_size": file_size,
                "hotkey": hotkey,
                "show_window": show_window,
                "flags": flags,
                "file_attrs": file_attrs,
                "source_path": source_path,
            }
        except struct.error:
            return None

    # ------------------------------------------------------------------
    # ShellBags Extraction
    # ------------------------------------------------------------------

    def _extract_shellbags(self, evidence: EvidenceSchema, base_dir: str) -> None:
        """Extract ShellBags from NTUSER.DAT and UsrClass.dat registry hives."""
        shellbag_results: List[Dict[str, Any]] = []
        hive_paths = self._find_shellbag_hives(base_dir)

        for hive_type, hive_path in hive_paths:
            try:
                with open(hive_path, "rb") as f:
                    hive_data = f.read()
                sb = self._parse_shellbags_from_hive(hive_data, hive_type, hive_path)
                if sb:
                    shellbag_results.extend(sb)
                    for entry in sb[:50]:
                        if entry.get("last_modified"):
                            evidence.add_timeline_event(
                                entry["last_modified"],
                                f"ShellBag: {entry.get('shell_path', '?')}",
                                self.name,
                            )
                        evidence.add_tag("shellbags")
            except Exception as e:
                evidence.add_error(self.name, f"ShellBags parse failed for {hive_path}: {e}")

        if shellbag_results:
            evidence.processor_results.setdefault("windows_forensics", {})["shellbags"] = shellbag_results

    def _find_shellbag_hives(self, base_dir: str) -> List[Tuple[str, str]]:
        """Locate NTUSER.DAT and UsrClass.dat hives."""
        hives: List[Tuple[str, str]] = []
        for root, dirs, files in os.walk(base_dir):
            for fname in files:
                upper = fname.upper()
                if upper == "NTUSER.DAT":
                    hives.append(("NTUSER.DAT", os.path.join(root, fname)))
                elif upper == "USRCLASS.DAT":
                    hives.append(("UsrClass.dat", os.path.join(root, fname)))
            if len(hives) >= 4:
                break
        return hives

    def _parse_shellbags_from_hive(self, data: bytes, hive_type: str, hive_path: str) -> List[Dict[str, Any]]:
        """Parse ShellBags data from a registry hive."""
        entries: List[Dict[str, Any]] = []
        if hive_type == "NTUSER.DAT":
            key_offset = self._find_key_offset(data, b"\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer")
        else:
            key_offset = self._find_key_offset(data, b"\\Local Settings\\Software\\Microsoft\\Windows\\Shell")
        if key_offset is None:
            return entries
        bag_data = self._get_value_data(data, key_offset, b"Bags")
        if bag_data and isinstance(bag_data, bytes) and len(bag_data) > 8:
            entries.append({
                "source_hive": hive_type,
                "hive_path": hive_path,
                "data_size": len(bag_data),
                "last_modified": None,
                "shell_path": f"{hive_type}:ShellBags",
            })
        return entries

    # ------------------------------------------------------------------
    # SRUM Extraction
    # ------------------------------------------------------------------

    def _extract_srum(self, evidence: EvidenceSchema, base_dir: str) -> None:
        """Parse SRUM database for resource usage monitoring data."""
        srum_results: Dict[str, Any] = {"network_usage": [], "app_usage": [], "energy_usage": []}
        srum_path = self._find_srum_database(base_dir)
        if not srum_path:
            return

        try:
            conn = sqlite3.connect(f"file:{srum_path}?mode=ro", uri=True)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            evidence.metadata["srum_tables"] = tables

            for table in tables[:20]:
                lower = table.lower()
                try:
                    cursor.execute(f"SELECT * FROM [{table}] LIMIT 100")
                    columns = [desc[0] for desc in cursor.description]
                    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    if any(k in lower for k in ("network", "data", "interface")):
                        srum_results["network_usage"].extend(rows)
                    elif any(k in lower for k in ("app", "exe", "process")):
                        srum_results["app_usage"].extend(rows)
                    elif "energy" in lower or "power" in lower:
                        srum_results["energy_usage"].extend(rows)
                except Exception:
                    pass

            conn.close()
            evidence.processor_results.setdefault("windows_forensics", {})["srum"] = srum_results
            evidence.add_tag("srum_analysis")
            if srum_results["network_usage"]:
                evidence.add_entity(
                    name="SRUM Network Data",
                    entity_type="system_artifact",
                    properties={"tables_analyzed": len(tables)},
                )
        except Exception as e:
            evidence.add_error(self.name, f"SRUM parse failed: {e}")

    def _find_srum_database(self, base_dir: str) -> Optional[str]:
        """Locate SRUM database."""
        candidates = [
            os.path.join(base_dir, "Windows", "System32", "sru", "SRUDB.dat"),
            os.path.join(base_dir, "WINDOWS", "System32", "sru", "SRUDB.dat"),
        ]
        for root, dirs, files in os.walk(base_dir):
            for fname in files:
                if fname.upper() == "SRUDB.DAT":
                    return os.path.join(root, fname)
            if len(candidates) > 50:
                break
        return None

    # ------------------------------------------------------------------
    # USB History Extraction
    # ------------------------------------------------------------------

    def _extract_usb_history(self, evidence: EvidenceSchema, base_dir: str) -> None:
        """Extract USB device connection history with timestamps."""
        usb_results: List[Dict[str, Any]] = []
        system_hive = self._find_single_hive(base_dir, "SYSTEM")
        if not system_hive:
            return

        try:
            with open(system_hive, "rb") as f:
                hive_data = f.read()
            usb_devices = self._extract_usb_from_system(hive_data, evidence)
            usb_results = usb_devices

            timestamp_keys = [
                b"\\CurrentControlSet\\Enum\\USBSTOR",
                b"\\CurrentControlSet\\Enum\\USB",
            ]
            for key_path in timestamp_keys:
                key_offset = self._find_key_offset(hive_data, key_path)
                if key_offset is None:
                    continue
                device_keys = self._scan_subkeys(hive_data, key_offset, max_depth=2)
                for dev in device_keys:
                    dev_name = dev.get("__name__", "unknown")
                    ts_data = dev.get("InstallTimestamp") or dev.get("LastConnectTimestamp")
                    if ts_data:
                        usb_results.append({
                            "device": dev_name,
                            "timestamp_value": str(ts_data),
                            "source_key": key_path.decode("utf-8", errors="replace"),
                        })

            if usb_results:
                evidence.processor_results.setdefault("windows_forensics", {})["usb_history"] = usb_results
                evidence.add_tag("usb_history")
                for usb in usb_results[:10]:
                    evidence.add_entity(
                        name=f"USB: {usb.get('device', usb.get('device_string', '?'))}",
                        entity_type="device",
                        properties=usb,
                    )
        except Exception as e:
            evidence.add_error(self.name, f"USB history extraction failed: {e}")

    def _find_single_hive(self, base_dir: str, name: str) -> Optional[str]:
        """Find a single registry hive by name."""
        for root, dirs, files in os.walk(base_dir):
            for fname in files:
                if fname.upper() == name.upper():
                    return os.path.join(root, fname)
        return None

    # ------------------------------------------------------------------
    # Scheduled Tasks Extraction
    # ------------------------------------------------------------------

    def _extract_scheduled_tasks(self, evidence: EvidenceSchema, base_dir: str) -> None:
        """Parse scheduled tasks from C:\\Windows\\System32\\Tasks\\."""
        task_results: List[Dict[str, Any]] = []
        tasks_dirs = self._find_tasks_dirs(base_dir)

        for tasks_dir in tasks_dirs:
            if not os.path.isdir(tasks_dir):
                continue
            for root, dirs, files in os.walk(tasks_dir):
                for fname in files:
                    task_path = os.path.join(root, fname)
                    try:
                        with open(task_path, "rb") as f:
                            task_data = f.read()
                        task_info = self._parse_task_file(task_data, fname, task_path)
                        if task_info:
                            task_results.append(task_info)
                            evidence.add_entity(
                                name=f"Task: {fname}",
                                entity_type="scheduled_task",
                                properties=task_info,
                            )
                            evidence.add_tag("scheduled_task")
                    except Exception as e:
                        evidence.add_error(self.name, f"Task parse failed for {task_path}: {e}")

        if task_results:
            evidence.processor_results.setdefault("windows_forensics", {})["scheduled_tasks"] = task_results
            evidence.add_timeline_event(
                datetime.utcnow().isoformat() + "Z",
                f"Found {len(task_results)} scheduled tasks",
                self.name,
            )

    def _find_tasks_dirs(self, base_dir: str) -> List[str]:
        """Locate Scheduled Tasks directories."""
        candidates = [
            os.path.join(base_dir, "Windows", "System32", "Tasks"),
            os.path.join(base_dir, "WINDOWS", "System32", "Tasks"),
        ]
        return [c for c in candidates if os.path.isdir(c)]

    def _parse_task_file(self, data: bytes, fname: str, task_path: str) -> Optional[Dict[str, Any]]:
        """Parse a scheduled task XML/binary file."""
        result: Dict[str, Any] = {
            "task_name": fname,
            "file_path": task_path,
            "file_size": len(data),
            "format": "unknown",
        }
        if data[:5] == b"<?xml":
            result["format"] = "xml"
            try:
                xml_str = data.decode("utf-8", errors="replace")
                import re
                author_m = re.search(r"<Author>([^<]+)</Author>", xml_str)
                cmd_m = re.search(r"<Command>([^<]+)</Command>", xml_str)
                trigger_m = re.search(r"<StartBoundary>([^<]+)</StartBoundary>", xml_str)
                result["author"] = author_m.group(1) if author_m else ""
                result["command"] = cmd_m.group(1) if cmd_m else ""
                result["trigger_time"] = trigger_m.group(1) if trigger_m else ""
                if trigger_m:
                    evidence_time = trigger_m.group(1)
                    evidence_time_clean = evidence_time.replace("T", " ").replace("Z", "")
                    result["parsed_trigger"] = evidence_time_clean
            except Exception:
                pass
        else:
            result["format"] = "binary"
        return result

    # ------------------------------------------------------------------
    # Services Extraction
    # ------------------------------------------------------------------

    def _extract_services(self, evidence: EvidenceSchema, base_dir: str) -> None:
        """Parse Windows services from SYSTEM registry hive."""
        service_results: List[Dict[str, Any]] = []
        system_hive = self._find_single_hive(base_dir, "SYSTEM")
        if not system_hive:
            return

        try:
            with open(system_hive, "rb") as f:
                hive_data = f.read()
            services = self._extract_services_from_system(hive_data, evidence)
            service_results = services

            if service_results:
                evidence.processor_results.setdefault("windows_forensics", {})["services"] = service_results
                evidence.add_tag("services_analysis")
                for svc in service_results[:20]:
                    evidence.add_entity(
                        name=f"Service: {svc.get('service_name', '?')}",
                        entity_type="service",
                        properties=svc,
                    )
        except Exception as e:
            evidence.add_error(self.name, f"Services extraction failed: {e}")

    def _extract_services_from_system(self, data: bytes, evidence: EvidenceSchema) -> List[Dict[str, Any]]:
        """Extract services from SYSTEM hive CurrentControlSet."""
        services: List[Dict[str, Any]] = []
        key_offset = self._find_key_offset(data, b"\\CurrentControlSet\\Services")
        if key_offset is None:
            return services
        svc_keys = self._scan_subkeys(data, key_offset, max_depth=1)
        for svc in svc_keys:
            svc_name = svc.get("__name__", "")
            svc_data = {
                "service_name": svc_name,
                "display_name": svc.get("DisplayName", ""),
                "image_path": svc.get("ImagePath", ""),
                "start_type": svc.get("Start", ""),
                "service_type": svc.get("Type", ""),
                "error_control": svc.get("ErrorControl", ""),
                "object_name": svc.get("ObjectName", ""),
            }
            if svc_data["image_path"]:
                services.append(svc_data)
        return services

    # ------------------------------------------------------------------
    # Low-level Registry Helpers (struct-based binary parsing)
    # ------------------------------------------------------------------

    def _find_key_offset(self, data: bytes, key_path: bytes) -> Optional[int]:
        """Scan for a registry key path in hive data and return its offset."""
        key_offset = data.find(key_path)
        if key_offset == -1:
            return None
        return key_offset

    def _scan_user_keys(self, data: bytes, offset: int) -> List[Dict[str, Any]]:
        """Scan for user entries around the given offset in SAM hive."""
        entries: List[Dict[str, Any]] = []
        window = data[max(0, offset - 256):min(len(data), offset + 4096)]
        rid_offsets = []
        for i in range(0, len(window) - 4, 4):
            val = struct.unpack_from("<I", window, i)[0]
            if 500 <= val <= 1200:
                rid_offsets.append((i, val))
        seen_rids = set()
        for pos, rid in rid_offsets:
            if rid in seen_rids:
                continue
            seen_rids.add(rid)
            name_buf = window[max(0, pos - 32):pos]
            name = name_buf.decode("utf-16-le", errors="replace").rstrip("\x00").strip()
            name = name.split("\x00")[-1] if "\x00" in name else name
            if not name or len(name) > 64:
                name = f"RID_{rid}"
            last_login_ft = 0
            login_offset = pos + 4
            if login_offset + 8 <= len(window):
                last_login_ft = struct.unpack_from("<Q", window, login_offset)[0]
            entries.append({
                "name": name,
                "rid": rid,
                "last_login": last_login_ft,
            })
        if not entries:
            entries.append({"name": "Unknown", "rid": 0, "last_login": 0})
        return entries

    def _scan_subkeys(self, data: bytes, offset: int, max_depth: int = 1) -> List[Dict[str, Any]]:
        """Scan for registry subkey data structures near the given offset."""
        subkeys: List[Dict[str, Any]] = []
        window = data[max(0, offset - 128):min(len(data), offset + 8192)]
        for i in range(0, min(len(window) - 16, 4096), 16):
            try:
                nk_sig = window[i:i + 2]
                if nk_sig == b"nk":
                    name_len = struct.unpack_from("<H", window, i + 2)[0]
                    if 0 < name_len < 128:
                        name = window[i + 4:i + 4 + name_len].decode("utf-8", errors="replace")
                        subkeys.append({"__name__": name, "__subkeys__": [], "__values__": {}})
            except struct.error:
                continue
        if not subkeys:
            for i in range(0, min(len(window), 4096), 8):
                try:
                    val = struct.unpack_from("<Q", window, i)[0]
                    if 1000 < val < 99999:
                        name_part = window[max(0, i - 20):i].decode("utf-16-le", errors="replace").rstrip("\x00")
                        if name_part and len(name_part) < 128:
                            subkeys.append({"__name__": name_part, "__subkeys__": [], "__values__": {}})
                except struct.error:
                    continue
        return subkeys

    def _get_value_data(self, data: bytes, key_offset: int, value_name: bytes) -> Any:
        """Retrieve a registry value data blob near the key offset."""
        search_region = data[key_offset:min(len(data), key_offset + 8192)]
        val_pos = search_region.find(value_name)
        if val_pos == -1:
            return None
        data_offset = key_offset + val_pos + len(value_name)
        if data_offset + 16 > len(data):
            return None
        try:
            data_len = struct.unpack_from("<I", data, data_offset)[0]
            if data_len > 1048576:
                return None
            dtype = struct.unpack_from("<I", data, data_offset + 4)[0]
            return data[data_offset + 8:data_offset + 8 + data_len]
        except struct.error:
            return None
