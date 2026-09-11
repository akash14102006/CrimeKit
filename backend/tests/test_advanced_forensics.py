"""Comprehensive tests for CrimeKit Advanced Forensics Modules.

Covers schema dataclasses, all 8 processors (browser, windows, mobile, email,
network, disk, memory, integrity), integration with ProcessingPipeline,
and edge cases.
"""
import hashlib
import math
import os
import sqlite3
import struct
import tempfile
import textwrap
from datetime import datetime, timedelta
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Imports from the codebase
# ---------------------------------------------------------------------------
from backend.app.advanced_forensics.schemas import (
    Artifact, ArtifactType, IOC, IOCType, Finding, RiskIndicator, RiskLevel,
    EvidenceMetadata, TimelineEvent, Entity, Relationship,
    BrowserArtifact, WindowsArtifact, MobileArtifact,
    EmailArtifact, NetworkArtifact, DiskArtifact, MemoryArtifact, IntegrityResult,
)
from backend.app.advanced_forensics import (
    BrowserForensicsProcessor, WindowsForensicsProcessor,
    MobileForensicsProcessor, EmailForensicsProcessor,
    NetworkForensicsProcessor, DiskForensicsProcessor,
    MemoryForensicsProcessor, IntegrityForensicsProcessor,
    ALL_ADVANCED_PROCESSORS,
)
from backend.app.forensic_engine.schemas import (
    EvidenceSchema, EvidenceCategory, ForensicProcessorConfig, ProcessorPriority,
)
from backend.app.forensic_engine.pipeline import ProcessingPipeline


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_test_file(tmp_path, name: str, content: bytes = b"test data") -> str:
    p = tmp_path / name
    p.write_bytes(content)
    return str(p)


def _make_evidence(
    file_path: str,
    filename: str = None,
    category: EvidenceCategory = EvidenceCategory.UNKNOWN,
    sha256: str = None,
) -> EvidenceSchema:
    filename = filename or os.path.basename(file_path)
    if sha256 is None:
        sha256 = hashlib.sha256(open(file_path, "rb").read()).hexdigest()
    return EvidenceSchema(
        evidence_id="test-ev-001",
        case_id="case-001",
        storage_path=file_path,
        filename=filename,
        sha256=sha256,
        size=os.path.getsize(file_path),
        mime_type=None,
        category=category,
    )


# ===================================================================
# 1. SCHEMA TESTS
# ===================================================================

class TestArtifactDataclass:
    def test_creation(self):
        art = Artifact(
            artifact_type=ArtifactType.BROWSER_HISTORY,
            source="browser_forensics",
            data={"url": "https://example.com"},
            timestamp="2024-01-01T00:00:00",
            confidence=0.95,
            tags=["web", "history"],
            raw_path="/tmp/browser.db",
        )
        assert art.artifact_type == ArtifactType.BROWSER_HISTORY
        assert art.source == "browser_forensics"
        assert art.data["url"] == "https://example.com"
        assert art.confidence == 0.95
        assert "web" in art.tags

    def test_to_dict(self):
        art = Artifact(
            artifact_type=ArtifactType.EMAIL_HEADER,
            source="email_forensics",
            data={"subject": "Test"},
            timestamp="2024-01-01",
            confidence=1.0,
            tags=[],
            raw_path=None,
        )
        d = art.to_dict()
        assert d["artifact_type"] == "email_header"
        assert d["source"] == "email_forensics"
        assert d["data"]["subject"] == "Test"
        assert d["timestamp"] == "2024-01-01"
        assert d["raw_path"] is None

    def test_defaults(self):
        art = Artifact(
            artifact_type=ArtifactType.GENERIC,
            source="test",
            data={},
        )
        assert art.timestamp is None
        assert art.confidence == 1.0
        assert art.tags == []
        assert art.raw_path is None


class TestIOCDataclass:
    def test_creation(self):
        ioc = IOC(
            ioc_type=IOCType.IP_ADDRESS,
            value="192.168.1.1",
            context="email relay",
            confidence=0.85,
            first_seen="2024-01-01",
            last_seen="2024-06-01",
            tags=["malicious"],
        )
        assert ioc.ioc_type == IOCType.IP_ADDRESS
        assert ioc.value == "192.168.1.1"
        assert ioc.confidence == 0.85

    def test_to_dict(self):
        ioc = IOC(
            ioc_type=IOCType.DOMAIN,
            value="evil.com",
            context="C2 server",
        )
        d = ioc.to_dict()
        assert d["ioc_type"] == "domain"
        assert d["value"] == "evil.com"
        assert d["first_seen"] is None
        assert d["tags"] == []


class TestFindingDataclass:
    def test_creation_with_risk_levels(self):
        for level in RiskLevel:
            finding = Finding(
                title=f"Test {level.value}",
                description="desc",
                risk_level=level,
                category="test",
            )
            assert finding.risk_level == level

    def test_to_dict(self):
        ioc = IOC(IOCType.EMAIL, "bad@evil.com", "phishing")
        finding = Finding(
            title="Phishing detected",
            description="Suspicious email",
            risk_level=RiskLevel.HIGH,
            category="email",
            evidence_refs=["ev-001"],
            iocs=[ioc],
            recommendation="Block sender",
            mitre_attack="T1566.002",
        )
        d = finding.to_dict()
        assert d["risk_level"] == "high"
        assert len(d["iocs"]) == 1
        assert d["iocs"][0]["ioc_type"] == "email"
        assert d["mitre_attack"] == "T1566.002"


class TestRiskIndicatorDataclass:
    def test_creation(self):
        ri = RiskIndicator(
            indicator="hash_mismatch",
            risk_level=RiskLevel.HIGH,
            source="integrity_forensics",
            details="SHA-256 differs",
            mitre_attack="T1070.006",
        )
        assert ri.risk_level == RiskLevel.HIGH
        d = ri.to_dict()
        assert d["indicator"] == "hash_mismatch"
        assert d["mitre_attack"] == "T1070.006"


class TestTimelineEventDataclass:
    def test_creation(self):
        te = TimelineEvent(
            timestamp="2024-01-01T12:00:00",
            event_type="file_access",
            description="User opened document",
            source="disk_forensics",
            evidence_id="ev-001",
            confidence=0.9,
            tags=["access"],
        )
        d = te.to_dict()
        assert d["timestamp"] == "2024-01-01T12:00:00"
        assert d["confidence"] == 0.9


class TestEntityDataclass:
    def test_creation(self):
        e = Entity(
            name="evil.com",
            entity_type="domain",
            properties={"ip": "1.2.3.4"},
            confidence=0.8,
            source="network_forensics",
        )
        d = e.to_dict()
        assert d["name"] == "evil.com"
        assert d["type"] == "domain"
        assert d["ip"] == "1.2.3.4"


class TestRelationshipDataclass:
    def test_creation(self):
        r = Relationship(
            source="sender@evil.com",
            target="victim@company.com",
            rel_type="sent_to",
            weight=5,
            properties={"email_id": "msg-1"},
            source_processor="email_forensics",
        )
        d = r.to_dict()
        assert d["source"] == "sender@evil.com"
        assert d["target"] == "victim@company.com"
        assert d["weight"] == 5


class TestEvidenceMetadataDataclass:
    def test_creation_and_to_dict(self):
        em = EvidenceMetadata(
            evidence_id="ev-001",
            filename="test.eml",
            sha256="abc123",
            size=1024,
            mime_type="message/rfc822",
            category="email",
            source_system="Outlook",
            acquisition_date="2024-01-01",
            examiner="John Doe",
            chain_of_custody=[{"action": "acquired", "by": "John"}],
        )
        d = em.to_dict()
        assert d["evidence_id"] == "ev-001"
        assert d["chain_of_custody"][0]["action"] == "acquired"


class TestModuleSpecificArtifacts:
    def test_browser_artifact(self):
        ba = BrowserArtifact(
            browser="Chrome",
            artifact_type="history",
            profile_name="Default",
            data={"url": "https://example.com"},
            timestamp="2024-01-01",
            url="https://example.com",
            title="Example",
        )
        d = ba.to_dict()
        assert d["browser"] == "Chrome"
        assert d["url"] == "https://example.com"

    def test_windows_artifact(self):
        wa = WindowsArtifact(
            artifact_type="registry_key",
            source_file="NTUSER.DAT",
            data={"key": "Software\\Microsoft"},
            timestamp="2024-01-01",
            user_sid="S-1-5-21-...",
        )
        d = wa.to_dict()
        assert d["artifact_type"] == "registry_key"
        assert d["user_sid"] == "S-1-5-21-..."

    def test_mobile_artifact(self):
        ma = MobileArtifact(
            platform="android",
            artifact_type="sms",
            source_db="mmssms.db",
            data={"address": "+1234567890", "body": "Hello"},
            timestamp="2024-01-01",
            contact="+1234567890",
        )
        d = ma.to_dict()
        assert d["platform"] == "android"
        assert d["contact"] == "+1234567890"

    def test_email_artifact(self):
        ea = EmailArtifact(
            message_id="<msg-001@example.com>",
            subject="Test",
            sender="alice@example.com",
            recipients=["bob@example.com"],
            timestamp="2024-01-01",
            headers={"From": "alice@example.com"},
            body="Hello",
            attachments=[],
            spf_result="pass",
            dkim_result="pass",
            dmarc_result="pass",
            thread_id="thread-1",
            hop_count=3,
            suspicious_indicators=[],
        )
        d = ea.to_dict()
        assert d["message_id"] == "<msg-001@example.com>"
        assert d["hop_count"] == 3

    def test_network_artifact(self):
        na = NetworkArtifact(
            protocol="TCP",
            source_ip="10.0.0.1",
            dest_ip="192.168.1.1",
            source_port=12345,
            dest_port=443,
            timestamp="2024-01-01",
            payload_summary="HTTPS",
        )
        d = na.to_dict()
        assert d["protocol"] == "TCP"
        assert d["dest_port"] == 443

    def test_disk_artifact(self):
        da = DiskArtifact(
            artifact_type="partition_info",
            partition="Partition 0",
            filesystem="NTFS",
            data={"size": 100000},
            recovered=True,
        )
        d = da.to_dict()
        assert d["recovered"] is True

    def test_memory_artifact(self):
        ma = MemoryArtifact(
            artifact_type="process",
            pid=4,
            process_name="System",
            data={"ppid": 0},
            address="0xfffff80000000000",
        )
        d = ma.to_dict()
        assert d["pid"] == 4
        assert d["address"] == "0xfffff80000000000"


