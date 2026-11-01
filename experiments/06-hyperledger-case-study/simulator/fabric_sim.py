#!/usr/bin/env python3
"""
Experiment 6 - Hyperledger case study simulator.

Models the concepts behind a permissioned Fabric network for an IBM Food Trust
style supply chain:

  * MSP identity registration and channel membership
  * peers, orderer, channel and chaincode
  * endorsement policy (Org1 AND Org2)
  * private data collection (price visible only to Org1)
  * hash-linked blocks and tamper detection

This is a teaching simulator, not a replacement for the real Fabric network
that was deployed in Experiment 5.
"""
from __future__ import annotations

import copy
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


@dataclass(frozen=True)
class Identity:
    name: str
    org: str
    role: str = "member"


class MSP:
    """Membership Service Provider: only registered identities may transact."""

    def __init__(self) -> None:
        self._members: dict[tuple[str, str], Identity] = {}

    def register(self, identity: Identity) -> None:
        self._members[(identity.name, identity.org)] = identity

    def is_member(self, identity: Identity) -> bool:
        return self._members.get((identity.name, identity.org)) == identity

    def require(self, identity: Identity) -> None:
        if not self.is_member(identity):
            raise PermissionError(f"{identity.name}@{identity.org} is not a registered MSP member")


@dataclass(frozen=True)
class Collection:
    """Private data collection with an org-level access policy."""

    name: str
    allowed_orgs: frozenset[str]


@dataclass(frozen=True)
class Proposal:
    function: str
    args: tuple[Any, ...]
    identity: Identity


@dataclass
class Transaction:
    function: str
    args: tuple[Any, ...]
    submitter: str
    public_writes: dict[str, dict]
    private_hash: str
    private_writes: dict[str, dict] = field(default_factory=dict)
    endorsements: tuple[str, ...] = ()

    def public_payload(self) -> dict:
        # Private data itself is not part of the block; only its hash is.
        return {
            "function": self.function,
            "args": list(self.args),
            "submitter": self.submitter,
            "public_writes": self.public_writes,
            "private_hash": self.private_hash,
            "endorsements": list(self.endorsements),
        }


@dataclass
class Block:
    index: int
    previous_hash: str
    transactions: list[Transaction]
    timestamp: float = field(default_factory=time.time)
    hash_value: str = ""

    def __post_init__(self) -> None:
        if not self.hash_value:
            self.hash_value = self.compute_hash()

    def compute_hash(self) -> str:
        payload = {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "timestamp": round(self.timestamp, 6),
            "transactions": [tx.public_payload() for tx in self.transactions],
        }
        return sha256(json.dumps(payload, sort_keys=True))


class Ledger:
    """A peer's copy of the public world state plus permitted private data."""

    def __init__(self, org: str) -> None:
        self.org = org
        self.public: dict[str, dict] = {}
        self.private: dict[str, dict] = {}
        self.blocks: list[Block] = []

    def apply(self, block: Block, collections: dict[str, Collection]) -> None:
        for tx in block.transactions:
            for key, value in tx.public_writes.items():
                self.public[key] = json.loads(json.dumps(value))
            for collection_name, entries in tx.private_writes.items():
                collection = collections[collection_name]
                if self.org in collection.allowed_orgs:
                    self.private.setdefault(collection_name, {}).update(
                        json.loads(json.dumps(entries))
                    )
        # Each peer keeps its own copy, as in a real distributed ledger.
        self.blocks.append(copy.deepcopy(block))

    def validate(self) -> bool:
        for index, block in enumerate(self.blocks):
            if block.compute_hash() != block.hash_value:
                return False
            if index > 0 and block.previous_hash != self.blocks[index - 1].hash_value:
                return False
        return True


