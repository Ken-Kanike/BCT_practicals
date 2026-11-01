#!/usr/bin/env python3
"""Experiment 8 - blockchain application with transactions, mining and validation."""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from ecdsa import SECP256k1, SigningKey, VerifyingKey
from ecdsa.util import sigdecode_der, sigencode_der

COINBASE = "COINBASE"


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def rule(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


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

    def create_transaction(self, receiver: "Wallet", amount: float, fee: float = 0.0) -> "Transaction":
        tx = Transaction(
            sender=self.address,
            receiver=receiver.address,
            amount=float(amount),
            fee=float(fee),
            timestamp=time.time(),
        )
        tx.sign(self)
        return tx

    def short(self) -> str:
        return f"{self.name}({self.address[:10]}...)"


@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
    fee: float
    timestamp: float
    sender_pubkey: str = ""
    signature: str = ""
    coinbase: bool = False

    def payload(self) -> str:
        return json.dumps(
            {
                "sender": self.sender,
                "receiver": self.receiver,
                "amount": self.amount,
                "fee": self.fee,
                "timestamp": self.timestamp,
                "coinbase": self.coinbase,
            },
            sort_keys=True,
        )

    def txid(self) -> str:
        return sha256(self.payload())

    def sign(self, wallet: Wallet) -> None:
        self.sender_pubkey = wallet.pubkey
        self.signature = wallet.sign(self.txid())

    def verify(self) -> bool:
        if self.coinbase:
            return True
        if not self.sender_pubkey or not self.signature:
            return False
        if sha256(self.sender_pubkey)[:40] != self.sender:
            return False
        return verify_signature(self.sender_pubkey, self.txid(), self.signature)

    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "fee": self.fee,
            "timestamp": self.timestamp,
            "sender_pubkey": self.sender_pubkey,
            "signature": self.signature,
            "coinbase": self.coinbase,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        return cls(**data)


@dataclass
class Block:
    index: int
    previous_hash: str
    timestamp: float
    transactions: list[Transaction]
    merkle_root: str
    nonce: int
    hash: str

    @staticmethod
    def compute_merkle_root(transactions: list[Transaction]) -> str:
        if not transactions:
            return sha256("")
        layer = [tx.txid() for tx in transactions]
        while len(layer) > 1:
            if len(layer) % 2 == 1:
                layer.append(layer[-1])
            layer = [sha256(layer[i] + layer[i + 1]) for i in range(0, len(layer), 2)]
        return layer[0]

    def compute_hash(self) -> str:
        header = "|".join(
            [
                str(self.index),
                self.previous_hash,
                f"{self.timestamp:.6f}",
                self.merkle_root,
                str(self.nonce),
            ]
        )
        return sha256(header)

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "merkle_root": self.merkle_root,
            "nonce": self.nonce,
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Block":
        transactions = [Transaction.from_dict(tx) for tx in data["transactions"]]
        return cls(
            index=data["index"],
            previous_hash=data["previous_hash"],
            timestamp=data["timestamp"],
            transactions=transactions,
            merkle_root=data["merkle_root"],
            nonce=data["nonce"],
            hash=data["hash"],
        )


class Blockchain:
    def __init__(
        self,
        allocations: dict[str, float],
        difficulty: int = 4,
        reward: float = 50.0,
    ) -> None:
        self.difficulty = difficulty
        self.reward = reward
        self.mempool: list[Transaction] = []
        self.chain: list[Block] = []
        genesis_txs = [
            Transaction(
                sender=COINBASE,
                receiver=address,
                amount=amount,
                fee=0.0,
                timestamp=time.time(),
                coinbase=True,
            )
            for address, amount in allocations.items()
        ]
        self.chain.append(self._mine_block(genesis_txs, previous_hash="0" * 64))

    def _mine_block(self, transactions: list[Transaction], previous_hash: str) -> Block:
        timestamp = time.time()
        merkle_root = Block.compute_merkle_root(transactions)
        index = len(self.chain)
        nonce = 0
        while True:
            header = "|".join(
                [
                    str(index),
                    previous_hash,
                    f"{timestamp:.6f}",
                    merkle_root,
                    str(nonce),
                ]
            )
            block_hash = sha256(header)
            if block_hash.startswith("0" * self.difficulty):
                break
            nonce += 1
        return Block(index, previous_hash, timestamp, transactions, merkle_root, nonce, block_hash)

    def _apply(self, balances: dict[str, float], tx: Transaction) -> None:
        if tx.coinbase:
            balances[tx.receiver] = balances.get(tx.receiver, 0.0) + tx.amount
            return
        balances[tx.sender] = balances.get(tx.sender, 0.0) - tx.amount - tx.fee
        balances[tx.receiver] = balances.get(tx.receiver, 0.0) + tx.amount

    def balances(self, include_mempool: bool = False) -> dict[str, float]:
        balances: dict[str, float] = {}
        for block in self.chain:
            for tx in block.transactions:
                self._apply(balances, tx)
        if include_mempool:
            for tx in self.mempool:
                self._apply(balances, tx)
        return balances

    def balance(self, address: str, include_mempool: bool = False) -> float:
        return self.balances(include_mempool).get(address, 0.0)

    def _confirmed_txids(self) -> set[str]:
        return {tx.txid() for block in self.chain for tx in block.transactions}

    def add_transaction(self, tx: Transaction) -> None:
        if tx.coinbase:
            raise ValueError("coinbase transactions can only be created by mining")
        if tx.amount <= 0:
            raise ValueError("amount must be positive")
        if tx.fee < 0:
            raise ValueError("fee cannot be negative")
        if tx.sender == tx.receiver:
            raise ValueError("sender and receiver must differ")
        if not tx.verify():
            raise ValueError("invalid ECDSA signature")
        if tx.txid() in self._confirmed_txids() or any(t.txid() == tx.txid() for t in self.mempool):
            raise ValueError("duplicate transaction")
        if self.balance(tx.sender, include_mempool=True) < tx.amount + tx.fee:
            raise ValueError("insufficient funds")

        self.mempool.append(tx)

    def mine_pending(self, miner: Wallet) -> Block:
        if not self.mempool:
            raise ValueError("mempool is empty")
        fees = sum(tx.fee for tx in self.mempool)
        coinbase = Transaction(
            sender=COINBASE,
            receiver=miner.address,
            amount=self.reward + fees,
            fee=0.0,
            timestamp=time.time(),
            coinbase=True,
        )
        transactions = [coinbase, *self.mempool]
        block = self._mine_block(transactions, self.chain[-1].hash)
        self.chain.append(block)
        self.mempool.clear()
        return block

    def validate_chain(self) -> tuple[bool, list[str]]:
        errors: list[str] = []
        balances: dict[str, float] = {}
        seen_txids: set[str] = set()

        for index, block in enumerate(self.chain):
            if block.hash != block.compute_hash():
                errors.append(f"block {index}: hash does not match header")
            if block.hash[: self.difficulty] != "0" * self.difficulty:
                errors.append(f"block {index}: insufficient proof of work")
            if index == 0:
                if block.previous_hash != "0" * 64:
                    errors.append("genesis: previous hash must be zero")
                if any(not tx.coinbase for tx in block.transactions):
                    errors.append("genesis: all transactions must be coinbase")
            else:
                if block.previous_hash != self.chain[index - 1].hash:
                    errors.append(f"block {index}: previous hash mismatch")
                if not block.transactions or not block.transactions[0].coinbase:
                    errors.append(f"block {index}: first transaction must be coinbase")
                if any(tx.coinbase for tx in block.transactions[1:]):
                    errors.append(f"block {index}: only the first transaction may be coinbase")

            if block.merkle_root != Block.compute_merkle_root(block.transactions):
                errors.append(f"block {index}: merkle root mismatch")

            fees = sum(tx.fee for tx in block.transactions if not tx.coinbase)
            for position, tx in enumerate(block.transactions):
                if tx.txid() in seen_txids:
                    errors.append(f"block {index}: duplicate transaction {tx.txid()[:12]}")
                seen_txids.add(tx.txid())

                if tx.amount <= 0:
                    errors.append(f"block {index}: non-positive amount")
                if tx.fee < 0:
                    errors.append(f"block {index}: negative fee")
                if tx.coinbase:
                    if index > 0 and position == 0 and tx.amount != self.reward + fees:
                        errors.append(f"block {index}: coinbase reward mismatch")
                elif not tx.verify():
                    errors.append(f"block {index}: invalid signature in {tx.txid()[:12]}")

                self._apply(balances, tx)
                if any(value < -1e-9 for value in balances.values()):
                    errors.append(f"block {index}: negative balance detected")

        return not errors, errors

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "difficulty": self.difficulty,
            "reward": self.reward,
            "chain": [block.to_dict() for block in self.chain],
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "Blockchain":
        data = json.loads(path.read_text(encoding="utf-8"))
        chain = cls.__new__(cls)
        chain.difficulty = data["difficulty"]
        chain.reward = data["reward"]
        chain.mempool = []
        chain.chain = [Block.from_dict(block) for block in data["chain"]]
        return chain


def short_address(address: str) -> str:
    return f"{address[:12]}..."


def demo() -> None:
    alice, bob, carol, miner = Wallet("Alice"), Wallet("Bob"), Wallet("Carol"), Wallet("Miner")
    chain = Blockchain(
        allocations={
            alice.address: 1000.0,
            bob.address: 500.0,
            carol.address: 500.0,
        },
        difficulty=4,
        reward=50.0,
    )

    rule("1. WALLETS AND GENESIS BLOCK")
    for wallet in (alice, bob, carol, miner):
        print(f"{wallet.name:5s} address={short_address(wallet.address)}")
    genesis = chain.chain[0]
    print(f"Genesis: {len(genesis.transactions)} allocations, nonce={genesis.nonce}, hash={genesis.hash}")

    rule("2. TRANSACTION HANDLING (MEMPOOL)")
    tx1 = alice.create_transaction(bob, 120.0, fee=2.0)
    tx2 = bob.create_transaction(carol, 50.0, fee=1.0)
    tx3 = carol.create_transaction(alice, 30.0, fee=1.0)
    for tx in (tx1, tx2, tx3):
        chain.add_transaction(tx)
        sender = alice.name if tx.sender == alice.address else bob.name if tx.sender == bob.address else carol.name
        receiver = bob.name if tx.receiver == bob.address else carol.name if tx.receiver == carol.address else alice.name
        print(f"{sender} -> {receiver}: amount={tx.amount:.2f} fee={tx.fee:.2f} txid={tx.txid()[:16]}...")
    print(f"Mempool size: {len(chain.mempool)}")

    rule("3. MINING BLOCK 1")
    started = time.time()
    block1 = chain.mine_pending(miner)
    elapsed = time.time() - started
    print(f"Mined block {block1.index} in {elapsed:.3f}s")
    print(f"nonce={block1.nonce} hash={block1.hash}")
    print(f"merkle_root={block1.merkle_root}")
    print(f"transactions={len(block1.transactions)} (1 coinbase + {len(block1.transactions) - 1} transfers)")

    rule("4. BALANCES AFTER MINING")
    for wallet in (alice, bob, carol, miner):
        print(f"{wallet.name:5s} {chain.balance(wallet.address):9.2f}")

    rule("5. INVALID TRANSACTIONS")
    try:
        chain.add_transaction(alice.create_transaction(bob, 1_000_000.0))
    except ValueError as error:
        print(f"Insufficient funds rejected: {error}")

    tampered = alice.create_transaction(bob, 10.0)
    tampered.amount = 999_999.0
    try:
        chain.add_transaction(tampered)
    except ValueError as error:
        print(f"Tampered signature rejected: {error}")

    try:
        chain.add_transaction(tx1)
    except ValueError as error:
        print(f"Duplicate transaction rejected: {error}")

    rule("6. SECOND BLOCK")
    tx4 = alice.create_transaction(carol, 200.0, fee=3.0)
    chain.add_transaction(tx4)
    block2 = chain.mine_pending(miner)
    print(f"Alice -> Carol: amount=200.00 fee=3.00 txid={tx4.txid()[:16]}...")
    print(f"Mined block {block2.index}: nonce={block2.nonce} hash={block2.hash}")
    for wallet in (alice, bob, carol, miner):
        print(f"{wallet.name:5s} {chain.balance(wallet.address):9.2f}")

    rule("7. CHAIN VALIDATION")
    valid, errors = chain.validate_chain()
    print(f"Chain valid: {valid}")
    print(f"Errors: {errors if errors else 'none'}")
    print(f"Blocks: {len(chain.chain)}, transactions: {sum(len(b.transactions) for b in chain.chain)}")

    rule("8. TAMPER DETECTION")
    original_amount = chain.chain[1].transactions[1].amount
    original_nonce = chain.chain[1].nonce
    chain.chain[1].transactions[1].amount = 999_999.0
    chain.chain[1].nonce += 1
    valid, errors = chain.validate_chain()
    print(f"Chain valid after tampering block 1: {valid}")
    for error in errors[:4]:
        print(f"  - {error}")
    chain.chain[1].transactions[1].amount = original_amount
    chain.chain[1].nonce = original_nonce
    valid, errors = chain.validate_chain()
    print(f"Chain valid after restoring block 1: {valid}")

    rule("9. PERSISTENCE")
    output_path = Path(__file__).resolve().parent.parent / "output/blockchain.json"
    chain.save(output_path)
    print(f"Saved chain to {output_path}")
    print(f"File size: {output_path.stat().st_size} bytes")
    loaded = Blockchain.load(output_path)
    valid, errors = loaded.validate_chain()
    print(f"Reloaded chain valid: {valid}")
    print(f"Reloaded blocks: {len(loaded.chain)}")

    rule("10. CHAIN SUMMARY")
    for block in loaded.chain:
        print(
            f"block {block.index}: txs={len(block.transactions):2d} "
            f"nonce={block.nonce:6d} hash={block.hash[:20]}... "
            f"merkle={block.merkle_root[:16]}..."
        )


if __name__ == "__main__":
    demo()
