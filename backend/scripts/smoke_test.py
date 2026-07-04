#!/usr/bin/env python3
"""Smoke test — verify a MockAI backend is up and healthy.

Runs a few read-only checks against a running backend so you can confirm a
local or deployed instance is actually serving before poking the UI.

Usage:
    python scripts/smoke_test.py                         # default 127.0.0.1:8000
    python scripts/smoke_test.py http://127.0.0.1:8000
    python scripts/smoke_test.py https://net-bzr9.onrender.com

Exit code 0 = all checks passed, 1 = at least one failed.
Only dependency is httpx (already in requirements.txt).
"""
import sys
import httpx

DEFAULT_BASE = "http://127.0.0.1:8000"


def main() -> int:
    base = (sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE).rstrip("/")
    print(f"Smoke test against: {base}\n")
    failures = 0

    def check(name, fn):
        nonlocal failures
        try:
            fn()
            print(f"  [PASS] {name}")
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"  [FAIL] {name}: {e}")

    with httpx.Client(timeout=30.0) as client:
        def health():
            r = client.get(f"{base}/health")
            assert r.status_code == 200, f"HTTP {r.status_code}"
            data = r.json()
            db = data.get("services", {}).get("db")
            assert db == "ok", f"db status is '{db}' (full: {data})"

        def info():
            r = client.get(f"{base}/api/info")
            assert r.status_code == 200, f"HTTP {r.status_code}"

        def root():
            r = client.get(f"{base}/")
            assert r.status_code == 200, f"HTTP {r.status_code}"

        check("GET /health -> services.db == ok", health)
        check("GET /api/info -> 200", info)
        check("GET / -> 200", root)

    print()
    if failures:
        print(f"SMOKE TEST FAILED — {failures} check(s) failed.")
        return 1
    print("SMOKE TEST PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
