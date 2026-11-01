const { keccak256, toUtf8Bytes, concat } = require("ethers");

/**
 * Hash a transaction string into a Merkle leaf.
 * leaf = keccak256(utf8(transaction))
 */
function hashLeaf(data) {
  return keccak256(toUtf8Bytes(data));
}

/**
 * Hash two child nodes in deterministic (sorted) order so that a proof does
 * not need to carry left/right direction bits.
 */
function hashPair(a, b) {
  const [left, right] = a.toLowerCase() <= b.toLowerCase() ? [a, b] : [b, a];
  return keccak256(concat([left, right]));
}

/**
 * Build a full Merkle tree. Odd nodes are promoted unchanged to the next level.
 * @param {string[]} leaves transaction strings
 * @returns {{layers: string[][], root: string, leaves: string[]}}
 */
function buildMerkleTree(leaves) {
  if (!leaves.length) throw new Error("Cannot build a Merkle tree with no leaves");
  const leafHashes = leaves.map(hashLeaf);
  const layers = [leafHashes];

  while (layers[layers.length - 1].length > 1) {
    const prev = layers[layers.length - 1];
    const next = [];
    for (let i = 0; i < prev.length; i += 2) {
      if (i + 1 < prev.length) {
        next.push(hashPair(prev[i], prev[i + 1]));
      } else {
        next.push(prev[i]);
      }
    }
    layers.push(next);
  }

  return {
    layers,
    root: layers[layers.length - 1][0],
    leaves: leafHashes
  };
}

/**
 * Return the Merkle proof (sibling hashes) for a leaf index.
 */
function getProof(tree, index) {
  if (index < 0 || index >= tree.leaves.length) {
    throw new Error("Leaf index out of range");
  }
  const proof = [];
  let idx = index;

  for (let level = 0; level < tree.layers.length - 1; level++) {
    const layer = tree.layers[level];
    const siblingIdx = idx % 2 === 0 ? idx + 1 : idx - 1;
    if (siblingIdx < layer.length) {
      proof.push(layer[siblingIdx]);
    }
    idx = Math.floor(idx / 2);
  }

  return proof;
}

/**
 * Verify a proof entirely off-chain (same algorithm as MerkleStore.sol).
 */
function verifyProof(root, leafHash, proof) {
  let computed = leafHash;
  for (const sibling of proof) {
    computed = hashPair(computed, sibling);
  }
  return computed.toLowerCase() === root.toLowerCase();
}

module.exports = { hashLeaf, hashPair, buildMerkleTree, getProof, verifyProof };
