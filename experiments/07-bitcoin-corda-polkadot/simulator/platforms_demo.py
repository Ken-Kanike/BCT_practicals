#!/usr/bin/env python3
"""Experiment 7 - Bitcoin, Corda and Polkadot case-study demos."""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field

from ecdsa import SECP256k1, SigningKey, VerifyingKey
from ecdsa.util import sigdecode_der, sigencode_der

COIN = 100_000_000


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def rule(title: str) -> None:
    print(f"\n{'=' * 76}\n{title}\n{'=' * 76}")


class Wallet:
    def __init__(self, name: str) -> None:
        self.name = name
        self._sk = SigningKey.generate(curve=SECP256k1)
        self._vk = self._sk.get_verifying_key()
        self.pubkey = self._vk.to_string().hex()
        self.address = sha256(self.pubkey)[:40]

    def sign(self, message: str) -> str:
        return self._sk.sign_deterministic(
            message.encode(), hashfunc=hashlib.sha256, sigencode=sigencode_der
        ).hex()


def verify_signature(pubkey_hex: str, message: str, signature_hex: str) -> bool:
    try:
        vk = VerifyingKey.from_string(bytes.fromhex(pubkey_hex), curve=SECP256k1)
        return vk.verify(
            bytes.fromhex(signature_hex),
            message.encode(),
            hashfunc=hashlib.sha256,
            sigdecode=sigdecode_der,
        )
    except Exception:
        return False


@dataclass
class TxIn:
    prev_tx: str
    prev_index: int
    pubkey: str = ""
    signature: str = ""


@dataclass
class TxOut:
    value: int
    address: str


@dataclass
class Transaction:
    inputs: list[TxIn]
    outputs: list[TxOut]
    tag: str = ""

    def unsigned_payload(self) -> str:
        return json.dumps(
            {
                "inputs": [
                    {"prev_tx": txin.prev_tx, "prev_index": txin.prev_index}
                    for txin in self.inputs
                ],
                "outputs": [
                    {"value": txout.value, "address": txout.address}
                    for txout in self.outputs
                ],
                "tag": self.tag,
            },
            sort_keys=True,
        )

    def txid(self) -> str:
        return sha256(self.unsigned_payload())

    def sign_input(self, index: int, wallet: Wallet) -> None:
        self.inputs[index].pubkey = wallet.pubkey
        self.inputs[index].signature = wallet.sign(self.txid())


@dataclass
class Block:
    index: int
    previous_hash: str
    transactions: list[Transaction]
    nonce: int
    hash: str

    def compute_hash(self) -> str:
        header = "|".join(
            [
                str(self.index),
                self.previous_hash,
                str(self.nonce),
                ",".join(tx.txid() for tx in self.transactions),
            ]
        )
        return sha256(header)


