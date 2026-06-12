# Telecom Tower Lease Vetting Agent

Takes plain-text lease requests from telecom operators, checks them against a
tower inventory and regional policies, and returns an **APPROVED / REJECTED** verdict.

---

## Architecture

```
 Plain-text request
        │
        ▼
 ┌──────────────┐
 │    Parser     │   regex NLP extraction → LeaseRequest
 └──────┬───────┘
        ▼
 ┌──────────────┐
 │  Agent Loop   │   runs tools in sequence
 │               │
 │  ┌──────────┐ │   Tool 1: tower_lookup
 │  │  Tools   │ │   Tool 2: weight_capacity_check
 │  │          │ │   Tool 3: policy_lookup
 │  └──────────┘ │
 └──────┬───────┘
        ▼
 ┌──────────────┐
 │   Judgment    │   aggregate checks → Verdict + JSON
 └──────────────┘
```

### Data files

| File | Description |
|------|-------------|
| `data/towers_inventory.json` | 120 towers across 3 regions (DXB-North, SHJ-Coastal, SHJ-South) |
| `data/regional_policies.txt` | Municipality rules for 3 regions (height caps, asset-weight limits) |

### Agent tools

| Tool | Input | Output |
|------|-------|--------|
| `tower_lookup` | tower_id | TowerInfo (region, weight capacity) or None |
| `weight_capacity_check` | current_kg, max_kg, new_kg | (fits: bool, total_kg) |
| `policy_lookup` | region | RegionalPolicy (height/weight caps) or None |

---

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python generate_data.py
```

## Usage

```bash
python main.py
python main.py "Operator Etisalat requests a 30kg panel on Tower TWR-102."
python main.py --interactive
python main.py -v
python tests.py
streamlit run app.py
```

Each run prints the tool trace, per-check results, verdict, and a structured JSON output at the end.

For a browser UI, run `streamlit run app.py` — shows operator, tower, reason, verdict, checks, and the full JSON on one page.

`tests.py` runs checks across random towers covering weight limits, height limits, unknown towers, and multi-rule rejections.

## Design Decisions

- **Tool-calling pattern**: each tool is a callable class with typed inputs/outputs. The engine calls them in order and every call is recorded in the trace.
- **Pydantic models**: all data in and out is validated, so the JSON output is always valid.
- **Regex parser**: no NLP libraries — just regex. Covers the request formats in the spec.
- **No-policy regions**: if a region has no rules in the policy file, the request passes rather than getting blocked.
