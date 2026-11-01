const SimpleCryptoCurrency = artifacts.require("SimpleCryptoCurrency");

contract("SimpleCryptoCurrency - cryptocurrency token", (accounts) => {
  const [deployer, alice, bob, carol] = accounts;
  const DECIMALS = 18;
  const INITIAL_SUPPLY = 1000000;
  const UNIT = 10n ** 18n;

  let token;

  beforeEach(async () => {
    token = await SimpleCryptoCurrency.new("MyToken", "MTK", DECIMALS, INITIAL_SUPPLY, {
      from: deployer
    });
  });

  it("stores token metadata", async () => {
    assert.equal(await token.name(), "MyToken");
    assert.equal(await token.symbol(), "MTK");
    assert.equal((await token.decimals()).toString(), String(DECIMALS));
    assert.equal(await token.owner(), deployer);
  });

  it("mints the whole initial supply to the deployer", async () => {
    const expected = BigInt(INITIAL_SUPPLY) * UNIT;
    assert.equal((await token.totalSupply()).toString(), expected.toString());
    assert.equal((await token.balanceOf(deployer)).toString(), expected.toString());
  });

  it("transfers tokens and emits Transfer", async () => {
    const amount = 1000n * UNIT;
    const receipt = await token.transfer(alice, amount, { from: deployer });
    const event = receipt.logs.find((log) => log.event === "Transfer");

    assert.ok(event);
    assert.equal(event.args.from, deployer);
    assert.equal(event.args.to, alice);
    assert.equal(event.args.value.toString(), amount.toString());
    assert.equal((await token.balanceOf(alice)).toString(), amount.toString());
  });

  it("rejects a transfer larger than the balance", async () => {
    try {
      await token.transfer(alice, (BigInt(INITIAL_SUPPLY) + 1n) * UNIT, { from: deployer });
      assert.fail("over-transfer must revert");
    } catch (error) {
      assert.include(error.message, "insufficient balance");
    }
  });

  it("rejects transfers to the zero address", async () => {
    try {
      await token.transfer("0x0000000000000000000000000000000000000000", UNIT, { from: deployer });
      assert.fail("zero-address transfer must revert");
    } catch (error) {
      assert.include(error.message, "zero address");
    }
  });

  it("approves an allowance and emits Approval", async () => {
    const amount = 5000n * UNIT;
    const receipt = await token.approve(bob, amount, { from: alice });
    const event = receipt.logs.find((log) => log.event === "Approval");

    assert.ok(event);
    assert.equal(event.args.owner, alice);
    assert.equal(event.args.spender, bob);
    assert.equal((await token.allowance(alice, bob)).toString(), amount.toString());
  });

  it("executes transferFrom within the allowance", async () => {
    await token.transfer(alice, 10000n * UNIT, { from: deployer });
    await token.approve(bob, 4000n * UNIT, { from: alice });

    const receipt = await token.transferFrom(alice, carol, 3000n * UNIT, { from: bob });
    const event = receipt.logs.find((log) => log.event === "Transfer");
    assert.ok(event);
    assert.equal(event.args.from, alice);
    assert.equal(event.args.to, carol);

    assert.equal((await token.balanceOf(carol)).toString(), (3000n * UNIT).toString());
    assert.equal((await token.allowance(alice, bob)).toString(), (1000n * UNIT).toString());
  });

  it("rejects transferFrom above the allowance", async () => {
    await token.transfer(alice, 1000n * UNIT, { from: deployer });
    await token.approve(bob, 100n * UNIT, { from: alice });

    try {
      await token.transferFrom(alice, carol, 200n * UNIT, { from: bob });
      assert.fail("over-allowance transfer must revert");
    } catch (error) {
      assert.include(error.message, "insufficient allowance");
    }
  });
});
