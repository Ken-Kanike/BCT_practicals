const fs = require("fs");
const path = require("path");
const { buildMerkleTree } = require("../lib/merkle");

const transactions = [
  "TX1 alice pays bob 1.5 ETH",
  "TX2 bob pays carol 0.75 ETH",
  "TX3 carol pays dave 2.0 ETH",
  "TX4 dave pays alice 0.25 ETH",
  "TX5 alice pays carol 0.5 ETH"
];

const tree = buildMerkleTree(transactions);
const out = path.join(__dirname, "..", "output", "merkle-tree.json");
fs.writeFileSync(out, JSON.stringify({ transactions, ...tree }, null, 2));
console.log(`wrote ${out}`);
console.log(`root ${tree.root}`);
