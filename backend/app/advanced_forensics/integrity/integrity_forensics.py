"""Evidence integrity verification processor.

Multi-algorithm hash verification, perceptual hashing, extension/header mismatch
detection, entropy analysis, corruption detection, YARA scanning, ClamAV integration.
"""
import logging
import math
import os
import struct
from collections import Counter
from typing import Any, Dict, List, Optional, Set

from ...forensic_engine.base import BaseProcessor
from ...forensic_engine.schemas import (
    EvidenceCategory,
    EvidenceSchema,
    ForensicProcessorConfig,
    ProcessorPriority,
)
from ..schemas import Finding, IOC, IOCType, RiskIndicator, RiskLevel

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Magic-byte signatures: prefix bytes -> (extension, description)
# ---------------------------------------------------------------------------
MAGIC_SIGNATURES: list[tuple[bytes, str, str]] = [
    (b"\xff\xd8\xff", "jpg", "JPEG image"),
    (b"\x89PNG\r\n\x1a\n", "png", "PNG image"),
    (b"%PDF", "pdf", "PDF document"),
    (b"PK\x03\x04", "zip", "ZIP archive / Office Open XML"),
    (b"PK\x05\x06", "zip", "ZIP archive (empty)"),
    (b"PK\x06\x06", "zip", "ZIP64 archive"),
    (b"MZ", "exe", "PE executable (Windows)"),
    (b"\x7fELF", "elf", "ELF executable (Linux)"),
    (b"GIF87a", "gif", "GIF image"),
    (b"GIF89a", "gif", "GIF image"),
    (b"RIFF", "webp", "RIFF container (WebP)"),
    (b"\x00\x00\x00\x18ftypmp4", "mp4", "MP4 video"),
    (b"\x00\x00\x00\x1cftypisom", "mp4", "MP4 video (isom)"),
    (b"\x00\x00\x00\x20ftyp", "mp4", "MP4 video"),
    (b"\x1f\x8b", "gz", "Gzip compressed data"),
    (b"BZh", "bz2", "Bzip2 compressed data"),
    (b"\xfd7zXZ\x00", "xz", "XZ compressed data"),
    (b"7z\xbc\xaf\x27\x1c", "7z", "7-Zip archive"),
    (b"\x50\x4b\x03\x04", "zip", "ZIP archive"),
    (b"\x42\x5a\x68", "bz2", "Bzip2"),
    (b"\x4c\x00\x00\x00\x01\x14\x02\x00", "lnk", "Windows LNK shortcut"),
    (b"\x49\x44\x33", "mp3", "MP3 audio (ID3)"),
    (b"\xff\xfb", "mp3", "MP3 audio"),
    (b"\xff\xf3", "mp3", "MP3 audio"),
    (b"\x4f\x67\x67\x53", "ogg", "Ogg container"),
    (b"\x66\x4c\x61\x43", "flac", "FLAC audio"),
]

# MIME-type -> expected extension mapping (subset for mismatch detection)
MIME_EXT_MAP: dict[str, list[str]] = {
    "image/jpeg": ["jpg", "jpeg"],
    "image/png": ["png"],
    "image/gif": ["gif"],
    "image/webp": ["webp"],
    "image/bmp": ["bmp"],
    "image/tiff": ["tiff", "tif"],
    "image/svg+xml": ["svg"],
    "application/pdf": ["pdf"],
    "application/zip": ["zip"],
    "application/x-7z-compressed": ["7z"],
    "application/x-rar-compressed": ["rar"],
    "application/gzip": ["gz"],
    "application/x-bzip2": ["bz2"],
    "application/x-xz": ["xz"],
    "application/x-tar": ["tar"],
    "application/java-archive": ["jar"],
    "application/vnd.openxmlformats-officedocument": ["docx", "xlsx", "pptx"],
    "application/msword": ["doc"],
    "application/vnd.ms-excel": ["xls"],
    "application/vnd.ms-powerpoint": ["ppt"],
    "application/x-executable": ["elf"],
    "application/x-dosexec": ["exe", "dll", "sys"],
    "audio/mpeg": ["mp3"],
    "audio/ogg": ["ogg"],
    "audio/flac": ["flac"],
    "audio/wav": ["wav"],
    "video/mp4": ["mp4"],
    "video/x-msvideo": ["avi"],
    "video/quicktime": ["mov"],
    "text/plain": ["txt", "log", "csv"],
    "text/html": ["html", "htm"],
    "text/css": ["css"],
    "text/javascript": ["js"],
    "application/json": ["json"],
    "application/xml": ["xml"],
    "application/x-font-ttf": ["ttf"],
    "application/x-font-otf": ["otf"],
}

