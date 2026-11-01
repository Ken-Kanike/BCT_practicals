const MerkleStore = artifacts.require("MerkleStore");
const { buildMerkleTree, getProof, hashLeaf } = require("../lib/merkle");

function short(hash) {
  return `${hash.slice(0, 10)}...${hash.slice(-8)}`;
}

module.exports = async function (callback) {
  try {
    const store = await MerkleStore.deployed();
    const transactions = [
      "TX1 alice pays bob 1.5 ETH",
      "TX2 bob pays carol 0.75 ETH",
      "TX3 carol pays dave 2.0 ETH",
      "TX4 dave pays alice 0.25 ETH",
      "TX5 alice pays carol 0.5 ETH"
    ];

    const tree = buildMerkleTree(transactions);

    console.log("=== MERKLE TREE CONSTRUCTION ===");
    transactions.forEach((tx, i) => {
      console.log(`Leaf ${i}: ${tx}`);
      console.log(`   hash: ${tree.leaves[i]}`);
    });
    console.log(`\nMerkle root: ${tree.root}`);
    console.log(`Tree levels: ${tree.layers.map((l) => l.length).join(" -> ")}`);
    console.log(`Contract: ${store.address}`);
    console.log(`Owner:    ${await store.owner()}`);

    console.log("\n=== COMMIT ROOT ON-CHAIN (Truffle -> Ganache) ===");
    const receipt = await store.setMerkleRoot(tree.root, transactions.length);
    console.log(`Transaction hash: ${receipt.tx}`);
    console.log(`Block number:     ${receipt.receipt.blockNumber}`);
    console.log(`Gas used:         ${receipt.receipt.gasUsed}`);
    console.log(`Stored root:      ${await store.merkleRoot()}`);

    console.log("\n=== ON-CHAIN PROOF VERIFICATION ===");
    for (let i = 0; i < transactions.length; i++) {
      const proof = getProof(tree, i);
      const ok = await store.verify(proof, tree.leaves[i]);
      console.log(`Leaf ${i} proof (${proof.length} siblings, ${proof.map(short).join(", ")}) => ${ok}`);
    }

    console.log("\n=== TAMPER DETECTION ===");
    const tampered = hashLeaf("TX1 alice pays bob 999 ETH");
    const tamperedOk = await store.verify(getProof(tree, 0), tampered);
    console.log(`Tampered TX1 leaf: ${tampered}`);
    console.log(`Proof valid:       ${tamperedOk} (expected false)`);

    console.log("\n=== COMMIT INDIVIDUAL LEAF ===");
    const leafReceipt = await store.commitLeaf(tree.leaves[0]);
    console.log(`Leaf 0 committed in tx ${leafReceipt.tx}`);
    console.log(`committedLeaves(leaf0) = ${await store.committedLeaves(tree.leaves[0])}`);

    console.log("\nExperiment 1 execution complete.");
    callback();
  } catch (error) {
    callback(error);
  }
};
