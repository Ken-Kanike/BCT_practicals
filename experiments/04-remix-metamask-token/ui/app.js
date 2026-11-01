const state = {
  config: null,
  provider: null,
  contract: null,
  accounts: [],
  decimals: 18
};

const LABELS = ["deployer", "alice", "bob", "carol"];

function short(address) {
  return `${address.slice(0, 8)}...${address.slice(-6)}`;
}

function setStatus(message, kind = "") {
  const el = document.getElementById("status");
  el.textContent = message;
  el.className = `status ${kind}`.trim();
}

async function loadConfig() {
  const response = await fetch("config.json", { cache: "no-store" });
  if (!response.ok) throw new Error("config.json not found - run the deployment script first");
  state.config = await response.json();
}

async function init() {
  await loadConfig();

  state.provider = new ethers.JsonRpcProvider(state.config.rpcUrl);
  const network = await state.provider.getNetwork();
  document.getElementById("chainBadge").textContent = `chain ${network.chainId}`;

  state.accounts = await Promise.all(
    LABELS.map(async (label, index) => {
      const signer = await state.provider.getSigner(index);
      return { label, index, address: await signer.getAddress() };
    })
  );

  state.contract = new ethers.Contract(
    state.config.address,
    state.config.abi,
    state.provider
  );

  const [name, symbol, decimals, totalSupply, owner, blockNumber] = await Promise.all([
    state.contract.name(),
    state.contract.symbol(),
    state.contract.decimals(),
    state.contract.totalSupply(),
    state.contract.owner(),
    state.provider.getBlockNumber()
  ]);

  state.decimals = Number(decimals);
  document.getElementById("tokenName").textContent = name;
  document.getElementById("tokenSymbol").textContent = symbol;
  document.getElementById("tokenDecimals").textContent = decimals.toString();
  document.getElementById("tokenOwner").textContent = short(owner);
  document.getElementById("totalSupply").textContent = Number(
    ethers.formatUnits(totalSupply, decimals)
  ).toLocaleString("en-US");
  document.getElementById("contractAddress").textContent = state.config.address;
  document.getElementById("contractAddress").title = state.config.address;
  document.getElementById("blockNumber").textContent = `block ${blockNumber}`;

  const fromSelect = document.getElementById("fromAccount");
  const toSelect = document.getElementById("toAccount");
  state.accounts.forEach((account, index) => {
    const label = `${account.label} · ${short(account.address)}`;
    fromSelect.add(new Option(label, String(index)));
    toSelect.add(new Option(label, String(index)));
  });
  toSelect.value = "1";

  await refreshBalances();
  fromSelect.addEventListener("change", refreshBalances);
}

async function refreshBalances() {
  const selectedFrom = document.getElementById("fromAccount").value || "0";
  const rows = await Promise.all(
    state.accounts.map(async (account) => {
      const balance = await state.contract.balanceOf(account.address);
      return { ...account, balance };
    })
  );

  const tbody = document.getElementById("balances");
  tbody.innerHTML = rows
    .map(
      (row) => `
      <tr>
        <td><span class="tag">${row.label}</span>${row.index === Number(selectedFrom) ? " <small>· source</small>" : ""}</td>
        <td class="addr">${row.address}</td>
        <td class="right balance">${Number(ethers.formatUnits(row.balance, state.decimals)).toLocaleString("en-US")}</td>
      </tr>`
    )
    .join("");
}

async function transfer(event) {
  event.preventDefault();
  const button = document.getElementById("transferButton");
  const fromIndex = Number(document.getElementById("fromAccount").value);
  const toIndex = Number(document.getElementById("toAccount").value);
  const amount = document.getElementById("amount").value;

  if (fromIndex === toIndex) {
    setStatus("Choose two different accounts.", "err");
    return;
  }

  button.disabled = true;
  setStatus(`Sending ${amount} MTK from ${state.accounts[fromIndex].label} to ${state.accounts[toIndex].label}...`);

  try {
    const signer = await state.provider.getSigner(fromIndex);
    const contract = state.contract.connect(signer);
    const tx = await contract.transfer(
      state.accounts[toIndex].address,
      ethers.parseUnits(amount, state.decimals)
    );
    setStatus(`Transaction submitted: ${tx.hash}. Waiting for confirmation...`);
    const receipt = await tx.wait();
    setStatus(
      `Confirmed in block ${receipt.blockNumber} · gas ${receipt.gasUsed.toString()} · tx ${tx.hash}`,
      "ok"
    );
    await refreshBalances();
    document.getElementById("blockNumber").textContent = `block ${await state.provider.getBlockNumber()}`;
  } catch (error) {
    setStatus(error.shortMessage || error.reason || error.message, "err");
  } finally {
    button.disabled = false;
  }
}

document.getElementById("transferForm").addEventListener("submit", transfer);

init().catch((error) => {
  setStatus(`Initialisation failed: ${error.message}`, "err");
});