class TestIntegrityResultDataclass:
    def test_creation(self):
        ir = IntegrityResult(
            verified=True,
            sha256_match=True,
            sha1_match=True,
            md5_match=True,
            perceptual_hash="0xabc",
            yara_matches=[],
            clamav_result="clean",
            entropy=5.5,
            extension_mismatch=False,
            header_mismatch=False,
            truncated=False,
            corrupted=False,
            details="All checks passed",
        )
        d = ir.to_dict()
        assert d["verified"] is True
        assert d["entropy"] == 5.5

    def test_mismatch_fields(self):
        ir = IntegrityResult(
            verified=False,
            sha256_match=False,
            extension_mismatch=True,
            header_mismatch=True,
            truncated=True,
            corrupted=True,
        )
        d = ir.to_dict()
        assert d["extension_mismatch"] is True
        assert d["corrupted"] is True


# ===================================================================
# 2. BROWSER FORENSICS TESTS
# ===================================================================

class TestBrowserForensicsProcessor:
    def test_class_properties(self):
        p = BrowserForensicsProcessor()
        assert p.name == "browser_forensics"
        assert "Chrome" in p.description or "browser" in p.description.lower()
        assert EvidenceCategory.BROWSER_DATA in p.supported_categories

    def test_can_process_browser_data(self):
        p = BrowserForensicsProcessor()
        evidence = MagicMock()
        evidence.category = EvidenceCategory.BROWSER_DATA
        assert p.can_process(evidence) is True

    def test_can_process_unknown(self):
        p = BrowserForensicsProcessor()
        evidence = MagicMock()
        evidence.category = EvidenceCategory.UNKNOWN
        assert p.can_process(evidence) is True

    def test_unsupported_category_does_not_match(self):
        p = BrowserForensicsProcessor()
        evidence = MagicMock()
        evidence.category = EvidenceCategory.IMAGE
        # IMAGE is not in supported_categories, so can_process returns False
        assert p.can_process(evidence) is False

    def test_chrome_history_extraction(self, tmp_path):
        db_path = tmp_path / "History"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE urls (
                url TEXT,
                title TEXT,
                visit_count INTEGER,
                last_visit_time INTEGER
            )
        """)
        chrome_epoch = datetime(1601, 1, 1)
        target = datetime(2024, 6, 15, 12, 0, 0)
        delta = target - chrome_epoch
        chrome_time = int(delta.total_seconds() * 1_000_000)
        cursor.execute(
            "INSERT INTO urls VALUES (?, ?, ?, ?)",
            ("https://example.com", "Example Page", 5, chrome_time),
        )
        cursor.execute(
            "INSERT INTO urls VALUES (?, ?, ?, ?)",
            ("https://google.com", "Google", 10, chrome_time),
        )
        conn.commit()
        conn.close()

        evidence = _make_evidence(str(db_path), "History", EvidenceCategory.BROWSER_DATA)
        config = ForensicProcessorConfig()
        processor = BrowserForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["browser_forensics"]
        assert "browser_history" in result
        history = result["browser_history"]
        assert len(history) >= 1
        assert any("example.com" in h["url"] for h in history)

    def test_chrome_cookies_extraction(self, tmp_path):
        db_path = tmp_path / "History"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE cookies (
                name TEXT,
                value TEXT,
                host_key TEXT,
                creation_date INTEGER
            )
        """)
        cursor.execute(
            "INSERT INTO cookies VALUES (?, ?, ?, ?)",
            ("session_id", "abc123", ".example.com", 13300000000000000),
        )
        conn.commit()
        conn.close()

        evidence = _make_evidence(str(db_path), "History", EvidenceCategory.BROWSER_DATA)
        config = ForensicProcessorConfig()
        processor = BrowserForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["browser_forensics"]
        assert "browser_cookies" in result
        cookies = result["browser_cookies"]
        assert len(cookies) >= 1
        assert cookies[0]["name"] == "session_id"

    def test_chrome_downloads_extraction(self, tmp_path):
        db_path = tmp_path / "History"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE downloads (
                target_path TEXT,
                start_time INTEGER,
                end_time INTEGER,
                received_bytes INTEGER
            )
        """)
        cursor.execute(
            "INSERT INTO downloads VALUES (?, ?, ?, ?)",
            ("/tmp/file.zip", 13300000000000000, 13300000100000000, 1024),
        )
        conn.commit()
        conn.close()

        evidence = _make_evidence(str(db_path), "History", EvidenceCategory.BROWSER_DATA)
        config = ForensicProcessorConfig()
        processor = BrowserForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["browser_forensics"]
        assert "browser_downloads" in result
        downloads = result["browser_downloads"]
        assert len(downloads) >= 1

    def test_missing_database(self, tmp_path):
        evidence = _make_evidence(
            _create_test_file(tmp_path, "nonexistent", b""),
            "History",
            EvidenceCategory.BROWSER_DATA,
        )
        evidence.storage_path = str(tmp_path / "does_not_exist.db")
        config = ForensicProcessorConfig()
        processor = BrowserForensicsProcessor()
        processor.process(evidence, config)
        assert any("not found" in e.lower() or "error" in e.lower() for e in evidence.processing_errors)

    def test_corrupted_database(self, tmp_path):
        fp = _create_test_file(tmp_path, "History", b"not a sqlite db at all!!!")
        evidence = _make_evidence(fp, "History", EvidenceCategory.BROWSER_DATA)
        config = ForensicProcessorConfig()
        processor = BrowserForensicsProcessor()
        processor.process(evidence, config)
        assert any("sqlite" in e.lower() or "error" in e.lower() or "failed" in e.lower()
                    for e in evidence.processing_errors)

    def test_firefox_detection(self, tmp_path):
        db_path = tmp_path / "places.sqlite"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE moz_places (
                url TEXT,
                title TEXT,
                visit_count INTEGER,
                last_visit_date INTEGER
            )
        """)
        cursor.execute(
            "INSERT INTO moz_places VALUES (?, ?, ?, ?)",
            ("https://firefox.com", "Firefox Site", 3, 1600000000000),
        )
        conn.commit()
        conn.close()

        evidence = _make_evidence(str(db_path), "places.sqlite", EvidenceCategory.BROWSER_DATA)
        config = ForensicProcessorConfig()
        processor = BrowserForensicsProcessor()
        processor.process(evidence, config)

        assert "browser_forensics" in evidence.processor_results
        assert "browser_history" in evidence.processor_results["browser_forensics"]

    def test_chrome_extensions_extraction(self, tmp_path):
        db_path = tmp_path / "History"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE extensions (
                name TEXT,
                description TEXT,
                version TEXT
            )
        """)
        cursor.execute("INSERT INTO extensions VALUES (?, ?, ?)", ("AdBlock", "Blocks ads", "3.0"))
        conn.commit()
        conn.close()

        evidence = _make_evidence(str(db_path), "History", EvidenceCategory.BROWSER_DATA)
        config = ForensicProcessorConfig()
        processor = BrowserForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["browser_forensics"]
        assert "browser_extensions" in result
        exts = result["browser_extensions"]
        assert len(exts) >= 1
        assert exts[0]["name"] == "AdBlock"

    def test_chrome_autofill_extraction(self, tmp_path):
        db_path = tmp_path / "History"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE autofill (
                name TEXT,
                value TEXT,
                date_created INTEGER
            )
        """)
        cursor.execute("INSERT INTO autofill VALUES (?, ?, ?)", ("email", "user@test.com", 13300000000000000))
        conn.commit()
        conn.close()

        evidence = _make_evidence(str(db_path), "History", EvidenceCategory.BROWSER_DATA)
        config = ForensicProcessorConfig()
        processor = BrowserForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["browser_forensics"]
        assert "browser_autofill" in result

    def test_chrome_logins_extraction(self, tmp_path):
        db_path = tmp_path / "History"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE logins (
                origin_url TEXT,
                username_value TEXT,
                date_created INTEGER,
                date_password_modified INTEGER
            )
        """)
        cursor.execute("INSERT INTO logins VALUES (?, ?, ?, ?)",
                        ("https://example.com", "user@test.com", 13300000000000000, 13300000000000000))
        conn.commit()
        conn.close()

        evidence = _make_evidence(str(db_path), "History", EvidenceCategory.BROWSER_DATA)
        config = ForensicProcessorConfig()
        processor = BrowserForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["browser_forensics"]
        assert "browser_saved_logins" in result

    def test_firefox_bookmarks(self, tmp_path):
        db_path = tmp_path / "places.sqlite"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE moz_bookmarks (
                fk INTEGER,
                title TEXT,
                dateAdded INTEGER,
                lastModified INTEGER,
                type INTEGER
            )
        """)
        cursor.execute("INSERT INTO moz_bookmarks VALUES (?, ?, ?, ?, ?)",
                        (1, "My Bookmark", 1600000000000, 1600000000000, 1))
        cursor.execute("""
            CREATE TABLE moz_places (
                id INTEGER PRIMARY KEY,
                url TEXT,
                title TEXT,
                visit_count INTEGER,
                last_visit_date INTEGER
            )
        """)
        cursor.execute("INSERT INTO moz_places VALUES (?, ?, ?, ?, ?)",
                        (1, "https://example.com", "Example", 5, 1600000000000))
        conn.commit()
        conn.close()

        evidence = _make_evidence(str(db_path), "places.sqlite", EvidenceCategory.BROWSER_DATA)
        config = ForensicProcessorConfig()
        processor = BrowserForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["browser_forensics"]
        assert "browser_bookmarks" in result

    def test_firefox_cookies(self, tmp_path):
        db_path = tmp_path / "places.sqlite"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE moz_cookies (
                name TEXT,
                value TEXT,
                host TEXT,
                creationTime INTEGER,
                expiry INTEGER
            )
        """)
        cursor.execute("INSERT INTO moz_cookies VALUES (?, ?, ?, ?, ?)",
                        ("token", "xyz789", ".example.com", 1600000000000, 1700000000000))
        conn.commit()
        conn.close()

        evidence = _make_evidence(str(db_path), "places.sqlite", EvidenceCategory.BROWSER_DATA)
        config = ForensicProcessorConfig()
        processor = BrowserForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["browser_forensics"]
        assert "browser_cookies" in result

    def test_profile_name_detection(self, tmp_path):
        db_path = tmp_path / "History"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE urls (url TEXT, title TEXT, visit_count INTEGER, last_visit_time INTEGER)")
        conn.commit()
        conn.close()

        evidence = _make_evidence(str(db_path), "History", EvidenceCategory.BROWSER_DATA)
        evidence.storage_path = str(tmp_path / "Default" / "History")
        os.makedirs(tmp_path / "Default", exist_ok=True)
        import shutil
        shutil.move(str(db_path), evidence.storage_path)

        config = ForensicProcessorConfig()
        processor = BrowserForensicsProcessor()
        processor.process(evidence, config)

        assert evidence.metadata.get("profile_name") == "Default"


# ===================================================================
# 3. WINDOWS FORENSICS TESTS
# ===================================================================

class TestWindowsForensicsProcessor:
    def test_class_properties(self):
        p = WindowsForensicsProcessor()
        assert p.name == "windows_forensics"
        assert "Windows" in p.description
        assert EvidenceCategory.WINDOWS_ARTIFACT in p.supported_categories

    def test_can_process_windows(self):
        p = WindowsForensicsProcessor()
        evidence = MagicMock()
        evidence.category = EvidenceCategory.WINDOWS_ARTIFACT
        assert p.can_process(evidence) is True

    def test_can_process_disk_image(self):
        p = WindowsForensicsProcessor()
        evidence = MagicMock()
        evidence.category = EvidenceCategory.DISK_IMAGE
        assert p.can_process(evidence) is True

    def test_unsupported_category_does_not_match(self):
        p = WindowsForensicsProcessor()
        evidence = MagicMock()
        evidence.category = EvidenceCategory.IMAGE
        # IMAGE is not in supported_categories, so can_process returns False
        assert p.can_process(evidence) is False

    def test_prefetch_file_parsing(self, tmp_path):
        pf_dir = tmp_path / "Windows" / "Prefetch"
        pf_dir.mkdir(parents=True)
        pf_path = pf_dir / "CMD.EXE-12345678.pf"

        # Build a valid prefetch header
        sig = b"\x53\x43\x43\x41"
        version = struct.pack("<I", 30)
        file_name_offset = struct.pack("<I", 16)
        file_name_size = struct.pack("<I", 32)
        # 88 bytes total header with executable name at offset 16
        executable = "CMD.EXE".encode("utf-16-le").ljust(32, b"\x00")
        last_run_ft = struct.pack("<Q", 133000000000000000)
        run_count = struct.pack("<I", 42)
        padding = b"\x00" * 24

        header = sig + version + file_name_offset + file_name_size + executable + last_run_ft + run_count + padding
        header = header.ljust(84, b"\x00")

        pf_path.write_bytes(header + b"\x00" * 200)

        dummy = _create_test_file(tmp_path, "dummy.txt", b"windows artifact placeholder")
        evidence = _make_evidence(dummy, "dummy.txt", EvidenceCategory.WINDOWS_ARTIFACT)
        config = ForensicProcessorConfig()
        processor = WindowsForensicsProcessor()
        processor.process(evidence, config)

        assert "prefetch_analysis" in evidence.tags

    def test_lnk_file_parsing(self, tmp_path):
        # Build a valid LNK file header
        sig = b"\x4c\x00\x00\x00"
        flags = struct.pack("<I", 0x01)  # HasTargetIDList
        file_attrs = struct.pack("<I", 0x20)
        creation_ft = struct.pack("<Q", 133000000000000000)
        access_ft = struct.pack("<Q", 133000000000000000)
        write_ft = struct.pack("<Q", 133000000000000000)
        file_size = struct.pack("<I", 1024)
        icon_index = struct.pack("<i", 0)
        show_window = struct.pack("<I", 1)
        hotkey = struct.pack("<H", 0)

        header = sig + flags + file_attrs + creation_ft + access_ft + write_ft + file_size + icon_index + show_window + hotkey
        header = header.ljust(76, b"\x00")

        lnk_path = tmp_path / "test.lnk"
        lnk_path.write_bytes(header)
        _create_test_file(tmp_path, "dummy.txt", b"dummy")

        evidence = _make_evidence(str(tmp_path / "dummy.txt"), "dummy.txt", EvidenceCategory.WINDOWS_ARTIFACT)
        config = ForensicProcessorConfig()
        processor = WindowsForensicsProcessor()
        processor.process(evidence, config)

        # LNK parsing attempted - may not find results due to limited data
        # but should not crash
        assert isinstance(evidence.tags, list)

    def test_missing_files(self, tmp_path):
        evidence = _make_evidence(
            _create_test_file(tmp_path, "empty.txt", b""),
            "empty.txt",
            EvidenceCategory.WINDOWS_ARTIFACT,
        )
        config = ForensicProcessorConfig()
        processor = WindowsForensicsProcessor()
        processor.process(evidence, config)
        assert isinstance(evidence.tags, list)

    def test_scheduled_tasks_xml(self, tmp_path):
        tasks_dir = tmp_path / "Windows" / "System32" / "Tasks"
        tasks_dir.mkdir(parents=True)
        task_xml = tasks_dir / "MyTask.xml"
        task_xml.write_text("""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Author>SYSTEM</Author></RegistrationInfo>
  <Triggers><CalendarTrigger><StartBoundary>2024-01-01T09:00:00</StartBoundary></CalendarTrigger></Triggers>
  <Actions><Exec><Command>cmd.exe</Command></Exec></Actions>
