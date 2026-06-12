from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from .models import TowerInfo, RegionalPolicy


class TowerLookupTool:

    name = "tower_lookup"

    def __init__(self, inventory_path: str | Path):
        with open(inventory_path) as f:
            data = json.load(f)
        self._index: dict[str, TowerInfo] = {
            t["tower_id"]: TowerInfo(**t) for t in data
        }

    def __call__(self, tower_id: str) -> Optional[TowerInfo]:
        return self._index.get(tower_id)


class PolicyLookupTool:

    name = "policy_lookup"

    def __init__(self, policies_path: str | Path):
        self._policies: dict[str, RegionalPolicy] = {}
        self._parse(policies_path)

    def _parse(self, path: str | Path) -> None:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = re.sub(r"^[\s·•\-*]+", "", line).strip()
                if not line:
                    continue
                m = re.match(r"(.+?)\s+Zone:\s+(.+)", line)
                if not m:
                    continue

                region = m.group(1).strip()
                rule_text = m.group(2).strip()

                policy = RegionalPolicy(region=region, raw_rule=rule_text)

                h = re.search(
                    r"(?:maximum|max).*?height.*?(\d+(?:\.\d+)?)\s*m",
                    rule_text, re.IGNORECASE,
                )
                if h:
                    policy.max_height_m = float(h.group(1))

                w = re.search(
                    r"exceed\s+(\d+(?:\.\d+)?)\s*kg", rule_text, re.IGNORECASE,
                )
                if w:
                    policy.max_single_asset_weight_kg = float(w.group(1))

                self._policies[region] = policy

    def __call__(self, region: str) -> Optional[RegionalPolicy]:
        return self._policies.get(region)


class WeightCapacityTool:

    name = "weight_capacity_check"

    def __call__(
        self,
        current_kg: float,
        max_kg: float,
        new_kg: float,
    ) -> tuple[bool, float]:
        total = current_kg + new_kg
        return total <= max_kg, total
