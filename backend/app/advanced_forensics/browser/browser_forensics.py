import logging
import os
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Set, List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse

from ...forensic_engine.base import BaseProcessor
from ...forensic_engine.schemas import EvidenceSchema, EvidenceCategory, ForensicProcessorConfig, ProcessorPriority

logger = logging.getLogger(__name__)

CHROME_EPOCH = datetime(1601, 1, 1)
FIREFOX_EPOCH = datetime(1970, 1, 1)

CHROME_LIKE_TABLES = {
    "urls": "url, title, visit_count, last_visit_time",
    "downloads": "target_path, start_time, end_time, received_bytes",
    "cookies": "name, value, host_key, creation_date",
    "autofill": "name, value, date_created",
    "logins": "origin_url, username_value, date_created, date_password_modified",
    "extensions": "name, description, version",
    "keywords": "short_name, keyword, url",
}

FIREFOX_TABLES = {
    "moz_places": "url, title, visit_count, last_visit_date",
    "moz_bookmarks": "fk, title, dateAdded, lastModified, type",
    "moz_cookies": "name, value, host, creationTime, expiry",
    "moz_historyvisits": "place_id, visit_date, visit_type",
}

BROWSER_IDENTIFIERS = {
    "chrome": {"db_pattern": "History", "browser_name": "Chrome"},
    "edge": {"db_pattern": "History", "browser_name": "Microsoft Edge"},
    "brave": {"db_pattern": "History", "browser_name": "Brave"},
    "opera": {"db_pattern": "History", "browser_name": "Opera"},
    "firefox": {"db_pattern": "places.sqlite", "browser_name": "Firefox"},
}