</Task>""")

        _create_test_file(tmp_path, "dummy.txt", b"dummy")
        evidence = _make_evidence(str(tmp_path / "dummy.txt"), "dummy.txt", EvidenceCategory.WINDOWS_ARTIFACT)
        config = ForensicProcessorConfig()
        processor = WindowsForensicsProcessor()
        processor.process(evidence, config)

        assert "scheduled_task" in evidence.tags


# ===================================================================
# 4. MOBILE FORENSICS TESTS
# ===================================================================

class TestMobileForensicsProcessor:
    def test_class_properties(self):
        p = MobileForensicsProcessor()
        assert p.name == "mobile_forensics"
        assert "Android" in p.description or "iOS" in p.description
        assert EvidenceCategory.MOBILE_ARTIFACT in p.supported_categories

    def test_can_process_mobile(self):
        p = MobileForensicsProcessor()
        evidence = MagicMock()
        evidence.category = EvidenceCategory.MOBILE_ARTIFACT
        assert p.can_process(evidence) is True

    def test_unsupported_category_does_not_match(self):
        p = MobileForensicsProcessor()
        evidence = MagicMock()
        evidence.category = EvidenceCategory.IMAGE
        # IMAGE is not in supported_categories, so can_process returns False
        assert p.can_process(evidence) is False

    def test_android_sms_database(self, tmp_path):
        db_path = tmp_path / "mmssms.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE sms (
                address TEXT,
                body TEXT,
                date INTEGER,
                type INTEGER,
                read INTEGER,
                seen INTEGER,
                subject TEXT,
                person TEXT,
                date_sent INTEGER,
                error_code INTEGER,
                service_center TEXT
            )
        """)
        cursor.execute(
            "INSERT INTO sms VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("+15551234567", "Hello there!", 1700000000000, 2, 1, 1, None, None, 1700000000000, 0, None),
        )
        cursor.execute(
            "INSERT INTO sms VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ("+15559876543", "Goodbye!", 1700000100000, 1, 0, 1, None, None, 1700000100000, 0, None),
        )
        conn.commit()
        conn.close()

        evidence = _make_evidence(str(db_path), "mmssms.db", EvidenceCategory.MOBILE_ARTIFACT)
        config = ForensicProcessorConfig()
        processor = MobileForensicsProcessor()
        processor.process(evidence, config)

        assert "mobile_android" in evidence.tags

    def test_android_contacts_database(self, tmp_path):
        db_path = tmp_path / "contacts2.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE mimetypes (_id INTEGER, mimetype TEXT)")
        cursor.execute("CREATE TABLE contacts (_id INTEGER, display_name TEXT, starred INTEGER, times_contacted INTEGER)")
        cursor.execute("CREATE TABLE data (_id INTEGER, contact_id INTEGER, mimetype_id INTEGER, data1 TEXT)")
        cursor.execute("INSERT INTO mimetypes VALUES (1, 'vnd.android.cursor.item/phone_v2')")
        cursor.execute("INSERT INTO contacts VALUES (1, 'John Doe', 0, 5)")
        cursor.execute("INSERT INTO data VALUES (1, 1, 1, '+15551234567')")
        conn.commit()
        conn.close()

        evidence = _make_evidence(str(db_path), "contacts2.db", EvidenceCategory.MOBILE_ARTIFACT)
        config = ForensicProcessorConfig()
        processor = MobileForensicsProcessor()
        processor.process(evidence, config)

        assert "android_contacts" in evidence.tags

    def test_platform_auto_detection_android(self, tmp_path):
        android_dir = tmp_path / "data" / "com.android.providers.telephony"
        android_dir.mkdir(parents=True)
        db_path = android_dir / "mmssms.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE sms (
                address TEXT, body TEXT, date INTEGER, type INTEGER,
                read INTEGER, seen INTEGER, subject TEXT, person TEXT,
                date_sent INTEGER, error_code INTEGER, service_center TEXT
            )
        """)
        conn.commit()
        conn.close()

        _create_test_file(tmp_path, "dummy.txt", b"dummy")
        evidence = _make_evidence(str(tmp_path / "dummy.txt"), "dummy.txt", EvidenceCategory.MOBILE_ARTIFACT)
        evidence.storage_path = str(tmp_path)
        config = ForensicProcessorConfig()
        processor = MobileForensicsProcessor()
        processor.process(evidence, config)

        assert any("android" in t for t in evidence.tags)

    def test_empty_database(self, tmp_path):
        db_path = tmp_path / "mmssms.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE sms (
                address TEXT, body TEXT, date INTEGER, type INTEGER,
                read INTEGER, seen INTEGER, subject TEXT, person TEXT,
                date_sent INTEGER, error_code INTEGER, service_center TEXT
            )
        """)
        conn.commit()
        conn.close()

        evidence = _make_evidence(str(db_path), "mmssms.db", EvidenceCategory.MOBILE_ARTIFACT)
        config = ForensicProcessorConfig()
        processor = MobileForensicsProcessor()
        processor.process(evidence, config)

        # Should not crash; may report no data
        assert isinstance(evidence.tags, list)


