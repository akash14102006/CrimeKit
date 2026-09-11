import io
import os
import hashlib
import zipfile
import tempfile
import pytest
from backend.app.forensic_engine.schemas import EvidenceSchema, EvidenceCategory, ForensicProcessorConfig
from backend.app.forensic_engine.base import BaseProcessor
from backend.app.forensic_engine.pipeline import ProcessingPipeline
from backend.app.forensic_engine.utils.hashing import compute_hashes, verify_integrity
from backend.app.forensic_engine.utils.metadata import classify_evidence, classify_forensic_image, extract_file_metadata
from backend.app.forensic_engine.processors import ALL_PROCESSORS


def _create_test_file(tmp_path, name, content=b"test content for forensic processing"):
    p = tmp_path / name
    p.write_bytes(content)
    return str(p)


def _make_evidence(file_path, filename=None):
    sha = compute_hashes(file_path)
    filename = filename or os.path.basename(file_path)
    return EvidenceSchema(
        evidence_id="test-ev-001",
        case_id="case-001",
        storage_path=file_path,
        filename=filename,
        sha256=sha["sha256"],
        size=os.path.getsize(file_path),
        mime_type=None,
    )


class TestEvidenceSchema:
    def test_add_result(self):
        schema = EvidenceSchema(
            evidence_id="ev1", case_id=None, storage_path="/tmp/f",
            filename="f.txt", sha256="abc", size=10, mime_type="text/plain",
        )
        schema.add_result("hash", {"sha256": "abc"})
        assert "hash" in schema.processor_results
        assert schema.processor_results["hash"]["sha256"] == "abc"

    def test_add_error(self):
        schema = EvidenceSchema(
            evidence_id="ev1", case_id=None, storage_path="/tmp/f",
            filename="f.txt", sha256="abc", size=10, mime_type=None,
        )
        schema.add_error("proc1", "something failed")
        assert "proc1: something failed" in schema.processing_errors

    def test_add_timeline_event(self):
        schema = EvidenceSchema(
            evidence_id="ev1", case_id=None, storage_path="/tmp/f",
            filename="f.txt", sha256="abc", size=10, mime_type=None,
        )
        schema.add_timeline_event("2024-01-01", "New Year", "test")
        assert len(schema.timeline_events) == 1
        assert schema.timeline_events[0]["date"] == "2024-01-01"

    def test_add_entity_and_relationship(self):
        schema = EvidenceSchema(
            evidence_id="ev1", case_id=None, storage_path="/tmp/f",
            filename="f.txt", sha256="abc", size=10, mime_type=None,
        )
        schema.add_entity("John", "person", {"age": 30})
        schema.add_relationship("John", "Doe", "related_to")
        assert len(schema.entities) == 1
        assert len(schema.relationships) == 1

    def test_add_tag_dedup(self):
        schema = EvidenceSchema(
            evidence_id="ev1", case_id=None, storage_path="/tmp/f",
            filename="f.txt", sha256="abc", size=10, mime_type=None,
        )
        schema.add_tag("pdf")
        schema.add_tag("pdf")
        assert schema.tags.count("pdf") == 1

    def test_to_dict(self):
        schema = EvidenceSchema(
            evidence_id="ev1", case_id="c1", storage_path="/tmp/f",
            filename="f.txt", sha256="abc", size=10, mime_type="text/plain",
        )
        d = schema.to_dict()
        assert d["evidence_id"] == "ev1"
        assert d["category"] == "unknown"
        assert isinstance(d["tags"], list)


class TestBaseProcessor:
    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            BaseProcessor()


class TestHashing:
    def test_compute_hashes(self, tmp_path):
        fp = _create_test_file(tmp_path, "hash_test.txt", b"hello world")
        hashes = compute_hashes(fp)
        assert "sha256" in hashes
        assert "sha1" in hashes
        assert "md5" in hashes
        expected_sha256 = hashlib.sha256(b"hello world").hexdigest()
        assert hashes["sha256"] == expected_sha256

    def test_verify_integrity(self, tmp_path):
        fp = _create_test_file(tmp_path, "integrity.txt", b"test data")
        hashes = compute_hashes(fp)
        assert verify_integrity(fp, hashes["sha256"])
        assert not verify_integrity(fp, "0000000000000000000000000000000000000000000000000000000000000000")


