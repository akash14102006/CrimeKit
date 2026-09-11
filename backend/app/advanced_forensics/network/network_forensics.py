"""Network Forensics Processor – PCAP parsing, DNS/HTTP extraction, session reconstruction, threat detection.

Uses raw struct parsing for PCAP/PCAPNG files (no scapy dependency), with optional tshark fallback.
"""
import hashlib
import math
import os
import re
import shutil
import struct
import subprocess
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from ...forensic_engine.base import BaseProcessor
from ...forensic_engine.schemas import EvidenceSchema, EvidenceCategory, ForensicProcessorConfig, ProcessorPriority

logger = __import__("logging").getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_LINKTYPE_ETHERNET = 1
_LINKTYPE_LINUX_SLL = 113
_LINKTYPE_RAW_IP = 101
_ETHERTYPE_IP = 0x0800
_ETHERTYPE_IPV6 = 0x86DD
_ETHERTYPE_8021Q = 0x8100
_IPPROTO_TCP = 6
_IPPROTO_UDP = 17
_IPPROTO_ICMP = 1
_DNS_PORT = 53
_HTTP_PORTS = {80, 8080, 8000, 8888, 3000, 5000}
_HTTPS_PORT = 443

_TSHARK_MIN_VERSION = "3.0.0"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ip_to_str(addr_bytes: bytes) -> str:
    return ".".join(str(b) for b in addr_bytes)


def _ipv6_to_str(addr_bytes: bytes) -> str:
    parts = []
    for i in range(0, 16, 2):
        parts.append(f"{addr_bytes[i]:02x}{addr_bytes[i+1]:02x}")
    return ":".join(parts)


def _mac_to_str(b: bytes) -> str:
    return ":".join(f"{x:02x}" for x in b)


def _ts_to_iso(sec: int, usec: int) -> str:
    try:
        dt = datetime.fromtimestamp(sec + usec / 1_000_000, tz=timezone.utc)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    except (OSError, ValueError):
        return f"{sec}.{usec:06d}"


def _dns_name_decode(data: bytes, offset: int) -> Tuple[str, int]:
    """Decode a DNS name handling compression pointers."""
    parts: list[str] = []
    jumped = False
    original_offset = offset
    max_jumps = 50
    jumps = 0
    while offset < len(data):
        length = data[offset]
        if length == 0:
            offset += 1
            break
        if (length & 0xC0) == 0xC0:
            if not jumped:
                original_offset = offset + 2
            pointer = struct.unpack("!H", data[offset:offset+2])[0] & 0x3FFF
            offset = pointer
            jumped = True
            jumps += 1
            if jumps > max_jumps:
                break
            continue
        offset += 1
        if offset + length > len(data):
            break
        parts.append(data[offset:offset+length].decode("ascii", errors="replace"))
        offset += length
    name = ".".join(parts)
    return name, original_offset if jumped else offset


def _domain_entropy(domain: str) -> float:
    """Shannon entropy of the domain string."""
    if not domain:
        return 0.0
    freq = Counter(domain)
    length = len(domain)
    return -sum((c / length) * math.log2(c / length) for c in freq.values())


def _is_dga_candidate(domain: str) -> bool:
    """Heuristic: long subdomain label with high entropy."""
    labels = domain.split(".")
    if not labels:
        return False
    label = labels[0]
    if len(label) > 20 and _domain_entropy(label) > 3.5:
        return True
    return False


def _tshark_available() -> bool:
    return shutil.which("tshark") is not None