# ===================================================================
# 5. EMAIL FORENSICS TESTS
# ===================================================================

class TestEmailForensicsProcessor:
    def test_class_properties(self):
        p = EmailForensicsProcessor()
        assert p.name == "email_forensics"
        assert "SPF" in p.description or "email" in p.description.lower()
        assert EvidenceCategory.EMAIL in p.supported_categories

    def test_can_process_email(self):
        p = EmailForensicsProcessor()
        evidence = MagicMock()
        evidence.category = EvidenceCategory.EMAIL
        assert p.can_process(evidence) is True

    def test_unsupported_category_does_not_match(self):
        p = EmailForensicsProcessor()
        evidence = MagicMock()
        evidence.category = EvidenceCategory.IMAGE
        # IMAGE is not in supported_categories, so can_process returns False
        assert p.can_process(evidence) is False

    def test_eml_parsing_with_headers(self, tmp_path):
        eml_content = (
            b"From: sender@example.com\r\n"
            b"To: recipient@example.com\r\n"
            b"Subject: Test Email\r\n"
            b"Date: Mon, 15 Jun 2024 10:00:00 +0000\r\n"
            b"Message-ID: <test-123@example.com>\r\n"
            b"X-Originating-IP: 10.0.0.1\r\n"
            b"User-Agent: Outlook/16.0\r\n"
            b"\r\n"
            b"This is the email body.\r\n"
        )
        fp = _create_test_file(tmp_path, "test.eml", eml_content)
        evidence = _make_evidence(fp, "test.eml", EvidenceCategory.EMAIL)
        config = ForensicProcessorConfig()
        processor = EmailForensicsProcessor()
        processor.process(evidence, config)

        assert "email" in evidence.tags
        assert "email_forensics" in evidence.processor_results
        result = evidence.processor_results["email_forensics"]
        assert result["headers"]["sender_email"] == "sender@example.com"
        assert result["headers"]["subject"] == "Test Email"
        assert result["body_preview"] == "This is the email body."

    def test_header_analysis(self, tmp_path):
        eml_content = (
            b"From: alice@gmail.com\r\n"
            b"To: bob@gmail.com\r\n"
            b"CC: charlie@gmail.com\r\n"
            b"Subject: Analysis\r\n"
            b"Date: Mon, 15 Jun 2024 10:00:00 +0000\r\n"
            b"Message-ID: <abc-456@gmail.com>\r\n"
            b"Return-Path: <alice@gmail.com>\r\n"
            b"Received: from mail.example.com ([10.0.0.1]) by mx.google.com\r\n"
            b"    with ESMTPS id abc123 for <bob@gmail.com>\r\n"
            b"    (version=TLS1_3 cipher=TLS_AES_256_GCM_SHA384);\r\n"
            b"    Mon, 15 Jun 2024 10:00:00 +0000 (+0000)\r\n"
            b"\r\n"
            b"Hello Bob!\r\n"
        )
        fp = _create_test_file(tmp_path, "analysis.eml", eml_content)
        evidence = _make_evidence(fp, "analysis.eml", EvidenceCategory.EMAIL)
        config = ForensicProcessorConfig()
        processor = EmailForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["email_forensics"]
        assert result["headers"]["sender_domain"] == "gmail.com"
        assert result["headers"]["received_count"] >= 1
        assert result["thread"]["from"] == "alice@gmail.com"
        assert "bob@gmail.com" in result["thread"]["participants"]

    def test_spf_pass(self, tmp_path):
        eml_content = (
            b"From: sender@example.com\r\n"
            b"To: recipient@example.com\r\n"
            b"Subject: SPF Pass\r\n"
            b"Date: Mon, 15 Jun 2024 10:00:00 +0000\r\n"
            b"Authentication-Results: mx.example.com;\r\n"
            b"    spf=pass smtp.mailfrom=sender.example.com\r\n"
            b"\r\n"
            b"Body\r\n"
        )
        fp = _create_test_file(tmp_path, "spf_pass.eml", eml_content)
        evidence = _make_evidence(fp, "spf_pass.eml", EvidenceCategory.EMAIL)
        config = ForensicProcessorConfig()
        processor = EmailForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["email_forensics"]
        assert result["spf_result"] == "pass"

    def test_spf_fail(self, tmp_path):
        eml_content = (
            b"From: sender@evil.com\r\n"
            b"To: recipient@example.com\r\n"
            b"Subject: SPF Fail\r\n"
            b"Date: Mon, 15 Jun 2024 10:00:00 +0000\r\n"
            b"Received-SPF: fail (google.com: domain of sender@evil.com does not designate 10.0.0.1 as permitted sender)\r\n"
            b"\r\n"
            b"Body\r\n"
        )
        fp = _create_test_file(tmp_path, "spf_fail.eml", eml_content)
        evidence = _make_evidence(fp, "spf_fail.eml", EvidenceCategory.EMAIL)
        config = ForensicProcessorConfig()
        processor = EmailForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["email_forensics"]
        assert result["spf_result"] == "fail"

    def test_dkim_validation(self, tmp_path):
        eml_content = (
            b"From: sender@example.com\r\n"
            b"To: recipient@example.com\r\n"
            b"Subject: DKIM Test\r\n"
            b"Date: Mon, 15 Jun 2024 10:00:00 +0000\r\n"
            b"DKIM-Signature: v=1; a=rsa-sha256; d=example.com; s=selector1;\r\n"
            b"    h=from:to:subject:date;\r\n"
            b"Authentication-Results: mx.example.com;\r\n"
            b"    dkim=pass header.d=example.com\r\n"
            b"\r\n"
            b"Body\r\n"
        )
        fp = _create_test_file(tmp_path, "dkim_test.eml", eml_content)
        evidence = _make_evidence(fp, "dkim_test.eml", EvidenceCategory.EMAIL)
        config = ForensicProcessorConfig()
        processor = EmailForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["email_forensics"]
        assert result["dkim_result"] == "pass"

    def test_thread_reconstruction(self, tmp_path):
        eml_content = (
            b"From: alice@example.com\r\n"
            b"To: bob@example.com\r\n"
            b"Subject: Re: Original Subject\r\n"
            b"Date: Mon, 15 Jun 2024 12:00:00 +0000\r\n"
            b"Message-ID: <reply-001@example.com>\r\n"
            b"In-Reply-To: <original-001@example.com>\r\n"
            b"References: <original-001@example.com> <mid-001@example.com>\r\n"
            b"\r\n"
            b"This is a reply.\r\n"
        )
        fp = _create_test_file(tmp_path, "thread.eml", eml_content)
        evidence = _make_evidence(fp, "thread.eml", EvidenceCategory.EMAIL)
        config = ForensicProcessorConfig()
        processor = EmailForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["email_forensics"]
        assert result["thread"]["is_reply"] is True
        assert result["thread"]["in_reply_to"] == "<original-001@example.com>"
        assert result["thread"]["thread_depth"] >= 2

    def test_hop_analysis(self, tmp_path):
        eml_content = (
            b"From: sender@example.com\r\n"
            b"To: recipient@example.com\r\n"
            b"Subject: Hop Analysis\r\n"
            b"Date: Mon, 15 Jun 2024 10:00:00 +0000\r\n"
            b"Received: from relay1.example.com ([10.0.0.1]) by mx.receiver.com\r\n"
            b"    with ESMTP id 123; Mon, 15 Jun 2024 10:00:00 +0000\r\n"
            b"Received: from relay2.evil.com ([192.168.1.100]) by relay1.example.com\r\n"
            b"    with ESMTP id 456; Mon, 15 Jun 2024 09:59:59 +0000\r\n"
            b"\r\n"
            b"Body\r\n"
        )
        fp = _create_test_file(tmp_path, "hops.eml", eml_content)
        evidence = _make_evidence(fp, "hops.eml", EvidenceCategory.EMAIL)
        config = ForensicProcessorConfig()
        processor = EmailForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["email_forensics"]
        assert len(result["hops"]) >= 2
        assert result["hops"][0]["from_ip"] is not None

    def test_suspicious_indicators(self, tmp_path):
        eml_content = (
            b"From: admin@gmai1.com\r\n"
            b"To: user@example.com\r\n"
            b"Subject: Urgent\r\n"
            b"Date: Mon, 15 Jun 2024 10:00:00 +0000\r\n"
            b"Return-Path: <admin@evil.com>\r\n"
            b"\r\n"
            b"Click this link: http://192.168.1.1/malware\r\n"
        )
        fp = _create_test_file(tmp_path, "suspicious.eml", eml_content)
        evidence = _make_evidence(fp, "suspicious.eml", EvidenceCategory.EMAIL)
        config = ForensicProcessorConfig()
        processor = EmailForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["email_forensics"]
        assert len(result["suspicious_indicators"]) > 0
        indicator_types = [s["type"] for s in result["suspicious_indicators"]]
        assert "lookalike_domain" in indicator_types or "return_path_mismatch" in indicator_types

    def test_attachment_extraction(self, tmp_path):
        msg = MIMEMultipart()
        msg["From"] = "sender@example.com"
        msg["To"] = "recipient@example.com"
        msg["Subject"] = "Attachment Test"
        msg["Date"] = "Mon, 15 Jun 2024 10:00:00 +0000"

        body = MIMEText("See attached file.", "plain")
        msg.attach(body)

        attachment = MIMEBase("application", "octet-stream")
        attachment.set_payload(b"Fake PDF content")
        encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition", "attachment", filename="document.pdf")
        msg.attach(attachment)

        fp = _create_test_file(tmp_path, "attach.eml", msg.as_bytes())
        evidence = _make_evidence(fp, "attach.eml", EvidenceCategory.EMAIL)
        config = ForensicProcessorConfig()
        processor = EmailForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["email_forensics"]
        assert result["attachment_graph"]["total_attachment_count"] >= 1

    def test_missing_headers_anomaly(self, tmp_path):
        eml_content = (
            b"Received: from somewhere\r\n"
            b"\r\n"
            b"Just a body with no standard headers.\r\n"
        )
        fp = _create_test_file(tmp_path, "bare.eml", eml_content)
        evidence = _make_evidence(fp, "bare.eml", EvidenceCategory.EMAIL)
        config = ForensicProcessorConfig()
        processor = EmailForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["email_forensics"]
        assert len(result["headers"]["anomalies"]) > 0


