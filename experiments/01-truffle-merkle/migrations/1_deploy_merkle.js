const MerkleStore = artifacts.require("MerkleStore");

module.exports = function (deployer, network, accounts) {
  deployer.deploy(MerkleStore, { from: accounts[0] });
};
