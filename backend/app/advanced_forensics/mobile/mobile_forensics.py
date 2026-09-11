import logging
import os
import plistlib
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from ...forensic_engine.base import BaseProcessor
from ...forensic_engine.schemas import EvidenceSchema, EvidenceCategory, ForensicProcessorConfig, ProcessorPriority

logger = logging.getLogger(__name__)


class MobileForensicsProcessor(BaseProcessor):
    """Enterprise-grade mobile forensic artifact extraction processor.

    Extracts Android and iOS artifacts including SMS, calls, contacts,
    messaging apps, photos, GPS, installed apps, and system data.
    """

    name = "mobile_forensics"
    description = "Extracts Android and iOS artifacts: SMS, calls, contacts, messaging apps, photos, GPS, installed apps"
    supported_categories = frozenset({EvidenceCategory.MOBILE_ARTIFACT, EvidenceCategory.UNKNOWN})
    priority = ProcessorPriority.ARTIFACT_EXTRACTION

    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        """Process mobile evidence and extract all available artifacts."""
        self._pending_entities = []

        platform = self._detect_platform(evidence)

        if platform == "android":
            self._process_android(evidence)
        elif platform == "ios":
            self._process_ios(evidence)
        else:
            evidence.add_error(self.name, "Unable to detect mobile platform")

        evidence.add_tag(f"mobile_{platform}" if platform else "mobile_unknown")
        self._add_communication_entities_batch(evidence)
        return evidence

    def _detect_platform(self, evidence: EvidenceSchema) -> Optional[str]:
        """Auto-detect mobile platform from file signatures and directory structures."""
        storage_path = evidence.storage_path
        filename = evidence.filename.lower()

        android_db_names = {"mmssms.db", "calls.db", "contacts2.db", "packages.xml", "packages.list"}
        ios_db_names = {"sms.db", "callhistory.storedata", "addressbook.sqlitedb",
                        "photos.sqlite", "history.db", "knowledgec.db"}

        if os.path.isdir(storage_path):
            for root, dirs, files in os.walk(storage_path):
                for d in dirs:
                    if d.startswith("com.") or d.startswith("org."):
                        return "android"
                for f in files:
                    if f in android_db_names or (f.endswith(".db") and any(x in f.lower() for x in ("sms", "call", "contact"))):
                        return "android"
                for f in files:
                    if f in ios_db_names or f.endswith(".plist"):
                        return "ios"
        elif os.path.isfile(storage_path):
            if filename in android_db_names or (filename.endswith(".db") and any(x in filename for x in ("sms", "call", "contact"))):
                return "android"
            if filename in ios_db_names or filename.endswith((".plist", ".ab", ".tar")):
                return "ios"

        return None

    def _process_android(self, evidence: EvidenceSchema) -> None:
        """Process Android artifacts."""
        db_files = self._find_android_databases(evidence.storage_path)

        extraction_methods = [
            ("sms", self._extract_android_sms),
            ("calls", self._extract_android_calls),
            ("contacts", self._extract_android_contacts),
            ("whatsapp", self._extract_android_whatsapp),
            ("telegram", self._extract_android_telegram),
            ("signal", self._extract_android_signal),
            ("chrome", self._extract_android_chrome),
            ("installs", self._extract_android_installs),
            ("notifications", self._extract_android_notifications),
            ("gps", self._extract_android_gps),
        ]

        results = {}
        for artifact_type, method in extraction_methods:
            try:
                data = method(evidence.storage_path, db_files)
                if data:
                    results[artifact_type] = data
                    evidence.add_tag(f"android_{artifact_type}")
            except Exception as e:
                logger.warning(f"Android {artifact_type} extraction failed: {e}")

        evidence.add_result(self.name, {"platform": "android", "artifacts": results})

    def _process_ios(self, evidence: EvidenceSchema) -> None:
        """Process iOS artifacts."""
        db_files = self._find_ios_databases(evidence.storage_path)
        plist_files = self._find_ios_plists(evidence.storage_path)

        extraction_methods = [
            ("sms", self._extract_ios_sms),
            ("calls", self._extract_ios_calls),
            ("contacts", self._extract_ios_contacts),
            ("photos", self._extract_ios_photos),
            ("safari", self._extract_ios_safari),
            ("knowledgec", self._extract_ios_knowledgec),
            ("keychain", self._extract_ios_keychain),
        ]

        results = {}
        for artifact_type, method in extraction_methods:
            try:
                data = method(evidence.storage_path, db_files)
                if data:
                    results[artifact_type] = data
                    evidence.add_tag(f"ios_{artifact_type}")
            except Exception as e:
                logger.warning(f"iOS {artifact_type} extraction failed: {e}")

        if plist_files:
            plist_data = self._extract_ios_plists(evidence.storage_path, plist_files)
            if plist_data:
                results["plists"] = plist_data
                evidence.add_tag("ios_plists")

        evidence.add_result(self.name, {"platform": "ios", "artifacts": results})

    def _find_android_databases(self, storage_path: str) -> Dict[str, str]:
        """Find Android database files."""
        db_files = {}
        if os.path.isfile(storage_path):
            filename = os.path.basename(storage_path).lower()
            db_files[filename] = storage_path
        elif os.path.isdir(storage_path):
            for root, dirs, files in os.walk(storage_path):
                for f in files:
                    if f.endswith((".db", ".sqlite")):
                        full_path = os.path.join(root, f)
                        db_files[f.lower()] = full_path
        return db_files

    def _find_ios_databases(self, storage_path: str) -> Dict[str, str]:
        """Find iOS database files."""
        db_files = {}
        if os.path.isdir(storage_path):
            for root, dirs, files in os.walk(storage_path):
                for f in files:
                    if f.endswith((".db", ".sqlite", ".storedata")):
                        full_path = os.path.join(root, f)
                        db_files[f.lower()] = full_path
        return db_files

    def _find_ios_plists(self, storage_path: str) -> List[str]:
        """Find iOS plist files."""
        plist_files = []
        if os.path.isdir(storage_path):
            for root, dirs, files in os.walk(storage_path):
                for f in files:
                    if f.endswith(".plist"):
                        plist_files.append(os.path.join(root, f))
        return plist_files

    def _query_sqlite(self, db_path: str, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute SQLite query and return results as list of dicts."""
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return rows
        except Exception as e:
            logger.warning(f"SQLite query failed on {db_path}: {e}")
            return []

    def _convert_android_timestamp(self, ts: int) -> Optional[str]:
        """Convert Android millisecond timestamp to ISO format."""
        if not ts or ts <= 0:
            return None
        try:
            return datetime.fromtimestamp(ts / 1000).isoformat()
        except (ValueError, OSError):
            return None

    def _convert_ios_timestamp(self, ts: float) -> Optional[str]:
        """Convert iOS Core Data timestamp to ISO format."""
        if not ts or ts <= 0:
            return None
        try:
            return datetime.fromtimestamp(ts + 978307200).isoformat()
        except (ValueError, OSError):
            return None

    def _safe_get(self, row: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Safely get value from dictionary."""
        return row.get(key, default)

    # ==================== ANDROID EXTRACTION METHODS ====================

    def _extract_android_sms(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse Android mmssms.db: address, body, date, type, read status."""
        sms_db = db_files.get("mmssms.db")
        if not sms_db:
            for key in db_files:
                if "sms" in key:
                    sms_db = db_files[key]
                    break
        if not sms_db:
            return []

        query = """
            SELECT address, body, date, type, read, seen, subject, person,
                   date_sent, error_code, service_center
            FROM sms
            ORDER BY date DESC
        """
        rows = self._query_sqlite(sms_db, query)
        results = []
        for row in rows:
            timestamp = self._convert_android_timestamp(self._safe_get(row, "date", 0))
            msg_type = self._safe_get(row, "type", 0)
            type_map = {1: "received", 2: "sent", 3: "draft", 4: "outbox"}
            direction = type_map.get(msg_type, "unknown")

            result = {
                "address": self._safe_get(row, "address"),
                "body": self._safe_get(row, "body"),
                "date": timestamp,
                "type": direction,
                "read": bool(self._safe_get(row, "read", 0)),
                "seen": bool(self._safe_get(row, "seen", 0)),
                "subject": self._safe_get(row, "subject"),
                "service_center": self._safe_get(row, "service_center"),
                "source_db": "mmssms.db",
            }
            results.append(result)

            address = self._safe_get(row, "address", "")
            if address:
                self._add_communication_entities(address, "sms", direction, timestamp)

        return results

    def _extract_android_calls(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse Android calls.db or contacts.db: number, type, date, duration."""
        calls_db = db_files.get("calls.db") or db_files.get("contacts.db")
        if not calls_db:
            for key in db_files:
                if "call" in key:
                    calls_db = db_files[key]
                    break
        if not calls_db:
            return []

        query = """
            SELECT number, type, date, duration, new, geocoded_location, photo_id
            FROM calls
            ORDER BY date DESC
        """
        rows = self._query_sqlite(calls_db, query)
        results = []
        for row in rows:
            timestamp = self._convert_android_timestamp(self._safe_get(row, "date", 0))
            call_type = self._safe_get(row, "type", 0)
            type_map = {1: "incoming", 2: "outgoing", 3: "missed", 4: "voicemail", 5: "rejected"}
            direction = type_map.get(call_type, "unknown")

            result = {
                "number": self._safe_get(row, "number"),
                "type": direction,
                "date": timestamp,
                "duration_seconds": self._safe_get(row, "duration", 0),
                "new": bool(self._safe_get(row, "new", 0)),
                "location": self._safe_get(row, "geocoded_location"),
                "source_db": "calls.db",
            }
            results.append(result)

            number = self._safe_get(row, "number", "")
            if number:
                self._add_communication_entities(number, "call", direction, timestamp)

        return results

    def _extract_android_contacts(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse Android contacts2.db: display_name, phone, email, organization."""
        contacts_db = db_files.get("contacts2.db")
        if not contacts_db:
            for key in db_files:
                if "contact" in key:
                    contacts_db = db_files[key]
                    break
        if not contacts_db:
            return []

        query = """
            SELECT c.display_name, p.data1 as phone, e.data1 as email,
                   o.data1 as organization, c.starred, c.times_contacted
            FROM contacts c
            LEFT JOIN data p ON c._id = p.contact_id AND p.mimetype_id = (
                SELECT _id FROM mimetypes WHERE mimetype = 'vnd.android.cursor.item/phone_v2'
            )
            LEFT JOIN data e ON c._id = e.contact_id AND e.mimetype_id = (
                SELECT _id FROM mimetypes WHERE mimetype = 'vnd.android.cursor.item/email_v2'
            )
            LEFT JOIN data o ON c._id = o.contact_id AND o.mimetype_id = (
                SELECT _id FROM mimetypes WHERE mimetype = 'vnd.android.cursor.item/organization'
            )
            WHERE c.display_name IS NOT NULL
        """
        rows = self._query_sqlite(contacts_db, query)
        results = []
        for row in rows:
            name = self._safe_get(row, "display_name")
            if not name:
                continue

            result = {
                "display_name": name,
                "phone": self._safe_get(row, "phone"),
                "email": self._safe_get(row, "email"),
                "organization": self._safe_get(row, "organization"),
                "starred": bool(self._safe_get(row, "starred", 0)),
                "times_contacted": self._safe_get(row, "times_contacted", 0),
                "source_db": "contacts2.db",
            }
            results.append(result)

            phone = self._safe_get(row, "phone")
            if phone:
                self._add_communication_entities(name, "contact", "phone", phone)

        return results

    def _extract_android_whatsapp(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse WhatsApp msgstore.db and wa.db: messages, contacts, groups, media references."""
        msgstore = db_files.get("msgstore.db") or db_files.get("messages.db")
        wa_db = db_files.get("wa.db") or db_files.get("contacts.db")

        results = []
        if msgstore:
            query = """
                SELECT key_remote_jid, data, timestamp, status, media_url,
                       media_mime_type, media_size, from_me, quote_text
                FROM messages
                ORDER BY timestamp DESC
                LIMIT 10000
            """
            rows = self._query_sqlite(msgstore, query)
            for row in rows:
                timestamp = self._convert_android_timestamp(self._safe_get(row, "timestamp", 0))
                result = {
                    "jid": self._safe_get(row, "key_remote_jid"),
                    "message": self._safe_get(row, "data"),
                    "date": timestamp,
                    "from_me": bool(self._safe_get(row, "from_me", 0)),
                    "status": self._safe_get(row, "status"),
                    "media_url": self._safe_get(row, "media_url"),
                    "media_mime_type": self._safe_get(row, "media_mime_type"),
                    "source_db": "msgstore.db",
                }
                results.append(result)

                jid = self._safe_get(row, "key_remote_jid", "")
                if jid and "@" in jid:
                    direction = "sent" if self._safe_get(row, "from_me", 0) else "received"
                    self._add_communication_entities(jid.split("@")[0], "whatsapp", direction, timestamp)

        if results:
            self._add_communication_entities("WhatsApp", "app", "installed", None)

        return results

    def _extract_android_telegram(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse Telegram databases: messages, chats, users."""
        results = []
        for key, db_path in db_files.items():
            if "telegram" in key:
                query = """
                    SELECT message_id, uid, date, text, media_type
                    FROM messages
                    ORDER BY date DESC
                    LIMIT 5000
                """
                rows = self._query_sqlite(db_path, query)
                for row in rows:
                    ts = self._safe_get(row, "date", 0)
                    timestamp = self._convert_ios_timestamp(ts) if isinstance(ts, float) else self._convert_android_timestamp(int(ts))
                    result = {
                        "message_id": self._safe_get(row, "message_id"),
                        "user_id": self._safe_get(row, "uid"),
                        "date": timestamp,
                        "text": self._safe_get(row, "text"),
                        "source_db": key,
                    }
                    results.append(result)
                break

        if results:
            self._add_communication_entities("Telegram", "app", "installed", None)

        return results

    def _extract_android_signal(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse Signal databases: messages, contacts."""
        results = []
        for key, db_path in db_files.items():
            if "signal" in key:
                query = """
                    SELECT _id, address, body, date_sent, date_received, type
                    FROM message
                    ORDER BY date_received DESC
                    LIMIT 5000
                """
                rows = self._query_sqlite(db_path, query)
                for row in rows:
                    timestamp = self._convert_android_timestamp(self._safe_get(row, "date_received", 0))
                    msg_type = self._safe_get(row, "type", 0)
                    direction = "sent" if msg_type == 2 else "received"

                    result = {
                        "message_id": self._safe_get(row, "_id"),
                        "address": self._safe_get(row, "address"),
                        "body": self._safe_get(row, "body"),
                        "date": timestamp,
                        "type": direction,
                        "source_db": key,
                    }
                    results.append(result)

                    address = self._safe_get(row, "address", "")
                    if address:
                        self._add_communication_entities(address, "signal", direction, timestamp)
                break

        if results:
            self._add_communication_entities("Signal", "app", "installed", None)

        return results

    def _extract_android_chrome(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse Chrome browser data (delegates to browser forensics patterns)."""
        results = []
        for key, db_path in db_files.items():
            if "chrome" in key and "history" in key:
                query = """
                    SELECT url, title, visit_count, last_visit_time
                    FROM urls
                    ORDER BY last_visit_time DESC
                    LIMIT 5000
                """
                rows = self._query_sqlite(db_path, query)
                for row in rows:
                    timestamp = self._convert_android_timestamp(self._safe_get(row, "last_visit_time", 0))
                    result = {
                        "url": self._safe_get(row, "url"),
                        "title": self._safe_get(row, "title"),
                        "visit_count": self._safe_get(row, "visit_count", 0),
                        "last_visit": timestamp,
                        "source_db": key,
                    }
                    results.append(result)

                    url = self._safe_get(row, "url", "")
                    if url:
                        self._add_communication_entities(url, "url", "visited", timestamp)
                break

        if results:
            self._add_communication_entities("Chrome", "app", "installed", None)

        return results

    def _extract_android_installs(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse packages.xml or packages.list: installed apps with install/update dates."""
        results = []
        packages_xml = None
        packages_list = None

        for root, dirs, files in os.walk(storage_path):
            for f in files:
                if f == "packages.xml":
                    packages_xml = os.path.join(root, f)
                elif f == "packages.list":
                    packages_list = os.path.join(root, f)

        if packages_xml:
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(packages_xml)
                root_elem = tree.getroot()

                for pkg in root_elem.findall("package"):
                    name = pkg.get("name", "")
                    code_path = pkg.get("codePath", "")
                    install_time = pkg.get("installer", "")
                    last_update = pkg.get("lastUpdate", "")

                    result = {
                        "package_name": name,
                        "code_path": code_path,
                        "installer": install_time,
                        "last_update": last_update,
                        "source": "packages.xml",
                    }
                    results.append(result)

                    if name:
                        self._add_communication_entities(name, "app", "installed", None)
            except Exception as e:
                logger.warning(f"Failed to parse packages.xml: {e}")

        elif packages_list:
            try:
                with open(packages_list, "r") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            name = parts[0]
                            result = {
                                "package_name": name,
                                "source": "packages.list",
                            }
                            results.append(result)
                            self._add_communication_entities(name, "app", "installed", None)
            except Exception as e:
                logger.warning(f"Failed to parse packages.list: {e}")

        return results

    def _extract_android_notifications(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse notification log databases."""
        results = []
        for key, db_path in db_files.items():
            if "notification" in key:
                query = """
                    SELECT package, title, text, timestamp
                    FROM notifications
                    ORDER BY timestamp DESC
                    LIMIT 5000
                """
                rows = self._query_sqlite(db_path, query)
                for row in rows:
                    timestamp = self._convert_android_timestamp(self._safe_get(row, "timestamp", 0))
                    result = {
                        "package": self._safe_get(row, "package"),
                        "title": self._safe_get(row, "title"),
                        "text": self._safe_get(row, "text"),
                        "date": timestamp,
                        "source_db": key,
                    }
                    results.append(result)
                break

        return results

    def _extract_android_gps(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse GPS/wifi location databases, cell tower data."""
        results = []
        for key, db_path in db_files.items():
            if "location" in key or "gps" in key or "wifi" in key or "cell" in key:
                query = """
                    SELECT * FROM location
                    LIMIT 5000
                """
                rows = self._query_sqlite(db_path, query)
                for row in rows:
                    timestamp = self._convert_android_timestamp(self._safe_get(row, "timestamp", 0))
                    result = {
                        "latitude": self._safe_get(row, "latitude"),
                        "longitude": self._safe_get(row, "longitude"),
                        "accuracy": self._safe_get(row, "accuracy"),
                        "altitude": self._safe_get(row, "altitude"),
                        "speed": self._safe_get(row, "speed"),
                        "date": timestamp,
                        "source_db": key,
                    }
                    results.append(result)

                    lat = self._safe_get(row, "latitude")
                    lng = self._safe_get(row, "longitude")
                    if lat and lng:
                        self._add_communication_entities(
                            f"{lat},{lng}", "location", "gps_fix", timestamp
                        )
                break

        return results

    # ==================== iOS EXTRACTION METHODS ====================

    def _extract_ios_sms(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse iOS sms.db: messages with iMessage indicators."""
        sms_db = db_files.get("sms.db")
        if not sms_db:
            return []

        query = """
            SELECT m.text, m.date/1000000000 as date, m.is_from_me,
                   m.is_read, m.cache_has_attachments,
                   h.id as contact, h.service
            FROM message m
            JOIN chat_handle_join chj ON m.ROWID = chj.message_id
            JOIN handle h ON chj.handle_id = h.ROWID
            ORDER BY m.date DESC
        """
        rows = self._query_sqlite(sms_db, query)
        results = []
        for row in rows:
            ts = self._safe_get(row, "date", 0)
            timestamp = self._convert_ios_timestamp(ts)
            is_from_me = self._safe_get(row, "is_from_me", 0)
            service = self._safe_get(row, "service", "SMS")
            direction = "sent" if is_from_me else "received"

            result = {
                "text": self._safe_get(row, "text"),
                "date": timestamp,
                "direction": direction,
                "is_read": bool(self._safe_get(row, "is_read", 0)),
                "has_attachments": bool(self._safe_get(row, "cache_has_attachments", 0)),
                "contact": self._safe_get(row, "contact"),
                "service": service,
                "is_imessage": service == "iMessage",
                "source_db": "sms.db",
            }
            results.append(result)

            contact = self._safe_get(row, "contact", "")
            if contact:
                self._add_communication_entities(contact, "ios_sms", direction, timestamp)

        return results

    def _extract_ios_calls(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse iOS CallHistory.storedata: call log."""
        calls_db = db_files.get("callhistory.storedata")
        if not calls_db:
            for key in db_files:
                if "call" in key:
                    calls_db = db_files[key]
                    break
        if not calls_db:
            return []

        query = """
            SELECT ZORIGINATINGADDRESS as number, ZCALLTYPE as type,
                   ZDATE/1000000000 + 978307200 as date,
                   ZDURATION as duration, ZORIGINATED as originated,
                   ZANSWERED as answered
            FROM ZCALLRECORD
            ORDER BY ZDATE DESC
        """
        rows = self._query_sqlite(calls_db, query)
        results = []
        for row in rows:
            ts = self._safe_get(row, "date", 0)
            try:
                timestamp = datetime.fromtimestamp(ts).isoformat() if ts else None
            except (ValueError, OSError):
                timestamp = None

            call_type = self._safe_get(row, "type", 0)
            originated = self._safe_get(row, "originated", 0)
            direction = "outgoing" if originated else "incoming"

            result = {
                "number": self._safe_get(row, "number"),
                "type": direction,
                "date": timestamp,
                "duration_seconds": self._safe_get(row, "duration", 0),
                "answered": bool(self._safe_get(row, "answered", 0)),
                "source_db": "CallHistory.storedata",
            }
            results.append(result)

            number = self._safe_get(row, "number", "")
            if number:
                self._add_communication_entities(number, "ios_call", direction, timestamp)

        return results

    def _extract_ios_contacts(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse iOS AddressBook.sqlitedb: contacts."""
        contacts_db = db_files.get("addressbook.sqlitedb")
        if not contacts_db:
            for key in db_files:
                if "address" in key or "contact" in key:
                    contacts_db = db_files[key]
                    break
        if not contacts_db:
            return []

        query = """
            SELECT cFirst as first_name, cLast as last_name,
                   cOrganization as organization, cDepartment as department,
                   cBirthday as birthday, cNote as note
            FROM ZABCDRECORD
        """
        rows = self._query_sqlite(contacts_db, query)
        results = []
        for row in rows:
            first_name = self._safe_get(row, "first_name", "")
            last_name = self._safe_get(row, "last_name", "")
            full_name = f"{first_name} {last_name}".strip()

            if not full_name:
                continue

            result = {
                "display_name": full_name,
                "first_name": first_name,
                "last_name": last_name,
                "organization": self._safe_get(row, "organization"),
                "department": self._safe_get(row, "department"),
                "birthday": self._safe_get(row, "birthday"),
                "notes": self._safe_get(row, "note"),
                "source_db": "AddressBook.sqlitedb",
            }
            results.append(result)

            self._add_communication_entities(full_name, "contact", "phone", None)

        return results

    def _extract_ios_photos(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse iOS Photos.sqlite: photo metadata, GPS coordinates."""
        photos_db = db_files.get("photos.sqlite")
        if not photos_db:
            for key in db_files:
                if "photo" in key:
                    photos_db = db_files[key]
                    break
        if not photos_db:
            return []

        query = """
            SELECT ZDATECREATED/1000000000 + 978307200 as date,
                   ZLATITUDE as latitude, ZLONGITUDE as longitude,
                   ZCAMERAMAKE as camera_make, ZCAMERAMODEL as camera_model,
                   ZORIGINALFILENAME as filename, ZDURATION as duration,
                   ZFAVORITE as favorite
            FROM ZADDITIONALASSETATTRIBUTES
            WHERE ZLATITUDE IS NOT NULL OR ZDATECREATED IS NOT NULL
            ORDER BY ZDATECREATED DESC
            LIMIT 5000
        """
        rows = self._query_sqlite(photos_db, query)
        results = []
        for row in rows:
            ts = self._safe_get(row, "date", 0)
            try:
                timestamp = datetime.fromtimestamp(ts).isoformat() if ts else None
            except (ValueError, OSError):
                timestamp = None

            result = {
                "filename": self._safe_get(row, "filename"),
                "date": timestamp,
                "latitude": self._safe_get(row, "latitude"),
                "longitude": self._safe_get(row, "longitude"),
                "camera_make": self._safe_get(row, "camera_make"),
                "camera_model": self._safe_get(row, "camera_model"),
                "duration": self._safe_get(row, "duration"),
                "favorite": bool(self._safe_get(row, "favorite", 0)),
                "source_db": "Photos.sqlite",
            }
            results.append(result)

            lat = self._safe_get(row, "latitude")
            lng = self._safe_get(row, "longitude")
            if lat and lng:
                self._add_communication_entities(
                    f"{lat},{lng}", "location", "photo_location", timestamp
                )

        return results

    def _extract_ios_safari(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse iOS History.db and Bookmarks.db: browsing history."""
        results = []
        history_db = db_files.get("history.db")
        if history_db:
            query = """
                SELECT url, title, visit_count, lastVisitedDate/1000000000 + 978307200 as date
                FROM history_items
                ORDER BY lastVisitedDate DESC
                LIMIT 5000
            """
            rows = self._query_sqlite(history_db, query)
            for row in rows:
                ts = self._safe_get(row, "date", 0)
                try:
                    timestamp = datetime.fromtimestamp(ts).isoformat() if ts else None
                except (ValueError, OSError):
                    timestamp = None

                result = {
                    "url": self._safe_get(row, "url"),
                    "title": self._safe_get(row, "title"),
                    "visit_count": self._safe_get(row, "visit_count", 0),
                    "last_visited": timestamp,
                    "source_db": "History.db",
                }
                results.append(result)

                url = self._safe_get(row, "url", "")
                if url:
                    self._add_communication_entities(url, "url", "visited", timestamp)

        bookmarks_db = db_files.get("bookmarks.db")
        if bookmarks_db:
            query = """
                SELECT b.url, b.title, b.date_added/1000000000 + 978307200 as date
                FROM bookmarks b
                ORDER BY date_added DESC
            """
            rows = self._query_sqlite(bookmarks_db, query)
            for row in rows:
                ts = self._safe_get(row, "date", 0)
                try:
                    timestamp = datetime.fromtimestamp(ts).isoformat() if ts else None
                except (ValueError, OSError):
                    timestamp = None

                result = {
                    "url": self._safe_get(row, "url"),
                    "title": self._safe_get(row, "title"),
                    "date_added": timestamp,
                    "source_db": "Bookmarks.db",
                }
                results.append(result)

        return results

    def _extract_ios_knowledgec(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse iOS KnowledgeC.db: app usage, Siri suggestions, location."""
        knowledgec_db = db_files.get("knowledgec.db")
        if not knowledgec_db:
            return []

        results = []

        app_query = """
            SELECT ZBUNDLEID, ZSTARTDATE/1000000000 + 978307200 as start_date,
                   ZENDDATE/1000000000 + 978307200 as end_date
            FROM ZSTRUCTUREDEVENTMETADATA
            WHERE ZBUNDLEID IS NOT NULL
            ORDER BY ZSTARTDATE DESC
            LIMIT 5000
        """
        rows = self._query_sqlite(knowledgec_db, app_query)
        for row in rows:
            start_ts = self._safe_get(row, "start_date", 0)
            end_ts = self._safe_get(row, "end_date", 0)
            try:
                start = datetime.fromtimestamp(start_ts).isoformat() if start_ts else None
                end = datetime.fromtimestamp(end_ts).isoformat() if end_ts else None
            except (ValueError, OSError):
                start = end = None

            result = {
                "type": "app_usage",
                "bundle_id": self._safe_get(row, "bundle_id"),
                "start_date": start,
                "end_date": end,
                "source_db": "KnowledgeC.db",
            }
            results.append(result)

            bundle_id = self._safe_get(row, "bundle_id", "")
            if bundle_id:
                self._add_communication_entities(bundle_id, "app", "used", start)

        return results

    def _extract_ios_plists(self, storage_path: str, plist_files: List[str]) -> List[Dict[str, Any]]:
        """Parse Info.plist, preferences plist files."""
        results = []
        for plist_path in plist_files:
            try:
                with open(plist_path, "rb") as f:
                    data = plistlib.load(f)

                if isinstance(data, dict):
                    result = {
                        "filename": os.path.basename(plist_path),
                        "path": plist_path,
                        "data": self._sanitize_plist(data),
                        "type": "plist",
                    }
                    results.append(result)
            except Exception as e:
                logger.warning(f"Failed to parse plist {plist_path}: {e}")

        return results

    def _extract_ios_keychain(self, storage_path: str, db_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Parse keychain metadata (metadata only, not actual secrets)."""
        results = []
        for key, db_path in db_files.items():
            if "keychain" in key:
                query = """
                    SELECT item_class, date_created, date_modified,
                           description, label, service, account
                    FROM keychain_items
                    ORDER BY date_created DESC
                    LIMIT 5000
                """
                rows = self._query_sqlite(db_path, query)
                for row in rows:
                    ts = self._safe_get(row, "date_created", 0)
                    try:
                        timestamp = datetime.fromtimestamp(ts).isoformat() if ts else None
                    except (ValueError, OSError):
                        timestamp = None

                    result = {
                        "item_class": self._safe_get(row, "item_class"),
                        "description": self._safe_get(row, "description"),
                        "label": self._safe_get(row, "label"),
                        "service": self._safe_get(row, "service"),
                        "account": self._safe_get(row, "account"),
                        "date_created": timestamp,
                        "source_db": key,
                    }
                    results.append(result)
                break

        return results

    # ==================== HELPER METHODS ====================

    def _add_communication_entities(
        self, identifier: str, comm_type: str, direction: str, timestamp: Optional[str]
    ) -> None:
        """Add communication entities and relationships for tracking patterns."""
        self._pending_entities.append({
            "name": identifier,
            "entity_type": comm_type,
            "properties": {"direction": direction, "timestamp": timestamp},
        })

    def _add_communication_entities_batch(self, evidence: EvidenceSchema) -> None:
        """Flush pending entities and relationships to evidence."""
        for entity in self._pending_entities:
            evidence.add_entity(
                name=entity["name"],
                entity_type=entity["entity_type"],
                properties=entity["properties"],
            )
        self._pending_entities.clear()