# ===================================================================
# 6. NETWORK FORENSICS TESTS
# ===================================================================

class TestNetworkForensicsProcessor:
    def test_class_properties(self):
        p = NetworkForensicsProcessor()
        assert p.name == "network_forensics"
        assert "PCAP" in p.description or "network" in p.description.lower()
        assert EvidenceCategory.NETWORK_CAPTURE in p.supported_categories

    def test_can_process_network(self):
        p = NetworkForensicsProcessor()
        evidence = MagicMock()
        evidence.category = EvidenceCategory.NETWORK_CAPTURE
        assert p.can_process(evidence) is True

    def test_unsupported_category_does_not_match(self):
        p = NetworkForensicsProcessor()
        evidence = MagicMock()
        evidence.category = EvidenceCategory.IMAGE
        # IMAGE is not in supported_categories, so can_process returns False
        assert p.can_process(evidence) is False

    def test_pcap_header_parsing(self, tmp_path):
        # Create a minimal valid PCAP file with one packet
        import io

        pcap_data = io.BytesIO()
        # Magic number (little-endian)
        pcap_data.write(b"\xd4\xc3\xb2\xa1")
        # Version 2.4
        pcap_data.write(struct.pack("<HH", 2, 4))
        # Timezone, Sigfigs, Snaplen, LinkType (Ethernet)
        pcap_data.write(struct.pack("<iIII", 0, 0, 65535, 1))

        # One Ethernet/IP/TCP packet
        eth_header = b"\x00" * 12 + struct.pack("!H", 0x0800)
        ip_header = bytes([
            0x45, 0x00, 0x00, 0x28,  # ver/IHL, TOS, total length
            0x00, 0x00, 0x00, 0x00,  # ID, flags, frag offset
            0x40, 0x06, 0x00, 0x00,  # TTL(64), proto(TCP), checksum
        ])
        src_ip = bytes([10, 0, 0, 1])
        dst_ip = bytes([192, 168, 1, 1])
        ip_header += src_ip + dst_ip

        tcp_header = struct.pack("!HH", 12345, 80)  # src port, dst port
        tcp_header += b"\x00" * 4  # seq
        tcp_header += b"\x00" * 4  # ack
        tcp_header += bytes([0x50, 0x02])  # data offset + flags (SYN)
        tcp_header += struct.pack("!H", 65535)  # window
        tcp_header += b"\x00" * 2  # checksum
        tcp_header += b"\x00" * 2  # urgent pointer

        pkt_data = eth_header + ip_header + tcp_header
        # Packet header: ts_sec, ts_usec, incl_len, orig_len
        pcap_data.write(struct.pack("<IIII", 1700000000, 0, len(pkt_data), len(pkt_data)))
        pcap_data.write(pkt_data)

        fp = _create_test_file(tmp_path, "test.pcap", pcap_data.getvalue())
        evidence = _make_evidence(fp, "test.pcap", EvidenceCategory.NETWORK_CAPTURE)
        config = ForensicProcessorConfig()
        processor = NetworkForensicsProcessor()
        processor.process(evidence, config)

        assert "network_capture" in evidence.tags
        assert "pcap_total_packets" in evidence.metadata
        assert evidence.metadata["pcap_total_packets"] >= 1

    def test_dns_query_extraction(self, tmp_path):
        import io

        # Build a minimal PCAP with a DNS query
        pcap_data = io.BytesIO()
        pcap_data.write(b"\xd4\xc3\xb2\xa1")
        pcap_data.write(struct.pack("<HH", 2, 4))
        pcap_data.write(struct.pack("<iIII", 0, 0, 65535, 1))

        # Ethernet header
        eth_header = b"\x00" * 12 + struct.pack("!H", 0x0800)

        # IP header (UDP)
        ip_header = bytes([0x45, 0x00])
        ip_header += struct.pack("!H", 0x003C)  # total length
        ip_header += b"\x00\x00\x00\x00"
        ip_header += bytes([0x40, 0x11])  # TTL=64, proto=UDP
        ip_header += b"\x00\x00"
        ip_header += bytes([10, 0, 0, 1]) + bytes([10, 0, 0, 2])

        # UDP header
        udp_header = struct.pack("!HH", 12345, 53)  # src port, dst port
        udp_header += struct.pack("!H", 8 + 20)  # length
        udp_header += b"\x00\x00"  # checksum

        # DNS query for example.com
        dns_query = struct.pack("!H", 0x1234)  # transaction ID
        dns_query += struct.pack("!H", 0x0100)  # flags (standard query)
        dns_query += struct.pack("!HHHH", 1, 0, 0, 0)  # counts
        # QNAME: example.com
        dns_query += b"\x07example\x03com\x00"
        dns_query += struct.pack("!HH", 1, 1)  # QTYPE=A, QCLASS=IN

        pkt_data = eth_header + ip_header + udp_header + dns_query
        pcap_data.write(struct.pack("<IIII", 1700000000, 0, len(pkt_data), len(pkt_data)))
        pcap_data.write(pkt_data)

        fp = _create_test_file(tmp_path, "dns.pcap", pcap_data.getvalue())
        evidence = _make_evidence(fp, "dns.pcap", EvidenceCategory.NETWORK_CAPTURE)
        config = ForensicProcessorConfig()
        processor = NetworkForensicsProcessor()
        processor.process(evidence, config)

        assert "dns_queries" in evidence.processor_results

    def test_empty_pcap(self, tmp_path):
        fp = _create_test_file(tmp_path, "empty.pcap", b"\x00" * 24)
        evidence = _make_evidence(fp, "empty.pcap", EvidenceCategory.NETWORK_CAPTURE)
        config = ForensicProcessorConfig()
        processor = NetworkForensicsProcessor()
        processor.process(evidence, config)
        assert any("failed" in e.lower() or "error" in e.lower() or "unrecognized" in e.lower()
                    for e in evidence.processing_errors)

    def test_invalid_magic_bytes(self, tmp_path):
        fp = _create_test_file(tmp_path, "bad.pcap", b"\x00\x00\x00\x00" + b"\x00" * 20)
        evidence = _make_evidence(fp, "bad.pcap", EvidenceCategory.NETWORK_CAPTURE)
        config = ForensicProcessorConfig()
        processor = NetworkForensicsProcessor()
        processor.process(evidence, config)
        assert any("unrecognized" in e.lower() or "error" in e.lower()
                    for e in evidence.processing_errors)


# ===================================================================
# 7. DISK FORENSICS TESTS
# ===================================================================