class BitcoinLedger:
    def __init__(self) -> None:
        self.utxos: dict[tuple[str, int], TxOut] = {}
        self.blocks: list[Block] = []
        self.mempool: list[Transaction] = []

    def _apply(self, tx: Transaction) -> None:
        for txin in tx.inputs:
            self.utxos.pop((txin.prev_tx, txin.prev_index), None)
        for index, txout in enumerate(tx.outputs):
            self.utxos[(tx.txid(), index)] = txout

    def _verify(self, tx: Transaction) -> None:
        if not tx.inputs:
            raise ValueError("coinbase transactions cannot be submitted by users")
        if not tx.outputs:
            raise ValueError("transaction must have at least one output")
        if any(txout.value <= 0 for txout in tx.outputs):
            raise ValueError("output values must be positive")

        seen: set[tuple[str, int]] = set()
        input_total = 0
        for txin in tx.inputs:
            key = (txin.prev_tx, txin.prev_index)
            if key in seen:
                raise ValueError("duplicate input in transaction")
            seen.add(key)
            if key not in self.utxos:
                raise ValueError(f"UTXO {key} does not exist or is already spent")
            utxo = self.utxos[key]
            if sha256(txin.pubkey)[:40] != utxo.address:
                raise ValueError("input public key does not own the UTXO")
            if not verify_signature(txin.pubkey, tx.txid(), txin.signature):
                raise ValueError("invalid ECDSA signature")
            input_total += utxo.value

        if sum(txout.value for txout in tx.outputs) > input_total:
            raise ValueError("outputs exceed inputs")

        for pending in self.mempool:
            pending_keys = {(i.prev_tx, i.prev_index) for i in pending.inputs}
            if seen & pending_keys:
                raise ValueError("double spend: UTXO already used by a mempool transaction")

    def submit(self, tx: Transaction) -> None:
        self._verify(tx)
        self.mempool.append(tx)

    def mine(self, miner: Wallet, difficulty: int = 3, reward: int = 50 * COIN) -> Block:
        coinbase = Transaction(
            inputs=[],
            outputs=[TxOut(reward, miner.address)],
            tag=f"coinbase-{len(self.blocks)}",
        )
        transactions = [coinbase, *self.mempool]
        previous_hash = self.blocks[-1].hash if self.blocks else "0" * 64
        nonce = 0
        while True:
            header = "|".join(
                [
                    str(len(self.blocks)),
                    previous_hash,
                    str(nonce),
                    ",".join(tx.txid() for tx in transactions),
                ]
            )
            block_hash = sha256(header)
            if block_hash.startswith("0" * difficulty):
                break
            nonce += 1

        block = Block(len(self.blocks), previous_hash, transactions, nonce, block_hash)
        self.blocks.append(block)
        for tx in transactions:
            self._apply(tx)
        self.mempool.clear()
        return block

    def balance(self, wallet: Wallet) -> int:
        return sum(txout.value for txout in self.utxos.values() if txout.address == wallet.address)

    def utxos_for(self, wallet: Wallet) -> list[tuple[tuple[str, int], TxOut]]:
        return [
            (key, txout)
            for key, txout in self.utxos.items()
            if txout.address == wallet.address
        ]

    def validate_chain(self) -> bool:
        for index, block in enumerate(self.blocks):
            if block.compute_hash() != block.hash:
                return False
            if index > 0 and block.previous_hash != self.blocks[index - 1].hash:
                return False
        return True


def btc(satoshis: int) -> str:
    return f"{satoshis / COIN:.8f} BTC"


def demo_bitcoin() -> None:
    rule("PART A - BITCOIN: UTXO, ECDSA SIGNING AND PROOF OF WORK")
    alice, bob, carol = Wallet("Alice"), Wallet("Bob"), Wallet("Carol")
    ledger = BitcoinLedger()

    genesis = ledger.mine(alice, difficulty=3, reward=100 * COIN)
    print(f"Genesis block 0: nonce={genesis.nonce} hash={genesis.hash}")
    print(f"Alice balance after genesis coinbase: {btc(ledger.balance(alice))}")

    genesis_tx = genesis.transactions[0]
    payment = Transaction(
        inputs=[TxIn(genesis_tx.txid(), 0)],
        outputs=[
            TxOut(30 * COIN, bob.address),
            TxOut(20 * COIN, carol.address),
            TxOut(50 * COIN, alice.address),
        ],
    )
    payment.sign_input(0, alice)
    ledger.submit(payment)
    print(f"\nAlice -> Bob 30, Carol 20, change 50")
    print(f"txid: {payment.txid()}")
    print(f"ECDSA signature valid: {verify_signature(payment.inputs[0].pubkey, payment.txid(), payment.inputs[0].signature)}")
    block1 = ledger.mine(alice, difficulty=3)
    print(f"Block 1 mined: nonce={block1.nonce} hash={block1.hash}")
    print(f"Balances: Alice={btc(ledger.balance(alice))} Bob={btc(ledger.balance(bob))} Carol={btc(ledger.balance(carol))}")

    bob_utxo_key, bob_utxo = ledger.utxos_for(bob)[0]
    spend_one = Transaction(
        inputs=[TxIn(bob_utxo_key[0], bob_utxo_key[1])],
        outputs=[TxOut(10 * COIN, carol.address), TxOut(20 * COIN, bob.address)],
    )
    spend_one.sign_input(0, bob)
    spend_two = Transaction(
        inputs=[TxIn(bob_utxo_key[0], bob_utxo_key[1])],
        outputs=[TxOut(10 * COIN, alice.address), TxOut(20 * COIN, bob.address)],
    )
    spend_two.sign_input(0, bob)

    ledger.submit(spend_one)
    try:
        ledger.submit(spend_two)
    except ValueError as error:
        print(f"\nDouble-spend in mempool rejected: {error}")

    block2 = ledger.mine(alice, difficulty=3)
    print(f"Block 2 mined: nonce={block2.nonce} hash={block2.hash}")
    try:
        ledger.submit(spend_two)
    except ValueError as error:
        print(f"Double-spend after mining rejected: {error}")

    carol_utxo_key, carol_utxo = ledger.utxos_for(carol)[0]
    tampered = Transaction(
        inputs=[TxIn(carol_utxo_key[0], carol_utxo_key[1])],
        outputs=[TxOut(carol_utxo.value, alice.address)],
    )
    tampered.sign_input(0, carol)
    tampered.outputs[0].value = 300 * COIN
    try:
        ledger.submit(tampered)
    except ValueError as error:
        print(f"Tampered transaction rejected: {error}")

    tampered.outputs[0].value = carol_utxo.value
    ledger.submit(tampered)
    block3 = ledger.mine(alice, difficulty=3)
    print(f"Block 3 mined after restoring the value: nonce={block3.nonce} hash={block3.hash}")
    print(f"Final balances: Alice={btc(ledger.balance(alice))} Bob={btc(ledger.balance(bob))} Carol={btc(ledger.balance(carol))}")
    print(f"Chain valid before tampering: {ledger.validate_chain()}")

    ledger.blocks[1].transactions[0].outputs[0].value = 999 * COIN
    print(f"Chain valid after tampering block 1: {ledger.validate_chain()}")


