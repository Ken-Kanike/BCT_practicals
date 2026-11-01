/**
 * Experiment 2 - interact with the deployed Wallet contract using Web3.js.
 * Run after: npx truffle migrate --config .../truffle-config.js --network development
 */
const { Web3 } = require("web3");
const WalletArtifact = require("../build/contracts/Wallet.json");

const RPC_URL = process.env.RPC_URL || "http://127.0.0.1:7545";
const web3 = new Web3(RPC_URL);

const ether = (wei) => web3.utils.fromWei(String(wei), "ether");

async function main() {
  const netId = await web3.eth.net.getId();
  const deployment = WalletArtifact.networks[netId.toString()];

  if (!deployment) {
    throw new Error(`Wallet is not deployed on network ${netId}. Run truffle migrate first.`);
  }

  const wallet = new web3.eth.Contract(WalletArtifact.abi, deployment.address);
  const accounts = await web3.eth.getAccounts();
  const [owner, student, stranger] = accounts;

  console.log("=== WALLET CONTRACT (Web3.js) ===");
  console.log(`RPC URL:          ${RPC_URL}`);
  console.log(`Network id:       ${netId}`);
  console.log(`Contract address: ${deployment.address}`);
  console.log(`Contract owner:   ${await wallet.methods.owner().call()}`);
  console.log(`Account[0]:       ${owner}`);
  console.log(`Account[1]:       ${student}`);
  console.log(`Account[2]:       ${stranger}`);

  console.log("\n=== INITIAL STATE ===");
  console.log(`Contract balance: ${ether(await wallet.methods.getBalance().call())} ETH`);

  console.log("\n=== DEPOSIT 1 ETH FROM ACCOUNT[1] ===");
  const depositReceipt = await wallet.methods.deposit().send({
    from: student,
    value: web3.utils.toWei("1", "ether"),
    gas: 200000
  });
  console.log(`Transaction hash: ${depositReceipt.transactionHash}`);
  console.log(`Block number:     ${depositReceipt.blockNumber}`);
  console.log(`Gas used:         ${depositReceipt.gasUsed}`);
  const depositEvent = depositReceipt.events.Deposit;
  console.log(`Deposit event:    sender=${depositEvent.returnValues.sender}, amount=${ether(depositEvent.returnValues.amount)} ETH`);
  console.log(`Contract balance: ${ether(await wallet.methods.getBalance().call())} ETH`);

  console.log("\n=== WITHDRAW 0.5 ETH AS OWNER ===");
  const withdrawReceipt = await wallet.methods.withdraw(web3.utils.toWei("0.5", "ether")).send({
    from: owner,
    gas: 200000
  });
  console.log(`Transaction hash: ${withdrawReceipt.transactionHash}`);
  console.log(`Block number:     ${withdrawReceipt.blockNumber}`);
  console.log(`Gas used:         ${withdrawReceipt.gasUsed}`);
  const withdrawEvent = withdrawReceipt.events.Withdraw;
  console.log(`Withdraw event:   recipient=${withdrawEvent.returnValues.recipient}, amount=${ether(withdrawEvent.returnValues.amount)} ETH`);
  console.log(`Contract balance: ${ether(await wallet.methods.getBalance().call())} ETH`);

  console.log("\n=== UNAUTHORISED WITHDRAW FROM ACCOUNT[2] ===");
  try {
    await wallet.methods.withdraw(web3.utils.toWei("0.1", "ether")).call({ from: stranger });
    console.log("Unexpected success - access control failed");
  } catch (error) {
    console.log(`eth_call rejected as expected -> ${error.cause ? error.cause.message : error.message}`);
    try {
      await wallet.methods.withdraw(web3.utils.toWei("0.1", "ether")).send({
        from: stranger,
        gas: 200000
      });
      console.log("Unexpected success - access control failed");
    } catch (sendError) {
      console.log(`On-chain transaction reverted (receipt status ${sendError.receipt ? sendError.receipt.status : "n/a"})`);
    }
  }

  console.log("\n=== DEPOSIT EVENT HISTORY ===");
  const depositTopic = web3.utils.sha3("Deposit(address,uint256)");
  const logs = await web3.eth.getPastLogs({
    address: deployment.address,
    fromBlock: 0,
    toBlock: "latest",
    topics: [depositTopic]
  });
  logs.forEach((log, index) => {
    const decoded = web3.eth.abi.decodeLog(
      [
        { type: "address", name: "sender", indexed: true },
        { type: "uint256", name: "amount", indexed: false }
      ],
      log.data,
      log.topics.slice(1)
    );
    console.log(
      `#${index + 1} block ${log.blockNumber}: ${decoded.sender} deposited ${ether(decoded.amount)} ETH`
    );
  });

  console.log("\n=== FINAL STATE ===");
  console.log(`Contract balance: ${ether(await wallet.methods.getBalance().call())} ETH`);
  console.log("Experiment 2 execution complete.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