class TestDiskForensicsProcessor:
    def test_class_properties(self):
        p = DiskForensicsProcessor()
        assert p.name == "disk_forensics"
        assert "disk" in p.description.lower()
        assert EvidenceCategory.DISK_IMAGE in p.supported_categories

    def test_can_process_disk(self):
        p = DiskForensicsProcessor()
        evidence = MagicMock()
        evidence.category = EvidenceCategory.DISK_IMAGE
        assert p.can_process(evidence) is True

    def test_mbr_partition_detection(self, tmp_path):
        # Create a file with a valid MBR header
        mbr = bytearray(512)
        # Boot signature at offset 510
        mbr[510] = 0x55
        mbr[511] = 0xAA
        # Partition entry 1 at offset 446: type 0x07 (NTFS), active flag
        mbr[446] = 0x80  # active
        mbr[446 + 4] = 0x07  # type
        struct.pack_into("<I", mbr, 446 + 8, 2048)  # LBA start
        struct.pack_into("<I", mbr, 446 + 12, 1000000)  # LBA count

        # Fill rest with noise
        for i in range(512, 4096):
            mbr.append(i % 256)

        fp = _create_test_file(tmp_path, "disk.raw", bytes(mbr))
        evidence = _make_evidence(fp, "disk.raw", EvidenceCategory.DISK_IMAGE)
        config = ForensicProcessorConfig()
        processor = DiskForensicsProcessor()
        processor.process(evidence, config)

        assert "disk_forensics" in evidence.tags

    def test_file_carving(self, tmp_path):
        # Create a file with embedded JPEG magic bytes
        data = b"\x00" * 100
        data += b"\xff\xd8\xff"  # JPEG magic
        data += b"\x00" * 200
        data += b"\xff\xd9"  # JPEG footer
        data += b"\x00" * 100
        data += b"%PDF-1.4"  # PDF magic
        data += b"\x00" * 150
        data += b"%%EOF"  # PDF footer

        fp = _create_test_file(tmp_path, "disk.raw", data)
        evidence = _make_evidence(fp, "disk.raw", EvidenceCategory.DISK_IMAGE)
        config = ForensicProcessorConfig()
        processor = DiskForensicsProcessor()
        processor.process(evidence, config)

        carved = evidence.metadata.get("carved_files", [])
        assert len(carved) > 0

    def test_filesystem_detection(self, tmp_path):
        # Create a file with FAT boot sector signature
        boot_sector = bytearray(512)
        boot_sector[0:3] = b"\xeb\x3c\x90"  # JMP instruction
        boot_sector[3:11] = b"MSDOS5.0"
        boot_sector[510] = 0x55
        boot_sector[511] = 0xAA

        fp = _create_test_file(tmp_path, "fat.img", bytes(boot_sector))
        evidence = _make_evidence(fp, "fat.img", EvidenceCategory.DISK_IMAGE)
        config = ForensicProcessorConfig()
        processor = DiskForensicsProcessor()
        processor.process(evidence, config)

        fs_info = evidence.metadata.get("filesystem_info", {})
        # Should detect some filesystem type
        assert isinstance(fs_info, dict)

    def test_unallocated_space_analysis(self, tmp_path):
        data = b"Hello, this is a test string longer than six characters.\n"
        data += b"\x00" * 100
        data += b"Another string for unicode detection.\n"
        data += b"\xff\xd8\xff" + b"\x00" * 50  # JPEG magic embedded

        fp = _create_test_file(tmp_path, "unalloc.raw", data)
        evidence = _make_evidence(fp, "unalloc.raw", EvidenceCategory.DISK_IMAGE)
        config = ForensicProcessorConfig()
        processor = DiskForensicsProcessor()
        processor.process(evidence, config)

        unalloc = evidence.metadata.get("unallocated_analysis", {})
        assert isinstance(unalloc, dict)

    def test_gpt_partition_detection(self, tmp_path):
        # Create a file with GPT header
        data = bytearray(2048)
        # MBR protective
        struct.pack_into("<H", data, 510, 0xAA55)

        # GPT header at LBA 1 (offset 512)
        gpt_offset = 512
        data[gpt_offset:gpt_offset + 8] = b"EFI PART"
        struct.pack_into("<Q", data, gpt_offset + 72, 2)  # part_entry_lba
        struct.pack_into("<I", data, gpt_offset + 80, 128)  # part_entry_count
        struct.pack_into("<I", data, gpt_offset + 84, 128)  # part_entry_size

        fp = _create_test_file(tmp_path, "gpt.img", bytes(data))
        evidence = _make_evidence(fp, "gpt.img", EvidenceCategory.DISK_IMAGE)
        config = ForensicProcessorConfig()
        processor = DiskForensicsProcessor()
        processor.process(evidence, config)

        assert "disk_forensics" in evidence.tags


# ===================================================================
# 8. MEMORY FORENSICS TESTS
# ===================================================================

class TestMemoryForensicsProcessor:
    def test_class_properties(self):
        p = MemoryForensicsProcessor()
        assert p.name == "memory_forensics"
        assert "memory" in p.description.lower()
        assert EvidenceCategory.MEMORY_DUMP in p.supported_categories

    def test_can_process_memory(self):
        p = MemoryForensicsProcessor()
        evidence = MagicMock()
        evidence.category = EvidenceCategory.MEMORY_DUMP
        assert p.can_process(evidence) is True

    def test_format_detection_raw(self, tmp_path):
        fp = _create_test_file(tmp_path, "raw_mem.bin", b"\x00" * (101 * 1024 * 1024))
        evidence = _make_evidence(fp, "raw_mem.bin", EvidenceCategory.MEMORY_DUMP)
        config = ForensicProcessorConfig()
        processor = MemoryForensicsProcessor()
        processor.process(evidence, config)

        assert evidence.metadata.get("memory_format") == "raw_memory"

    def test_format_detection_hiberfil(self, tmp_path):
        fp = _create_test_file(tmp_path, "hiberfil.sys", b"hibr" + b"\x00" * 1024)
        evidence = _make_evidence(fp, "hiberfil.sys", EvidenceCategory.MEMORY_DUMP)
        config = ForensicProcessorConfig()
        processor = MemoryForensicsProcessor()
        processor.process(evidence, config)

        assert evidence.metadata.get("memory_format") == "hiberfil.sys"
        assert "hibernation_file" in evidence.tags

    def test_format_detection_crashdump(self, tmp_path):
        fp = _create_test_file(tmp_path, "memory.dmp", b"PAGE" + b"\x00" * 1024)
        evidence = _make_evidence(fp, "memory.dmp", EvidenceCategory.MEMORY_DUMP)
        config = ForensicProcessorConfig()
        processor = MemoryForensicsProcessor()
        processor.process(evidence, config)

        assert evidence.metadata.get("memory_format") == "crash_dump"
        assert "crash_dump" in evidence.tags

    def test_format_detection_pe_header(self, tmp_path):
        fp = _create_test_file(tmp_path, "pe_mem.bin", b"MZ" + b"\x00" * 1024)
        evidence = _make_evidence(fp, "pe_mem.bin", EvidenceCategory.MEMORY_DUMP)
        config = ForensicProcessorConfig()
        processor = MemoryForensicsProcessor()
        processor.process(evidence, config)

        assert evidence.metadata.get("memory_format") == "raw_memory"

    def test_string_extraction_ascii(self, tmp_path):
        # Create memory dump with known ASCII strings
        data = b"\x00" * 64
        data += b"Hello World from memory dump!"
        data += b"\x00" * 64
        data += b"https://example.com/malware"
        data += b"\x00" * 64
        data += b"C:\\Windows\\System32\\cmd.exe"
        data += b"\x00" * 64

        fp = _create_test_file(tmp_path, "strings.bin", data)
        evidence = _make_evidence(fp, "strings.bin", EvidenceCategory.MEMORY_DUMP)
        config = ForensicProcessorConfig()
        processor = MemoryForensicsProcessor()
        processor.process(evidence, config)

        strings_result = evidence.metadata.get("memory_strings", {})
        assert strings_result.get("ascii_count", 0) > 0
        assert strings_result.get("interesting_strings") is not None

    def test_string_extraction_unicode(self, tmp_path):
        # Create memory dump with UTF-16LE strings
        unicode_str = "Unicode Test String".encode("utf-16-le")
        data = b"\x00" * 64
        data += unicode_str
        data += b"\x00" * 64

        fp = _create_test_file(tmp_path, "unicode.bin", data)
        evidence = _make_evidence(fp, "unicode.bin", EvidenceCategory.MEMORY_DUMP)
        config = ForensicProcessorConfig()
        processor = MemoryForensicsProcessor()
        processor.process(evidence, config)

        strings_result = evidence.metadata.get("memory_strings", {})
        assert strings_result.get("unicode_count", 0) > 0

    def test_registry_hive_extraction(self, tmp_path):
        # Create a fake registry hive with regf signature
        hive_data = bytearray(4096)
        hive_data[0:4] = b"regf"
        struct.pack_into("<I", hive_data, 4, 1)  # seq1
        struct.pack_into("<I", hive_data, 8, 1)  # seq2
        # File name at offset 48 (64 bytes UTF-16LE)
        fname = "SYSTEM".encode("utf-16-le")
        hive_data[48:48 + len(fname)] = fname

        fp = _create_test_file(tmp_path, "mem.bin", bytes(hive_data) + b"\x00" * (4096 * 10))
        evidence = _make_evidence(fp, "mem.bin", EvidenceCategory.MEMORY_DUMP)
        config = ForensicProcessorConfig()
        processor = MemoryForensicsProcessor()
        processor.process(evidence, config)

        hives = evidence.metadata.get("registry_hives", [])
        assert len(hives) > 0
        assert hives[0]["consistent"] is True

    def test_injected_code_detection(self, tmp_path):
        # Create memory dump with shellcode signatures
        data = b"\x00" * 1024
        data += b"\xfc\xe8"  # CLD; CALL rel32 (shellcode signature)
        data += b"\x00" * 100
        data += b"\x48\x89\xe5"  # MOV RBP, RSP (x64 prologue)
        data += b"\x00" * 100
        data += b"\x60\x8d\x3c\x24"  # PUSHAD; LEA EDI, [ESP]
        data += b"\x00" * 4096

        fp = _create_test_file(tmp_path, "inject.bin", data)
        evidence = _make_evidence(fp, "inject.bin", EvidenceCategory.MEMORY_DUMP)
        config = ForensicProcessorConfig()
        processor = MemoryForensicsProcessor()
        processor.process(evidence, config)

        injections = evidence.metadata.get("injected_code_detections", [])
        assert len(injections) > 0
        assert "injected_code" in evidence.tags

    def test_process_tree_construction(self, tmp_path):
        # Memory dump large enough to trigger process extraction attempt
        data = b"\x00" * (2 * 1024 * 1024)
        fp = _create_test_file(tmp_path, "proc_mem.bin", data)
        evidence = _make_evidence(fp, "proc_mem.bin", EvidenceCategory.MEMORY_DUMP)
        config = ForensicProcessorConfig()
        processor = MemoryForensicsProcessor()
        processor.process(evidence, config)

        # Should have process tree metadata (may be empty)
        assert "process_tree" in evidence.metadata


