const Wallet = artifacts.require("Wallet");

const toEther = (wei) => web3.utils.fromWei(wei, "ether");

contract("Wallet - Solidity smart contract", (accounts) => {
  const [owner, depositor, stranger] = accounts;
  let wallet;

  beforeEach(async () => {
    wallet = await Wallet.new({ from: owner });
  });

  it("sets the deployer as owner", async () => {
    assert.equal(await wallet.owner(), owner);
  });

  it("accepts a deposit and emits Deposit", async () => {
    const amount = web3.utils.toWei("1", "ether");
    const receipt = await wallet.deposit({ from: depositor, value: amount });

    const event = receipt.logs.find((log) => log.event === "Deposit");
    assert.ok(event, "Deposit event must be emitted");
    assert.equal(event.args.sender, depositor);
    assert.equal(event.args.amount.toString(), amount);
    assert.equal((await wallet.getBalance()).toString(), amount);
  });

  it("accepts plain ETH transfers through receive()", async () => {
    const amount = web3.utils.toWei("0.25", "ether");
    await web3.eth.sendTransaction({ from: depositor, to: wallet.address, value: amount });
    assert.equal((await wallet.getBalance()).toString(), amount);
  });

  it("lets the owner withdraw and emits Withdraw", async () => {
    await wallet.deposit({ from: owner, value: web3.utils.toWei("1", "ether") });
    const before = BigInt(await web3.eth.getBalance(owner));

    const receipt = await wallet.withdraw(web3.utils.toWei("0.4", "ether"), { from: owner });
    const event = receipt.logs.find((log) => log.event === "Withdraw");
    assert.ok(event);
    assert.equal(event.args.recipient, owner);
    assert.equal((await wallet.getBalance()).toString(), web3.utils.toWei("0.6", "ether"));

    const after = BigInt(await web3.eth.getBalance(owner));
    assert.isTrue(after > before, "owner balance must increase after withdrawal");
  });

  it("rejects withdrawals from non-owners", async () => {
    await wallet.deposit({ from: depositor, value: web3.utils.toWei("1", "ether") });
    try {
      await wallet.withdraw(web3.utils.toWei("0.1", "ether"), { from: stranger });
      assert.fail("non-owner withdrawal must revert");
    } catch (error) {
      assert.include(error.message, "caller is not the owner");
    }
  });

  it("rejects withdrawals larger than the balance", async () => {
    await wallet.deposit({ from: owner, value: web3.utils.toWei("0.1", "ether") });
    try {
      await wallet.withdraw(web3.utils.toWei("1", "ether"), { from: owner });
      assert.fail("over-withdrawal must revert");
    } catch (error) {
      assert.include(error.message, "insufficient balance");
    }
  });

  it("rejects zero-value deposits", async () => {
    try {
      await wallet.deposit({ from: depositor, value: 0 });
      assert.fail("zero deposit must revert");
    } catch (error) {
      assert.include(error.message, "greater than zero");
    }
  });
});
