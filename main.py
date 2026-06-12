#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from agent import LeaseVettingAgent

ROOT = Path(__file__).parent
INVENTORY = ROOT / "data" / "towers_inventory.json"
POLICIES = ROOT / "data" / "regional_policies.txt"

DEMO_REQUEST = (
    "Operator Du wants to mount a 15kg 5G antenna "
    "at a height of 40 meters on Tower TWR-101."
)


def run_once(agent: LeaseVettingAgent, text: str) -> None:
    print(f"\n{'='*70}")
    print(f"  INCOMING REQUEST")
    print(f"{'='*70}")
    print(f"  {text}\n")

    judgment = agent.vet(text)

    print(f"{'─'*70}")
    print(f"  AGENT TOOL TRACE")
    print(f"{'─'*70}")
    for i, tc in enumerate(judgment.tool_trace, 1):
        print(f"  [{i}] {tc.tool}({tc.input})")
        print(f"      → {tc.output}")
    print()

    print(f"{'─'*70}")
    print(f"  CHECKS")
    print(f"{'─'*70}")
    for c in judgment.checks:
        icon = "PASS" if c.passed else "FAIL"
        print(f"  [{icon}]  {c.check}: {c.detail}")
    print()

    print(f"{'━'*70}")
    print(f"  VERDICT:  {judgment.verdict.value}")
    print(f"  {judgment.summary}")
    print(f"{'━'*70}")

    print(f"\n── Structured JSON ──")
    print(json.dumps(judgment.model_dump(), indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Telecom Lease Vetting Agent")
    parser.add_argument("request", nargs="?", default=None,
                        help="Plain-text lease request (omit for demo)")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Interactive prompt loop")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(name)s | %(message)s",
    )

    agent = LeaseVettingAgent(INVENTORY, POLICIES)

    if args.interactive:
        print("Lease Vetting Agent — type a request or 'quit' to exit.\n")
        while True:
            try:
                text = input("Request> ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if text.lower() in ("quit", "exit", "q"):
                break
            if text:
                run_once(agent, text)
    else:
        run_once(agent, args.request or DEMO_REQUEST)


if __name__ == "__main__":
    main()
