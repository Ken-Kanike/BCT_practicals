const TestnetStorage = artifacts.require("TestnetStorage");

module.exports = function (deployer, network, accounts) {
  deployer.deploy(TestnetStorage, 42, { from: accounts[0] });
};
