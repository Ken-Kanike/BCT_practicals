const path = require("path");

module.exports = {
  contracts_directory: path.join(__dirname, "contracts"),
  contracts_build_directory: path.join(__dirname, "build", "contracts"),
  migrations_directory: path.join(__dirname, "migrations"),
  test_directory: path.join(__dirname, "test"),

  networks: {
    development: {
      host: "127.0.0.1",
      port: 7545,
      network_id: "*",
      gas: 6721975,
      gasPrice: 20000000000
    }
  },

  mocha: { timeout: 100000 },

  compilers: {
    solc: {
      version: "0.8.26",
      settings: { optimizer: { enabled: true, runs: 200 } }
    }
  }
};
