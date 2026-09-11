# CrimeKit — Digital Forensics Architecture & Standard Operating Procedures

## 1. Principles of Digital Forensics (ISO/IEC 27037)
CrimeKit enforces strict adherence to forensic evidence handling:
1. **Never Alter Original Evidence**: Forensic source files (raw disk images, memory dumps, packet captures) are mounted read-only and preserved in immutable storage.
2. **Cryptographic Validation**: SHA-256 and MD5 hashes are generated at acquisition and re-verified before and after every processing pipeline step.
3. **Reproducibility**: All extraction algorithms produce deterministic, repeatable outputs tagged with the exact engine version and timestamp.

---

## 2. Pluggable Processor Architecture

Processors implement the `BaseProcessor` interface in `backend/app/advanced_forensics/`:

- **TSK Engine (`pytsk3`)**:
  - Image format detection: RAW, DD, E01 (Expert Witness), VMDK, VHD.
  - Partition analysis: MBR, GPT, APM.
  - Filesystem inspection: NTFS (MFT records, USN journal, ADS streams), FAT12/16/32, EXT2/3/4.
- **Memory Forensics Processor**:
  - Windows kernel structure parsing (`EPROCESS` enumeration, active links validation).
  - Loaded DLLs, token privileges, and parent-child process tree reconstruction.
  - Injected shellcode detection (CLD/CALL, PEB manipulation, XOR decode loops).
  - Fast vectorized ASCII and UTF-16LE string search.
  - In-memory registry hive detection (`regf` header parsing).
- **Network Forensics Processor**:
  - PCAP/PCAPNG header parsing, packet dissection, protocol breakdown (DNS, HTTP, TLS, SSH).
- **Windows Artifact Processor**:
  - EVTX binary XML parsing, Prefetch file execution traces, Shell LNK shortcuts.
- **Integrity & File Carving Processor**:
  - Magic byte sniffing, extension mismatch detection, high-entropy payload identification (compressed/encrypted data).
