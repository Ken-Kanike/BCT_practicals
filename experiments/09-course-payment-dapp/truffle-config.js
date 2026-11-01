module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 7545,
      network_id: "*",
    },
  },
  compilers: {
    solc: {
      version: "0.8.26",
      settings: {
        evmVersion: "shanghai",
        optimizer: {
          enabled: true,
          runs: 200,
        },
      },
    },
  },
  contracts_directory: "./contracts",
  migrations_directory: "./migrations",
  test_directory: "./test",
};
