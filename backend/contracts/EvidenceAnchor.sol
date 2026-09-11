// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title EvidenceAnchor
 * @dev CrimeKit Evidence Anchoring Smart Contract
 * @version CRIMEKIT-EIP-001 v1.0
 *
 * @notice Anchors forensic evidence commitments on EVM chains.
 *         Only hashes/commitments are stored — never PII.
 */
contract EvidenceAnchor {
    // ── Structs ─────────────────────────────────────────────────────────────

    struct AnchorRecord {
        bytes32 proofId;
        bytes32 caseCommitment;
        bytes32 evidenceCommitment;
        bytes32 merkleRoot;
        uint8   anchorType;
        uint256 timestamp;
        bytes32 issuerId;
        uint256 protocolVersion;
        bytes32 metadataHash;
        bool    active;
    }

    // ── Enums ───────────────────────────────────────────────────────────────

    enum AnchorType {
        Evidence,
        Batch,
        Lineage,
        Custody,
        Verification
    }

    // ── State ───────────────────────────────────────────────────────────────

    address public owner;
    bytes32 public contractVersion;

    mapping(bytes32 => AnchorRecord) private _anchors;
    bytes32[] private _proofIds;
    mapping(bytes32 => bool) private _proofIdExists;
    mapping(bytes32 => bytes32) private _caseIndex;
    mapping(bytes32 => bytes32) private _evidenceIndex;

    uint256 public constant MAX_BATCH_SIZE = 128;
    uint256 public constant PROTOCOL_VERSION = 1;

    // ── Events ──────────────────────────────────────────────────────────────

    event EvidenceAnchored(
        bytes32 indexed proofId,
        bytes32 indexed caseCommitment,
        bytes32 indexed evidenceCommitment,
        bytes32 merkleRoot,
        uint8   anchorType,
        uint256 timestamp,
        bytes32 issuerId,
        uint256 protocolVersion
    );

    event AnchorRevoked(
        bytes32 indexed proofId,
        address indexed revokedBy,
        uint256 timestamp
    );

    // ── Errors ──────────────────────────────────────────────────────────────

    error AlreadyAnchored(bytes32 proofId);
    error ProofNotFound(bytes32 proofId);
    error ProofRevoked(bytes32 proofId);
    error InvalidMerkleRoot();
    error InvalidIssuer();
    error BatchTooLarge(uint256 requested, uint256 max);
    error Unauthorized(address caller);
    error EmptyBatch();

    // ── Modifiers ───────────────────────────────────────────────────────────

    modifier onlyOwner() {
        if (msg.sender != owner) revert Unauthorized(msg.sender);
        _;
    }

    // ── Constructor ─────────────────────────────────────────────────────────

    constructor() {
        owner = msg.sender;
        contractVersion = keccak256(abi.encodePacked("CRIMEKIT-EIP-001 v1.0"));
    }

    // ── Core Functions ──────────────────────────────────────────────────────

    /**
     * @notice Anchor a single proof on-chain.
     * @param proofId            Unique proof identifier (hash).
     * @param caseCommitment     Commitment hash for the case.
     * @param evidenceCommitment Commitment hash for the evidence.
     * @param merkleRoot         Merkle root of the evidence batch.
     * @param anchorType         Type of anchor (Evidence, Batch, etc.).
     * @param issuerId           Pseudonymous issuer identifier hash.
     * @param metadataHash       Hash of associated metadata.
     */
    function anchorProof(
        bytes32 proofId,
        bytes32 caseCommitment,
        bytes32 evidenceCommitment,
        bytes32 merkleRoot,
        uint8   anchorType,
        bytes32 issuerId,
        bytes32 metadataHash
    ) external {
        if (_proofIdExists[proofId]) revert AlreadyAnchored(proofId);
        if (merkleRoot == bytes32(0)) revert InvalidMerkleRoot();
        if (issuerId == bytes32(0)) revert InvalidIssuer();

        AnchorRecord memory record = AnchorRecord({
            proofId:            proofId,
            caseCommitment:     caseCommitment,
            evidenceCommitment: evidenceCommitment,
            merkleRoot:         merkleRoot,
            anchorType:         anchorType,
            timestamp:          block.timestamp,
            issuerId:           issuerId,
            protocolVersion:    PROTOCOL_VERSION,
            metadataHash:       metadataHash,
            active:             true
        });

        _anchors[proofId] = record;
        _proofIds.push(proofId);
        _proofIdExists[proofId] = true;
        _caseIndex[caseCommitment] = proofId;
        _evidenceIndex[evidenceCommitment] = proofId;

        emit EvidenceAnchored(
            proofId,
            caseCommitment,
            evidenceCommitment,
            merkleRoot,
            anchorType,
            block.timestamp,
            issuerId,
            PROTOCOL_VERSION
        );
    }

    /**
     * @notice Batch-anchor multiple proofs in a single transaction.
     * @param proofIds            Array of proof identifiers.
     * @param caseCommitments     Array of case commitment hashes.
     * @param evidenceCommitments Array of evidence commitment hashes.
     * @param merkleRoots         Array of merkle roots.
     * @param anchorTypes         Array of anchor types.
     * @param issuerId            Pseudonymous issuer identifier hash.
     * @param metadataHashes      Array of metadata hashes.
     */
    function batchAnchor(
        bytes32[] calldata proofIds,
        bytes32[] calldata caseCommitments,
        bytes32[] calldata evidenceCommitments,
        bytes32[] calldata merkleRoots,
        uint8[]  calldata anchorTypes,
        bytes32  issuerId,
        bytes32[] calldata metadataHashes
    ) external {
        uint256 len = proofIds.length;
        if (len == 0) revert EmptyBatch();
        if (len > MAX_BATCH_SIZE) revert BatchTooLarge(len, MAX_BATCH_SIZE);
        if (
            len != caseCommitments.length ||
            len != evidenceCommitments.length ||
            len != merkleRoots.length ||
            len != anchorTypes.length ||
            len != metadataHashes.length
        ) revert EmptyBatch();
        if (issuerId == bytes32(0)) revert InvalidIssuer();

        for (uint256 i = 0; i < len; ) {
            bytes32 pid = proofIds[i];
            if (_proofIdExists[pid]) {
                revert AlreadyAnchored(pid);
            }
            if (merkleRoots[i] == bytes32(0)) revert InvalidMerkleRoot();

            AnchorRecord memory record = AnchorRecord({
                proofId:            pid,
                caseCommitment:     caseCommitments[i],
                evidenceCommitment: evidenceCommitments[i],
                merkleRoot:         merkleRoots[i],
                anchorType:         anchorTypes[i],
                timestamp:          block.timestamp,
                issuerId:           issuerId,
                protocolVersion:    PROTOCOL_VERSION,
                metadataHash:       metadataHashes[i],
                active:             true
            });

            _anchors[pid] = record;
            _proofIds.push(pid);
            _proofIdExists[pid] = true;
            _caseIndex[caseCommitments[i]] = pid;
            _evidenceIndex[evidenceCommitments[i]] = pid;

            emit EvidenceAnchored(
                pid,
                caseCommitments[i],
                evidenceCommitments[i],
                merkleRoots[i],
                anchorTypes[i],
                block.timestamp,
                issuerId,
                PROTOCOL_VERSION
            );

            unchecked { ++i; }
        }
    }

    /**
     * @notice Revoke (invalidate) an existing anchor.
     * @param proofId The proof identifier to revoke.
     */
    function revokeProof(bytes32 proofId) external onlyOwner {
        if (!_proofIdExists[proofId]) revert ProofNotFound(proofId);
        if (!_anchors[proofId].active) revert ProofRevoked(proofId);

        _anchors[proofId].active = false;

        emit AnchorRevoked(proofId, msg.sender, block.timestamp);
    }

    // ── View Functions ──────────────────────────────────────────────────────

    /**
     * @notice Retrieve an anchor record by proof ID.
     * @param proofId The proof identifier.
     * @return The anchor record.
     */
    function getAnchor(bytes32 proofId) external view returns (AnchorRecord memory) {
        if (!_proofIdExists[proofId]) revert ProofNotFound(proofId);
        return _anchors[proofId];
    }

    /**
     * @notice Get the total number of anchored proofs.
     * @return Count of anchors.
     */
    function getAnchorCount() external view returns (uint256) {
        return _proofIds.length;
    }

    /**
     * @notice Verify that a proof exists and its merkle root matches.
     * @param proofId       The proof identifier.
     * @param expectedRoot  The expected merkle root.
     * @return valid True if the proof is active and the root matches.
     */
    function verifyProof(bytes32 proofId, bytes32 expectedRoot)
        external
        view
        returns (bool valid)
    {
        if (!_proofIdExists[proofId]) return false;
        AnchorRecord storage record = _anchors[proofId];
        return record.active && record.merkleRoot == expectedRoot;
    }

    /**
     * @notice Look up a proof ID by case commitment.
     * @param caseCommitment The case commitment hash.
     * @return proofId The associated proof ID (bytes32(0) if not found).
     */
    function getProofByCaseCommitment(bytes32 caseCommitment)
        external
        view
        returns (bytes32)
    {
        return _caseIndex[caseCommitment];
    }

    /**
     * @notice Look up a proof ID by evidence commitment.
     * @param evidenceCommitment The evidence commitment hash.
     * @return proofId The associated proof ID (bytes32(0) if not found).
     */
    function getProofByEvidenceCommitment(bytes32 evidenceCommitment)
        external
        view
        returns (bytes32)
    {
        return _evidenceIndex[evidenceCommitment];
    }
}