@dataclass(frozen=True)
class CordaState:
    state_id: str
    issuer: str
    owner: str
    amount: int
    participants: frozenset[str]


class CordaNetwork:
    def __init__(self) -> None:
        self.states: dict[str, CordaState] = {}
        self.consumed: set[str] = set()

    def _new_id(self, issuer: str, owner: str, amount: int) -> str:
        return sha256(f"{issuer}:{owner}:{amount}:{len(self.states)}:{time.time_ns()}")[:16]

    def issue(self, issuer: str, owner: str, amount: int) -> CordaState:
        if amount <= 0:
            raise ValueError("contract: amount must be positive")
        if issuer == owner:
            raise ValueError("contract: issuer and owner must differ")
        state = CordaState(
            state_id=self._new_id(issuer, owner, amount),
            issuer=issuer,
            owner=owner,
            amount=amount,
            participants=frozenset({issuer, owner}),
        )
        self.states[state.state_id] = state
        return state

    def transfer(self, state_id: str, new_owner: str, signatures: set[str]) -> CordaState:
        if state_id in self.consumed:
            raise PermissionError("notary: state has already been consumed")
        state = self.states[state_id]
        required = state.participants | {new_owner}
        missing = required - signatures
        if missing:
            raise PermissionError(f"contract: missing signatures from {sorted(missing)}")
        if new_owner == state.owner:
            raise ValueError("contract: new owner must differ from current owner")

        new_state = CordaState(
            state_id=self._new_id(state.issuer, new_owner, state.amount),
            issuer=state.issuer,
            owner=new_owner,
            amount=state.amount,
            participants=frozenset({state.issuer, new_owner}),
        )
        self.consumed.add(state_id)
        self.states[new_state.state_id] = new_state
        return new_state

    def visible_to(self, state_id: str, party: str) -> CordaState | None:
        state = self.states[state_id]
        return state if party in state.participants else None


def demo_corda() -> None:
    rule("PART B - CORDA: PRIVATE STATE, CONTRACT AND NOTARY")
    corda = CordaNetwork()
    issued = corda.issue("Alice", "Bob", 100)
    print(f"Issued state {issued.state_id}: {issued.issuer} -> {issued.owner}, amount={issued.amount}")
    print(f"Participants: {sorted(issued.participants)}")

    transferred = corda.transfer(issued.state_id, "Carol", {"Alice", "Bob", "Carol"})
    print(f"\nTransferred {transferred.amount} units to Carol")
    print(f"New state {transferred.state_id}: participants={sorted(transferred.participants)}")
    print(f"Old state consumed by notary: {issued.state_id in corda.consumed}")

    try:
        corda.transfer(issued.state_id, "Dave", {"Alice", "Bob", "Dave"})
    except PermissionError as error:
        print(f"Double-spend rejected: {error}")

    try:
        corda.transfer(transferred.state_id, "Dave", {"Alice"})
    except PermissionError as error:
        print(f"Incomplete signatures rejected: {error}")

    print(f"Bob can see new state: {corda.visible_to(transferred.state_id, 'Bob') is not None}")
    print(f"Dave can see new state: {corda.visible_to(transferred.state_id, 'Dave') is not None}")
    print(f"Active (unconsumed) states: {[s.state_id for s in corda.states.values() if s.state_id not in corda.consumed]}")


