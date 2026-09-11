import email
import hashlib
import logging
import re
import socket
import struct
from collections import defaultdict
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime, parseaddr, parseaddr
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

from ...forensic_engine.base import BaseProcessor
from ...forensic_engine.schemas import (
    EvidenceCategory,
    EvidenceSchema,
    ForensicProcessorConfig,
    ProcessorPriority,
)
from ..schemas import Artifact, ArtifactType, IOC, IOCType, Finding, RiskIndicator, RiskLevel

logger = logging.getLogger(__name__)

SUSPICIOUS_EXTENSIONS = frozenset({
    ".exe", ".scr", ".js", ".vbs", ".ps1", ".bat", ".cmd", ".com",
    ".pif", ".msi", ".wsf", ".wsh", ".hta", ".cpl", ".lnk",
})

LOOKALIKE_DOMAINS = {
    "gmail.com": ["gmai1.com", "gmail.co", "gmaill.com", "gnail.com", "gmxail.com"],
    "yahoo.com": ["yaho0.com", "yahooo.com", "yahoo.co"],
    "hotmail.com": ["hotmai1.com", "hotmal.com", "hotmail.co"],
    "outlook.com": ["outlooK.com", "outllook.com"],
}


class EmailForensicsProcessor(BaseProcessor):
    """Deep email analysis: SPF/DKIM/DMARC validation, thread reconstruction,
    header analysis, hop analysis, attachment graph, suspicious indicators."""

    @property
    def name(self) -> str:
        return "email_forensics"

    @property
    def description(self) -> str:
        return (
            "Deep email analysis: SPF/DKIM/DMARC validation, thread reconstruction, "
            "header analysis, hop analysis, attachment graph, suspicious indicators"
        )

    @property
    def supported_categories(self) -> frozenset:
        return frozenset({EvidenceCategory.EMAIL, EvidenceCategory.UNKNOWN})

    @property
    def priority(self) -> ProcessorPriority:
        return ProcessorPriority.DEEP_ANALYSIS

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        try:
            msg = self._parse_email_file(evidence)
            if msg is None:
                return evidence

            headers = self._analyze_headers(msg)
            spf_result = self._validate_spf(headers)
            dkim_result = self._validate_dkim(headers)
            dmarc_result = self._validate_dmarc(headers)
            hops = self._analyze_hops(headers)
            attachments = self._extract_attachments(msg)
            attachment_graph = self._build_attachment_graph(headers, attachments)
            suspicious = self._detect_suspicious_indicators(headers, spf_result, dkim_result, dmarc_result, attachments)
            thread = self._reconstruct_thread(headers)

            body = self._extract_body(msg)

            self._emit_artifacts(evidence, headers, body, attachments, spf_result, dkim_result, dmarc_result,
                                 hops, attachment_graph, suspicious, thread)

            evidence.add_tag("email")
            evidence.add_tag("email_forensics")
            if suspicious:
                evidence.add_tag("suspicious_email")
            if spf_result not in ("pass", None):
                evidence.add_tag(f"spf_{spf_result}")
            if dkim_result not in ("pass", None):
                evidence.add_tag(f"dkim_{dkim_result}")
            if dmarc_result not in ("pass", None):
                evidence.add_tag(f"dmarc_{dmarc_result}")

            result_data = {
                "headers": headers,
                "body_preview": body[:2000] if body else "",
                "spf_result": spf_result,
                "dkim_result": dkim_result,
                "dmarc_result": dmarc_result,
                "hops": hops,
                "attachments": attachments,
                "attachment_graph": attachment_graph,
                "suspicious_indicators": suspicious,
                "thread": thread,
            }
            evidence.add_result(self.name, result_data)

        except Exception as e:
            logger.exception("Email forensics processing failed")
            evidence.add_error(self.name, f"Email forensics failed: {e}")

        return evidence

    # ------------------------------------------------------------------
    # 1. Parse email file
    # ------------------------------------------------------------------

    def _parse_email_file(self, evidence: EvidenceSchema) -> Optional[email.message.Message]:
        try:
            with open(evidence.storage_path, "rb") as fh:
                msg = BytesParser(policy=policy.default).parse(fh)
            return msg
        except Exception as e:
            evidence.add_error(self.name, f"Failed to parse email file: {e}")
            return None

    def _extract_body(self, msg: email.message.Message) -> str:
        body = ""
        body_part = msg.get_body(preferencelist=("plain", "html"))
        if body_part:
            try:
                body = body_part.get_content() or ""
            except Exception:
                payload = body_part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    body = payload.decode("utf-8", errors="replace")
                else:
                    body = str(payload) if payload else ""
        return body.strip()

    # ------------------------------------------------------------------
    # 2. Header analysis
    # ------------------------------------------------------------------

    def _analyze_headers(self, msg: email.message.Message) -> Dict[str, Any]:
        all_headers: Dict[str, Any] = {}
        received_headers: List[str] = []
        header_counts: Dict[str, int] = defaultdict(int)

        for key, value in msg.items():
            header_counts[key.lower()] += 1
            if key.lower() == "received":
                received_headers.append(value)
            if key not in all_headers:
                all_headers[key] = value
            else:
                if isinstance(all_headers[key], list):
                    all_headers[key].append(value)
                else:
                    all_headers[key] = [all_headers[key], value]

        # anomalies
        anomalies: List[str] = []
        if "from" not in all_headers:
            anomalies.append("Missing From header")
        if "to" not in all_headers:
            anomalies.append("Missing To header")
        if "date" not in all_headers:
            anomalies.append("Missing Date header")
        if "message-id" not in all_headers:
            anomalies.append("Missing Message-ID header")
        if "subject" not in all_headers:
            anomalies.append("Missing Subject header")

        for hdr, count in header_counts.items():
            if count > 1 and hdr not in ("received", "received-spf", "authentication-results"):
                anomalies.append(f"Duplicate header: {hdr} ({count} occurrences)")

        # extract key fields
        from_header = msg.get("from", "")
        sender_name, sender_email = parseaddr(from_header)
        sender_domain = sender_email.split("@")[-1] if "@" in sender_email else ""
        return_path = msg.get("return-path", "")
        return_email = parseaddr(return_path)[1] if return_path else ""
        return_domain = return_email.split("@")[-1] if "@" in return_email else ""

        x_originating_ip = msg.get("x-originating-ip", "")
        user_agent = msg.get("user-agent", "") or msg.get("x-mailer", "") or msg.get("x-mimeole", "")

        try:
            date_dt = parsedate_to_datetime(msg.get("date", ""))
            date_str = date_dt.isoformat()
        except Exception:
            date_str = msg.get("date", "unknown")

        ip_headers: List[str] = []
        for hdr_name in ("x-originating-ip", "x-forwarded-for", "x-real-ip"):
            val = msg.get(hdr_name, "")
            if val:
                ip_match = re.findall(r"[\d]+\.[\d]+\.[\d]+\.[\d]+", val)
                ip_headers.extend(ip_match)

        analysis = {
            "message_id": msg.get("message-id", ""),
            "in_reply_to": msg.get("in-reply-to", ""),
            "references": msg.get("references", ""),
            "subject": msg.get("subject", ""),
            "from": from_header,
            "sender_name": sender_name,
            "sender_email": sender_email,
            "sender_domain": sender_domain,
            "to": msg.get("to", ""),
            "cc": msg.get("cc", ""),
            "bcc": msg.get("bcc", ""),
            "return_path": return_path,
            "return_email": return_email,
            "return_domain": return_domain,
            "date": date_str,
            "date_parsed": date_dt if "date_dt" in dir() else None,
            "x_originating_ip": x_originating_ip,
            "user_agent": user_agent,
            "received_headers": received_headers,
            "received_count": len(received_headers),
            "ip_addresses": ip_headers,
            "anomalies": anomalies,
            "header_count": dict(header_counts),
            "all_headers": all_headers,
        }
        return analysis

    # ------------------------------------------------------------------
    # 3. SPF validation
    # ------------------------------------------------------------------

    def _validate_spf(self, headers: Dict[str, Any]) -> Optional[str]:
        # Check received-spf header first
        all_h = headers.get("all_headers", {})
        received_spf = all_h.get("received-spf") or all_h.get("Received-SPF") or ""
        if received_spf:
            lower = str(received_spf).lower()
            if "pass" in lower:
                return "pass"
            if "softfail" in lower:
                return "softfail"
            if "fail" in lower:
                return "fail"
            if "neutral" in lower:
                return "neutral"
            if "none" in lower:
                return "none"

        # Check authentication-results (case-insensitive lookup)
        auth_results = ""
        for key in all_h:
            if key.lower() == "authentication-results":
                auth_results = all_h[key]
                break
        if auth_results:
            spf_match = re.search(r"spf=(pass|fail|softfail|neutral|none|temperror|permerror)", str(auth_results), re.I)
            if spf_match:
                return spf_match.group(1).lower()

        return None

    # ------------------------------------------------------------------
    # 4. DKIM validation
    # ------------------------------------------------------------------

    def _validate_dkim(self, headers: Dict[str, Any]) -> Optional[str]:
        all_h = headers.get("all_headers", {})
        dkim_sig = all_h.get("dkim-signature") or all_h.get("DKIM-Signature") or ""
        if not dkim_sig:
            return None

        # Check authentication-results for DKIM verdict
        auth_results = ""
        for key in all_h:
            if key.lower() == "authentication-results":
                auth_results = all_h[key]
                break
        if auth_results:
            dkim_match = re.search(r"dkim=(pass|fail|none|neutral|temperror|permerror)", str(auth_results), re.I)
            if dkim_match:
                return dkim_match.group(1).lower()

        # Parse DKIM-Signature to extract domain and selector
        dkim_fields = {}
        for part in str(dkim_sig).split(";"):
            part = part.strip()
            if "=" in part:
                k, v = part.split("=", 1)
                dkim_fields[k.strip().lower()] = v.strip()

        domain = dkim_fields.get("d", "")
        selector = dkim_fields.get("s", "")
        if domain:
            return "unsigned"  # signature present but not verified inline
        return "none"

    # ------------------------------------------------------------------
    # 5. DMARC validation
    # ------------------------------------------------------------------

    def _validate_dmarc(self, headers: Dict[str, Any]) -> Optional[str]:
        all_h = headers.get("all_headers", {})
        auth_results = ""
        for key in all_h:
            if key.lower() == "authentication-results":
                auth_results = all_h[key]
                break
        if auth_results:
            dmarc_match = re.search(r"dmarc=(pass|fail|none|bestguess|skipped)", str(auth_results), re.I)
            if dmarc_match:
                val = dmarc_match.group(1).lower()
                return "pass" if val == "pass" else ("none" if val in ("none", "skipped") else "fail")
        return None

    # ------------------------------------------------------------------
    # 6. Thread reconstruction
    # ------------------------------------------------------------------

    def _reconstruct_thread(self, headers: Dict[str, Any]) -> Dict[str, Any]:
        message_id = headers.get("message_id", "")
        in_reply_to = headers.get("in_reply_to", "")
        references = headers.get("references", "")
        subject = headers.get("subject", "")
        from_addr = headers.get("sender_email", "")
        to_addr = headers.get("to", "")
        date = headers.get("date", "")

        ref_list = [r.strip() for r in references.split() if r.strip()] if references else []
        if in_reply_to and in_reply_to not in ref_list:
            ref_list.append(in_reply_to)

        participants = set()
        if from_addr:
            participants.add(from_addr)
        for addr_field in ("to", "cc"):
            raw = headers.get(addr_field, "")
            if raw:
                for part in raw.split(","):
                    _, email_addr = parseaddr(part.strip())
                    if email_addr:
                        participants.add(email_addr)

        thread = {
            "message_id": message_id,
            "subject": subject,
            "from": from_addr,
            "to": to_addr,
            "date": date,
            "in_reply_to": in_reply_to,
            "references": ref_list,
            "thread_depth": len(ref_list),
            "participants": sorted(participants),
            "is_reply": bool(in_reply_to),
        }
        return thread

    # ------------------------------------------------------------------
    # 7. Hop analysis
    # ------------------------------------------------------------------

    def _analyze_hops(self, headers: Dict[str, Any]) -> List[Dict[str, Any]]:
        received = headers.get("received_headers", [])
        hops: List[Dict[str, Any]] = []

        for i, recv in enumerate(reversed(received)):
            hop: Dict[str, Any] = {
                "hop_number": i + 1,
                "raw": recv,
                "from_ip": None,
                "from_host": None,
                "by_host": None,
                "timestamp": None,
                "protocol": None,
            }

            from_match = re.search(r"from\s+(\S+)", recv)
            if from_match:
                hop["from_host"] = from_match.group(1)

            by_match = re.search(r"by\s+(\S+)", recv)
            if by_match:
                hop["by_host"] = by_match.group(1)

            ip_match = re.search(r"\[(\d+\.\d+\.\d+\.\d+)\]", recv)
            if ip_match:
                hop["from_ip"] = ip_match.group(1)

            proto_match = re.search(r"\((.+?)\)", recv)
            if proto_match:
                proto_str = proto_match.group(1)
                hop["protocol"] = proto_str.split(";")[0].strip() if ";" in proto_str else proto_str.strip()

            for line_part in recv.split():
                try:
                    ts = parsedate_to_datetime(line_part)
                    hop["timestamp"] = ts.isoformat()
                    break
                except Exception:
                    continue

            hops.append(hop)

        return hops

    # ------------------------------------------------------------------
    # 8. Attachment graph
    # ------------------------------------------------------------------

    def _extract_attachments(self, msg: email.message.Message) -> List[Dict[str, Any]]:
        attachments: List[Dict[str, Any]] = []
        for part in msg.iter_attachments():
            filename = part.get_filename() or "unnamed"
            content_type = part.get_content_type()
            payload = part.get_payload(decode=True)
            size = len(payload) if payload else 0
            sha256 = hashlib.sha256(payload).hexdigest() if payload else ""
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

            attachments.append({
                "filename": filename,
                "content_type": content_type,
                "size": size,
                "sha256": sha256,
                "extension": ext,
                "is_suspicious_extension": f".{ext}" in SUSPICIOUS_EXTENSIONS if ext else False,
            })
        return attachments

    def _build_attachment_graph(self, headers: Dict[str, Any], attachments: List[Dict[str, Any]]) -> Dict[str, Any]:
        sender = headers.get("sender_email", "")
        graph: Dict[str, Any] = {
            "sender": sender,
            "attachments": attachments,
            "shared_hashes": {},
            "filename_reuse": {},
            "total_attachment_count": len(attachments),
            "suspicious_count": sum(1 for a in attachments if a.get("is_suspicious_extension")),
        }

        hash_map: Dict[str, List[str]] = defaultdict(list)
        name_map: Dict[str, List[str]] = defaultdict(list)
        for att in attachments:
            if att["sha256"]:
                hash_map[att["sha256"]].append(att["filename"])
            name_map[att["filename"]].append(att["sha256"])

        graph["shared_hashes"] = {h: fns for h, fns in hash_map.items() if len(fns) > 1}
        graph["filename_reuse"] = {n: shas for n, shas in name_map.items() if len(shas) > 1}
        return graph

    # ------------------------------------------------------------------
    # 9. Suspicious indicators
    # ------------------------------------------------------------------

    def _detect_suspicious_indicators(
        self,
        headers: Dict[str, Any],
        spf_result: Optional[str],
        dkim_result: Optional[str],
        dmarc_result: Optional[str],
        attachments: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        indicators: List[Dict[str, Any]] = []

        # Spoofed / lookalike domains
        sender_domain = headers.get("sender_domain", "")
        return_domain = headers.get("return_domain", "")
        for legit, lookalikes in LOOKALIKE_DOMAINS.items():
            if sender_domain in lookalikes:
                indicators.append({
                    "type": "lookalike_domain",
                    "detail": f"Sender domain '{sender_domain}' resembles '{legit}'",
                    "risk_level": RiskLevel.HIGH.value,
                    "mitre_attack": "T1586.002",
                })
        if sender_domain and return_domain and sender_domain != return_domain:
            indicators.append({
                "type": "return_path_mismatch",
                "detail": f"Return-Path domain '{return_domain}' differs from sender domain '{sender_domain}'",
                "risk_level": RiskLevel.MEDIUM.value,
            })

        # Display name vs email mismatch
        sender_name = headers.get("sender_name", "")
        sender_email = headers.get("sender_email", "")
        if sender_name and sender_email:
            name_words = set(sender_name.lower().split())
            local_part = sender_email.split("@")[0].lower()
            if local_part and not any(w in local_part for w in name_words) and len(sender_name) > 3:
                indicators.append({
                    "type": "display_name_mismatch",
                    "detail": f"Display name '{sender_name}' does not match email '{sender_email}'",
                    "risk_level": RiskLevel.MEDIUM.value,
                })

        # SPF / DKIM / DMARC failures
        if spf_result and spf_result not in ("pass", "none"):
            indicators.append({
                "type": "spf_failure",
                "detail": f"SPF check returned: {spf_result}",
                "risk_level": RiskLevel.HIGH.value,
                "mitre_attack": "T1586.002",
            })
        if dkim_result and dkim_result not in ("pass", "none"):
            indicators.append({
                "type": "dkim_failure",
                "detail": f"DKIM check returned: {dkim_result}",
                "risk_level": RiskLevel.HIGH.value,
                "mitre_attack": "T1586.002",
            })
        if dmarc_result and dmarc_result not in ("pass", "none"):
            indicators.append({
                "type": "dmarc_failure",
                "detail": f"DMARC check returned: {dmarc_result}",
                "risk_level": RiskLevel.HIGH.value,
                "mitre_attack": "T1586.002",
            })

        # Header anomalies
        for anomaly in headers.get("anomalies", []):
            indicators.append({
                "type": "header_anomaly",
                "detail": anomaly,
                "risk_level": RiskLevel.LOW.value,
            })

        # Suspicious attachments
        for att in attachments:
            if att.get("is_suspicious_extension"):
                indicators.append({
                    "type": "suspicious_attachment",
                    "detail": f"Potentially dangerous attachment: {att['filename']} (.{att['extension']})",
                    "risk_level": RiskLevel.CRITICAL.value,
                    "mitre_attack": "T1566.001",
                })

        # Body-based indicators (IP addresses as URLs, shortened URLs)
        # These are checked during _emit_artifacts with extracted body
        return indicators

    # ------------------------------------------------------------------
    # Artifact emission helpers
    # ------------------------------------------------------------------

    def _emit_artifacts(
        self,
        evidence: EvidenceSchema,
        headers: Dict[str, Any],
        body: str,
        attachments: List[Dict[str, Any]],
        spf_result: Optional[str],
        dkim_result: Optional[str],
        dmarc_result: Optional[str],
        hops: List[Dict[str, Any]],
        attachment_graph: Dict[str, Any],
        suspicious: List[Dict[str, Any]],
        thread: Dict[str, Any],
    ) -> None:
        sender_email = headers.get("sender_email", "")
        sender_domain = headers.get("sender_domain", "")
        date = headers.get("date", "")
        message_id = headers.get("message_id", "")

        # Timeline event
        if date and date != "unknown":
            summary = f"Email from {sender_email}: {headers.get('subject', '(no subject)')}"
            evidence.add_timeline_event(date, summary, self.name)

        # Entity: sender email
        if sender_email:
            evidence.add_entity(sender_email, "email_address", {"role": "sender", "domain": sender_domain})

        # Entity: sender domain
        if sender_domain:
            evidence.add_entity(sender_domain, "domain", {"type": "sender_domain"})

        # Entity: recipient emails
        for field_name in ("to", "cc"):
            raw = headers.get(field_name, "")
            if raw:
                for part in raw.split(","):
                    _, email_addr = parseaddr(part.strip())
                    if email_addr:
                        evidence.add_entity(email_addr, "email_address", {"role": field_name})
                        evidence.add_relationship(sender_email, email_addr, "sent_to")

        # Entity: attachments
        for att in attachments:
            evidence.add_entity(att["filename"], "attachment", {
                "content_type": att["content_type"],
                "size": att["size"],
                "sha256": att["sha256"],
            })
            if sender_email:
                evidence.add_relationship(sender_email, att["filename"], "attached")

        # Entity: IPs from headers
        for ip in headers.get("ip_addresses", []):
            evidence.add_entity(ip, "ip_address", {"source": "email_header"})
            evidence.add_relationship(sender_email, ip, "originated_from")

        # Relationship: thread
        in_reply_to = headers.get("in_reply_to", "")
        if in_reply_to:
            evidence.add_relationship(message_id, in_reply_to, "reply_to")

        for ref in headers.get("references", ""):
            ref_clean = ref.strip()
            if ref_clean:
                evidence.add_relationship(message_id, ref_clean, "references")

        # IOCs
        iocs_found: List[Dict[str, Any]] = []
        if spf_result and spf_result not in ("pass", "none"):
            iocs_found.append(IOC(IOCType.EMAIL, sender_email, f"SPF {spf_result}", 0.7).to_dict())
        if dkim_result and dkim_result not in ("pass", "none"):
            iocs_found.append(IOC(IOCType.EMAIL, sender_email, f"DKIM {dkim_result}", 0.7).to_dict())
        if dmarc_result and dmarc_result not in ("pass", "none"):
            iocs_found.append(IOC(IOCType.EMAIL, sender_email, f"DMARC {dmarc_result}", 0.7).to_dict())

        for ind in suspicious:
            if ind["type"] == "lookalike_domain":
                iocs_found.append(IOC(IOCType.DOMAIN, headers.get("sender_domain", ""), "lookalike domain", 0.9).to_dict())
            elif ind["type"] == "suspicious_attachment":
                fname = ind["detail"].split(": ")[-1].split(" ")[0] if ": " in ind["detail"] else ""
                if fname:
                    iocs_found.append(IOC(IOCType.FILE_PATH, fname, "suspicious attachment", 0.9).to_dict())

        # IP-based IOCs from hop analysis
        for hop in hops:
            if hop.get("from_ip"):
                iocs_found.append(IOC(IOCType.IP_ADDRESS, hop["from_ip"], "email relay hop", 0.6).to_dict())

        # URL-based IOCs in body
        if body:
            url_pattern = re.compile(r"https?://[^\s<>\"']+")
            for url_match in url_pattern.finditer(body):
                url = url_match.group(0).rstrip(".,;:)")
                if re.match(r"https?://\d+\.\d+\.\d+\.\d+", url):
                    iocs_found.append(IOC(IOCType.URL, url, "IP-based URL in email body", 0.8).to_dict())
                    indicators_for_url = next((s for s in suspicious if s["type"] == "ip_url"), None)
                    if not indicators_for_url:
                        suspicious.append({
                            "type": "ip_url",
                            "detail": f"URL uses IP address instead of domain: {url}",
                            "risk_level": RiskLevel.MEDIUM.value,
                        })

            shortener_pattern = re.compile(
                r"https?://(?:bit\.ly|tinyurl\.com|t\.co|goo\.gl|is\.gd|buff\.ly|ow\.ly|cutt\.ly|short\.io)/[^\s<>\"']+"
            )
            for short_match in shortener_pattern.finditer(body):
                short_url = short_match.group(0).rstrip(".,;:)")
                iocs_found.append(IOC(IOCType.URL, short_url, "shortened URL in email body", 0.5).to_dict())
                indicators_for_short = next((s for s in suspicious if s["type"] == "shortened_url"), None)
                if not indicators_for_short:
                    suspicious.append({
                        "type": "shortened_url",
                        "detail": f"Shortened URL detected: {short_url}",
                        "risk_level": RiskLevel.LOW.value,
                    })

        # Findings
        findings: List[Dict[str, Any]] = []
        if suspicious:
            high_risk = [s for s in suspicious if s.get("risk_level") in (RiskLevel.HIGH.value, RiskLevel.CRITICAL.value)]
            if high_risk:
                finding = Finding(
                    title="Suspicious email indicators detected",
                    description=f"{len(high_risk)} high-risk indicators found in email from {sender_email}",
                    risk_level=RiskLevel.HIGH,
                    category="email_forensics",
                    evidence_refs=[evidence.evidence_id],
                    iocs=[IOC(IOCType.EMAIL, sender_email, "suspicious email", 0.8)],
                    recommendation="Review email content and headers manually. Verify sender authenticity.",
                )
                findings.append(finding.to_dict())

        if spf_result and spf_result not in ("pass", "none"):
            findings.append(Finding(
                title=f"SPF validation: {spf_result}",
                description=f"Email from {sender_email} failed SPF check ({spf_result})",
                risk_level=RiskLevel.HIGH,
                category="email_authentication",
            ).to_dict())

        if dkim_result and dkim_result not in ("pass", "none"):
            findings.append(Finding(
                title=f"DKIM validation: {dkim_result}",
                description=f"Email from {sender_email} failed DKIM check ({dkim_result})",
                risk_level=RiskLevel.HIGH,
                category="email_authentication",
            ).to_dict())

        if dmarc_result and dmarc_result not in ("pass", "none"):
            findings.append(Finding(
                title=f"DMARC validation: {dmarc_result}",
                description=f"Email from {sender_email} failed DMARC check ({dmarc_result})",
                risk_level=RiskLevel.HIGH,
                category="email_authentication",
            ).to_dict())

        # Attach results
        result = evidence.processor_results.get(self.name, {})
        result["iocs"] = iocs_found
        result["findings"] = findings
        result["suspicious_indicators"] = suspicious
        result["hops"] = hops
        result["thread"] = thread
        result["attachment_graph"] = attachment_graph
        evidence.processor_results[self.name] = result
