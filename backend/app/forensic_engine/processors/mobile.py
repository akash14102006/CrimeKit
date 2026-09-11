import logging
import os
import plistlib
import sqlite3
from typing import Set

from ..base import BaseProcessor
from ..schemas import EvidenceSchema, EvidenceCategory, ForensicProcessorConfig, ProcessorPriority

logger = logging.getLogger(__name__)


class MobileArtifactProcessor(BaseProcessor):
    name = "mobile_artifact"
    description = "Processes mobile artifacts: plist parsing, SQLite DB extraction, backup analysis"
    supported_categories = frozenset({EvidenceCategory.MOBILE_ARTIFACT})
    priority = ProcessorPriority.ANALYSIS

    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        ext = self._get_file_extension(evidence)
        if ext == "plist":
            self._parse_plist(evidence)
        elif ext in ("db", "sqlite"):
            self._inspect_sqlite(evidence)
        elif ext in ("ab",):
            self._process_android_backup(evidence)
        evidence.add_tag("mobile_artifact")
        return evidence

    def _parse_plist(self, evidence: EvidenceSchema) -> None:
        try:
            with open(evidence.storage_path, "rb") as f:
                data = plistlib.load(f)
            evidence.metadata["plist_data"] = _sanitize_plist(data)
            if isinstance(data, dict):
                for k, v in data.items():
                    if "date" in str(k).lower():
                        evidence.add_timeline_event(str(v), f"Plist {k}: {v}", self.name)
        except Exception as e:
            evidence.add_error(self.name, f"Plist parsing failed: {e}")

    def _inspect_sqlite(self, evidence: EvidenceSchema) -> None:
        try:
            conn = sqlite3.connect(evidence.storage_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            evidence.metadata["sqlite_tables"] = tables
            table_info = {}
            for table in tables[:10]:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM [{table}]")
                    count = cursor.fetchone()[0]
                    cursor.execute(f"SELECT * FROM [{table}] LIMIT 3")
                    columns = [desc[0] for desc in cursor.description]
                    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    table_info[table] = {"row_count": count, "columns": columns, "sample": rows}
                except Exception:
                    pass
            evidence.metadata["sqlite_details"] = table_info
            conn.close()
        except Exception as e:
            evidence.add_error(self.name, f"SQLite inspection failed: {e}")

    def _process_android_backup(self, evidence: EvidenceSchema) -> None:
        evidence.metadata["format"] = "android_backup"
        evidence.add_tag("android_backup")


def _sanitize_plist(data):
    """Convert plist data to JSON-serializable format."""
    if isinstance(data, bytes):
        return f"<{len(data)} bytes>"
    if isinstance(data, dict):
        return {k: _sanitize_plist(v) for k, v in data.items()}
    if isinstance(data, (list, tuple)):
        return [_sanitize_plist(item) for item in data]
    return data