class FoodTrustChaincode:
    """Business logic for creating and transferring food batches."""

    def __init__(self, collection: Collection) -> None:
        self.collection = collection

    def simulate(
        self,
        function: str,
        args: tuple[Any, ...],
        identity: Identity,
        ledger: Ledger,
    ) -> Transaction | dict:
        if function == "create_asset":
            return self._create_asset(args, identity, ledger)
        if function == "transfer_asset":
            return self._transfer_asset(args, identity, ledger)
        if function == "read_asset":
            return self._read_asset(args, ledger)
        raise ValueError(f"unknown chaincode function: {function}")

    def _create_asset(self, args: tuple, identity: Identity, ledger: Ledger) -> Transaction:
        asset_id, owner, value, price = args
        if asset_id in ledger.public:
            raise ValueError(f"asset {asset_id} already exists")
        if int(value) <= 0:
            raise ValueError("asset value must be positive")

        private = {asset_id: {"price": str(price)}}
        private_hash = sha256(json.dumps(private, sort_keys=True))
        public = {
            "id": asset_id,
            "owner": owner,
            "value": int(value),
            "status": "ACTIVE",
            "private_hash": private_hash,
        }
        return Transaction(
            function="create_asset",
            args=args,
            submitter=identity.name,
            public_writes={asset_id: public},
            private_hash=private_hash,
            private_writes={self.collection.name: private},
        )

    def _transfer_asset(self, args: tuple, identity: Identity, ledger: Ledger) -> Transaction:
        asset_id, new_owner = args
        if asset_id not in ledger.public:
            raise ValueError(f"asset {asset_id} does not exist")

        public = dict(ledger.public[asset_id])
        public["owner"] = new_owner
        return Transaction(
            function="transfer_asset",
            args=args,
            submitter=identity.name,
            public_writes={asset_id: public},
            private_hash=public["private_hash"],
        )

    def _read_asset(self, args: tuple, ledger: Ledger) -> dict:
        asset_id = args[0]
        if asset_id not in ledger.public:
            raise ValueError(f"asset {asset_id} does not exist")

        result = dict(ledger.public[asset_id])
        if ledger.org in self.collection.allowed_orgs:
            result["price"] = ledger.private.get(self.collection.name, {}).get(asset_id, {}).get("price")
            result["private_data"] = "disclosed to this organization"
        else:
            result["price"] = None
            result["private_data"] = "withheld - only the private hash is visible"
        return result


@dataclass(frozen=True)
class Endorsement:
    peer: str
    org: str
    identity: str
    signature: str


class Peer:
    def __init__(
        self,
        name: str,
        org: str,
        msp: MSP,
        chaincode: FoodTrustChaincode,
        collections: dict[str, Collection],
    ) -> None:
        self.name = name
        self.org = org
        self.msp = msp
        self.chaincode = chaincode
        self.collections = collections
        self.ledger = Ledger(org)

    def endorse(self, proposal: Proposal) -> tuple[Endorsement, Transaction]:
        # Any registered channel member may submit a proposal to this peer;
        # the endorsement itself is signed by the peer's organization.
        self.msp.require(proposal.identity)
        tx = self.chaincode.simulate(
            proposal.function, proposal.args, proposal.identity, self.ledger
        )
        if not isinstance(tx, Transaction):
            raise TypeError("endorsement requires a state-changing transaction")
        signature = sha256(
            f"{self.name}:{self.org}:{proposal.identity.name}:{proposal.function}:{proposal.args}"
        )[:24]
        return Endorsement(self.name, self.org, proposal.identity.name, signature), tx

    def commit(self, block: Block) -> None:
        self.ledger.apply(block, self.collections)


class Orderer:
    """Raft-style ordering service: checks endorsement policy and builds blocks."""

    def __init__(self, required_orgs: set[str]) -> None:
        self.required_orgs = required_orgs
        self.blocks: list[Block] = []

    def submit(self, endorsements: list[Endorsement], tx: Transaction) -> Block:
        orgs = {endorsement.org for endorsement in endorsements}
        missing = self.required_orgs - orgs
        if missing:
            raise PermissionError(
                f"endorsement policy not met; missing approval from {sorted(missing)}"
            )

        tx.endorsements = tuple(endorsement.signature for endorsement in endorsements)
        previous_hash = self.blocks[-1].hash_value if self.blocks else "0" * 64
        block = Block(len(self.blocks), previous_hash, [tx])
        self.blocks.append(block)
        return block


class FabricNetwork:
    def __init__(self) -> None:
        self.msp = MSP()
        self.collection = Collection("assetPrivateDetails", frozenset({"Org1"}))
        self.chaincode = FoodTrustChaincode(self.collection)
        self.channel_members = {"Org1", "Org2"}
        self.peers = {
            "Org1": Peer(
                "peer0.org1.example.com",
                "Org1",
                self.msp,
                self.chaincode,
                {self.collection.name: self.collection},
            ),
            "Org2": Peer(
                "peer0.org2.example.com",
                "Org2",
                self.msp,
                self.chaincode,
                {self.collection.name: self.collection},
            ),
        }
        self.orderer = Orderer({"Org1", "Org2"})

    def register(self, identity: Identity) -> None:
        self.msp.register(identity)

    def join_channel(self, identity: Identity) -> None:
        self.msp.require(identity)
        if identity.org not in self.channel_members:
            raise PermissionError(f"organization {identity.org} is not a member of mychannel")

    def invoke(
        self,
        identity: Identity,
        function: str,
        *args: Any,
        endorsing_orgs: tuple[str, ...] = ("Org1", "Org2"),
    ) -> tuple[Block, list[Endorsement]]:
        self.join_channel(identity)
        proposal = Proposal(function, tuple(args), identity)
        endorsements: list[Endorsement] = []
        transactions: list[Transaction] = []

        for org in endorsing_orgs:
            endorsement, tx = self.peers[org].endorse(proposal)
            endorsements.append(endorsement)
            transactions.append(tx)

        if not transactions:
            raise PermissionError("no endorsements were collected")

        block = self.orderer.submit(endorsements, transactions[0])
        for peer in self.peers.values():
            peer.commit(block)
        return block, endorsements

    def query(self, identity: Identity, function: str, *args: Any) -> dict:
        self.join_channel(identity)
        peer = self.peers[identity.org]
        result = self.chaincode.simulate(function, tuple(args), identity, peer.ledger)
        if not isinstance(result, dict):
            raise TypeError("query must be read-only")
        return result


