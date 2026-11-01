/**
 * Deploy TestnetStorage to any EVM network.
 *
 * Local Ganache (default):
 *   node experiments/03-testnet-deployment/scripts/deploy_testnet.js
 *
 * Sepolia:
 *   $env:RPC_URL="https://ethereum-sepolia-rpc.publicnode.com"
 *   $env:PRIVATE_KEY="0x..."   # funded testnet account
 *   node experiments/03-testnet-deployment/scripts/deploy_testnet.js
 */
const { ethers } = require("ethers");
const artifact = require("../build/contracts/TestnetStorage.json");

const RPC_URL = process.env.RPC_URL || "http://127.0.0.1:7545";
const EXPLORERS = {
  11155111: "https://sepolia.etherscan.io",
  17000: "https://holesky.etherscan.io",
  1337: null
};

async function main() {
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const network = await provider.getNetwork();
  const chainId = Number(network.chainId);

  let signer;
  let signerLabel;
  if (process.env.PRIVATE_KEY) {
    signer = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
    signerLabel = "local wallet from PRIVATE_KEY";
  } else {
    signer = await provider.getSigner(0);
    signerLabel = "unlocked RPC account (Ganache)";
  }

  const address = await signer.getAddress();
  const balance = await provider.getBalance(address);

  console.log("=== TESTNET DEPLOYMENT ===");
  console.log(`RPC URL:        ${RPC_URL}`);
  console.log(`Chain id:       ${chainId}`);
  console.log(`Network:        ${network.name}`);
  console.log(`Signer:         ${address} (${signerLabel})`);
  console.log(`Signer balance: ${ethers.formatEther(balance)} ETH`);

  if (balance === 0n) {
    throw new Error("Signer has 0 ETH; fund it from a faucet before deploying to a public testnet.");
  }

  const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, signer);
  const contract = await factory.deploy(42);
  const deployTx = contract.deploymentTransaction();
  console.log(`\nDeployment tx:  ${deployTx.hash}`);

  const deployReceipt = await deployTx.wait();
  await contract.waitForDeployment();
  const contractAddress = await contract.getAddress();

  console.log(`Contract:       ${contractAddress}`);
  console.log(`Mined block:    ${deployReceipt.blockNumber}`);
  console.log(`Gas used:       ${deployReceipt.gasUsed.toString()}`);

  console.log("\n=== CALL setValue(137) ===");
  const tx = await contract.setValue(137);
  console.log(`Transaction:    ${tx.hash}`);
  const receipt = await tx.wait();
  console.log(`Mined block:    ${receipt.blockNumber}`);
  console.log(`Gas used:       ${receipt.gasUsed.toString()}`);
  console.log(`getValue():     ${(await contract.getValue()).toString()}`);

  const explorer = EXPLORERS[chainId];
  if (explorer) {
    console.log(`\nExplorer:       ${explorer}/address/${contractAddress}`);
    console.log(`Transaction:    ${explorer}/tx/${deployTx.hash}`);
  }

  console.log("\nDeployment complete.");
}

main().catch((error) => {
  console.error(`\nDeployment failed: ${error.shortMessage || error.message}`);
  process.exitCode = 1;
});