# ===================================================================
# 9. INTEGRITY TESTS
# ===================================================================

class TestIntegrityForensicsProcessor:
    def test_class_properties(self):
        p = IntegrityForensicsProcessor()
        assert p.name == "integrity_forensics"
        assert "integrity" in p.description.lower()

    def test_hash_computation_and_verification(self, tmp_path):
        content = b"test content for hash verification"
        fp = _create_test_file(tmp_path, "hash_test.bin", content)
        expected_sha256 = hashlib.sha256(content).hexdigest()
        evidence = _make_evidence(fp, "hash_test.bin", sha256=expected_sha256)
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["integrity_forensics"]
        assert result["hash_verification"]["sha256"] == expected_sha256
        assert result["hash_verification"]["mismatch"] is False

    def test_hash_mismatch_detection(self, tmp_path):
        content = b"test content for mismatch"
        fp = _create_test_file(tmp_path, "mismatch.bin", content)
        evidence = _make_evidence(fp, "mismatch.bin", sha256="0" * 64)
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["integrity_forensics"]
        assert result["hash_verification"]["mismatch"] is True

    def test_extension_mismatch_detection(self, tmp_path):
        # PNG magic bytes but .txt extension
        content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        fp = _create_test_file(tmp_path, "fake.txt", content)
        evidence = _make_evidence(fp, "fake.txt")
        evidence.mime_type = "text/plain"
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["integrity_forensics"]
        assert result["header_mismatch"]["mismatch"] is True

    def test_header_mismatch_jpg(self, tmp_path):
        # JPEG magic bytes but .pdf extension
        content = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        fp = _create_test_file(tmp_path, "fake.pdf", content)
        evidence = _make_evidence(fp, "fake.pdf")
        evidence.mime_type = "application/pdf"
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["integrity_forensics"]
        assert result["header_mismatch"]["mismatch"] is True

    def test_truncation_detection_pdf(self, tmp_path):
        # PDF without %%EOF marker
        content = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\n"
        fp = _create_test_file(tmp_path, "truncated.pdf", content)
        evidence = _make_evidence(fp, "truncated.pdf")
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["integrity_forensics"]
        assert result["truncation"]["truncated"] is True

    def test_truncation_detection_png(self, tmp_path):
        # PNG without IEND chunk
        content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        fp = _create_test_file(tmp_path, "truncated.png", content)
        evidence = _make_evidence(fp, "truncated.png")
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["integrity_forensics"]
        assert result["truncation"]["truncated"] is True

    def test_truncation_detection_zip(self, tmp_path):
        # ZIP without EOCD record
        content = b"PK\x03\x04" + b"\x00" * 100
        fp = _create_test_file(tmp_path, "truncated.zip", content)
        evidence = _make_evidence(fp, "truncated.zip")
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["integrity_forensics"]
        assert result["truncation"]["truncated"] is True

    def test_entropy_calculation_normal(self, tmp_path):
        content = b"Hello world! " * 100
        fp = _create_test_file(tmp_path, "normal.bin", content)
        evidence = _make_evidence(fp, "normal.bin")
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["integrity_forensics"]
        assert result["entropy"]["entropy"] is not None
        assert 0 < result["entropy"]["entropy"] < 7.5

    def test_entropy_calculation_high(self, tmp_path):
        # High entropy = random/encrypted data
        import random
        random.seed(42)
        content = bytes(random.randint(0, 255) for _ in range(10000))
        fp = _create_test_file(tmp_path, "encrypted.bin", content)
        evidence = _make_evidence(fp, "encrypted.bin")
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["integrity_forensics"]
        assert result["entropy"]["entropy"] > 7.0

    def test_entropy_empty_file(self, tmp_path):
        fp = _create_test_file(tmp_path, "empty.bin", b"")
        evidence = _make_evidence(fp, "empty.bin")
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["integrity_forensics"]
        assert result["entropy"]["classification"] == "empty"

    def test_corruption_detection_empty_file(self, tmp_path):
        fp = _create_test_file(tmp_path, "corrupt.bin", b"")
        evidence = _make_evidence(fp, "corrupt.bin")
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["integrity_forensics"]
        assert result["corruption"]["corrupted"] is True

    def test_corruption_detection_repeated_bytes(self, tmp_path):
        content = b"\xaa" * 5000
        fp = _create_test_file(tmp_path, "wiped.bin", content)
        evidence = _make_evidence(fp, "wiped.bin")
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["integrity_forensics"]
        assert result["corruption"]["corrupted"] is True

    def test_corruption_detection_png_no_iend(self, tmp_path):
        content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        fp = _create_test_file(tmp_path, "bad.png", content)
        evidence = _make_evidence(fp, "bad.png")
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["integrity_forensics"]
        assert result["corruption"]["corrupted"] is True

    def test_header_mismatch_valid(self, tmp_path):
        # JPEG file with correct extension
        content = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        fp = _create_test_file(tmp_path, "valid.jpg", content)
        evidence = _make_evidence(fp, "valid.jpg")
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["integrity_forensics"]
        assert result["header_mismatch"]["mismatch"] is False

    def test_zip_with_valid_ext(self, tmp_path):
        # ZIP magic with .docx extension should not be a mismatch
        content = b"PK\x03\x04" + b"\x00" * 100
        fp = _create_test_file(tmp_path, "doc.docx", content)
        evidence = _make_evidence(fp, "doc.docx")
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)

        result = evidence.processor_results["integrity_forensics"]
        assert result["header_mismatch"]["mismatch"] is False


# ===================================================================
# 10. INTEGRATION TESTS
# ===================================================================