class TestMetadata:
    def test_classify_evidence(self):
        assert classify_evidence("photo.jpg") == EvidenceCategory.IMAGE
        assert classify_evidence("video.mp4") == EvidenceCategory.VIDEO
        assert classify_evidence("doc.pdf") == EvidenceCategory.PDF
        assert classify_evidence("report.docx") == EvidenceCategory.OFFICE
        assert classify_evidence("mail.eml") == EvidenceCategory.EMAIL
        assert classify_evidence("backup.zip") == EvidenceCategory.ARCHIVE
        assert classify_evidence("data.iso") == EvidenceCategory.DISK_IMAGE

    def test_extract_file_metadata(self, tmp_path):
        fp = _create_test_file(tmp_path, "meta_test.txt")
        meta = extract_file_metadata(fp)
        assert meta["size"] == len(b"test content for forensic processing")
        assert meta["extension"] == "txt"
        assert meta["mime_type"] is not None

    def test_e01_classification_ignores_octet_stream_mime(self, tmp_path):
        image = tmp_path / "carry-tablet-2012-07-16-final.E01"
        image.write_bytes(b"EVF\x00" + b"\x00" * 128)

        result = classify_forensic_image(str(image), image.name, "application/octet-stream")

        assert result["is_forensic_image"] is True
        assert result["evidence_type"] == "forensic_disk_image"
        assert result["image_format"] == "E01/EWF"
        assert result["processor"] == "TSK"
        assert result["mime_type_signal"] == "application/octet-stream"

    def test_non_e01_binary_is_not_forensic_image(self, tmp_path):
        binary = tmp_path / "payload.bin"
        binary.write_bytes(b"EVF\x00" + b"\x00" * 16)

        result = classify_forensic_image(str(binary), binary.name, "application/octet-stream")

        assert result == {"is_forensic_image": False}


class TestPipeline:
    def test_pipeline_lists_processors(self):
        pipeline = ProcessingPipeline()
        available = pipeline.get_available_processors()
        assert "image" in available
        assert "pdf" in available
        assert "email" in available
        assert "archive" in available

    def test_pipeline_processes_text_file(self, tmp_path):
        fp = _create_test_file(tmp_path, "simple.txt")
        pipeline = ProcessingPipeline()
        result = pipeline.process_from_path(
            evidence_id="ev1", file_path=fp, filename="simple.txt",
            sha256=compute_hashes(fp)["sha256"], size=os.path.getsize(fp),
            mime_type="text/plain",
        )
        assert result.success
        assert result.schema is not None
        assert "integrity_verified" in result.schema.tags

    def test_pipeline_with_config_filter(self, tmp_path):
        fp = _create_test_file(tmp_path, "filtered.txt")
        config = ForensicProcessorConfig(enabled_processors=["image"])
        pipeline = ProcessingPipeline(config)
        result = pipeline.process_from_path(
            evidence_id="ev2", file_path=fp, filename="filtered.txt",
            sha256=compute_hashes(fp)["sha256"], size=os.path.getsize(fp),
        )
        assert result.success

    def test_pipeline_integrity_failure(self, tmp_path):
        fp = _create_test_file(tmp_path, "tampered.bin")
        evidence = EvidenceSchema(
            evidence_id="ev3", case_id=None, storage_path=fp,
            filename="tampered.bin", sha256="0" * 64, size=os.path.getsize(fp),
            mime_type=None,
        )
        pipeline = ProcessingPipeline()
        result = pipeline.process(evidence)
        assert result.success
        assert "integrity_warning" in evidence.tags

    def test_custom_processor(self, tmp_path):
        class DummyProcessor(BaseProcessor):
            name = "dummy"
            description = "Test processor"
            supported_categories = frozenset({EvidenceCategory.UNKNOWN})
            def process(self, evidence, config):
                evidence.add_tag("dummy_processed")
                return evidence
        fp = _create_test_file(tmp_path, "dummy.txt")
        pipeline = ProcessingPipeline()
        pipeline.register_processor(DummyProcessor())
        assert "dummy" in pipeline.get_available_processors()
        evidence = EvidenceSchema(
            evidence_id="ev4", case_id=None, storage_path=fp,
            filename="dummy.txt", sha256=compute_hashes(fp)["sha256"],
            size=os.path.getsize(fp), mime_type=None,
        )
        result = pipeline.process(evidence)
        assert "dummy_processed" in evidence.tags


