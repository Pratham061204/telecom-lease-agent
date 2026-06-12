"""
Test cases

1. Standard success        (TWR-101, Du, 15kg, 40m)        → APPROVED
2. Weight overflow          (TWR-101, heavy gear, 50kg)      → REJECTED
3. Height violation         (TWR-101, antenna at 50m)        → REJECTED
4. Coastal asset-weight     (TWR-102, 30kg panel)            → REJECTED (>25kg)
5. Coastal asset-weight OK  (TWR-102, 20kg panel)            → APPROVED
6. Unknown tower            (TWR-999)                        → REJECTED
7. SHJ-South asset weight   (TWR-181, 16kg > 15kg limit)     → REJECTED
8. Multi-rule rejection     (TWR-108, weight + height)       → REJECTED
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from agent import LeaseVettingAgent, Verdict

INVENTORY = ROOT / "data" / "towers_inventory.json"
POLICIES = ROOT / "data" / "regional_policies.txt"

agent = LeaseVettingAgent(INVENTORY, POLICIES)

passed = 0
failed = 0


def check(label: str, request: str, expected: Verdict) -> None:
    global passed, failed
    result = agent.vet(request)
    status = "PASS" if result.verdict == expected else "FAIL"
    print(f"  [{status}]  {label}")
    print(f"       Request : {request}")
    print()

    print(f"       Tool Calls:")
    for i, tc in enumerate(result.tool_trace, 1):
        print(f"         [{i}] {tc.tool}({tc.input})")
        print(f"             -> {tc.output}")
    print()

    print(f"       Reasoning:")
    for c in result.checks:
        mark = "PASS" if c.passed else "FAIL"
        print(f"         [{mark}] {c.check}: {c.detail}")
    print()

    print(f"       Expected: {expected.value}   Got: {result.verdict.value}")
    if result.verdict != expected:
        failed += 1
    else:
        passed += 1
    print()
    print(f"       {'─' * 50}")
    print()


print("=" * 60)
print("  LEASE VETTING AGENT — TEST SUITE")
print("=" * 60 + "\n")

check(
    "Test 1 - Standard success (spec test case)",
    "Operator Du wants to mount a 15kg 5G antenna at a height of 40 meters on Tower TWR-101.",
    Verdict.APPROVED,
)

check(
    "Test 2 - Weight capacity exceeded",
    "Operator Etisalat requests installation of a 50kg base station at 30m height on Tower TWR-101.",
    Verdict.REJECTED,
)

check(
    "Test 3 - Height exceeds DXB-North 45m limit",
    "Operator Vodafone wants to mount a 10kg antenna at a height of 50 meters on Tower TWR-101.",
    Verdict.REJECTED,
)

check(
    "Test 4 - Asset weight exceeds SHJ-Coastal 25kg limit",
    "Operator Verizon requests mounting a 30kg radio unit on Tower TWR-102.",
    Verdict.REJECTED,
)

check(
    "Test 5 - Coastal tower pass, within all limits",
    "Operator Du wants to install a 20kg small cell on Tower TWR-102.",
    Verdict.APPROVED,
)

check(
    "Test 6 - Unknown tower ID",
    "Operator Zain requests a 5kg relay on Tower TWR-999.",
    Verdict.REJECTED,
)

check(
    "Test 7 - Asset weight exceeds SHJ-South 15kg limit",
    "Operator Etisalat requests mounting a 16kg radio unit on Tower TWR-181.",
    Verdict.REJECTED,
)

check(
    "Test 8 - Multi-rule rejection (weight + height)",
    "Operator Etisalat requests mounting a 45kg radio unit at height of 50 meters on Tower TWR-108.",
    Verdict.REJECTED,
)

total = passed + failed
print("=" * 60)
print(f"  Results: {passed}/{total} passed", end="")
if failed:
    print(f"  ({failed} FAILED)")
else:
    print("  -- ALL PASSED")
print("=" * 60)

sys.exit(1 if failed else 0)