class BrowserForensicsProcessor(BaseProcessor):
    name = "browser_forensics"
    description = "Extracts browser artifacts from Chrome, Edge, Firefox, Brave, Opera"
    supported_categories = frozenset({EvidenceCategory.BROWSER_DATA, EvidenceCategory.UNKNOWN})
    priority = ProcessorPriority.ARTIFACT_EXTRACTION

    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        browser_type = self._detect_browser(evidence)
        if not browser_type:
            evidence.add_error(self.name, "Could not detect browser type from evidence")
            return evidence

        evidence.metadata["browser_type"] = browser_type
        evidence.add_tag(f"browser:{browser_type}")

        db_path = evidence.storage_path
        if not os.path.isfile(db_path):
            evidence.add_error(self.name, f"Database file not found: {db_path}")
            return evidence

        conn = None
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            tables = self._get_tables(cursor)
            evidence.metadata["available_tables"] = list(tables)

            if browser_type in ("chrome", "edge", "brave", "opera"):
                self._extract_chrome_like(browser_type, cursor, evidence, tables)
            elif browser_type == "firefox":
                self._extract_firefox(cursor, evidence, tables)

            profile_name = self._extract_profile_name(evidence)
            evidence.metadata["profile_name"] = profile_name
            evidence.add_tag(f"profile:{profile_name}")

        except sqlite3.DatabaseError as e:
            evidence.add_error(self.name, f"SQLite error: {e}")
        except Exception as e:
            evidence.add_error(self.name, f"Processing failed: {e}")
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass

        return evidence

    def _detect_browser(self, evidence: EvidenceSchema) -> Optional[str]:
        path_lower = evidence.storage_path.lower()
        filename_lower = evidence.filename.lower()

        if "places.sqlite" in path_lower or "places.sqlite" in filename_lower:
            return "firefox"
        if "cookies.sqlite" in path_lower or "formhistory.sqlite" in path_lower:
            return "firefox"

        for browser_id, info in BROWSER_IDENTIFIERS.items():
            if browser_id == "firefox":
                continue
            if info["db_pattern"].lower() in filename_lower:
                if "brave" in path_lower or "brave" in filename_lower:
                    return "brave"
                if "edge" in path_lower or "msedge" in path_lower:
                    return "edge"
                if "opera" in path_lower or "opera software" in path_lower:
                    return "opera"
                return "chrome"

        if "history" in filename_lower:
            if "brave" in path_lower:
                return "brave"
            if "edge" in path_lower or "msedge" in path_lower:
                return "edge"
            if "opera" in path_lower:
                return "opera"
            return "chrome"

        return None

    def _get_tables(self, cursor: sqlite3.Cursor) -> set:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return {row[0] for row in cursor.fetchall()}

    def _chrome_time_to_iso(self, chrome_time: int) -> Optional[str]:
        if not chrome_time or chrome_time == 0:
            return None
        try:
            dt = CHROME_EPOCH + timedelta(microseconds=chrome_time)
            return dt.isoformat()
        except (OverflowError, ValueError):
            return None

    def _firefox_time_to_iso(self, firefox_time: int) -> Optional[str]:
        if not firefox_time or firefox_time == 0:
            return None
        try:
            if firefox_time > 1e15:
                dt = FIREFOX_EPOCH + timedelta(microseconds=firefox_time)
            else:
                dt = FIREFOX_EPOCH + timedelta(milliseconds=firefox_time)
            return dt.isoformat()
        except (OverflowError, ValueError):
            return None

    def _extract_domain(self, url: str) -> Optional[str]:
        try:
            parsed = urlparse(url)
            return parsed.hostname
        except Exception:
            return None

    def _extract_chrome_like(self, browser_type: str, cursor: sqlite3.Cursor,
                             evidence: EvidenceSchema, tables: set) -> None:
        browser_name = BROWSER_IDENTIFIERS[browser_type]["browser_name"]

        if "urls" in tables:
            self._extract_chrome_history(browser_type, browser_name, cursor, evidence)

        if "downloads" in tables:
            self._extract_chrome_downloads(browser_type, browser_name, cursor, evidence)

        if "cookies" in tables:
            self._extract_chrome_cookies(browser_type, browser_name, cursor, evidence)

        if "autofill" in tables:
            self._extract_chrome_autofill(browser_type, browser_name, cursor, evidence)

        if "logins" in tables:
            self._extract_chrome_logins(browser_type, browser_name, cursor, evidence)

        if "extensions" in tables:
            self._extract_chrome_extensions(browser_type, browser_name, cursor, evidence)

        if "keywords" in tables:
            self._extract_chrome_search_engines(browser_type, browser_name, cursor, evidence)

    def _extract_chrome_history(self, browser_type: str, browser_name: str,
                                cursor: sqlite3.Cursor, evidence: EvidenceSchema) -> None:
        try:
            cursor.execute("""
                SELECT url, title, visit_count, last_visit_time
                FROM urls
                ORDER BY last_visit_time DESC
                LIMIT 10000
            """)
            results = []
            seen_urls = set()
            for row in cursor.fetchall():
                url = row["url"]
                title = row["title"] or ""
                visit_count = row["visit_count"]
                last_visit = self._chrome_time_to_iso(row["last_visit_time"])

                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                artifact = {
                    "url": url,
                    "title": title,
                    "visit_count": visit_count,
                    "last_visit_time": last_visit,
                    "browser": browser_name,
                    "browser_type": browser_type,
                }
                results.append(artifact)

                evidence.add_timeline_event(
                    last_visit or "unknown",
                    f"Visited {title or url}",
                    self.name
                )

                domain = self._extract_domain(url)
                if domain:
                    evidence.add_entity(domain, "domain", {"browser": browser_name})
                    evidence.add_entity(url, "url", {"title": title, "visit_count": visit_count})
                    evidence.add_relationship(evidence.evidence_id, domain, "visited_domain")
                    evidence.add_relationship(evidence.evidence_id, url, "visited_url")

            evidence.add_result(self.name, {"browser_history": results})
            evidence.add_tag("browser_history")

        except Exception as e:
            evidence.add_error(self.name, f"History extraction failed: {e}")

    def _extract_chrome_downloads(self, browser_type: str, browser_name: str,
                                  cursor: sqlite3.Cursor, evidence: EvidenceSchema) -> None:
        try:
            cursor.execute("""
                SELECT target_path, start_time, end_time, received_bytes
                FROM downloads
                ORDER BY start_time DESC
                LIMIT 5000
            """)
            results = []
            for row in cursor.fetchall():
                target_path = row["target_path"] or ""
                start_time = self._chrome_time_to_iso(row["start_time"])
                end_time = self._chrome_time_to_iso(row["end_time"])
                received_bytes = row["received_bytes"]

                artifact = {
                    "target_path": target_path,
                    "start_time": start_time,
                    "end_time": end_time,
                    "received_bytes": received_bytes,
                    "browser": browser_name,
                    "browser_type": browser_type,
                }
                results.append(artifact)

                if start_time:
                    evidence.add_timeline_event(
                        start_time,
                        f"Downloaded {os.path.basename(target_path)}",
                        self.name
                    )

                filename = os.path.basename(target_path)
                if filename:
                    evidence.add_entity(filename, "downloaded_file", {
                        "path": target_path,
                        "size": received_bytes,
                        "browser": browser_name,
                    })
                    evidence.add_relationship(evidence.evidence_id, filename, "downloaded")

            evidence.add_result(self.name, {"browser_downloads": results})
            evidence.add_tag("browser_downloads")

        except Exception as e:
            evidence.add_error(self.name, f"Downloads extraction failed: {e}")

    def _extract_chrome_cookies(self, browser_type: str, browser_name: str,
                                cursor: sqlite3.Cursor, evidence: EvidenceSchema) -> None:
        try:
            cursor.execute("""
                SELECT name, value, host_key, creation_date
                FROM cookies
                ORDER BY creation_date DESC
                LIMIT 10000
            """)
            results = []
            domains_seen = set()
            for row in cursor.fetchall():
                name = row["name"]
                value = row["value"] or ""
                host_key = row["host_key"]
                creation_date = self._chrome_time_to_iso(row["creation_date"])

                artifact = {
                    "name": name,
                    "value": value[:200] if value else "",
                    "host": host_key,
                    "creation_date": creation_date,
                    "browser": browser_name,
                    "browser_type": browser_type,
                }
                results.append(artifact)

                if host_key and host_key not in domains_seen:
                    domains_seen.add(host_key)
                    evidence.add_entity(host_key, "domain", {"browser": browser_name})

            evidence.add_result(self.name, {"browser_cookies": results})
            evidence.add_tag("browser_cookies")

        except Exception as e:
            evidence.add_error(self.name, f"Cookies extraction failed: {e}")

    def _extract_chrome_autofill(self, browser_type: str, browser_name: str,
                                 cursor: sqlite3.Cursor, evidence: EvidenceSchema) -> None:
        try:
            cursor.execute("""
                SELECT name, value, date_created
                FROM autofill
                ORDER BY date_created DESC
                LIMIT 5000
            """)
            results = []
            for row in cursor.fetchall():
                name = row["name"]
                value = row["value"] or ""
                date_created = self._chrome_time_to_iso(row["date_created"])

                artifact = {
                    "field_name": name,
                    "field_value": value[:200] if value else "",
                    "date_created": date_created,
                    "browser": browser_name,
                    "browser_type": browser_type,
                }
                results.append(artifact)

                if date_created:
                    evidence.add_timeline_event(
                        date_created,
                        f"Autofill entry: {name}",
                        self.name
                    )

            evidence.add_result(self.name, {"browser_autofill": results})
            evidence.add_tag("browser_autofill")

        except Exception as e:
            evidence.add_error(self.name, f"Autofill extraction failed: {e}")

    def _extract_chrome_logins(self, browser_type: str, browser_name: str,
                               cursor: sqlite3.Cursor, evidence: EvidenceSchema) -> None:
        try:
            cursor.execute("""
                SELECT origin_url, username_value, date_created, date_password_modified
                FROM logins
                ORDER BY date_created DESC
                LIMIT 5000
            """)
            results = []
            for row in cursor.fetchall():
                origin_url = row["origin_url"]
                username = row["username_value"] or ""
                date_created = self._chrome_time_to_iso(row["date_created"])
                date_modified = self._chrome_time_to_iso(row["date_password_modified"])

                artifact = {
                    "origin_url": origin_url,
                    "username": username,
                    "date_created": date_created,
                    "date_password_modified": date_modified,
                    "browser": browser_name,
                    "browser_type": browser_type,
                    "metadata_only": True,
                }
                results.append(artifact)

                if origin_url:
                    domain = self._extract_domain(origin_url)
                    if domain:
                        evidence.add_entity(domain, "credential_source", {
                            "username": username,
                            "browser": browser_name,
                        })
                        evidence.add_relationship(evidence.evidence_id, domain, "has_saved_credential")

            evidence.add_result(self.name, {"browser_saved_logins": results})
            evidence.add_tag("browser_saved_logins")

        except Exception as e:
            evidence.add_error(self.name, f"Logins extraction failed: {e}")

    def _extract_chrome_extensions(self, browser_type: str, browser_name: str,
                                   cursor: sqlite3.Cursor, evidence: EvidenceSchema) -> None:
        try:
            cursor.execute("""
                SELECT name, description, version
                FROM extensions
            """)
            results = []
            for row in cursor.fetchall():
                name = row["name"]
                description = row["description"] or ""
                version = row["version"] or ""

                artifact = {
                    "name": name,
                    "description": description,
                    "version": version,
                    "browser": browser_name,
                    "browser_type": browser_type,
                }
                results.append(artifact)

                if name:
                    evidence.add_entity(name, "browser_extension", {
                        "version": version,
                        "browser": browser_name,
                    })

            evidence.add_result(self.name, {"browser_extensions": results})
            evidence.add_tag("browser_extensions")

        except Exception as e:
            evidence.add_error(self.name, f"Extensions extraction failed: {e}")

    def _extract_chrome_search_engines(self, browser_type: str, browser_name: str,
                                       cursor: sqlite3.Cursor, evidence: EvidenceSchema) -> None:
        try:
            cursor.execute("""
                SELECT short_name, keyword, url
                FROM keywords
            """)
            results = []
            for row in cursor.fetchall():
                short_name = row["short_name"] or ""
                keyword = row["keyword"] or ""
                url = row["url"] or ""

                artifact = {
                    "short_name": short_name,
                    "keyword": keyword,
                    "url": url,
                    "browser": browser_name,
                    "browser_type": browser_type,
                }
                results.append(artifact)

                if keyword:
                    evidence.add_entity(keyword, "search_engine", {"url": url})

            evidence.add_result(self.name, {"browser_search_engines": results})

        except Exception as e:
            evidence.add_error(self.name, f"Search engines extraction failed: {e}")

    def _extract_firefox(self, cursor: sqlite3.Cursor,
                         evidence: EvidenceSchema, tables: set) -> None:
        browser_name = "Firefox"

        if "moz_places" in tables:
            self._extract_firefox_history(browser_name, cursor, evidence)

        if "moz_bookmarks" in tables:
            self._extract_firefox_bookmarks(browser_name, cursor, evidence)

        if "moz_cookies" in tables:
            self._extract_firefox_cookies(browser_name, cursor, evidence)

        if "moz_historyvisits" in tables:
            self._extract_firefox_visit_details(browser_name, cursor, evidence)

    def _extract_firefox_history(self, browser_name: str,
                                 cursor: sqlite3.Cursor, evidence: EvidenceSchema) -> None:
        try:
            cursor.execute("""
                SELECT url, title, visit_count, last_visit_date
                FROM moz_places
                WHERE visit_count > 0
                ORDER BY last_visit_date DESC
                LIMIT 10000
            """)
            results = []
            seen_urls = set()
            for row in cursor.fetchall():
                url = row["url"]
                title = row["title"] or ""
                visit_count = row["visit_count"]
                last_visit = self._firefox_time_to_iso(row["last_visit_date"])

                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                artifact = {
                    "url": url,
                    "title": title,
                    "visit_count": visit_count,
                    "last_visit_time": last_visit,
                    "browser": browser_name,
                    "browser_type": "firefox",
                }
                results.append(artifact)

                if last_visit:
                    evidence.add_timeline_event(
                        last_visit,
                        f"Visited {title or url}",
                        self.name
                    )

                domain = self._extract_domain(url)
                if domain:
                    evidence.add_entity(domain, "domain", {"browser": browser_name})
                    evidence.add_entity(url, "url", {"title": title, "visit_count": visit_count})
                    evidence.add_relationship(evidence.evidence_id, domain, "visited_domain")
                    evidence.add_relationship(evidence.evidence_id, url, "visited_url")

            evidence.add_result(self.name, {"browser_history": results})
            evidence.add_tag("browser_history")

        except Exception as e:
            evidence.add_error(self.name, f"Firefox history extraction failed: {e}")

    def _extract_firefox_bookmarks(self, browser_name: str,
                                    cursor: sqlite3.Cursor, evidence: EvidenceSchema) -> None:
        try:
            cursor.execute("""
                SELECT b.title, p.url, b.dateAdded, b.lastModified
                FROM moz_bookmarks b
                LEFT JOIN moz_places p ON b.fk = p.id
                WHERE p.url IS NOT NULL
                ORDER BY b.dateAdded DESC
                LIMIT 5000
            """)
            results = []
            for row in cursor.fetchall():
                title = row["title"] or ""
                url = row["url"]
                date_added = self._firefox_time_to_iso(row["dateAdded"])
                last_modified = self._firefox_time_to_iso(row["lastModified"])

                artifact = {
                    "title": title,
                    "url": url,
                    "date_added": date_added,
                    "last_modified": last_modified,
                    "browser": browser_name,
                    "browser_type": "firefox",
                }
                results.append(artifact)

                if date_added:
                    evidence.add_timeline_event(
                        date_added,
                        f"Bookmarked: {title or url}",
                        self.name
                    )

                if url:
                    evidence.add_entity(url, "bookmark", {"title": title})
                    evidence.add_relationship(evidence.evidence_id, url, "bookmarked")

            evidence.add_result(self.name, {"browser_bookmarks": results})
            evidence.add_tag("browser_bookmarks")

        except Exception as e:
            evidence.add_error(self.name, f"Firefox bookmarks extraction failed: {e}")

    def _extract_firefox_cookies(self, browser_name: str,
                                 cursor: sqlite3.Cursor, evidence: EvidenceSchema) -> None:
        try:
            cursor.execute("""
                SELECT name, value, host, creationTime, expiry
                FROM moz_cookies
                ORDER BY creationTime DESC
                LIMIT 10000
            """)
            results = []
            domains_seen = set()
            for row in cursor.fetchall():
                name = row["name"]
                value = row["value"] or ""
                host = row["host"]
                creation_time = self._firefox_time_to_iso(row["creationTime"])
                expiry = self._firefox_time_to_iso(row["expiry"])

                artifact = {
                    "name": name,
                    "value": value[:200] if value else "",
                    "host": host,
                    "creation_time": creation_time,
                    "expiry": expiry,
                    "browser": browser_name,
                    "browser_type": "firefox",
                }
                results.append(artifact)

                if host and host not in domains_seen:
                    domains_seen.add(host)
                    evidence.add_entity(host, "domain", {"browser": browser_name})

            evidence.add_result(self.name, {"browser_cookies": results})
            evidence.add_tag("browser_cookies")

        except Exception as e:
            evidence.add_error(self.name, f"Firefox cookies extraction failed: {e}")

    def _extract_firefox_visit_details(self, browser_name: str,
                                       cursor: sqlite3.Cursor, evidence: EvidenceSchema) -> None:
        try:
            cursor.execute("""
                SELECT hv.place_id, hv.visit_date, hv.visit_type, p.url, p.title
                FROM moz_historyvisits hv
                JOIN moz_places p ON hv.place_id = p.id
                ORDER BY hv.visit_date DESC
                LIMIT 10000
            """)
            results = []
            for row in cursor.fetchall():
                url = row["url"]
                title = row["title"] or ""
                visit_date = self._firefox_time_to_iso(row["visit_date"])
                visit_type = row["visit_type"]

                artifact = {
                    "url": url,
                    "title": title,
                    "visit_date": visit_date,
                    "visit_type": visit_type,
                    "browser": browser_name,
                    "browser_type": "firefox",
                }
                results.append(artifact)

            evidence.add_result(self.name, {"browser_visit_details": results})

        except Exception as e:
            evidence.add_error(self.name, f"Firefox visit details extraction failed: {e}")

    def _extract_profile_name(self, evidence: EvidenceSchema) -> str:
        path = evidence.storage_path.lower()

        profile_markers = {
            "default": "Default",
            "profile 1": "Profile 1",
            "profile 2": "Profile 2",
            "profile 3": "Profile 3",
            "guest profile": "Guest Profile",
            "private": "Private",
        }

        for marker, name in profile_markers.items():
            if marker in path:
                return name

        return "Default"
