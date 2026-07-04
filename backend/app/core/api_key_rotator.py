"""
Thread-safe round-robin API key rotator with automatic cooldown.

Usage:
    rotator = ApiKeyRotator(["key1", "key2", "key3"])
    key = rotator.next_key()          # round-robin pick
    rotator.mark_rate_limited(key)    # put key on cooldown after 429
"""

import threading
import time
import logging
from typing import List

logger = logging.getLogger(__name__)


class ApiKeyRotator:
    """Cycles through a list of API keys using round-robin.

    When a key receives a 429 (rate-limited), call `mark_rate_limited(key)`
    to temporarily exclude it from rotation for `cooldown_seconds`.
    """

    def __init__(self, keys: List[str], cooldown_seconds: float = 60.0):
        if not keys:
            raise ValueError("At least one API key is required.")
        # Deduplicate while preserving order
        seen: set[str] = set()
        self._keys: List[str] = []
        for k in keys:
            k = k.strip()
            if k and k not in seen:
                seen.add(k)
                self._keys.append(k)
        if not self._keys:
            raise ValueError("All provided API keys are empty.")

        self._cooldown_seconds = cooldown_seconds
        # Monotonic timestamp until which a key is blocked
        self._blocked_until: dict[str, float] = {}
        self._index = 0
        self._lock = threading.Lock()

        logger.info(
            "ApiKeyRotator initialised with %d key(s), cooldown=%ds",
            len(self._keys), int(cooldown_seconds),
        )

    @property
    def total_keys(self) -> int:
        return len(self._keys)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def next_key(self) -> str:
        """Return the next available key (round-robin, skipping cooled-down keys).

        If every key is on cooldown the *least-blocked* key is returned so the
        caller can still attempt the request (it will likely wait via Retry-After).
        """
        now = time.monotonic()
        with self._lock:
            best_key: str | None = None
            best_unblock: float = float("inf")

            for _ in range(len(self._keys)):
                key = self._keys[self._index % len(self._keys)]
                self._index += 1

                blocked = self._blocked_until.get(key, 0.0)
                if blocked <= now:
                    # Key is available
                    logger.debug("Rotator → key …%s (slot %d)", key[-4:], self._index - 1)
                    return key

                # Track the key with the shortest remaining cooldown
                if blocked < best_unblock:
                    best_unblock = blocked
                    best_key = key

            # All keys on cooldown — return the one that unblocks soonest
            remaining = max(0.0, best_unblock - now)
            logger.warning(
                "All %d key(s) rate-limited; returning least-blocked key …%s (%.1fs left)",
                len(self._keys), best_key[-4:] if best_key else "????", remaining,
            )
            return best_key or self._keys[0]

    def mark_rate_limited(self, key: str, extra_seconds: float | None = None) -> None:
        """Put *key* on cooldown so it is skipped by `next_key()`.

        Args:
            key: The API key that received a 429.
            extra_seconds: Override cooldown duration (e.g. from Retry-After header).
        """
        cooldown = extra_seconds if extra_seconds is not None else self._cooldown_seconds
        with self._lock:
            self._blocked_until[key] = time.monotonic() + cooldown
        logger.info(
            "Key …%s marked rate-limited for %.0fs", key[-4:], cooldown,
        )

    def is_available(self, key: str) -> bool:
        """Check whether a key is currently available (not on cooldown)."""
        with self._lock:
            return self._blocked_until.get(key, 0.0) <= time.monotonic()

    def available_count(self) -> int:
        """Return the number of keys NOT currently on cooldown."""
        now = time.monotonic()
        with self._lock:
            return sum(1 for k in self._keys if self._blocked_until.get(k, 0.0) <= now)

    def status(self) -> list[dict]:
        """Return a snapshot of every key's status (for health-check / debug)."""
        now = time.monotonic()
        with self._lock:
            result = []
            for k in self._keys:
                blocked = self._blocked_until.get(k, 0.0)
                remaining = max(0.0, blocked - now)
                result.append({
                    "key_hint": f"…{k[-4:]}",
                    "available": blocked <= now,
                    "cooldown_remaining_s": round(remaining, 1),
                })
            return result