IMAGE_EXTENSIONS = frozenset({"jpg", "jpeg", "png", "gif", "bmp", "tiff", "tif", "webp", "svg", "heic", "heif"})


class IntegrityForensicsProcessor(BaseProcessor):
    """Evidence integrity verification processor."""

    name = "integrity_forensics"
    description = (
        "Evidence integrity: hash verification, perceptual hashing, extension/header "
        "mismatch, entropy analysis, corruption detection, YARA scanning, ClamAV integration"
    )
    supported_categories: frozenset[EvidenceCategory] = frozenset({EvidenceCategory.UNKNOWN})
    priority: ProcessorPriority = ProcessorPriority.INTEGRITY

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        results: Dict[str, Any] = {}
        findings: List[Finding] = []
        risks: List[RiskIndicator] = []

        file_path = evidence.storage_path
        if not os.path.isfile(file_path):
            evidence.add_error(self.name, f"File not found: {file_path}")
            return evidence

        # --- hash verification ---
        hash_result = self._verify_hashes(evidence)
        results["hash_verification"] = hash_result
        if hash_result.get("mismatch"):
            findings.append(Finding(
                title="Hash mismatch detected",
                description=hash_result["mismatch_detail"],
                risk_level=RiskLevel.HIGH,
                category="integrity",
                evidence_refs=[evidence.evidence_id],
                recommendation="Verify chain of custody; evidence may have been altered.",
                mitre_attack="T1070.006",
            ))
            risks.append(RiskIndicator(
                indicator="hash_mismatch",
                risk_level=RiskLevel.HIGH,
                source=self.name,
                details=hash_result["mismatch_detail"],
                mitre_attack="T1070.006",
            ))

        # --- extension mismatch ---
        ext_result = self._check_extension_mismatch(evidence)
        results["extension_mismatch"] = ext_result
        if ext_result.get("mismatch"):
            findings.append(Finding(
                title="Extension vs MIME type mismatch",
                description=ext_result["detail"],
                risk_level=RiskLevel.MEDIUM,
                category="integrity",
                evidence_refs=[evidence.evidence_id],
                recommendation="Investigate possible file disguise or mislabeling.",
                mitre_attack="T1027.002",
            ))
            risks.append(RiskIndicator(
                indicator="extension_mismatch",
                risk_level=RiskLevel.MEDIUM,
                source=self.name,
                details=ext_result["detail"],
            ))

        # --- header mismatch ---
        hdr_result = self._check_header_mismatch(evidence)
        results["header_mismatch"] = hdr_result
        if hdr_result.get("mismatch"):
            findings.append(Finding(
                title="File header does not match claimed type",
                description=hdr_result["detail"],
                risk_level=RiskLevel.HIGH,
                category="integrity",
                evidence_refs=[evidence.evidence_id],
                recommendation="File header inconsistency may indicate tampering or obfuscation.",
                mitre_attack="T1027.002",
            ))
            risks.append(RiskIndicator(
                indicator="header_mismatch",
                risk_level=RiskLevel.HIGH,
                source=self.name,
                details=hdr_result["detail"],
            ))

        # --- truncation ---
        trunc_result = self._detect_truncation(evidence)
        results["truncation"] = trunc_result
        if trunc_result.get("truncated"):
            findings.append(Finding(
                title="Truncated file detected",
                description=trunc_result["detail"],
                risk_level=RiskLevel.MEDIUM,
                category="integrity",
                evidence_refs=[evidence.evidence_id],
                recommendation="File may be incomplete due to failed acquisition or intentional trimming.",
            ))
            risks.append(RiskIndicator(
                indicator="truncated_file",
                risk_level=RiskLevel.MEDIUM,
                source=self.name,
                details=trunc_result["detail"],
            ))

        # --- corruption ---
        corr_result = self._detect_corruption(evidence)
        results["corruption"] = corr_result
        if corr_result.get("corrupted"):
            findings.append(Finding(
                title="File corruption detected",
                description=corr_result["detail"],
                risk_level=RiskLevel.MEDIUM,
                category="integrity",
                evidence_refs=[evidence.evidence_id],
                recommendation="Validate file integrity and consider re-acquisition.",
            ))

        # --- entropy ---
        entropy_result = self._calculate_entropy(evidence)
        results["entropy"] = entropy_result
        entropy_val = entropy_result.get("entropy")
        if entropy_val is not None and entropy_val > 7.5:
            risks.append(RiskIndicator(
                indicator="high_entropy",
                risk_level=RiskLevel.LOW,
                source=self.name,
                details=f"Entropy {entropy_val:.2f} suggests encryption or compression.",
            ))
            evidence.add_tag("encrypted_or_compressed")

        # --- perceptual hash ---
        p_hash = self._perceptual_hash(evidence)
        results["perceptual_hash"] = p_hash
        if p_hash.get("phash"):
            evidence.add_tag("has_perceptual_hash")

        # --- YARA ---
        yara_result = self._yara_scan(evidence)
        results["yara_scan"] = yara_result
        if yara_result.get("matches"):
            findings.append(Finding(
                title="YARA rule matches detected",
                description=f"Matched rules: {', '.join(yara_result['matches'])}",
                risk_level=RiskLevel.HIGH,
                category="malware",
                evidence_refs=[evidence.evidence_id],
                recommendation="Investigate matched YARA signatures; potential malicious content.",
                mitre_attack="T1059",
            ))
            risks.append(RiskIndicator(
                indicator="yara_match",
                risk_level=RiskLevel.HIGH,
                source=self.name,
                details=f"Matched: {', '.join(yara_result['matches'])}",
            ))

        # --- ClamAV ---
        clam_result = self._clamav_scan(evidence)
        results["clamav_scan"] = clam_result
        if clam_result.get("infected"):
            findings.append(Finding(
                title="ClamAV detected malware",
                description=f"Virus: {clam_result.get('virus_name', 'unknown')}",
                risk_level=RiskLevel.CRITICAL,
                category="malware",
                evidence_refs=[evidence.evidence_id],
                recommendation="Quarantine and analyse the infected file immediately.",
                mitre_attack="T1059",
            ))
            risks.append(RiskIndicator(
                indicator="clamav_infected",
                risk_level=RiskLevel.CRITICAL,
                source=self.name,
                details=f"Virus: {clam_result.get('virus_name', 'unknown')}",
            ))

        # --- NSRL ---
        nsrl_result = self._nsrl_lookup(evidence)
        results["nsrl_lookup"] = nsrl_result
        if nsrl_result.get("known_good"):
            evidence.add_tag("nsrl_known_good")

        # --- duplicates ---
        dup_result = self._detect_duplicates(evidence)
        results["duplicate_detection"] = dup_result

        # --- persist all results ---
        evidence.processor_results[self.name] = results
        evidence.metadata[self.name] = {
            "findings_count": len(findings),
            "risks_count": len(risks),
            "known_good": nsrl_result.get("known_good", False),
        }

        # store findings and risks in metadata for downstream consumers
        evidence.metadata.setdefault("findings", []).extend([f.to_dict() for f in findings])
        evidence.metadata.setdefault("risk_indicators", []).extend([r.to_dict() for r in risks])

        evidence.add_tag("integrity_verified")
        return evidence

    # ------------------------------------------------------------------
    # 1. Multi-algorithm hash verification
    # ------------------------------------------------------------------
    def _verify_hashes(self, evidence: EvidenceSchema) -> Dict[str, Any]:
        import hashlib

        sha256 = hashlib.sha256()
        sha1 = hashlib.sha1()
        md5 = hashlib.md5()

        try:
            with open(evidence.storage_path, "rb") as fh:
                for chunk in iter(lambda: fh.read(65536), b""):
                    sha256.update(chunk)
                    sha1.update(chunk)
                    md5.update(chunk)
        except OSError as exc:
            evidence.add_error(self.name, f"Hash computation failed: {exc}")
            return {"error": str(exc)}

        computed_sha256 = sha256.hexdigest()
        computed_sha1 = sha1.hexdigest()
        computed_md5 = md5.hexdigest()

        result: Dict[str, Any] = {
            "sha256": computed_sha256,
            "sha1": computed_sha1,
            "md5": computed_md5,
            "mismatch": False,
            "mismatch_detail": "",
        }

        # compare against evidence-recorded sha256
        if evidence.sha256 and evidence.sha256.lower() != computed_sha256.lower():
            result["mismatch"] = True
            result["mismatch_detail"] = (
                f"Computed SHA-256 ({computed_sha256}) differs from recorded ({evidence.sha256})"
            )

        # check against known good hashes if provided in metadata
        known_hashes = evidence.metadata.get("known_good_hashes", {})
        for algo, expected in known_hashes.items():
            computed = {"sha256": computed_sha256, "sha1": computed_sha1, "md5": computed_md5}.get(algo)
            if computed and expected and computed.lower() != expected.lower():
                result["mismatch"] = True
                result["mismatch_detail"] += f" | {algo.upper()} mismatch (expected {expected})"

        return result

    # ------------------------------------------------------------------
    # 2. Perceptual hashing (image files)
    # ------------------------------------------------------------------
    def _perceptual_hash(self, evidence: EvidenceSchema) -> Dict[str, Any]:
        ext = self._get_file_extension(evidence)
        if ext not in IMAGE_EXTENSIONS:
            return {"supported": False}

        try:
            from PIL import Image

            img = Image.open(evidence.storage_path).convert("L")

            # --- dHash (difference hash) ---
            img_resized = img.resize((9, 8), Image.LANCZOS)
            pixels = list(img_resized.getdata())
            dhash_bits = []
            for row in range(8):
                for col in range(8):
                    idx = row * 9 + col
                    dhash_bits.append(1 if pixels[idx] > pixels[idx + 1] else 0)
            dhash = hex(int("".join(str(b) for b in dhash_bits), 2))

            # --- aHash (average hash) ---
            img_small = img.resize((8, 8), Image.LANCZOS)
            avg = sum(img_small.getdata()) / 64.0
            abits = [1 if p > avg else 0 for p in img_small.getdata()]
            ahash = hex(int("".join(str(b) for b in abits), 2))

            # --- pHash (simplified via DCT) ---
            phash = self._compute_phash(img)

            return {
                "dhash": dhash,
                "ahash": ahash,
                "phash": phash,
                "supported": True,
            }
        except Exception as exc:
            logger.debug("Perceptual hash failed for %s: %s", evidence.evidence_id, exc)
            return {"supported": False, "error": str(exc)}

    @staticmethod
    def _compute_phash(img: "Image.Image") -> Optional[str]:
        """Compute perceptual hash via DCT (simplified)."""
        try:
            import numpy as np

            img_small = img.resize((32, 32), Image.LANCZOS)
            pixels = np.array(img_small, dtype=float)

            # simple DCT-like transform using numpy
            from numpy.fft import dctn
            dct = dctn(pixels, norm="ortho")
            # take top-left 8x8 of DCT
            low_freq = dct[:8, :8]
            median_val = float(np.median(low_freq))
            bits = [1 if val > median_val else 0 for val in low_freq.flatten()]
            return hex(int("".join(str(b) for b in bits), 2))
        except ImportError:
            return None

    # ------------------------------------------------------------------
    # 3. Extension vs MIME type mismatch
    # ------------------------------------------------------------------
    def _check_extension_mismatch(self, evidence: EvidenceSchema) -> Dict[str, Any]:
        ext = self._get_file_extension(evidence)
        mime = evidence.mime_type or ""

        result: Dict[str, Any] = {"mismatch": False, "detail": "", "ext": ext, "mime": mime}

        if not ext or not mime:
            return result

        expected_exts = MIME_EXT_MAP.get(mime)
        if expected_exts and ext not in expected_exts:
            result["mismatch"] = True
            result["detail"] = f"File extension .{ext} does not match MIME type {mime} (expected: {', '.join(expected_exts)})"

        return result

    # ------------------------------------------------------------------
    # 4. Magic bytes / header validation
    # ------------------------------------------------------------------
    def _check_header_mismatch(self, evidence: EvidenceSchema) -> Dict[str, Any]:
        ext = self._get_file_extension(evidence)
        result: Dict[str, Any] = {"mismatch": False, "detail": "", "detected_type": None}

        try:
            with open(evidence.storage_path, "rb") as fh:
                header = fh.read(32)
        except OSError as exc:
            evidence.add_error(self.name, f"Cannot read header: {exc}")
            return result

        if len(header) < 4:
            result["detail"] = "File too small to validate header"
            return result

        detected_ext = None
        detected_desc = None
        for sig_bytes, sig_ext, sig_desc in MAGIC_SIGNATURES:
            if header.startswith(sig_bytes):
                detected_ext = sig_ext
                detected_desc = sig_desc
                break

        result["detected_type"] = detected_desc or detected_ext
        result["detected_ext"] = detected_ext

        if detected_ext and ext and detected_ext != ext:
            # some overlap allowed (zip contains docx/xlsx/pptx)
            if not (detected_ext == "zip" and ext in {"docx", "xlsx", "pptx", "jar", "odt", "ods", "odp"}):
                result["mismatch"] = True
                result["detail"] = (
                    f"File header indicates {detected_desc} (.{detected_ext}) but extension is .{ext}"
                )

        return result

    # ------------------------------------------------------------------
    # 5. Truncation detection
    # ------------------------------------------------------------------
    def _detect_truncation(self, evidence: EvidenceSchema) -> Dict[str, Any]:
        ext = self._get_file_extension(evidence)
        result: Dict[str, Any] = {"truncated": False, "detail": ""}

        try:
            file_size = os.path.getsize(evidence.storage_path)
            with open(evidence.storage_path, "rb") as fh:
                # read tail
                tail_size = min(512, file_size)
                fh.seek(max(0, file_size - tail_size))
                tail = fh.read()

                if ext == "pdf":
                    if b"%%EOF" not in tail:
                        result["truncated"] = True
                        result["detail"] = "PDF missing %%EOF marker"

                elif ext == "png":
                    if b"IEND" not in tail:
                        result["truncated"] = True
                        result["detail"] = "PNG missing IEND chunk"

                elif ext in ("zip", "docx", "xlsx", "pptx", "jar"):
                    # End of central directory signature: PK\x05\x06
                    if b"PK\x05\x06" not in tail:
                        result["truncated"] = True
                        result["detail"] = "ZIP missing end-of-central-directory record"

                elif ext == "gif":
                    if b"\x00" not in tail[-4:]:
                        # GIF should end with a block terminator
                        pass

                elif ext == "elf":
                    if file_size >= 40:
                        fh.seek(0)
                        elf_header = fh.read(52)
                        if len(elf_header) >= 40:
                            e_phoff = struct.unpack("<Q" if elf_header[4] == 2 else "<I", elf_header[28:36])[0]
                            e_phnum = struct.unpack("<H", elf_header[44:46])[0]
                            e_phentsize = struct.unpack("<H", elf_header[42:44])[0]
                            expected_end = e_phoff + e_phnum * e_phentsize
                            if file_size < expected_end:
                                result["truncated"] = True
                                result["detail"] = f"ELF file smaller than program header table ({file_size} < {expected_end})"

                elif ext in ("exe", "dll", "sys", "com"):
                    if file_size >= 64:
                        fh.seek(0)
                        pe_header = fh.read(64)
                        if pe_header[:2] == b"MZ":
                            e_lfanew = struct.unpack("<I", pe_header[0x3C:0x40])[0]
                            if e_lfanew + 24 <= file_size:
                                fh.seek(e_lfanew + 6)
                                num_sections = struct.unpack("<H", fh.read(2))[0]
                                opt_size = struct.unpack("<H", fh.read(2))[0]
                                pe_end = e_lfanew + 24 + opt_size + num_sections * 40
                                if file_size < pe_end:
                                    result["truncated"] = True
                                    result["detail"] = f"PE file smaller than section table ({file_size} < {pe_end})"

        except OSError as exc:
            evidence.add_error(self.name, f"Truncation check failed: {exc}")

        return result

    # ------------------------------------------------------------------
    # 6. Corruption detection
    # ------------------------------------------------------------------
    def _detect_corruption(self, evidence: EvidenceSchema) -> Dict[str, Any]:
        result: Dict[str, Any] = {"corrupted": False, "detail": "", "checks": []}

        try:
            file_size = os.path.getsize(evidence.storage_path)
            if file_size == 0:
                result["corrupted"] = True
                result["detail"] = "File is empty (0 bytes)"
                return result

            with open(evidence.storage_path, "rb") as fh:
                data = fh.read()

            # null bytes in small files (likely text)
            if file_size < 1048576:
                null_count = data.count(b"\x00")
                null_ratio = null_count / file_size if file_size > 0 else 0
                if null_ratio > 0.1 and null_count > 100:
                    result["corrupted"] = True
                    result["detail"] = f"High null byte ratio ({null_ratio:.2%}) in small file"
                    result["checks"].append("null_bytes")

            # repeated identical bytes (sign of wiping)
            if file_size > 1024:
                byte_counts = Counter(data[:min(file_size, 1048576)])
                most_common_count = byte_counts.most_common(1)[0][1]
                if most_common_count > file_size * 0.95:
                    result["corrupted"] = True
                    result["detail"] = f"File appears to be filled with repeated bytes ({most_common_count}/{file_size})"
                    result["checks"].append("repeated_bytes")

            # PNG-specific: verify IHDR and IEND chunks
            ext = self._get_file_extension(evidence)
            if ext == "png" and data[:8] == b"\x89PNG\r\n\x1a\n":
                if not data.endswith(b"IEND\xaeB`\x82"):
                    result["corrupted"] = True
                    result["detail"] = "PNG file missing IEND chunk"
                    result["checks"].append("png_iend")

        except OSError as exc:
            evidence.add_error(self.name, f"Corruption check failed: {exc}")

        return result

    # ------------------------------------------------------------------
    # 7. Shannon entropy analysis
    # ------------------------------------------------------------------
    def _calculate_entropy(self, evidence: EvidenceSchema) -> Dict[str, Any]:
        result: Dict[str, Any] = {"entropy": None, "block_entropies": [], "classification": ""}

        try:
            with open(evidence.storage_path, "rb") as fh:
                data = fh.read()

            if not data:
                result["classification"] = "empty"
                return result

            entropy = self._shannon_entropy(data)
            result["entropy"] = round(entropy, 4)

            if entropy > 7.5:
                result["classification"] = "high (likely encrypted or compressed)"
            elif entropy < 1.0:
                result["classification"] = "low (sparse or empty content)"
            else:
                result["classification"] = "normal"

            # block-wise entropy to detect embedded sections
            block_size = 4096
            if len(data) > block_size * 2:
                blocks = [data[i:i + block_size] for i in range(0, len(data), block_size)]
                block_entropies = []
                for idx, block in enumerate(blocks[:256]):  # cap at 256 blocks
                    be = self._shannon_entropy(block)
                    block_entropies.append({"offset": idx * block_size, "entropy": round(be, 4)})
                result["block_entropies"] = block_entropies

                # detect abrupt entropy changes
                entropies = [b["entropy"] for b in block_entropies]
                for i in range(1, len(entropies)):
                    if abs(entropies[i] - entropies[i - 1]) > 2.0:
                        result["classification"] += f"; entropy spike at offset {i * block_size}"
                        break

        except OSError as exc:
            evidence.add_error(self.name, f"Entropy analysis failed: {exc}")

        return result

    @staticmethod
    def _shannon_entropy(data: bytes) -> float:
        if not data:
            return 0.0
        byte_counts = Counter(data)
        length = len(data)
        entropy = 0.0
        for count in byte_counts.values():
            p = count / length
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    # ------------------------------------------------------------------
    # 8. YARA rule scanning
    # ------------------------------------------------------------------
    def _yara_scan(self, evidence: EvidenceSchema) -> Dict[str, Any]:
        result: Dict[str, Any] = {"available": False, "matches": [], "error": None}

        try:
            import yara

            rules_path = evidence.metadata.get("yara_rules_path")
            if rules_path and os.path.isfile(rules_path):
                rules = yara.compile(filepath=rules_path)
            else:
                # try built-in rules directory
                default_path = os.path.join(os.path.dirname(__file__), "..", "..", "yara_rules")
                if os.path.isdir(default_path):
                    rules = yara.compile(dirpath=default_path)
                else:
                    result["error"] = "No YARA rules found"
                    return result

            result["available"] = True
            matches = rules.match(evidence.storage_path)
            result["matches"] = [m.rule for m in matches]
            result["detailed"] = [
                {"rule": m.rule, "tags": m.tags, "meta": m.meta} for m in matches
            ]

        except ImportError:
            result["error"] = "yara-python not installed"
        except Exception as exc:
            result["error"] = str(exc)
            logger.debug("YARA scan error: %s", exc)

        return result

    # ------------------------------------------------------------------
    # 9. ClamAV integration
    # ------------------------------------------------------------------
    def _clamav_scan(self, evidence: EvidenceSchema) -> Dict[str, Any]:
        result: Dict[str, Any] = {"available": False, "infected": False, "virus_name": None, "error": None}

        clamd_sock = os.environ.get("CLAMD_SOCKET", "/var/run/clamav/clamd.ctl")
        clamd_host = os.environ.get("CLAMD_HOST", "127.0.0.1")
        clamd_port = int(os.environ.get("CLAMD_PORT", "3310"))

        # try Unix socket first, then TCP
        try:
            import clamd

            cd = clamd.ClamdUnixSocket(clamd_sock) if os.path.exists(clamd_sock) else clamd.ClamdNetworkSocket(clamd_host, clamd_port)
            scan_result = cd.scan(evidence.storage_path)
            result["available"] = True

            if scan_result and scan_result.get(evidence.storage_path):
                status, virus_name = scan_result[evidence.storage_path]
                if status == "FOUND":
                    result["infected"] = True
                    result["virus_name"] = virus_name

        except ImportError:
            # fallback: try subprocess call to clamscan
            import subprocess
            try:
                proc = subprocess.run(
                    ["clamscan", "--no-summary", evidence.storage_path],
                    capture_output=True, text=True, timeout=60,
                )
                if proc.returncode == 1:
                    result["available"] = True
                    result["infected"] = True
                    # output line format: /path: virus_name FOUND
                    for line in proc.stdout.strip().splitlines():
                        if "FOUND" in line:
                            result["virus_name"] = line.split(": ", 1)[-1].replace(" FOUND", "")
                            break
                elif proc.returncode == 0:
                    result["available"] = True
            except FileNotFoundError:
                result["error"] = "clamd/clamscan not available"
            except Exception as exc:
                result["error"] = str(exc)

        except Exception as exc:
            result["error"] = str(exc)
            logger.debug("ClamAV scan error: %s", exc)

        return result

    # ------------------------------------------------------------------
    # 10. NSRL lookup
    # ------------------------------------------------------------------
    def _nsrl_lookup(self, evidence: EvidenceSchema) -> Dict[str, Any]:
        result: Dict[str, Any] = {"known_good": False, "product": None, "error": None}

        nsrl_db = evidence.metadata.get("nsrl_db_path")
        if not nsrl_db:
            result["error"] = "No NSRL database configured"
            return result

        try:
            import sqlite3

            conn = sqlite3.connect(nsrl_db)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT product_name, version FROM file WHERE sha256 = ?",
                (evidence.sha256.lower(),),
            )
            row = cursor.fetchone()
            conn.close()

            if row:
                result["known_good"] = True
                result["product"] = {"name": row[0], "version": row[1]}

        except ImportError:
            result["error"] = "sqlite3 not available"
        except Exception as exc:
            result["error"] = str(exc)

        return result

    # ------------------------------------------------------------------
    # 11. Duplicate detection
    # ------------------------------------------------------------------
    def _detect_duplicates(self, evidence: EvidenceSchema) -> Dict[str, Any]:
        result: Dict[str, Any] = {"sha256_duplicates": [], "phash_duplicates": [], "note": ""}

        # exact duplicates are identified by SHA-256 at the pipeline level
        # here we store the hash for external dedup engines
        result["sha256"] = evidence.sha256

        # perceptual hash stored for near-duplicate comparison
        p_hash = evidence.processor_results.get(self.name, {}).get("perceptual_hash", {})
        if p_hash.get("phash"):
            result["phash"] = p_hash["phash"]

        result["note"] = "Exact duplicates are matched via SHA-256 across the evidence corpus."
        return result
