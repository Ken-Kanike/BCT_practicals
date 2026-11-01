/**
 * Deploy is done by Truffle (migrations/1_deploy_token.js).
 * This script reads the deployment, prints token data, performs real
 * transfers/approvals on Ganache, and exports a config for the local UI.
 */
const fs = require("fs");
const path = require("path");
const { ethers } = require("ethers");
const artifact = require("../build/contracts/SimpleCryptoCurrency.json");

const RPC_URL = process.env.RPC_URL || "http://127.0.0.1:7545";
const UNIT = 10n ** 18n;

function fmt(value) {
  return ethers.formatUnits(value, 18);
}

async function main() {
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const network = await provider.getNetwork();
  const netVersion = await provider.send("net_version", []);
  const deployment = artifact.networks[netVersion] || Object.values(artifact.networks || {}).at(-1);

  if (!deployment) {
    throw new Error(`Token is not deployed on chain ${network.chainId}. Run truffle migrate first.`);
  }

  const accounts = await Promise.all(
    [0, 1, 2, 3].map(async (index) => (await provider.getSigner(index)).getAddress())
  );
  const [deployer, alice, bob, carol] = accounts;

  const token = new ethers.Contract(deployment.address, artifact.abi, await provider.getSigner(0));

  console.log("=== CRYPTOCURRENCY TOKEN (Remix/MetaMask contract) ===");
  console.log(`RPC URL:          ${RPC_URL}`);
  console.log(`Chain id:         ${network.chainId}`);
  console.log(`Token address:    ${deployment.address}`);
  console.log(`Name:             ${await token.name()}`);
  console.log(`Symbol:           ${await token.symbol()}`);
  console.log(`Decimals:         ${await token.decimals()}`);
  console.log(`Total supply:     ${fmt(await token.totalSupply())} MTK`);
  console.log(`Owner:            ${await token.owner()}`);

  console.log("\n=== INITIAL BALANCES ===");
  for (const [label, address] of [["deployer", deployer], ["alice", alice], ["bob", bob], ["carol", carol]]) {
    console.log(`${label.padEnd(9)} ${address}  ${fmt(await token.balanceOf(address))} MTK`);
  }

  console.log("\n=== TRANSFER 250,000 MTK: deployer -> alice ===");
  const transferTx = await token.transfer(alice, ethers.parseUnits("250000", 18));
  console.log(`Transaction:      ${transferTx.hash}`);
  const transferReceipt = await transferTx.wait();
  console.log(`Mined block:      ${transferReceipt.blockNumber}`);
  console.log(`Gas used:         ${transferReceipt.gasUsed.toString()}`);
  const transferEvent = transferReceipt.logs
    .map((log) => {
      try {
        return token.interface.parseLog(log);
      } catch {
        return null;
      }
    })
    .find((event) => event && event.name === "Transfer");
  console.log(`Transfer event:   ${transferEvent.args.from} -> ${transferEvent.args.to} = ${fmt(transferEvent.args.value)} MTK`);

  console.log("\n=== APPROVE 5,000 MTK: alice -> bob ===");
  const approveTx = await token.connect(await provider.getSigner(1)).approve(bob, ethers.parseUnits("5000", 18));
  await approveTx.wait();
  console.log(`Allowance:        ${fmt(await token.allowance(alice, bob))} MTK`);

  console.log("\n=== TRANSFER-FROM 3,000 MTK: alice -> carol (signed by bob) ===");
  const fromTx = await token.connect(await provider.getSigner(2)).transferFrom(
    alice,
    carol,
    ethers.parseUnits("3000", 18)
  );
  console.log(`Transaction:      ${fromTx.hash}`);
  const fromReceipt = await fromTx.wait();
  console.log(`Mined block:      ${fromReceipt.blockNumber}`);
  console.log(`Remaining allowance: ${fmt(await token.allowance(alice, bob))} MTK`);

  console.log("\n=== INSUFFICIENT BALANCE CHECK: carol -> bob 1,000,000 MTK ===");
  try {
    await token.connect(await provider.getSigner(3)).transfer.staticCall(bob, ethers.parseUnits("1000000", 18));
    console.log("Unexpected success - balance check failed");
  } catch (error) {
    console.log(`Rejected as expected -> ${error.shortMessage || error.reason || error.message}`);
  }

  console.log("\n=== FINAL BALANCES ===");
  for (const [label, address] of [["deployer", deployer], ["alice", alice], ["bob", bob], ["carol", carol]]) {
    console.log(`${label.padEnd(9)} ${address}  ${fmt(await token.balanceOf(address))} MTK`);
  }

  const uiDir = path.join(__dirname, "..", "ui");
  fs.mkdirSync(uiDir, { recursive: true });
  fs.writeFileSync(
    path.join(uiDir, "config.json"),
    JSON.stringify(
      {
        rpcUrl: RPC_URL,
        chainId: Number(network.chainId),
        address: deployment.address,
        abi: artifact.abi
      },
      null,
      2
    )
  );
  console.log(`\nUI config written to ${path.join(uiDir, "config.json")}`);
  console.log("Experiment 4 execution complete.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
