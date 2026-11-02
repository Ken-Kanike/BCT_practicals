# Blockchain Lab — BCT Practicals

A reproducible portfolio of nine blockchain lab experiments covering Ethereum smart
contracts, local test networks, Hyperledger Fabric chaincode, public/permissioned
chain case studies, proof-of-work mining, and a full-stack course-payment DApp.

Every experiment includes runnable source code, a detailed README, captured terminal
output, and screenshots or JSON evidence from an actual local run.

## At a Glance

| Metric | Detail |
|---|---|
| **Experiments** | 9 of 9 implemented |
| **Automated tests** | 36 Truffle tests across Experiments 1–4 and 9 |
| **Fabric** | Asset-transfer chaincode deployed on a two-org test network |
| **Python demos** | 3 simulations: Hyperledger case study, multi-platform comparison, blockchain mining |
| **Lab records** | 9 DOCX reports plus the official experiment-list PDF in [`docs/`](docs/) |
| **Evidence** | Logs, screenshots, deployment JSON and generated diagrams under each `output/` directory |

## Contents

- [Experiment Index](#experiment-index)
- [What Each Experiment Covers](#what-each-experiment-covers)
- [Quick Start](#quick-start)
- [Test and Run Matrix](#test-and-run-matrix)
- [Experiment 9: Full-Stack DApp](#experiment-9-full-stack-dapp)
- [Documentation and Lab Records](#documentation-and-lab-records)
- [Repository Layout](#repository-layout)
- [Reproducibility Notes](#reproducibility-notes)

## Experiment Index

| # | Experiment | Stack | Evidence | README |
|---|---|---|---|---|
| 1 | Local blockchain with Truffle + Merkle root | Solidity, Truffle, Ganache, JavaScript | 8 tests, deployment/proof logs, screenshots | [Open](experiments/01-truffle-merkle/README.md) |
| 2 | Smart contracts with Solidity + Web3.js | Solidity, Web3.js, Truffle | 7 tests, deposit/withdraw/access-control logs | [Open](experiments/02-solidity-wallet/README.md) |
| 3 | Deployment and publishing on an Ethereum test network | Solidity, Truffle, Sepolia RPC, Ethers.js | 4 tests, Ganache deployment, live Sepolia check, unfunded-account preflight | [Open](experiments/03-testnet-deployment/README.md) |
| 4 | Cryptocurrency using Remix + MetaMask | Solidity, Remix/MetaMask workflow, Web3.js | 8 tests, token dashboard screenshots, UI transfer | [Open](experiments/04-remix-metamask-token/README.md) |
| 5 | Chaincode deployment in Hyperledger Fabric | Go chaincode, Fabric 2.4.9, Docker, WSL | Network/channel setup, Org1/Org2 approvals, invoke/query logs, screenshots | [Open](experiments/05-hyperledger-chaincode/README.md) |
| 6 | Case study on Hyperledger | IBM Food Trust, Python permissioned-ledger simulator | MSP/channel/endorsement/private-data/notary demo | [Open](experiments/06-hyperledger-case-study/README.md) |
| 7 | Case study on Bitcoin, Corda and Polkadot | Python ECDSA UTXO, Corda-style notary, Polkadot-style XCM | Real signatures, PoW, double-spend rejection, cross-chain demo | [Open](experiments/07-bitcoin-corda-polkadot/README.md) |
| 8 | Blockchain application with mining and validation | Python, ECDSA, Merkle tree, PoW, JSON persistence | Mining logs, invalid-transaction rejection, tamper detection | [Open](experiments/08-blockchain-mining/README.md) |
| 9 | Mini-project: course-payment DApp | Solidity, Truffle, Ganache, Ethers.js, Playwright | 9 tests, deployed contract, live UI purchase/withdrawal | [Open](experiments/09-course-payment-dapp/README.md) |

## What Each Experiment Covers

### Ethereum and Truffle (1–4, 9)

- **Experiment 1** builds a local Truffle/Ganache workflow and verifies data integrity
  with a Merkle tree. It includes a Solidity verifier, JavaScript proof generation, and
  tamper-detection tests.
- **Experiment 2** implements a deposit/withdraw wallet with ownership and access-control
  rules, then interacts with it from Web3.js.
- **Experiment 3** documents the complete testnet-deployment workflow: local deployment,
  Sepolia RPC connectivity, account preflight, and the exact commands needed once a
  funded account is available.
- **Experiment 4** follows the Remix + MetaMask token workflow and includes a local
  dashboard for transfer and balance checks.
- **Experiment 9** combines a Solidity course-payment contract, a Truffle test suite,
  deployment export, an Ethers.js UI, and Playwright screenshots.

### Hyperledger Fabric (5)

The `asset-transfer` Go chaincode is packaged, approved by Org1 and Org2, committed to
`mychannel`, and exercised with real invokes and queries. The experiment README includes
the full lifecycle, topology, output, and the Docker cleanup notes.

### Case Studies and Simulations (6–8)

- **Experiment 6** explains Hyperledger through the IBM Food Trust/Walmart case and a
  Python simulator that demonstrates permissioning, private data, endorsement, and
  tamper detection.
- **Experiment 7** compares Bitcoin, Corda, and Polkadot, with executable demos for UTXO
  signing, PoW, notary double-spend rejection, and XCM-style cross-chain messaging.
- **Experiment 8** implements signed transactions, Merkle roots, PoW mining, chain
  validation, tamper detection, and JSON persistence.

## Quick Start

### Prerequisites

- Node.js 20+ and npm
- Python 3.12+
- Docker Desktop + WSL Ubuntu for Experiment 5
- Microsoft Edge for Playwright screenshots in Experiment 9

Install the root Node dependencies:

```bash
npm install
```

Install the Python dependency used by the case-study simulations:

```bash
pip install ecdsa
```

The report-rendering scripts additionally use `Pillow`, `matplotlib`, and
`python-docx` when regenerating diagrams or DOCX output:

```bash
pip install pillow matplotlib python-docx
```

### Start Ganache

All Ethereum experiments use the local Ganache network on port `7545`:

```bash
npm run ganache
```

Keep that terminal running while compiling, testing, or serving the DApp.

### Run a Truffle Experiment

From any Ethereum experiment directory:

```bash
cd experiments/01-truffle-merkle
npx truffle test
```

Experiments 1–4 use their own `truffle-config.js`; Experiment 9 uses the same pattern
and additionally exports its deployment address for the UI.

### Run the Python Simulations

```bash
python experiments/06-hyperledger-case-study/simulator/fabric_sim.py
python experiments/07-bitcoin-corda-polkadot/simulator/platforms_demo.py
python experiments/08-blockchain-mining/simulator/blockchain_app.py
```

### Run the Fabric Demo

The script assumes a Fabric `test-network` checkout under `$FABRIC_SAMPLES` or
`$HOME/fabric-samples`:

```bash
bash experiments/05-hyperledger-chaincode/scripts/fabric_demo.sh
```

See the [Experiment 5 README](experiments/05-hyperledger-chaincode/README.md) for the
full network, channel, and chaincode lifecycle.

## Test and Run Matrix

| # | Command | Tests / Demo | More |
|---|---|---|---|
| 1 | `cd experiments/01-truffle-merkle && npx truffle test` | 8 tests + Merkle demo | [README](experiments/01-truffle-merkle/README.md) |
| 2 | `cd experiments/02-solidity-wallet && npx truffle test` | 7 tests | [README](experiments/02-solidity-wallet/README.md) |
| 3 | `cd experiments/03-testnet-deployment && npx truffle test` | 4 tests + Sepolia preflight | [README](experiments/03-testnet-deployment/README.md) |
| 4 | `cd experiments/04-remix-metamask-token && npx truffle test` | 8 tests + token UI | [README](experiments/04-remix-metamask-token/README.md) |
| 5 | `bash experiments/05-hyperledger-chaincode/scripts/fabric_demo.sh` | Fabric lifecycle + invoke/query | [README](experiments/05-hyperledger-chaincode/README.md) |
| 6 | `python experiments/06-hyperledger-case-study/simulator/fabric_sim.py` | Permissioned-ledger simulation | [README](experiments/06-hyperledger-case-study/README.md) |
| 7 | `python experiments/07-bitcoin-corda-polkadot/simulator/platforms_demo.py` | Bitcoin/Corda/Polkadot demo | [README](experiments/07-bitcoin-corda-polkadot/README.md) |
| 8 | `python experiments/08-blockchain-mining/simulator/blockchain_app.py` | Mining, validation and tamper detection | [README](experiments/08-blockchain-mining/README.md) |
| 9 | `cd experiments/09-course-payment-dapp && npx truffle test` | 9 tests + full-stack DApp | [README](experiments/09-course-payment-dapp/README.md) |

All Truffle commands assume Ganache is running on `127.0.0.1:7545`.

## Experiment 9: Full-Stack DApp

Deploy the contract and export its address:

```bash
cd experiments/09-course-payment-dapp
npx truffle migrate --reset --network development
npx truffle exec scripts/export_deployment.js --network development
```

Serve the UI from the repository root:

```bash
cd ../..
python -m http.server 8080 --bind 127.0.0.1
```

Open:

```text
http://127.0.0.1:8080/experiments/09-course-payment-dapp/ui/
```

The UI supports course purchase, enrollment display, and owner withdrawal. The
[Experiment 9 README](experiments/09-course-payment-dapp/README.md) documents the
contract model, security checks, and screenshot workflow.

## Documentation and Lab Records

- [Official experiment list — PDF](docs/BCT_Experiment_List.pdf)
- [Experiment 1 lab record](docs/BCT_EXP1.docx)
- [Experiment 2 lab record](docs/BCT_EXP2.docx)
- [Experiment 3 lab record](docs/BCT_EXP3.docx)
- [Experiment 4 lab record](docs/BCT_EXP4.docx)
- [Experiment 5 lab record](docs/BCT_EXP5.docx)
- [Experiment 6 lab record](docs/BCT_EXP6.docx)
- [Experiment 7 lab record](docs/BCT_EXP7.docx)
- [Experiment 8 lab record](docs/BCT_EXP8.docx)
- [Experiment 9 lab record](docs/BCT_EXP9.docx)

Each experiment README contains its aim, theory, contract or simulator design,
execution commands, actual output, and result discussion.

## Repository Layout

```text
BCT_practicals/
├── docs/                 # experiment list, redacted lab records and reports
├── experiments/
│   ├── 01-truffle-merkle/
│   ├── 02-solidity-wallet/
│   ├── 03-testnet-deployment/
│   ├── 04-remix-metamask-token/
│   ├── 05-hyperledger-chaincode/
│   ├── 06-hyperledger-case-study/
│   ├── 07-bitcoin-corda-polkadot/
│   ├── 08-blockchain-mining/
│   └── 09-course-payment-dapp/
├── scripts/              # terminal renderers, report builders and diagrams
├── package.json          # Truffle, Ganache, Ethers, Web3, Playwright
└── README.md
```

Each experiment directory contains some or all of:

```text
README.md       # aim, theory, implementation, output, result
contracts/      # Solidity contracts (Ethereum experiments)
simulator/      # Python simulations (case-study experiments)
test/           # Truffle test suites
output/         # logs, JSON state, diagrams and screenshots
scripts/        # deployment, interaction and helper scripts
migrations/     # Truffle migrations
ui/             # browser interface (Experiment 9)
```

## Reproducibility Notes

- **Local-only wallet material:** all Ethereum keys shown here are Ganache test keys.
  They are intentionally local and must never be used on a public network. The current
  tree does not contain production API keys or funded accounts.
- **Experiment 3 is honest about Sepolia:** the local Ganache deployment and live Sepolia
  RPC/account preflight were executed, but a public Sepolia deployment was not performed
  because no funded testnet account/API key was used.
- **Experiment 5 cleanup:** the Fabric Docker network and heavy images were removed after
  the lab. The chaincode source, demo script, and captured evidence remain.
- **Evidence over mockups:** screenshots come from real local runs. The committed logs
  and JSON files are the raw execution artifacts, including the tamper/invalid-input
  cases.
- **Redacted reports:** the DOCX lab records in `docs/` have student name/roll fields and
  embedded wallet secrets removed for public distribution.

## Verification

Check the recent history and run any experiment from the matrix above:

```bash
git log --oneline -10
npx truffle test --config experiments/01-truffle-merkle/truffle-config.js
```

The test suites and simulations are self-contained once the prerequisites are installed.
For exact per-experiment output and screenshots, open the corresponding README and
`output/` directory.
