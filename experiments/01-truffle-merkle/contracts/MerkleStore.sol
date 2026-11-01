// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title MerkleStore
/// @notice Stores a Merkle root of an off-chain transaction batch and verifies
///         membership proofs on-chain. Used to demonstrate how blockchains
///         compress many transactions into a single cryptographic commitment.
contract MerkleStore {
    bytes32 public merkleRoot;
    address public owner;
    uint256 public leafCount;

    mapping(bytes32 => bool) public committedLeaves;

    event RootUpdated(bytes32 indexed oldRoot, bytes32 indexed newRoot, uint256 leafCount);
    event LeafCommitted(bytes32 indexed leaf);

    modifier onlyOwner() {
        require(msg.sender == owner, "MerkleStore: caller is not the owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /// @notice Commit a new Merkle root (normally after a batch of transactions).
    function setMerkleRoot(bytes32 _root, uint256 _leafCount) external onlyOwner {
        emit RootUpdated(merkleRoot, _root, _leafCount);
        merkleRoot = _root;
        leafCount = _leafCount;
    }

    /// @notice Record an individual leaf hash, e.g. a settled transaction id.
    function commitLeaf(bytes32 leaf) external onlyOwner {
        require(!committedLeaves[leaf], "MerkleStore: leaf already committed");
        committedLeaves[leaf] = true;
        emit LeafCommitted(leaf);
    }

    /// @notice Verify a Merkle proof against the currently stored root.
    function verify(bytes32[] calldata proof, bytes32 leaf) external view returns (bool) {
        return _verify(merkleRoot, proof, leaf);
    }

    /// @notice Verify a Merkle proof against an arbitrary root (pure helper).
    function verifyWithRoot(
        bytes32 root,
        bytes32[] calldata proof,
        bytes32 leaf
    ) external pure returns (bool) {
        return _verify(root, proof, leaf);
    }

    function _verify(
        bytes32 root,
        bytes32[] calldata proof,
        bytes32 leaf
    ) internal pure returns (bool) {
        bytes32 computed = leaf;
        for (uint256 i = 0; i < proof.length; i++) {
            bytes32 sibling = proof[i];
            if (computed <= sibling) {
                computed = keccak256(abi.encodePacked(computed, sibling));
            } else {
                computed = keccak256(abi.encodePacked(sibling, computed));
            }
        }
        return computed == root;
    }
}