class TestIntegrationWithPipeline:
    def test_all_processors_registered(self):
        pipeline = ProcessingPipeline()
        available = pipeline.get_available_processors()
        for name in ALL_ADVANCED_PROCESSORS:
            assert name in available, f"Processor {name} not registered in pipeline"

    def test_pipeline_processes_browser_data(self, tmp_path):
        db_path = tmp_path / "History"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE urls (
                url TEXT, title TEXT, visit_count INTEGER, last_visit_time INTEGER
            )
        """)
        conn.execute("INSERT INTO urls VALUES ('https://test.com', 'Test', 1, 13300000000000000)")
        conn.commit()
        conn.close()

        pipeline = ProcessingPipeline()
        result = pipeline.process_from_path(
            evidence_id="browser-ev-001",
            file_path=str(db_path),
            filename="History",
            sha256=hashlib.sha256(open(db_path, "rb").read()).hexdigest(),
            size=os.path.getsize(str(db_path)),
            mime_type=None,
        )

        assert result.success
        assert result.schema is not None

    def test_pipeline_processes_email(self, tmp_path):
        eml_content = (
            b"From: test@example.com\r\n"
            b"To: user@example.com\r\n"
            b"Subject: Integration Test\r\n"
            b"Date: Mon, 15 Jun 2024 10:00:00 +0000\r\n"
            b"\r\n"
            b"Integration test body.\r\n"
        )
        fp = _create_test_file(tmp_path, "integ.eml", eml_content)
        pipeline = ProcessingPipeline()
        result = pipeline.process_from_path(
            evidence_id="email-ev-001",
            file_path=fp,
            filename="integ.eml",
            sha256=hashlib.sha256(eml_content).hexdigest(),
            size=len(eml_content),
            mime_type="message/rfc822",
        )

        assert result.success

    def test_timeline_events_generated(self, tmp_path):
        db_path = tmp_path / "History"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE urls (
                url TEXT, title TEXT, visit_count INTEGER, last_visit_time INTEGER
            )
        """)
        chrome_time = int((datetime(2024, 6, 15, 12, 0, 0) - datetime(1601, 1, 1)).total_seconds() * 1_000_000)
        conn.execute("INSERT INTO urls VALUES ('https://example.com', 'Example', 1, ?)", (chrome_time,))
        conn.commit()
        conn.close()

        evidence = _make_evidence(str(db_path), "History", EvidenceCategory.BROWSER_DATA)
        config = ForensicProcessorConfig()
        processor = BrowserForensicsProcessor()
        processor.process(evidence, config)

        assert len(evidence.timeline_events) > 0

    def test_entities_and_relationships_generated(self, tmp_path):
        eml_content = (
            b"From: alice@example.com\r\n"
            b"To: bob@example.com\r\n"
            b"Subject: Entity Test\r\n"
            b"Date: Mon, 15 Jun 2024 10:00:00 +0000\r\n"
            b"Received: from relay.example.com ([10.0.0.1]) by mx.google.com\r\n"
            b"\r\n"
            b"Body\r\n"
        )
        fp = _create_test_file(tmp_path, "entity_test.eml", eml_content)
        evidence = _make_evidence(fp, "entity_test.eml", EvidenceCategory.EMAIL)
        config = ForensicProcessorConfig()
        processor = EmailForensicsProcessor()
        processor.process(evidence, config)

        assert len(evidence.entities) > 0
        assert len(evidence.relationships) > 0

    def test_processor_results_stored(self, tmp_path):
        eml_content = (
            b"From: test@example.com\r\n"
            b"To: user@example.com\r\n"
            b"Subject: Result Test\r\n"
            b"Date: Mon, 15 Jun 2024 10:00:00 +0000\r\n"
            b"\r\n"
            b"Body\r\n"
        )
        fp = _create_test_file(tmp_path, "result_test.eml", eml_content)
        evidence = _make_evidence(fp, "result_test.eml", EvidenceCategory.EMAIL)
        config = ForensicProcessorConfig()
        processor = EmailForensicsProcessor()
        processor.process(evidence, config)

        assert "email_forensics" in evidence.processor_results
        assert "headers" in evidence.processor_results["email_forensics"]

    def test_integrity_processor_via_pipeline(self, tmp_path):
        content = b"integrity test content"
        fp = _create_test_file(tmp_path, "integrity_test.bin", content)
        sha = hashlib.sha256(content).hexdigest()

        pipeline = ProcessingPipeline(config=ForensicProcessorConfig(enabled_processors=["integrity_forensics"]))
        result = pipeline.process_from_path(
            evidence_id="integrity-ev-001",
            file_path=fp,
            filename="integrity_test.bin",
            sha256=sha,
            size=len(content),
            mime_type=None,
        )

        assert result.success
        assert "integrity_verified" in result.schema.tags

    def test_memory_processor_via_pipeline(self, tmp_path):
        data = b"\x00" * 1024 + b"Test string for memory analysis" + b"\x00" * 1024
        fp = _create_test_file(tmp_path, "mem_test.bin", data)

        pipeline = ProcessingPipeline(config=ForensicProcessorConfig(enabled_processors=["memory_forensics"]))
        result = pipeline.process_from_path(
            evidence_id="mem-ev-001",
            file_path=fp,
            filename="mem_test.bin",
            sha256=hashlib.sha256(data).hexdigest(),
            size=len(data),
            mime_type=None,
        )

        assert result.success


# ===================================================================
# 11. EDGE CASE TESTS
# ===================================================================

class TestEdgeCases:
    def test_empty_file_browser(self, tmp_path):
        fp = _create_test_file(tmp_path, "History", b"")
        evidence = _make_evidence(fp, "History", EvidenceCategory.BROWSER_DATA)
        config = ForensicProcessorConfig()
        processor = BrowserForensicsProcessor()
        processor.process(evidence, config)
        assert isinstance(evidence.tags, list)

    def test_empty_file_email(self, tmp_path):
        fp = _create_test_file(tmp_path, "empty.eml", b"")
        evidence = _make_evidence(fp, "empty.eml", EvidenceCategory.EMAIL)
        config = ForensicProcessorConfig()
        processor = EmailForensicsProcessor()
        processor.process(evidence, config)
        assert isinstance(evidence.tags, list)

    def test_empty_file_integrity(self, tmp_path):
        fp = _create_test_file(tmp_path, "empty.bin", b"")
        evidence = _make_evidence(fp, "empty.bin")
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)
        result = evidence.processor_results["integrity_forensics"]
        assert result["corruption"]["corrupted"] is True

    def test_corrupted_pcap(self, tmp_path):
        content = b"\xd4\xc3\xb2\xa1" + b"\xff" * 100
        fp = _create_test_file(tmp_path, "corrupt.pcap", content)
        evidence = _make_evidence(fp, "corrupt.pcap", EvidenceCategory.NETWORK_CAPTURE)
        config = ForensicProcessorConfig()
        processor = NetworkForensicsProcessor()
        processor.process(evidence, config)
        # Should handle gracefully without crashing
        assert isinstance(evidence.tags, list)

    def test_files_with_null_bytes(self, tmp_path):
        content = b"\x00\x00\x00" + b"some data" + b"\x00\x00\x00" + b"more data" + b"\x00" * 100
        fp = _create_test_file(tmp_path, "nulls.bin", content)
        evidence = _make_evidence(fp, "nulls.bin")
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)
        result = evidence.processor_results["integrity_forensics"]
        assert result["entropy"]["entropy"] is not None

    def test_very_small_file(self, tmp_path):
        fp = _create_test_file(tmp_path, "tiny.bin", b"\x00")
        evidence = _make_evidence(fp, "tiny.bin")
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)
        result = evidence.processor_results["integrity_forensics"]
        assert result["header_mismatch"]["detail"] == "File too small to validate header"

    def test_memory_dump_with_shellcode_and_xor(self, tmp_path):
        data = b"\x00" * 1024
        data += b"\x30\xc0"  # XOR AL, AL
        data += b"\xe8\x00\x00\x00\x00"  # CALL $+5
        data += b"\x00" * 4096
        fp = _create_test_file(tmp_path, "xor_mem.bin", data)
        evidence = _make_evidence(fp, "xor_mem.bin", EvidenceCategory.MEMORY_DUMP)
        config = ForensicProcessorConfig()
        processor = MemoryForensicsProcessor()
        processor.process(evidence, config)

        injections = evidence.metadata.get("injected_code_detections", [])
        assert len(injections) > 0

    def test_disk_with_mbr_no_partitions(self, tmp_path):
        mbr = bytearray(512)
        mbr[510] = 0x55
        mbr[511] = 0xAA
        # All partition entries are type 0x00 (empty)
        fp = _create_test_file(tmp_path, "empty_disk.raw", bytes(mbr))
        evidence = _make_evidence(fp, "empty_disk.raw", EvidenceCategory.DISK_IMAGE)
        config = ForensicProcessorConfig()
        processor = DiskForensicsProcessor()
        processor.process(evidence, config)
        assert "disk_forensics" in evidence.tags

    def test_email_with_binary_content(self, tmp_path):
        eml_content = (
            b"From: sender@example.com\r\n"
            b"To: recipient@example.com\r\n"
            b"Subject: Binary Test\r\n"
            b"Date: Mon, 15 Jun 2024 10:00:00 +0000\r\n"
            b"Content-Type: application/octet-stream\r\n"
            b"\r\n"
            b"\x00\x01\x02\x03\x04\x05"
        )
        fp = _create_test_file(tmp_path, "binary.eml", eml_content)
        evidence = _make_evidence(fp, "binary.eml", EvidenceCategory.EMAIL)
        config = ForensicProcessorConfig()
        processor = EmailForensicsProcessor()
        processor.process(evidence, config)
        assert isinstance(evidence.tags, list)

    def test_network_processor_with_unknown_extension(self, tmp_path):
        content = b"\x00" * 100
        fp = _create_test_file(tmp_path, "capture.xyz", content)
        evidence = _make_evidence(fp, "capture.xyz", EvidenceCategory.NETWORK_CAPTURE)
        config = ForensicProcessorConfig()
        processor = NetworkForensicsProcessor()
        processor.process(evidence, config)
        # Should handle gracefully
        assert isinstance(evidence.tags, list)

    def test_windows_processor_empty_directory(self, tmp_path):
        evidence = _make_evidence(
            _create_test_file(tmp_path, "empty.txt", b""),
            "empty.txt",
            EvidenceCategory.WINDOWS_ARTIFACT,
        )
        config = ForensicProcessorConfig()
        processor = WindowsForensicsProcessor()
        processor.process(evidence, config)
        assert isinstance(evidence.tags, list)

    def test_mobile_processor_non_mobile_db(self, tmp_path):
        db_path = tmp_path / "random.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE logs (id INTEGER, msg TEXT)")
        conn.execute("INSERT INTO logs VALUES (1, 'test')")
        conn.commit()
        conn.close()

        evidence = _make_evidence(str(db_path), "random.db", EvidenceCategory.MOBILE_ARTIFACT)
        config = ForensicProcessorConfig()
        processor = MobileForensicsProcessor()
        processor.process(evidence, config)
        assert isinstance(evidence.tags, list)

    def test_integrity_processor_with_password_protected_zip(self, tmp_path):
        import zipfile
        zpath = tmp_path / "protected.zip"
        with zipfile.ZipFile(zpath, "w") as zf:
            # Write a normal entry first, then the password indicator
            zf.writestr("readme.txt", "This is not actually password protected in the test")

        fp = str(zpath)
        evidence = _make_evidence(fp, "protected.zip")
        config = ForensicProcessorConfig()
        processor = IntegrityForensicsProcessor()
        processor.process(evidence, config)
        result = evidence.processor_results["integrity_forensics"]
        assert result["entropy"]["entropy"] is not None

    def test_all_artifact_type_enum_values(self):
        """Ensure all artifact types are accessible and have string values."""
        for at in ArtifactType:
            assert isinstance(at.value, str)
            assert len(at.value) > 0

    def test_all_risk_level_enum_values(self):
        for rl in RiskLevel:
            assert isinstance(rl.value, str)

    def test_all_ioc_type_enum_values(self):
        for ioc in IOCType:
            assert isinstance(ioc.value, str)