def _run_tshark(pcap_path: str, display_filter: str, fields: List[str], limit: int = 0) -> List[Dict[str, str]]:
    """Run tshark and return parsed output as list of dicts."""
    if not _tshark_available():
        return []
    field_args = ["-T", "fields"]
    for f in fields:
        field_args += ["-e", f]
    cmd = ["tshark", "-r", pcap_path, "-Y", display_filter] + field_args
    if limit > 0:
        cmd += ["-c", str(limit)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            logger.warning("tshark returned %d: %s", result.returncode, result.stderr[:500])
            return []
        rows = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            values = line.split("\t")
            row = {}
            for i, f in enumerate(fields):
                row[f] = values[i] if i < len(values) else ""
            rows.append(row)
        return rows
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


# ---------------------------------------------------------------------------
# PCAP Struct Parser
# ---------------------------------------------------------------------------

class _PacketInfo:
    """Lightweight packet container."""
    __slots__ = (
        "timestamp_sec", "timestamp_usec", "captured_len", "original_len",
        "src_mac", "dst_mac", "ethertype",
        "src_ip", "dst_ip", "ip_version", "ip_proto", "ttl",
        "src_port", "dst_port",
        "tcp_flags", "tcp_seq", "tcp_ack", "tcp_window",
        "payload", "raw_ethernet",
    )

    def __init__(self) -> None:
        self.timestamp_sec: int = 0
        self.timestamp_usec: int = 0
        self.captured_len: int = 0
        self.original_len: int = 0
        self.src_mac: str = ""
        self.dst_mac: str = ""
        self.ethertype: int = 0
        self.src_ip: str = ""
        self.dst_ip: str = ""
        self.ip_version: int = 4
        self.ip_proto: int = 0
        self.ttl: int = 0
        self.src_port: int = 0
        self.dst_port: int = 0
        self.tcp_flags: int = 0
        self.tcp_seq: int = 0
        self.tcp_ack: int = 0
        self.tcp_window: int = 0
        self.payload: bytes = b""
        self.raw_ethernet: bytes = b""

    @property
    def is_tcp(self) -> bool:
        return self.ip_proto == _IPPROTO_TCP

    @property
    def is_udp(self) -> bool:
        return self.ip_proto == _IPPROTO_UDP

    @property
    def timestamp_iso(self) -> str:
        return _ts_to_iso(self.timestamp_sec, self.timestamp_usec)

    @property
    def tcp_flag_str(self) -> str:
        flags = []
        if self.tcp_flags & 0x01:
            flags.append("FIN")
        if self.tcp_flags & 0x02:
            flags.append("SYN")
        if self.tcp_flags & 0x04:
            flags.append("RST")
        if self.tcp_flags & 0x08:
            flags.append("PSH")
        if self.tcp_flags & 0x10:
            flags.append("ACK")
        if self.tcp_flags & 0x20:
            flags.append("URG")
        return ",".join(flags)


class _PcapParser:
    """Parse a PCAP or PCAPNG file using struct (no external dependencies)."""

    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.packets: List[_PacketInfo] = []
        self.link_type: int = 0
        self.snaplen: int = 0
        self.version_major: int = 0
        self.version_minor: int = 0
        self.is_little_endian: bool = True
        self.is_pcapng: bool = False

    def parse(self) -> bool:
        try:
            with open(self.file_path, "rb") as f:
                magic = f.read(4)
                if len(magic) < 4:
                    return False
                if magic == b"\xd4\xc3\xb2\xa1":
                    return self._parse_pcap(f, little_endian=True)
                elif magic == b"\xa1\xb2\xc3\xd4":
                    return self._parse_pcap(f, little_endian=False)
                elif magic == b"\x0a\x0d\x0d\x0a":
                    self.is_pcapng = True
                    return self._parse_pcapng(f)
                else:
                    logger.warning("Unrecognized file magic: %s", magic.hex())
                    return False
        except (OSError, struct.error) as e:
            logger.error("Failed to parse PCAP file %s: %s", self.file_path, e)
            return False

    # -- PCAP v2.4 ----------------------------------------------------------

    def _parse_pcap(self, f, little_endian: bool) -> bool:
        self.is_little_endian = little_endian
        endian = "<" if little_endian else ">"
        header = f.read(20)
        if len(header) < 20:
            return False
        (
            _magic, self.version_major, self.version_minor,
            _tz, _sigfigs, self.snaplen, self.link_type,
        ) = struct.unpack(endian + "HHiIII", header)

        data = f.read()
        offset = 0
        while offset + 16 <= len(data):
            pkt_header = data[offset:offset+16]
            if len(pkt_header) < 16:
                break
            ts_sec, ts_usec, incl_len, orig_len = struct.unpack(
                endian + "IIII", pkt_header,
            )
            offset += 16
            if incl_len > len(data) - offset:
                break
            pkt_data = data[offset:offset+incl_len]
            offset += incl_len
            pkt = _PacketInfo()
            pkt.timestamp_sec = ts_sec
            pkt.timestamp_usec = ts_usec
            pkt.captured_len = incl_len
            pkt.original_len = orig_len
            self._parse_link_layer(pkt, pkt_data)
            self.packets.append(pkt)
        return len(self.packets) > 0

    # -- PCAPNG -------------------------------------------------------------

    def _parse_pcapng(self, f) -> bool:
        data = f.read()
        offset = 0
        section_byte_order = ">"  # default big-endian
        self.link_type = 0
        self.snaplen = 65535
        self.is_little_endian = False

        while offset + 8 <= len(data):
            block_type = struct.unpack(">I", data[offset:offset+4])[0]
            block_len = struct.unpack(">I", data[offset+4:offset+8])[0]
            if block_len < 12 or offset + block_len > len(data):
                break
            body = data[offset+8:offset+block_len-4]

            if block_type == 0x00000001:  # Section Header
                byte_order_magic = body[0:4]
                if byte_order_magic == b"\x1a\x2b\x3c\x4d":
                    section_byte_order = ">"
                    self.is_little_endian = False
                elif byte_order_magic == b"\x4d\x3c\x2b\x1a":
                    section_byte_order = "<"
                    self.is_little_endian = True
                else:
                    break

            elif block_type == 0x00000006:  # Interface Description
                if len(body) >= 4:
                    self.link_type = struct.unpack(section_byte_order + "H", body[0:2])[0]
                    if len(body) >= 8:
                        self.snaplen = struct.unpack(section_byte_order + "I", body[4:8])[0]

            elif block_type == 0x00000006 or block_type == 0x00000001:
                pass  # already handled

            elif block_type == 0x00000003:  # Enhanced Packet Block
                if len(body) >= 20:
                    _epb_interface_id = struct.unpack(section_byte_order + "I", body[0:4])[0]
                    ts_high = struct.unpack(section_byte_order + "I", body[4:8])[0]
                    ts_low = struct.unpack(section_byte_order + "I", body[8:12])[0]
                    incl_len = struct.unpack(section_byte_order + "I", body[12:16])[0]
                    orig_len = struct.unpack(section_byte_order + "I", body[16:20])[0]
                    pkt_data = body[20:20+incl_len]

                    # Use interface-defined link type
                    ts_sec = ts_high
                    ts_usec = ts_low

                    pkt = _PacketInfo()
                    pkt.timestamp_sec = ts_sec
                    pkt.timestamp_usec = ts_usec
                    pkt.captured_len = incl_len
                    pkt.original_len = orig_len
                    self._parse_link_layer(pkt, pkt_data)
                    self.packets.append(pkt)

            offset += block_len
            # Align to 4 bytes
            offset = (offset + 3) & ~3

        return len(self.packets) > 0

    # -- Link-layer dispatch ------------------------------------------------

    def _parse_link_layer(self, pkt: _PacketInfo, data: bytes) -> None:
        if self.link_type == _LINKTYPE_ETHERNET:
            self._parse_ethernet(pkt, data)
        elif self.link_type == _LINKTYPE_LINUX_SLL:
            if len(data) >= 16:
                pkt.ethertype = struct.unpack("!H", data[14:16])[0]
                self._parse_ip_layer(pkt, data[16:])
        elif self.link_type == _LINKTYPE_RAW_IP:
            self._parse_ip_layer(pkt, data)
        else:
            # Try Ethernet as default
            self._parse_ethernet(pkt, data)

    def _parse_ethernet(self, pkt: _PacketInfo, data: bytes) -> None:
        if len(data) < 14:
            return
        pkt.dst_mac = _mac_to_str(data[0:6])
        pkt.src_mac = _mac_to_str(data[6:12])
        ethertype = struct.unpack("!H", data[12:14])[0]
        offset = 14

        # VLAN tag
        if ethertype == _ETHERTYPE_8021Q:
            if len(data) >= 18:
                ethertype = struct.unpack("!H", data[16:18])[0]
                offset = 18

        pkt.ethertype = ethertype
        if ethertype == _ETHERTYPE_IP:
            self._parse_ip_layer(pkt, data[offset:])
        elif ethertype == _ETHERTYPE_IPV6:
            self._parse_ipv6_layer(pkt, data[offset:])

    def _parse_ip_layer(self, pkt: _PacketInfo, data: bytes) -> None:
        if len(data) < 20:
            return
        version_ihl = data[0]
        version = (version_ihl >> 4) & 0x0F
        ihl = (version_ihl & 0x0F) * 4
        if version == 4:
            pkt.ip_version = 4
            if len(data) < 20:
                return
            total_len = struct.unpack("!H", data[2:4])[0]
            pkt.ttl = data[8]
            pkt.ip_proto = data[9]
            pkt.src_ip = _ip_to_str(data[12:16])
            pkt.dst_ip = _ip_to_str(data[16:20])
            self._parse_transport(pkt, data[ihl:])
        elif version == 6:
            self._parse_ipv6_layer(pkt, data)

    def _parse_ipv6_layer(self, pkt: _PacketInfo, data: bytes) -> None:
        if len(data) < 40:
            return
        pkt.ip_version = 6
        pkt.ip_proto = data[6]
        pkt.ttl = data[7]  # hop limit
        pkt.src_ip = _ipv6_to_str(data[8:24])
        pkt.dst_ip = _ipv6_to_str(data[24:40])
        self._parse_transport(pkt, data[40:])

    def _parse_transport(self, pkt: _PacketInfo, data: bytes) -> None:
        if pkt.ip_proto == _IPPROTO_TCP and len(data) >= 20:
            pkt.src_port = struct.unpack("!H", data[0:2])[0]
            pkt.dst_port = struct.unpack("!H", data[2:4])[0]
            pkt.tcp_seq = struct.unpack("!I", data[4:8])[0]
            pkt.tcp_ack = struct.unpack("!I", data[8:12])[0]
            data_offset = ((data[12] >> 4) & 0x0F) * 4
            pkt.tcp_flags = data[13]
            pkt.tcp_window = struct.unpack("!H", data[14:16])[0]
            pkt.payload = data[data_offset:] if data_offset < len(data) else b""
        elif pkt.ip_proto == _IPPROTO_UDP and len(data) >= 8:
            pkt.src_port = struct.unpack("!H", data[0:2])[0]
            pkt.dst_port = struct.unpack("!H", data[2:4])[0]
            pkt.payload = data[8:]
        elif pkt.ip_proto == _IPPROTO_ICMP and len(data) >= 4:
            pkt.payload = data


# ---------------------------------------------------------------------------
# DNS Parser
# ---------------------------------------------------------------------------

_DNS_TYPE_MAP = {
    1: "A", 2: "NS", 5: "CNAME", 6: "SOA", 12: "PTR",
    15: "MX", 16: "TXT", 28: "AAAA", 33: "SRV", 41: "TKEY",
    43: "DS", 46: "RRSIG", 48: "DNSKEY", 255: "ANY", 256: "URI",
    257: "CAA", 65: "HTTPS",
}


def _parse_dns_message(data: bytes) -> Optional[Dict[str, Any]]:
    """Parse a DNS message into a structured dict."""
    if len(data) < 12:
        return None
    tx_id = struct.unpack("!H", data[0:2])[0]
    flags = struct.unpack("!H", data[2:4])[0]
    qdcount = struct.unpack("!H", data[4:6])[0]
    ancount = struct.unpack("!H", data[6:8])[0]
    nscount = struct.unpack("!H", data[8:10])[0]
    arcount = struct.unpack("!H", data[10:12])[0]

    is_response = bool(flags & 0x8000)
    opcode = (flags >> 11) & 0xF
    rcode = flags & 0x0F

    questions = []
    answers = []
    offset = 12

    # Questions
    for _ in range(qdcount):
        qname, offset = _dns_name_decode(data, offset)
        if offset + 4 > len(data):
            break
        qtype = struct.unpack("!H", data[offset:offset+2])[0]
        qclass = struct.unpack("!H", data[offset+2:offset+4])[0]
        offset += 4
        questions.append({
            "name": qname,
            "type": _DNS_TYPE_MAP.get(qtype, str(qtype)),
            "type_code": qtype,
            "class": qclass,
        })

    # Answers + authority + additional
    for _ in range(ancount + nscount + arcount):
        if offset >= len(data):
            break
        name, offset = _dns_name_decode(data, offset)
        if offset + 10 > len(data):
            break
        rtype = struct.unpack("!H", data[offset:offset+2])[0]
        rclass = struct.unpack("!H", data[offset+2:offset+4])[0]
        ttl = struct.unpack("!I", data[offset+4:offset+8])[0]
        rdlength = struct.unpack("!H", data[offset+8:offset+10])[0]
        offset += 10
        rdata_raw = data[offset:offset+rdlength]
        offset += rdlength

        rdata_str = ""
        if rtype == 1 and rdlength == 4:
            rdata_str = _ip_to_str(rdata_raw)
        elif rtype == 28 and rdlength == 16:
            rdata_str = _ipv6_to_str(rdata_raw)
        elif rtype in (5, 2, 12, 39):  # CNAME, NS, PTR, DNAME
            rdata_str, _ = _dns_name_decode(data, offset - rdlength)
        elif rtype == 15:  # MX
            if rdlength >= 3:
                preference = struct.unpack("!H", rdata_raw[0:2])[0]
                exchange, _ = _dns_name_decode(data, offset - rdlength + 2)
                rdata_str = f"{preference} {exchange}"
        elif rtype == 16:  # TXT
            rdata_str = rdata_raw[1:1+rdata_raw[0]].decode("utf-8", errors="replace") if rdlength > 0 else ""
        else:
            rdata_str = rdata_raw.hex()

        answers.append({
            "name": name,
            "type": _DNS_TYPE_MAP.get(rtype, str(rtype)),
            "type_code": rtype,
            "class": rclass,
            "ttl": ttl,
            "rdata": rdata_str,
        })

    return {
        "tx_id": tx_id,
        "is_response": is_response,
        "opcode": opcode,
        "rcode": rcode,
        "questions": questions,
        "answers": answers,
    }


# ---------------------------------------------------------------------------
# HTTP Parser
# ---------------------------------------------------------------------------

def _parse_http_message(data: bytes) -> Optional[Dict[str, Any]]:
    """Parse raw HTTP request or response bytes."""
    try:
        text = data.decode("utf-8", errors="replace")
    except Exception:
        return None

    parts = text.split("\r\n\r\n", 1)
    header_section = parts[0]
    body = parts[1] if len(parts) > 1 else ""
    lines = header_section.split("\r\n")
    if not lines:
        return None

    first_line = lines[0]
    headers: Dict[str, str] = {}
    for line in lines[1:]:
        if ":" in line:
            key, val = line.split(":", 1)
            headers[key.strip()] = val.strip()

    # Request
    req_match = re.match(r"^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS|CONNECT|TRACE)\s+(\S+)\s+HTTP/[\d.]+", first_line)
    if req_match:
        return {
            "type": "request",
            "method": req_match.group(1),
            "uri": req_match.group(2),
            "headers": headers,
            "body": body,
        }

    # Response
    resp_match = re.match(r"^HTTP/[\d.]+\s+(\d{3})", first_line)
    if resp_match:
        return {
            "type": "response",
            "status_code": int(resp_match.group(1)),
            "headers": headers,
            "body": body,
        }

    return None


# ---------------------------------------------------------------------------
# Main Processor
# ---------------------------------------------------------------------------

class NetworkForensicsProcessor(BaseProcessor):
    name = "network_forensics"
    description = (
        "Analyzes network captures: PCAP parsing, DNS analysis, HTTP extraction, "
        "session reconstruction, protocol analysis, host profiling, threat detection"
    )
    supported_categories = frozenset({EvidenceCategory.NETWORK_CAPTURE, EvidenceCategory.UNKNOWN})
    priority = ProcessorPriority.DEEP_ANALYSIS

    def process(self, evidence: EvidenceSchema, config: ForensicProcessorConfig) -> EvidenceSchema:
        ext = self._get_file_extension(evidence)
        if ext not in ("pcap", "pcapng", "cap", "net"):
            if not _tshark_available():
                evidence.add_error(self.name, f"Unsupported file extension '.{ext}' and tshark not available")
                return evidence

        packets = self._parse_pcap_file(evidence)
        if not packets:
            evidence.add_error(self.name, "Failed to parse PCAP/PCAPNG file – file may be corrupted or empty")
            return evidence

        evidence.metadata["pcap_total_packets"] = len(packets)
        evidence.add_tag("network_capture")

        # Build timeline
        self._build_timeline(evidence, packets)

        # Run all extraction phases
        dns_results = self._extract_dns_queries(evidence, packets)
        http_results = self._extract_http_requests(evidence, packets)
        sessions = self._extract_sessions(evidence, packets)
        hosts = self._build_host_profiles(evidence, packets)
        proto_stats = self._analyze_protocols(evidence, packets)
        connections = self._generate_connections_list(evidence, packets)
        threats = self._detect_threats(evidence, packets, dns_results, sessions, hosts)

        # Merge tshark results if available
        if _tshark_available():
            self._enrich_with_tshark(evidence)

        # Compile final result
        result = {
            "total_packets": len(packets),
            "link_type": evidence.metadata.get("pcap_link_type"),
            "dns_queries": len(dns_results),
            "http_requests": len(http_results),
            "tcp_sessions": len(sessions),
            "unique_hosts": len(hosts),
            "connections": len(connections),
            "threat_indicators": len(threats),
            "protocol_distribution": proto_stats,
        }
        evidence.add_result(self.name, result)
        evidence.add_tag("pcap_analyzed")

        return evidence

    # -----------------------------------------------------------------------
    # 1. PCAP File Parsing
    # -----------------------------------------------------------------------

    def _parse_pcap_file(self, evidence: EvidenceSchema) -> Optional[List[_PacketInfo]]:
        """Parse PCAP/PCAPNG files using struct.

        Reads global header (magic number, version, snaplen, link type),
        parses packet headers (timestamp, captured/original length),
        decodes Ethernet frames, IP headers, TCP/UDP headers,
        and extracts payloads for application-layer analysis.
        Handles both little-endian and big-endian formats.
        Returns list of parsed packets or None on failure.
        """
        file_path = evidence.storage_path
        try:
            with open(file_path, "rb") as f:
                magic = f.read(4)
                if len(magic) < 4:
                    evidence.add_error(self.name, "File too small for PCAP header")
                    return None

                # Determine format
                if magic == b"\xd4\xc3\xb2\xa1":
                    little_endian = True
                elif magic == b"\xa1\xb2\xc3\xd4":
                    little_endian = False
                elif magic == b"\x0a\x0d\x0d\x0a":
                    return self._parse_pcapng_file(f, evidence)
                else:
                    evidence.add_error(
                        self.name,
                        f"Unrecognized magic bytes: {magic.hex()} – not a valid PCAP/PCAPNG file",
                    )
                    return None

                # Parse PCAP v2.4 global header
                endian = "<" if little_endian else ">"
                header = f.read(20)
                if len(header) < 20:
                    evidence.add_error(self.name, "Incomplete PCAP global header")
                    return None

                (
                    version_major, version_minor,
                    _tz, _sigfigs, snaplen, link_type,
                ) = struct.unpack(endian + "HHiIII", header)

                evidence.metadata["pcap_version"] = f"{version_major}.{version_minor}"
                evidence.metadata["pcap_snaplen"] = snaplen
                evidence.metadata["pcap_link_type"] = link_type
                evidence.metadata["pcap_endian"] = "little" if little_endian else "big"

                packets: List[_PacketInfo] = []
                data = f.read()
                offset = 0

                while offset + 16 <= len(data):
                    pkt_header = data[offset:offset+16]
                    if len(pkt_header) < 16:
                        break
                    ts_sec, ts_usec, incl_len, orig_len = struct.unpack(
                        endian + "IIII", pkt_header,
                    )
                    offset += 16
                    if incl_len > len(data) - offset or incl_len > snaplen * 4:
                        # Corrupted/truncated packet – skip rest
                        break
                    pkt_data = data[offset:offset+incl_len]
                    offset += incl_len

                    pkt = _PacketInfo()
                    pkt.timestamp_sec = ts_sec
                    pkt.timestamp_usec = ts_usec
                    pkt.captured_len = incl_len
                    pkt.original_len = orig_len
                    self._decode_link_layer(pkt, pkt_data, link_type)
                    packets.append(pkt)

                return packets if packets else None

        except (OSError, struct.error) as e:
            evidence.add_error(self.name, f"PCAP parsing failed: {e}")
            return None

    def _parse_pcapng_file(self, f, evidence: EvidenceSchema) -> Optional[List[_PacketInfo]]:
        """Parse PCAPNG file format."""
        data = f.read()
        offset = 0
        section_byte_order = ">"
        link_type = 0
        snaplen = 65535
        packets: List[_PacketInfo] = []

        while offset + 8 <= len(data):
            block_type = struct.unpack(">I", data[offset:offset+4])[0]
            block_len = struct.unpack(">I", data[offset+4:offset+8])[0]
            if block_len < 12 or offset + block_len > len(data):
                break
            body = data[offset+8:offset+block_len-4]

            if block_type == 0x00000001:  # Section Header
                bom = body[0:4]
                if bom == b"\x1a\x2b\x3c\x4d":
                    section_byte_order = ">"
                elif bom == b"\x4d\x3c\x2b\x1a":
                    section_byte_order = "<"
                else:
                    break

            elif block_type == 0x00000001:  # Interface Description
                if len(body) >= 4:
                    link_type = struct.unpack(section_byte_order + "H", body[0:2])[0]
                    if len(body) >= 8:
                        snaplen = struct.unpack(section_byte_order + "I", body[4:8])[0]

            elif block_type == 0x00000006:  # Enhanced Packet Block
                if len(body) >= 20:
                    _epb_interface_id = struct.unpack(section_byte_order + "I", body[0:4])[0]
                    ts_high = struct.unpack(section_byte_order + "I", body[4:8])[0]
                    ts_low = struct.unpack(section_byte_order + "I", body[8:12])[0]
                    incl_len = struct.unpack(section_byte_order + "I", body[12:16])[0]
                    orig_len = struct.unpack(section_byte_order + "I", body[16:20])[0]
                    pkt_data = body[20:20+incl_len]

                    pkt = _PacketInfo()
                    pkt.timestamp_sec = ts_high
                    pkt.timestamp_usec = ts_low
                    pkt.captured_len = incl_len
                    pkt.original_len = orig_len
                    self._decode_link_layer(pkt, pkt_data, link_type)
                    packets.append(pkt)

            offset += block_len
            offset = (offset + 3) & ~3  # align to 4 bytes

        if not packets:
            return None

        evidence.metadata["pcap_is_pcapng"] = True
        evidence.metadata["pcap_link_type"] = link_type
        evidence.metadata["pcap_snaplen"] = snaplen
        return packets

    def _decode_link_layer(self, pkt: _PacketInfo, data: bytes, link_type: int) -> None:
        """Dispatch to the correct link-layer decoder."""
        if link_type == _LINKTYPE_ETHERNET:
            self._decode_ethernet(pkt, data)
        elif link_type == _LINKTYPE_LINUX_SLL:
            if len(data) >= 16:
                pkt.ethertype = struct.unpack("!H", data[14:16])[0]
                self._decode_ip_layer(pkt, data[16:])
        elif link_type == _LINKTYPE_RAW_IP:
            self._decode_ip_layer(pkt, data)
        else:
            self._decode_ethernet(pkt, data)

    def _decode_ethernet(self, pkt: _PacketInfo, data: bytes) -> None:
        if len(data) < 14:
            return
        pkt.dst_mac = _mac_to_str(data[0:6])
        pkt.src_mac = _mac_to_str(data[6:12])
        ethertype = struct.unpack("!H", data[12:14])[0]
        offset = 14
        if ethertype == _ETHERTYPE_8021Q and len(data) >= 18:
            ethertype = struct.unpack("!H", data[16:18])[0]
            offset = 18
        pkt.ethertype = ethertype
        if ethertype == _ETHERTYPE_IP:
            self._decode_ip_layer(pkt, data[offset:])
        elif ethertype == _ETHERTYPE_IPV6:
            self._decode_ipv6_layer(pkt, data[offset:])

    def _decode_ip_layer(self, pkt: _PacketInfo, data: bytes) -> None:
        if len(data) < 20:
            return
        version_ihl = data[0]
        version = (version_ihl >> 4) & 0x0F
        ihl = (version_ihl & 0x0F) * 4
        if version == 4:
            pkt.ip_version = 4
            pkt.ttl = data[8]
            pkt.ip_proto = data[9]
            pkt.src_ip = _ip_to_str(data[12:16])
            pkt.dst_ip = _ip_to_str(data[16:20])
            self._decode_transport(pkt, data[ihl:])
        elif version == 6:
            self._decode_ipv6_layer(pkt, data)

    def _decode_ipv6_layer(self, pkt: _PacketInfo, data: bytes) -> None:
        if len(data) < 40:
            return
        pkt.ip_version = 6
        pkt.ip_proto = data[6]
        pkt.ttl = data[7]
        pkt.src_ip = _ipv6_to_str(data[8:24])
        pkt.dst_ip = _ipv6_to_str(data[24:40])
        self._decode_transport(pkt, data[40:])

    def _decode_transport(self, pkt: _PacketInfo, data: bytes) -> None:
        if pkt.ip_proto == _IPPROTO_TCP and len(data) >= 20:
            pkt.src_port = struct.unpack("!H", data[0:2])[0]
            pkt.dst_port = struct.unpack("!H", data[2:4])[0]
            pkt.tcp_seq = struct.unpack("!I", data[4:8])[0]
            pkt.tcp_ack = struct.unpack("!I", data[8:12])[0]
            data_offset = ((data[12] >> 4) & 0x0F) * 4
            pkt.tcp_flags = data[13]
            pkt.tcp_window = struct.unpack("!H", data[14:16])[0]
            pkt.payload = data[data_offset:] if data_offset < len(data) else b""
        elif pkt.ip_proto == _IPPROTO_UDP and len(data) >= 8:
            pkt.src_port = struct.unpack("!H", data[0:2])[0]
            pkt.dst_port = struct.unpack("!H", data[2:4])[0]
            pkt.payload = data[8:]
        elif pkt.ip_proto == _IPPROTO_ICMP and len(data) >= 4:
            pkt.payload = data

    # -----------------------------------------------------------------------
    # 2. Timeline
    # -----------------------------------------------------------------------

    def _build_timeline(self, evidence: EvidenceSchema, packets: List[_PacketInfo]) -> None:
        if not packets:
            return
        first_ts = packets[0].timestamp_iso
        last_ts = packets[-1].timestamp_iso
        duration_s = packets[-1].timestamp_sec - packets[0].timestamp_sec
        evidence.add_timeline_event(first_ts, "PCAP capture started", self.name)
        evidence.add_timeline_event(last_ts, "PCAP capture ended", self.name)
        evidence.add_timeline_event(
            first_ts,
            f"Capture duration: {duration_s}s, {len(packets)} packets",
            self.name,
        )

    # -----------------------------------------------------------------------
    # 2. DNS Extraction
    # -----------------------------------------------------------------------

    def _extract_dns_queries(
        self, evidence: EvidenceSchema, packets: List[_PacketInfo]
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        seen_domains: Set[str] = set()
        resolution_graph: Dict[str, List[str]] = defaultdict(list)

        for pkt in packets:
            if not (pkt.is_udp and pkt.dst_port == _DNS_PORT or pkt.is_tcp and pkt.dst_port == _DNS_PORT):
                # Also check source port for responses
                if not (pkt.is_udp and pkt.src_port == _DNS_PORT or pkt.is_tcp and pkt.src_port == _DNS_PORT):
                    continue

            dns = _parse_dns_message(pkt.payload)
            if dns is None:
                continue

            for q in dns["questions"]:
                domain = q["name"]
                qtype = q["type"]
                entry = {
                    "domain": domain,
                    "query_type": qtype,
                    "is_response": dns["is_response"],
                    "timestamp": pkt.timestamp_iso,
                    "src_ip": pkt.src_ip,
                    "dst_ip": pkt.dst_ip,
                    "tx_id": dns["tx_id"],
                    "answers": [],
                }

                if dns["is_response"]:
                    for a in dns["answers"]:
                        if a["type_code"] == q["type_code"]:
                            entry["answers"].append(a["rdata"])
                            resolution_graph[domain].append(a["rdata"])

                results.append(entry)

                # Timeline event
                answer_str = ", ".join(entry["answers"]) if entry["answers"] else "no answer"
                evidence.add_timeline_event(
                    pkt.timestamp_iso,
                    f"DNS {'response' if dns['is_response'] else 'query'}: {domain} ({qtype}) -> {answer_str}",
                    self.name,
                )

                # Entity
                if domain not in seen_domains:
                    seen_domains.add(domain)
                    evidence.add_entity(domain, "domain", {
                        "query_type": qtype,
                        "first_seen": pkt.timestamp_iso,
                    })

                # IOC for high-entropy / DGA
                if _is_dga_candidate(domain):
                    evidence.add_tag("suspicious_dns_dga")
                    from ...forensic_engine.schemas import EvidenceSchema as _  # noqa: ensure available
                    evidence.processor_results.setdefault("dns_iocs", []).append({
                        "domain": domain,
                        "reason": "dga_candidate",
                        "entropy": round(_domain_entropy(domain), 3),
                        "timestamp": pkt.timestamp_iso,
                    })

        # Store DNS results
        evidence.processor_results["dns_queries"] = results
        evidence.processor_results["dns_resolution_graph"] = dict(resolution_graph)

        # Tag unique domains
        for domain in seen_domains:
            evidence.add_entity(domain, "domain")
            for resolved_ip in resolution_graph.get(domain, []):
                if re.match(r"^\d+\.\d+\.\d+\.\d+$", resolved_ip):
                    evidence.add_relationship(domain, resolved_ip, "resolves_to")

        return results

    # -----------------------------------------------------------------------
    # 3. HTTP Extraction
    # -----------------------------------------------------------------------

    def _extract_http_requests(
        self, evidence: EvidenceSchema, packets: List[_PacketInfo]
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        seen_urls: Set[str] = set()

        for pkt in packets:
            if not pkt.payload:
                continue
            if pkt.dst_port not in _HTTP_PORTS:
                continue

            http = _parse_http_message(pkt.payload)
            if http is None:
                continue

            if http["type"] == "request":
                method = http["method"]
                uri = http["uri"]
                host = http["headers"].get("Host", pkt.dst_ip)
                url = f"http://{host}{uri}" if not uri.startswith("http") else uri
                user_agent = http["headers"].get("User-Agent", "")
                content_type = http["headers"].get("Content-Type", "")
                content_length = int(http["headers"].get("Content-Length", "0") or "0")

                entry = {
                    "method": method,
                    "uri": uri,
                    "host": host,
                    "url": url,
                    "user_agent": user_agent,
                    "content_type": content_type,
                    "content_length": content_length,
                    "src_ip": pkt.src_ip,
                    "dst_ip": pkt.dst_ip,
                    "src_port": pkt.src_port,
                    "dst_port": pkt.dst_port,
                    "timestamp": pkt.timestamp_iso,
                }
                results.append(entry)

                evidence.add_timeline_event(
                    pkt.timestamp_iso,
                    f"HTTP {method} {url}",
                    self.name,
                )

                if url not in seen_urls:
                    seen_urls.add(url)
                    evidence.add_entity(url, "url", {
                        "method": method,
                        "host": host,
                        "user_agent": user_agent,
                    })
                    evidence.add_entity(host, "host", {"ip": pkt.dst_ip})
                    evidence.add_relationship(pkt.src_ip, host, "http_request")
                    evidence.add_tag("http_traffic")

                # Suspicious: POST to unusual ports
                if method == "POST" and pkt.dst_port not in _HTTP_PORTS:
                    evidence.add_tag("suspicious_http_post")
                    evidence.processor_results.setdefault("http_iocs", []).append({
                        "url": url,
                        "reason": "post_to_unusual_port",
                        "port": pkt.dst_port,
                        "timestamp": pkt.timestamp_iso,
                    })

            elif http["type"] == "response":
                status = http["status_code"]
                content_type = http["headers"].get("Content-Type", "")
                evidence.add_timeline_event(
                    pkt.timestamp_iso,
                    f"HTTP response {status} from {pkt.dst_ip}:{pkt.dst_port}",
                    self.name,
                )
                # Track large responses
                cl = int(http["headers"].get("Content-Length", "0") or "0")
                if cl > 1_000_000:
                    evidence.add_tag("large_http_response")

        evidence.processor_results["http_requests"] = results
        return results

    # -----------------------------------------------------------------------
    # 4. Session Reconstruction
    # -----------------------------------------------------------------------

    def _extract_sessions(
        self, evidence: EvidenceSchema, packets: List[_PacketInfo]
    ) -> List[Dict[str, Any]]:
        session_map: Dict[Tuple, Dict[str, Any]] = {}

        for pkt in packets:
            if not pkt.is_tcp:
                continue
            key = (
                min(pkt.src_ip, pkt.dst_ip),
                min(pkt.src_port, pkt.dst_port),
                max(pkt.src_ip, pkt.dst_ip),
                max(pkt.src_port, pkt.dst_port),
            )
            if key not in session_map:
                session_map[key] = {
                    "src_ip": key[0],
                    "src_port": key[1],
                    "dst_ip": key[2],
                    "dst_port": key[3],
                    "protocol": "TCP",
                    "start_time": pkt.timestamp_iso,
                    "end_time": pkt.timestamp_iso,
                    "packet_count": 0,
                    "bytes_sent": 0,
                    "bytes_received": 0,
                    "tcp_flags": set(),
                    "payloads": [],
                }

            s = session_map[key]
            s["end_time"] = pkt.timestamp_iso
            s["packet_count"] += 1
            s["tcp_flags"].add(pkt.tcp_flag_str)

            if pkt.src_ip == key[0]:
                s["bytes_sent"] += pkt.original_len
            else:
                s["bytes_received"] += pkt.original_len

            # Keep first few payloads for application-layer analysis
            if pkt.payload and len(s["payloads"]) < 5:
                s["payloads"].append(pkt.payload[:512])

        sessions = list(session_map.values())

        # Calculate duration
        for s in sessions:
            try:
                t1 = datetime.fromisoformat(s["start_time"].replace("Z", "+00:00"))
                t2 = datetime.fromisoformat(s["end_time"].replace("Z", "+00:00"))
                s["duration_seconds"] = (t2 - t1).total_seconds()
            except (ValueError, TypeError):
                s["duration_seconds"] = 0
            s["tcp_flags"] = sorted(s["tcp_flags"])
            del s["payloads"]  # don't store raw bytes in result

        # Add timeline events for interesting sessions
        for s in sessions:
            if s["bytes_sent"] > 500_000 or s["bytes_received"] > 500_000:
                evidence.add_timeline_event(
                    s["start_time"],
                    f"Large session: {s['src_ip']}:{s['src_port']} <-> {s['dst_ip']}:{s['dst_port']} "
                    f"({s['bytes_sent']}B sent, {s['bytes_received']}B recv, {s['duration_seconds']:.1f}s)",
                    self.name,
                )
                evidence.add_relationship(
                    s["src_ip"], s["dst_ip"], "large_session",
                    weight=max(1, s["bytes_sent"] + s["bytes_received"]),
                )

            evidence.add_entity(
                f"{s['src_ip']}:{s['src_port']}->{s['dst_ip']}:{s['dst_port']}",
                "network_session",
                {
                    "src_ip": s["src_ip"],
                    "dst_ip": s["dst_ip"],
                    "dst_port": s["dst_port"],
                    "duration": s["duration_seconds"],
                    "bytes_sent": s["bytes_sent"],
                    "bytes_received": s["bytes_received"],
                },
            )

        evidence.processor_results["sessions"] = sessions
        return sessions

    # -----------------------------------------------------------------------
    # 5. Host Profiling
    # -----------------------------------------------------------------------

    def _build_host_profiles(
        self, evidence: EvidenceSchema, packets: List[_PacketInfo]
    ) -> Dict[str, Dict[str, Any]]:
        hosts: Dict[str, Dict[str, Any]] = {}

        for pkt in packets:
            for ip in (pkt.src_ip, pkt.dst_ip):
                if not ip:
                    continue
                if ip not in hosts:
                    hosts[ip] = {
                        "ip": ip,
                        "first_seen": pkt.timestamp_iso,
                        "last_seen": pkt.timestamp_iso,
                        "ports_used": set(),
                        "bytes_sent": 0,
                        "bytes_received": 0,
                        "ttl_values": [],
                        "tcp_window_sizes": [],
                        "packet_count": 0,
                    }
                h = hosts[ip]
                h["last_seen"] = pkt.timestamp_iso
                h["packet_count"] += 1
                if pkt.src_ip == ip:
                    h["ports_used"].add(pkt.src_port)
                    h["bytes_sent"] += pkt.original_len
                    h["ttl_values"].append(pkt.ttl)
                    if pkt.is_tcp:
                        h["tcp_window_sizes"].append(pkt.tcp_window)
                else:
                    h["ports_used"].add(pkt.dst_port)
                    h["bytes_received"] += pkt.original_len

        # TCP/IP fingerprinting
        for ip, h in hosts.items():
            h["ports_used"] = sorted(h["ports_used"])
            if h["ttl_values"]:
                common_ttl = Counter(h["ttl_values"]).most_common(1)[0][0]
                h["common_ttl"] = common_ttl
                # OS guess based on TTL
                if common_ttl <= 64:
                    h["os_guess"] = "Linux/macOS/Unix"
                elif common_ttl <= 128:
                    h["os_guess"] = "Windows"
                else:
                    h["os_guess"] = "Network device / Unknown"
            if h["tcp_window_sizes"]:
                h["common_window_size"] = Counter(h["tcp_window_sizes"]).most_common(1)[0][0]

            del h["ttl_values"]
            del h["tcp_window_sizes"]

            # Create entity for each host
            evidence.add_entity(ip, "host", {
                "first_seen": h["first_seen"],
                "last_seen": h["last_seen"],
                "ports_used": h["ports_used"],
                "os_guess": h.get("os_guess", "unknown"),
                "bytes_sent": h["bytes_sent"],
                "bytes_received": h["bytes_received"],
                "packet_count": h["packet_count"],
            })

        evidence.processor_results["hosts"] = hosts
        return hosts

    # -----------------------------------------------------------------------
    # 6. Protocol Analysis
    # -----------------------------------------------------------------------

    def _analyze_protocols(
        self, evidence: EvidenceSchema, packets: List[_PacketInfo]
    ) -> Dict[str, Dict[str, int]]:
        stats: Dict[str, Dict[str, int]] = {}

        def _inc(proto: str, pkt: _PacketInfo) -> None:
            if proto not in stats:
                stats[proto] = {"packets": 0, "bytes": 0}
            stats[proto]["packets"] += 1
            stats[proto]["bytes"] += pkt.original_len

        for pkt in packets:
            if pkt.ip_proto == _IPPROTO_TCP:
                if pkt.dst_port in _HTTP_PORTS or pkt.src_port in _HTTP_PORTS:
                    _inc("HTTP", pkt)
                elif pkt.dst_port == _HTTPS_PORT or pkt.src_port == _HTTPS_PORT:
                    _inc("HTTPS/TLS", pkt)
                elif pkt.dst_port == _DNS_PORT or pkt.src_port == _DNS_PORT:
                    _inc("DNS-over-TCP", pkt)
                else:
                    _inc("TCP-other", pkt)
            elif pkt.ip_proto == _IPPROTO_UDP:
                if pkt.dst_port == _DNS_PORT or pkt.src_port == _DNS_PORT:
                    _inc("DNS", pkt)
                else:
                    _inc("UDP-other", pkt)
            elif pkt.ip_proto == _IPPROTO_ICMP:
                _inc("ICMP", pkt)
            else:
                _inc(f"IP-proto-{pkt.ip_proto}", pkt)

        # Detect anomalies: HTTP on non-standard ports, etc.
        anomalies = []
        for proto, s in stats.items():
            if proto == "HTTP" and s["packets"] > 0:
                pass  # normal
        evidence.processor_results["protocol_stats"] = stats

        # Tag protocol mix
        if "DNS" in stats and stats["DNS"]["packets"] > 100:
            evidence.add_tag("heavy_dns")
        if "HTTPS/TLS" in stats and "HTTP" in stats:
            if stats.get("HTTPS/TLS", {}).get("bytes", 0) > stats.get("HTTP", {}).get("bytes", 0):
                evidence.add_tag("predominantly_encrypted")

        return stats

    # -----------------------------------------------------------------------
    # 7. Threat Detection
    # -----------------------------------------------------------------------

    def _detect_threats(
        self,
        evidence: EvidenceSchema,
        packets: List[_PacketInfo],
        dns_results: List[Dict[str, Any]],
        sessions: List[Dict[str, Any]],
        hosts: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        threats: List[Dict[str, Any]] = []

        # --- Port scanning detection ---
        conn_attempts: Dict[str, Set[int]] = defaultdict(set)
        for pkt in packets:
            if pkt.is_tcp and (pkt.tcp_flags & 0x02):  # SYN
                conn_attempts[pkt.src_ip].add(pkt.dst_port)

        for ip, ports in conn_attempts.items():
            if len(ports) > 20:
                threat = {
                    "type": "port_scan",
                    "src_ip": ip,
                    "unique_ports": len(ports),
                    "ports_sample": sorted(ports)[:30],
                    "risk_level": "high",
                    "mitre_attack": "T1046 - Network Service Scanning",
                }
                threats.append(threat)
                evidence.add_tag("port_scan_detected")
                evidence.add_timeline_event(
                    hosts.get(ip, {}).get("first_seen", "unknown"),
                    f"Port scan detected from {ip}: {len(ports)} unique ports probed",
                    self.name,
                )

        # --- Beaconing / C2 detection ---
        for s in sessions:
            if s["packet_count"] < 5 or s.get("duration_seconds", 0) < 10:
                continue
            # Simplified beaconing: check if packets arrive at regular intervals
            # (Would need per-packet timestamps for real analysis; use session as proxy)
            pass

        # --- DNS tunneling indicators ---
        for dns_entry in dns_results:
            domain = dns_entry.get("domain", "")
            labels = domain.split(".")
            for label in labels:
                if len(label) > 50:
                    threat = {
                        "type": "dns_tunneling",
                        "domain": domain,
                        "long_label": label[:80] + ("..." if len(label) > 80 else ""),
                        "label_length": len(label),
                        "risk_level": "high",
                        "mitre_attack": "T1071.004 - Application Layer Protocol: DNS",
                    }
                    threats.append(threat)
                    evidence.add_tag("dns_tunneling_suspected")
                    evidence.add_timeline_event(
                        dns_entry.get("timestamp", ""),
                        f"DNS tunneling suspected: long subdomain label ({len(label)} chars) in {domain}",
                        self.name,
                    )
                    break

            if _is_dga_candidate(domain):
                if not any(t.get("type") == "dga_domain" and t.get("domain") == domain for t in threats):
                    threat = {
                        "type": "dga_domain",
                        "domain": domain,
                        "entropy": round(_domain_entropy(domain), 3),
                        "risk_level": "medium",
                        "mitre_attack": "T1568.002 - Dynamic Resolution: Domain Generation Algorithms",
                    }
                    threats.append(threat)
                    evidence.add_tag("dga_domain_detected")

        # --- Large data exfiltration ---
        for s in sessions:
            outbound = s["bytes_sent"]
            if outbound > 10_000_000:  # >10 MB outbound
                threat = {
                    "type": "data_exfiltration",
                    "src_ip": s["src_ip"],
                    "dst_ip": s["dst_ip"],
                    "dst_port": s["dst_port"],
                    "bytes_out": outbound,
                    "duration": s.get("duration_seconds", 0),
                    "risk_level": "high",
                    "mitre_attack": "T1041 - Exfiltration Over C2 Channel",
                }
                threats.append(threat)
                evidence.add_tag("large_data_exfiltration")
                evidence.add_timeline_event(
                    s["start_time"],
                    f"Large outbound transfer: {s['src_ip']} -> {s['dst_ip']}:{s['dst_port']} ({outbound:,} bytes)",
                    self.name,
                )

        evidence.processor_results["threats"] = threats
        return threats

    # -----------------------------------------------------------------------
    # 8. Connection Inventory
    # -----------------------------------------------------------------------

    def _generate_connections_list(
        self, evidence: EvidenceSchema, packets: List[_PacketInfo]
    ) -> List[Dict[str, Any]]:
        conn_map: Dict[Tuple, Dict[str, Any]] = {}

        for pkt in packets:
            if not pkt.is_tcp and not pkt.is_udp:
                continue
            proto = "TCP" if pkt.is_tcp else "UDP"
            key = (pkt.src_ip, pkt.src_port, pkt.dst_ip, pkt.dst_port, proto)
            if key not in conn_map:
                conn_map[key] = {
                    "src_ip": pkt.src_ip,
                    "src_port": pkt.src_port,
                    "dst_ip": pkt.dst_ip,
                    "dst_port": pkt.dst_port,
                    "protocol": proto,
                    "first_seen": pkt.timestamp_iso,
                    "last_seen": pkt.timestamp_iso,
                    "packet_count": 0,
                    "bytes_transferred": 0,
                }
            c = conn_map[key]
            c["last_seen"] = pkt.timestamp_iso
            c["packet_count"] += 1
            c["bytes_transferred"] += pkt.original_len

        connections = sorted(conn_map.values(), key=lambda x: x["first_seen"])
        evidence.processor_results["connections"] = connections

        # Create relationship for each unique connection
        for c in connections:
            evidence.add_relationship(
                f"{c['src_ip']}:{c['src_port']}",
                f"{c['dst_ip']}:{c['dst_port']}",
                f"{c['protocol']}_connection",
                weight=c["bytes_transferred"],
            )

        return connections

    # -----------------------------------------------------------------------
    # 9. Tshark Enrichment (optional)
    # -----------------------------------------------------------------------

    def _enrich_with_tshark(self, evidence: EvidenceSchema) -> None:
        """Use tshark for TLS JA3, HTTP host analysis, etc. when available."""
        try:
            tls_rows = _run_tshark(
                evidence.storage_path,
                "tls.handshake.type == 1",
                ["frame.time", "ip.src", "ip.dst", "tls.handshake.extensions_server_name", "tls.handshake.ja3"],
                limit=500,
            )
            if tls_rows:
                evidence.processor_results["tls_handshakes"] = tls_rows
                for row in tls_rows:
                    sni = row.get("tls.handshake.extensions_server_name", "")
                    if sni:
                        evidence.add_entity(sni, "tls_server_name")
                        evidence.add_timeline_event(
                            row.get("frame.time", ""),
                            f"TLS handshake with SNI: {sni}",
                            self.name,
                        )

            http_rows = _run_tshark(
                evidence.storage_path,
                "http.request.method",
                ["frame.time", "ip.src", "ip.dst", "http.host", "http.request.method", "http.request.uri", "http.user_agent"],
                limit=500,
            )
            if http_rows:
                evidence.processor_results["tshark_http"] = http_rows
        except Exception as e:
            logger.warning("tshark enrichment failed: %s", e)
