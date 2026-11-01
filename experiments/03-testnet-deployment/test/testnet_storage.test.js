const TestnetStorage = artifacts.require("TestnetStorage");

contract("TestnetStorage - deployment readiness", (accounts) => {
  const [deployer, user] = accounts;
  let storage;

  beforeEach(async () => {
    storage = await TestnetStorage.new(42, { from: deployer });
  });

  it("records the deployer and initial value", async () => {
    assert.equal(await storage.deployer(), deployer);
    assert.equal((await storage.getValue()).toString(), "42");
  });

  it("updates the value and emits ValueChanged", async () => {
    const receipt = await storage.setValue(137, { from: user });
    const event = receipt.logs.find((log) => log.event === "ValueChanged");
    assert.ok(event, "ValueChanged must be emitted");
    assert.equal(event.args.by, user);
    assert.equal(event.args.oldValue.toString(), "42");
    assert.equal(event.args.newValue.toString(), "137");
    assert.equal((await storage.getValue()).toString(), "137");
  });

  it("is writable by any account (public demo contract)", async () => {
    await storage.setValue(7, { from: user });
    assert.equal((await storage.getValue()).toString(), "7");
  });

  it("keeps independent state per deployment", async () => {
    const other = await TestnetStorage.new(100, { from: deployer });
    await storage.setValue(1, { from: user });
    assert.equal((await storage.getValue()).toString(), "1");
    assert.equal((await other.getValue()).toString(), "100");
  });
});