def rule(title: str) -> None:
    print(f"\n{'=' * 74}\n{title}\n{'=' * 74}")


def main() -> None:
    network = FabricNetwork()

    alice = Identity("alice", "Org1", "producer")
    bob = Identity("bob", "Org2", "retailer")
    mallory = Identity("mallory", "Org3", "intruder")

    rule("1. MSP REGISTRATION AND CHANNEL MEMBERSHIP")
    for identity in (alice, bob, mallory):
        network.register(identity)
        print(f"MSP registered: {identity.name}@{identity.org} ({identity.role})")

    for identity in (alice, bob):
        network.join_channel(identity)
        print(f"JOINED  mychannel: {identity.name}@{identity.org}")

    try:
        network.join_channel(mallory)
    except PermissionError as error:
        print(f"DENIED  mychannel: {error}")

    rule("2. CREATE ASSET WITH ORG1 + ORG2 ENDORSEMENT")
    block, endorsements = network.invoke(
        alice, "create_asset", "mango1", "FarmA", 100, "2.50"
    )
    print(f"Block {block.index} committed: {block.hash_value}")
    print(f"Previous hash: {block.previous_hash}")
    print(f"Endorsements: {[(e.org, e.peer) for e in endorsements]}")
    print("Public write:", json.dumps(block.transactions[0].public_writes, indent=2))

    rule("3. PRIVATE DATA COLLECTION (price is Org1-only)")
    print("Org1 read:", json.dumps(network.query(alice, "read_asset", "mango1"), indent=2))
    print("Org2 read:", json.dumps(network.query(bob, "read_asset", "mango1"), indent=2))
    try:
        network.query(mallory, "read_asset", "mango1")
    except PermissionError as error:
        print(f"Org3 read denied: {error}")

    rule("4. ENDORSEMENT POLICY ENFORCEMENT")
    try:
        network.invoke(
            alice,
            "transfer_asset",
            "mango1",
            "RetailerB",
            endorsing_orgs=("Org1",),
        )
    except PermissionError as error:
        print(f"DENIED: {error}")

    block2, endorsements2 = network.invoke(
        alice, "transfer_asset", "mango1", "RetailerB"
    )
    print(f"Block {block2.index} committed with Org1+Org2: {block2.hash_value}")
    print("Endorsements:", [(e.org, e.peer) for e in endorsements2])

    rule("5. UPDATED STATE")
    print("Org1 read:", json.dumps(network.query(alice, "read_asset", "mango1"), indent=2))
    print("Org2 read:", json.dumps(network.query(bob, "read_asset", "mango1"), indent=2))

    rule("6. HASH-LINKED LEDGER AND TAMPER DETECTION")
    for peer in network.peers.values():
        print(f"{peer.org} ledger blocks:")
        for block in peer.ledger.blocks:
            print(
                f"  block {block.index}: hash={block.hash_value[:24]}... "
                f"prev={block.previous_hash[:24]}... txs={len(block.transactions)}"
            )
        print(f"  chain valid: {peer.ledger.validate()}")

    org1_ledger = network.peers["Org1"].ledger
    org1_ledger.blocks[0].transactions[0].public_writes["mango1"]["owner"] = "Mallory"
    print("\nTampered block 0 on Org1 (owner changed to Mallory):")
    print(f"  Org1 chain valid: {org1_ledger.validate()}")
    print(f"  Org2 chain valid: {network.peers['Org2'].ledger.validate()}")

    rule("7. FINAL WORLD STATE PER ORGANIZATION")
    for peer in network.peers.values():
        print(f"{peer.org}:")
        print("  public :", json.dumps(peer.ledger.public, indent=2))
        print("  private:", json.dumps(peer.ledger.private, indent=2))


if __name__ == "__main__":
    main()