@dataclass
class Validator:
    name: str
    stake: int


@dataclass
class XcmMessage:
    sender: str
    receiver: str
    payload: dict
    message_id: str


@dataclass
class Parachain:
    name: str
    state: dict = field(default_factory=dict)

    def apply_xcm(self, message: XcmMessage) -> None:
        if message.payload.get("action") == "lock_and_mint":
            self.state["minted"] = self.state.get("minted", 0) + message.payload["amount"]
            self.state["asset"] = message.payload.get("asset")
            self.state["source"] = message.sender


class RelayChain:
    def __init__(self, validators: list[Validator], active_slots: int = 3) -> None:
        self.validators = validators
        self.active_slots = active_slots
        self.active: list[Validator] = []
        self.parachains: dict[str, Parachain] = {}

    def elect(self) -> list[Validator]:
        self.active = sorted(self.validators, key=lambda v: v.stake, reverse=True)[: self.active_slots]
        return self.active

    def register_parachain(self, parachain: Parachain) -> None:
        self.parachains[parachain.name] = parachain

    def send_xcm(self, sender: str, receiver: str, payload: dict) -> XcmMessage:
        if sender not in self.parachains:
            raise ValueError(f"unknown sender parachain: {sender}")
        if receiver not in self.parachains:
            raise ValueError(f"unknown receiver parachain: {receiver}")
        if len(self.active) < 2:
            raise PermissionError("relay chain has no active validator set")

        approvals = [validator.name for validator in self.active[:2]]
        message = XcmMessage(
            sender=sender,
            receiver=receiver,
            payload=payload,
            message_id=sha256(json.dumps(payload, sort_keys=True))[:16],
        )
        self.parachains[receiver].apply_xcm(message)
        print(f"Relay approvals: {approvals} (threshold 2/3)")
        return message

    def governance_vote(self, proposal: str, yes: int, no: int) -> bool:
        passed = yes > no
        print(f"Governance vote '{proposal}': yes={yes} DOT, no={no} DOT -> {'PASSED' if passed else 'REJECTED'}")
        if passed:
            print("Forkless runtime upgrade enacted by the relay chain.")
        return passed


def demo_polkadot() -> None:
    rule("PART C - POLKADOT: RELAY CHAIN, PARACHAINS AND XCM")
    validators = [
        Validator("V1", 1000),
        Validator("V2", 800),
        Validator("V3", 600),
        Validator("V4", 400),
        Validator("V5", 200),
    ]
    relay = RelayChain(validators, active_slots=3)
    active = relay.elect()
    print(f"NPoS active validator set: {[(v.name, v.stake) for v in active]}")

    relay.register_parachain(Parachain("DeFi", {"minted": 0}))
    relay.register_parachain(Parachain("Identity", {}))
    relay.register_parachain(Parachain("SupplyChain", {"minted": 0}))
    print(f"Registered parachains: {list(relay.parachains)}")

    message = relay.send_xcm(
        "DeFi", "SupplyChain", {"action": "lock_and_mint", "asset": "DOT", "amount": 25}
    )
    print(f"XCM {message.message_id}: {message.sender} -> {message.receiver} {message.payload}")
    print(f"SupplyChain state: {relay.parachains['SupplyChain'].state}")

    try:
        relay.send_xcm("DeFi", "UnknownChain", {"action": "lock_and_mint", "amount": 1})
    except ValueError as error:
        print(f"Invalid XCM rejected: {error}")

    relay.governance_vote("Increase block weight limit", yes=1500, no=500)
    print(f"All parachains share the security of validators: {[v.name for v in active]}")
    print(f"Final parachain states: { {name: p.state for name, p in relay.parachains.items()} }")


def main() -> None:
    demo_bitcoin()
    demo_corda()
    demo_polkadot()


if __name__ == "__main__":
    main()
