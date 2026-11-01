const SimpleCryptoCurrency = artifacts.require("SimpleCryptoCurrency");

module.exports = function (deployer, network, accounts) {
  deployer.deploy(
    SimpleCryptoCurrency,
    "MyToken",
    "MTK",
    18,
    1000000,
    { from: accounts[0] }
  );
};
