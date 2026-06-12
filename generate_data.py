import json, random, pathlib

random.seed(42)

REGIONS = {
    "DXB-North":   (450, 550),
    "SHJ-Coastal": (250, 350),
    "SHJ-South":   (200, 300),
}

towers = [
    {"tower_id": "TWR-101", "region": "DXB-North",
     "max_allowed_weight_kg": 500, "current_weight_kg": 460},
    {"tower_id": "TWR-102", "region": "SHJ-Coastal",
     "max_allowed_weight_kg": 300, "current_weight_kg": 120},
]

tower_num = 103
COUNTS = {"DXB-North": 39, "SHJ-Coastal": 39, "SHJ-South": 40}

for region, count in COUNTS.items():
    lo, hi = REGIONS[region]
    for _ in range(count):
        mx = random.randint(lo, hi)
        cur = random.randint(int(mx * 0.25), int(mx * 0.95))
        towers.append({
            "tower_id": f"TWR-{tower_num}",
            "region": region,
            "max_allowed_weight_kg": mx,
            "current_weight_kg": cur,
        })
        tower_num += 1

out = pathlib.Path(__file__).parent / "data" / "towers_inventory.json"
out.write_text(json.dumps(towers, indent=2))
print(f"Generated {len(towers)} towers -> {out}")

from collections import Counter
c = Counter(t["region"] for t in towers)
for r, n in sorted(c.items()):
    print(f"  {r}: {n}")
