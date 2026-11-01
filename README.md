# Blockchain Lab — BCT Practicals

**Thadomal Shahani Engineering College**  
Department of Artificial Intelligence and Data Science  
BE / SEM VII — Blockchain Lab (2026–27)

This repository contains the code, tests, execution logs and screenshots for all
nine experiments in the official Blockchain Lab experiment list. Each experiment
has its own README with theory, implementation details and real output.

---

## Experiment Index

| # | Experiment | Implementation | Evidence |
|---|---|---|---|
| 1 | Local blockchain with Truffle + Merkle root | Solidity, Truffle, Ganache, JavaScript | 8 tests, deployment and proof logs, screenshots |
| 2 | Smart contracts with Solidity + Web3.js | Solidity, Web3.js, Truffle | 7 tests, deposit/withdraw/access-control logs |
| 3 | Deployment on an Ethereum test network | Solidity, Truffle, Sepolia RPC | 4 tests, Ganache deployment, live Sepolia chain check, unfunded-account preflight |
| 4 | Remix + MetaMask cryptocurrency (MTK) | Solidity, Remix/MetaMask workflow, Web3.js | 8 tests, token dashboard screenshots, real UI transfer |
| 5 | Chaincode deployment in Hyperledger Fabric | Go chaincode, Fabric 2.4.9, Docker, WSL | Network + channel, Org1/Org2 approvals, invoke/query logs, screenshots |
| 6 | Case study on Hyperledger | IBM Food Trust, Python permissioned-ledger simulator | MSP/channel/endorsement/private-data/notary demo |
| 7 | Case study on Bitcoin, Corda and Polkadot | Python ECDSA UTXO, Corda-style notary, Polkadot-style XCM | Real signatures, PoW, notary double-spend rejection, cross-chain demo |
| 8 | Blockchain application: transactions, mining, validation | Python, ECDSA, Merkle tree, PoW, JSON persistence | Mining logs, invalid-transaction rejection, tamper detection |
| 9 | Mini-project: course payment DApp | Solidity, Truffle, Ganache, Ethers.js, Playwright | 9 tests, deployed contract, live UI purchase and owner withdrawal |

Each experiment directory contains:

```text
experiments/NN-name/
├── README.md          # aim, theory, implementation, actual output, screenshots
├── contracts/         # Solidity (Ethereum experiments)
├── simulator/         # Python (case-study experiments)
├── test/              # Truffle tests
├── output/            # logs, JSON state, screenshots
└── scripts/           # experiment-specific helpers
```

---

## Quick Start

### Prerequisites

- Node.js 20+ and npm
- Python 3.12+ with `python-docx`, `Pillow`, `matplotlib`
- Docker Desktop + WSL Ubuntu (only for Experiment 5)
- Microsoft Edge (used by Playwright for screenshots)

Install root Node dependencies:

```bash
npm install
```

Install Python dependencies used by the simulations:

```bash
pip install ecdsa
```

### Ethereum experiments (1–4, 9)

Start Ganache on port 7545:

```bash
npx ganache --port 7545 --deterministic --chain.chainId 1337
```

Then, from an experiment directory:

```bash
npx truffle test --network development
```

Experiment 9 additionally needs:

```bash
cd experiments/09-course-payment-dapp
npx truffle migrate --reset --network development
npx truffle exec scripts/export_deployment.js --network development
```

Serve the UI from the repository root:

```bash
python -m http.server 8080 --bind 127.0.0.1
```

Open `http://127.0.0.1:8080/experiments/09-course-payment-dapp/ui/index.html`.

### Python case studies (6–8)

```bash
python experiments/06-hyperledger-case-study/simulator/fabric_sim.py
python experiments/07-bitcoin-corda-polkadot/simulator/platforms_demo.py
python experiments/08-blockchain-mining/simulator/blockchain_app.py
```

### Hyperledger Fabric (5)

The chaincode source and demo script are in
`experiments/05-hyperledger-chaincode/`. The experiment README documents the
Fabric 2.4.9 test-network steps, the Go chaincode lifecycle and the actual
invoke/query output. The Fabric Docker network was shut down after the lab and
its heavy images were removed during final cleanup; the chaincode source remains
in this repository.

---

## Notes

- **Sepolia deployment (Experiment 3):** the local Ganache deployment and a live
  Sepolia RPC connectivity check were executed. A public Sepolia deployment was
  not performed because no funded testnet account/API key was available; this is
  documented honestly in the experiment README.
- **Hyperledger Fabric (Experiment 5):** the official `test-network` was used with
  `mychannel`, Org1 and Org2. The `asset-transfer` chaincode was packaged,
  approved by both organizations, committed, and exercised with real invokes and
  queries.
- **Local-only keys:** all Ethereum accounts and keys used here are public Ganache
  test accounts. Never use them on a public network.
- **Screenshots:** captured with Playwright and Microsoft Edge against the running
  local applications; no mock screenshots.

---

## Verification

Recent commits:

```bash
git log --oneline -10
```

The test suites can be re-run with the commands above. Execution logs and
screenshots for every experiment are committed under `experiments/*/output/`.

---

## Repository Layout

```text
BCT_practicals/
├── docs/                 # official experiment list and lab-record docx files
├── experiments/          # 01–09, each with README, code, tests and output
├── scripts/              # shared renderers and diagram generators
├── package.json          # Truffle, Ganache, Ethers, Playwright, Web3
└── README.md
```