class TestArchiveProcessor:
    def test_zip_processing(self, tmp_path):
        zpath = tmp_path / "test.zip"
        with zipfile.ZipFile(zpath, "w") as z:
            z.writestr("file1.txt", "hello world")
            z.writestr("subdir/file2.txt", "another file")
        evidence = _make_evidence(str(zpath), "test.zip")
        evidence.category = EvidenceCategory.ARCHIVE
        config = ForensicProcessorConfig()
        proc = ALL_PROCESSORS["archive"]()
        proc.process(evidence, config)
        assert evidence.metadata.get("archive_file_count") == 2
        assert "file1.txt" in (evidence.metadata.get("archive_files") or [])


class TestEmailProcessor:
    def test_email_processing(self, tmp_path):
        eml = tmp_path / "test.eml"
        eml.write_bytes(
            b"From: alice@example.com\r\n"
            b"To: bob@example.com\r\n"
            b"Subject: Test Email\r\n"
            b"Date: 2024-06-15T10:00:00\r\n"
            b"\r\n"
            b"Hello Bob, this is a test email."
        )
        evidence = _make_evidence(str(eml), "test.eml")
        evidence.category = EvidenceCategory.EMAIL
        config = ForensicProcessorConfig()
        proc = ALL_PROCESSORS["email"]()
        proc.process(evidence, config)
        assert evidence.metadata.get("email_subject") == "Test Email"
        assert evidence.metadata.get("email_from") == "alice@example.com"
        assert "Hello Bob" in (evidence.extracted_text or "")
        assert len(evidence.timeline_events) >= 1


class TestPDFProcessor:
    def test_pdf_processing(self, tmp_path):
        pytest.importorskip("pypdf")
        from pypdf import PdfWriter
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        pdf_path = tmp_path / "test.pdf"
        with open(pdf_path, "wb") as f:
            writer.write(f)
        evidence = _make_evidence(str(pdf_path), "test.pdf")
        evidence.category = EvidenceCategory.PDF
        config = ForensicProcessorConfig()
        proc = ALL_PROCESSORS["pdf"]()
        proc.process(evidence, config)
        assert evidence.metadata.get("page_count") == 1


class TestImageProcessor:
    def test_image_processing(self, tmp_path):
        pytest.importorskip("PIL")
        from PIL import Image
        img_path = tmp_path / "test.png"
        img = Image.new("RGB", (200, 100), color="blue")
        img.save(str(img_path))
        evidence = _make_evidence(str(img_path), "test.png")
        evidence.category = EvidenceCategory.IMAGE
        config = ForensicProcessorConfig(run_ocr=False)
        proc = ALL_PROCESSORS["image"]()
        proc.process(evidence, config)
        assert evidence.metadata.get("format") == "PNG"
        assert evidence.metadata.get("dimensions") == [200, 100]
        assert "image" in evidence.tags


class TestMobileProcessor:
    def test_sqlite_inspection(self, tmp_path):
        import sqlite3
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO users VALUES (1, 'Alice')")
        conn.execute("CREATE TABLE logs (ts TEXT, msg TEXT)")
        conn.commit()
        conn.close()
        evidence = _make_evidence(str(db_path), "test.db")
        evidence.category = EvidenceCategory.MOBILE_ARTIFACT
        config = ForensicProcessorConfig()
        proc = ALL_PROCESSORS["mobile_artifact"]()
        proc.process(evidence, config)
        assert "sqlite_tables" in evidence.metadata
        tables = evidence.metadata["sqlite_tables"]
        assert "users" in tables
        assert "logs" in tables


class TestDiskImageProcessor:
    def test_disk_image_tags(self, tmp_path):
        img_path = tmp_path / "disk.raw"
        img_path.write_bytes(b"\x00" * 1024)
        evidence = _make_evidence(str(img_path), "disk.raw")
        evidence.category = EvidenceCategory.DISK_IMAGE
        config = ForensicProcessorConfig()
        proc = ALL_PROCESSORS["disk_image"]()
        proc.process(evidence, config)
        assert "disk_image" in evidence.tags
