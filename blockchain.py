"""
blockchain.py - Lightweight Blockchain Logger
Logs each farmer query as a tamper-evident chain of records.
"""

import hashlib
import json
import time
import os
import logging

logger = logging.getLogger(__name__)

CHAIN_FILE = os.getenv("BLOCKCHAIN_FILE", "harvest_chain.json")


class Block:
    def __init__(self, index: int, data: dict, previous_hash: str):
        self.index         = index
        self.timestamp     = time.time()
        self.data          = data
        self.previous_hash = previous_hash
        self.hash          = self._compute_hash()

    def _compute_hash(self) -> str:
        block_str = json.dumps({
            "index":         self.index,
            "timestamp":     self.timestamp,
            "data":          self.data,
            "previous_hash": self.previous_hash,
        }, sort_keys=True)
        return hashlib.sha256(block_str.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "index":         self.index,
            "timestamp":     self.timestamp,
            "data":          self.data,
            "previous_hash": self.previous_hash,
            "hash":          self.hash,
        }


class HarvestChain:
    def __init__(self):
        self.chain: list[Block] = []
        self._load()

        if not self.chain:
            self._create_genesis()

    # ── persistence ──────────────────────────────────────────────────────────

    def _load(self):
        if os.path.exists(CHAIN_FILE):
            try:
                with open(CHAIN_FILE) as f:
                    raw = json.load(f)

                for b in raw:
                    block = Block.__new__(Block)
                    block.index         = b["index"]
                    block.timestamp     = b["timestamp"]
                    block.data          = b["data"]
                    block.previous_hash = b["previous_hash"]
                    block.hash          = b["hash"]
                    self.chain.append(block)

                logger.info(f"Loaded chain with {len(self.chain)} blocks")
            except Exception as e:
                logger.warning(f"Could not load chain: {e}. Starting fresh.")
                self.chain = []

    def _save(self):
        try:
            with open(CHAIN_FILE, "w") as f:
                json.dump([b.to_dict() for b in self.chain], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save chain: {e}")

    # ── core operations ───────────────────────────────────────────────────────

    def _create_genesis(self):
        genesis = Block(0, {"type": "genesis", "message": "HarvestSmart Chain"}, "0")
        self.chain.append(genesis)
        self._save()

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def add_record(self, sender: str, commodity: str, state: str,
                   quantity_kg: float, result: dict) -> str:
        """Log a query. Returns the block hash (record ID)."""
        data = {
            "sender":    sender[-4:] + "****",   # anonymise
            "commodity": commodity,
            "state":     state,
            "quantity":  quantity_kg,
            "median_price": result.get("median_price"),
            "advice":    result.get("advice", {}).get("label"),
        }

        block = Block(
            index=len(self.chain),
            data=data,
            previous_hash=self.last_block.hash,
        )
        self.chain.append(block)
        self._save()

        logger.info(f"Block #{block.index} added: {block.hash[:12]}…")
        return block.hash

    def is_valid(self) -> bool:
        """Verify chain integrity."""
        for i in range(1, len(self.chain)):
            cur  = self.chain[i]
            prev = self.chain[i - 1]

            if cur.hash != cur._compute_hash():
                return False
            if cur.previous_hash != prev.hash:
                return False
        return True

    def get_summary(self) -> dict:
        return {
            "total_records": len(self.chain) - 1,   # exclude genesis
            "is_valid":      self.is_valid(),
            "latest_hash":   self.last_block.hash[:16] + "…",
        }


# ── module-level singleton ────────────────────────────────────────────────────
_chain: HarvestChain | None = None


def get_chain() -> HarvestChain:
    global _chain
    if _chain is None:
        _chain = HarvestChain()
    return _chain


def log_query(sender: str, commodity: str, state: str,
              quantity_kg: float, result: dict) -> str:
    return get_chain().add_record(sender, commodity, state, quantity_kg, result)
