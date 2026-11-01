/**
 * Verify connectivity to the local test network and to the public Sepolia
 * Ethereum test network using only public RPC endpoints (no API key needed).
 */
const { ethers } = require("ethers");

const targets = [
  {
    name: "Ganache (local test network)",
    url: process.env.GANACHE_RPC_URL || "http://127.0.0.1:7545"
  },
  {
    name: "Sepolia (public Ethereum testnet)",
    url: process.env.SEPOLIA_RPC_URL || "https://ethereum-sepolia-rpc.publicnode.com"
  }
];

async function main() {
  for (const target of targets) {
    const started = Date.now();
    try {
      const provider = new ethers.JsonRpcProvider(target.url);
      const network = await provider.getNetwork();
      const blockNumber = await provider.getBlockNumber();
      const feeData = await provider.getFeeData();
      const gasPrice = feeData.gasPrice ? ethers.formatUnits(feeData.gasPrice, "gwei") : "n/a";
      console.log(
        `${target.name}\n  url=${target.url}\n  chainId=${network.chainId} block=${blockNumber} gasPrice=${gasPrice} gwei latency=${Date.now() - started}ms`
      );
    } catch (error) {
      console.log(`${target.name}\n  url=${target.url}\n  ERROR: ${error.shortMessage || error.message}`);
    }
  }
}

main();
