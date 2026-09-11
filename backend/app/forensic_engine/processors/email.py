import logging
from email import policy
from email.parser import BytesParser
from typing import Set

from ..base import BaseProcessor
from ..schemas import EvidenceSchema, EvidenceCategory, ForensicProcessorConfig, ProcessorPriority

logger = logging.getLogger(__name__)


class EmailProcessor(BaseProcessor):
    name = "email"
    description = "Processes email files (.eml, .msg): header parsing, body extraction, attachment listing"
    supported_categories = frozenset({EvidenceCategory.EMAIL})
    priority = ProcessorPriority.TEXT_EXTRACTION

    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        self._parse_email(evidence)
        evidence.add_tag("email")
        return evidence

    def _parse_email(self, evidence: EvidenceSchema) -> None:
        try:
            with open(evidence.storage_path, "rb") as f:
                msg = BytesParser(policy=policy.default).parse(f)
            evidence.metadata["email_subject"] = msg.get("subject")
            evidence.metadata["email_from"] = msg.get("from")
            evidence.metadata["email_to"] = msg.get("to")
            evidence.metadata["email_cc"] = msg.get("cc")
            evidence.metadata["email_date"] = msg.get("date")
            evidence.metadata["email_message_id"] = msg.get("message-id")
            if msg.get("date"):
                evidence.add_timeline_event(
                    str(msg["date"]),
                    f"Email from {msg.get('from', 'unknown')} to {msg.get('to', 'unknown')}: {msg.get('subject', '')}",
                    self.name,
                )
            body = ""
            body_part = msg.get_body(preferencelist=("plain", "html"))
            if body_part:
                body = body_part.get_content() or ""
            evidence.extracted_text = body
            attachments = []
            for part in msg.iter_attachments():
                attachments.append({
                    "filename": part.get_filename(),
                    "content_type": part.get_content_type(),
                    "size": len(part.get_payload(decode=True) or b""),
                })
            evidence.metadata["email_attachments"] = attachments
            evidence.metadata["attachment_count"] = len(attachments)
        except Exception as e:
            evidence.add_error(self.name, f"Email parsing failed: {e}")
