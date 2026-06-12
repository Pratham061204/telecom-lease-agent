import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from agent import LeaseVettingAgent

INVENTORY = ROOT / "data" / "towers_inventory.json"
POLICIES = ROOT / "data" / "regional_policies.txt"

agent = LeaseVettingAgent(INVENTORY, POLICIES)

EXAMPLES = [
    "Operator Du wants to mount a 15kg 5G antenna at a height of 40 meters on Tower TWR-101.",
    "Operator Etisalat requests installation of a 50kg base station at 30m height on Tower TWR-101.",
    "Operator Vodafone wants to mount a 10kg antenna at a height of 50 meters on Tower TWR-101.",
    "Operator Du wants to install a 20kg small cell on Tower TWR-102.",
    "Operator Zain requests a 5kg relay on Tower TWR-999.",
]

st.set_page_config(page_title="Tower Lease Review", layout="centered")
st.title("Tower Lease Review")

st.caption("Try an example:")
cols = st.columns(len(EXAMPLES))
selected = None
for i, (col, ex) in enumerate(zip(cols, EXAMPLES)):
    if col.button(f"Example {i+1}"):
        selected = ex

request = st.text_area(
    "Lease Request",
    value=selected or "",
    placeholder='e.g. "Operator Du wants to mount a 15kg 5G antenna at a height of 40 meters on Tower TWR-101."',
    height=100,
)

if st.button("Vet Request") and request.strip():
    result = agent.vet(request.strip())

    st.write(f"**Operator:** {result.operator}")
    st.write(f"**Tower:** {result.tower_id}" + (f"  |  **Region:** {result.region}" if result.region else ""))

    failed_checks = [c for c in result.checks if not c.passed]
    if failed_checks:
        reasons = ", ".join(c.check.replace("_", " ") for c in failed_checks)
        st.write(f"**Reason:** {reasons}")

    approved = result.verdict.value == "APPROVED"
    color = "green" if approved else "red"
    st.markdown(f"## Verdict: :{color}[{result.verdict.value}]")
    st.caption(result.summary)

    st.subheader("Checks")
    for c in result.checks:
        icon = "PASS" if c.passed else "FAIL"
        st.write(f"[{icon}] **{c.check}** — {c.detail}")

    st.subheader("Tool Trace")
    for i, tc in enumerate(result.tool_trace, 1):
        with st.expander(f"[{i}] {tc.tool}"):
            st.json(tc.input)
            st.text(f"→ {tc.output}")

    st.subheader("Structured JSON")
    st.json(result.model_dump())
