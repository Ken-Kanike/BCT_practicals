const MerkleStore = artifacts.require("MerkleStore");
const { buildMerkleTree, getProof, hashLeaf } = require("../lib/merkle");

contract("MerkleStore - Merkle root cryptography", (accounts) => {
  const [owner, alice, bob] = accounts;

  const transactions = [
    "alice->bob:1.5 ETH",
    "bob->carol:0.75 ETH",
    "carol->dave:2.0 ETH",
    "dave->alice:0.25 ETH",
    "alice->carol:0.5 ETH"
  ];

  let store;
  let tree;

  before(async () => {
    store = await MerkleStore.new({ from: owner });
    tree = buildMerkleTree(transactions);
  });

  it("sets the deployer as the contract owner", async () => {
    assert.equal(await store.owner(), owner);
  });

  it("stores the Merkle root and emits RootUpdated", async () => {
    const receipt = await store.setMerkleRoot(tree.root, transactions.length, { from: owner });
    const event = receipt.logs.find((log) => log.event === "RootUpdated");

    assert.ok(event, "RootUpdated event must be emitted");
    assert.equal(event.args.newRoot.toLowerCase(), tree.root.toLowerCase());
    assert.equal(event.args.leafCount.toString(), String(transactions.length));
    assert.equal((await store.merkleRoot()).toLowerCase(), tree.root.toLowerCase());
    assert.equal((await store.leafCount()).toString(), String(transactions.length));
  });

  it("verifies every valid Merkle proof on-chain", async () => {
    for (let i = 0; i < transactions.length; i++) {
      const proof = getProof(tree, i);
      const ok = await store.verify(proof, tree.leaves[i]);
      assert.isTrue(ok, `proof for leaf ${i} should verify`);
    }
  });

  it("rejects a tampered transaction leaf", async () => {
    const tampered = hashLeaf("alice->bob:999 ETH");
    const proof = getProof(tree, 0);
    assert.isFalse(await store.verify(proof, tampered));
  });

  it("rejects a valid proof when the root belongs to another tree", async () => {
    const otherTree = buildMerkleTree(["mallory->eve:100 ETH"]);
    const proof = getProof(otherTree, 0);
    assert.isFalse(await store.verify(proof, otherTree.leaves[0]));
    assert.isTrue(await store.verifyWithRoot(otherTree.root, proof, otherTree.leaves[0]));
  });

  it("restricts root updates to the owner", async () => {
    try {
      await store.setMerkleRoot(tree.root, transactions.length, { from: alice });
      assert.fail("non-owner should not update the root");
    } catch (error) {
      assert.include(error.message, "caller is not the owner");
    }
  });

  it("commits a leaf hash only once", async () => {
    const leaf = tree.leaves[0];
    const receipt = await store.commitLeaf(leaf, { from: owner });
    const event = receipt.logs.find((log) => log.event === "LeafCommitted");
    assert.ok(event);
    assert.isTrue(await store.committedLeaves(leaf));

    try {
      await store.commitLeaf(leaf, { from: owner });
      assert.fail("duplicate leaf must be rejected");
    } catch (error) {
      assert.include(error.message, "leaf already committed");
    }
  });

  it("produces a deterministic root for the same batch", () => {
    const rebuilt = buildMerkleTree(transactions);
    assert.equal(rebuilt.root, tree.root);
    assert.notEqual(buildMerkleTree([...transactions, "extra"]).root, tree.root);
  });
});
