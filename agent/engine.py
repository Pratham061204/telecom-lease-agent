from __future__ import annotations

import logging
from pathlib import Path

from .models import (
    AgentJudgment,
    CheckResult,
    LeaseRequest,
    ToolCall,
    Verdict,
)
from .parser import parse_lease_request
from .tools import TowerLookupTool, PolicyLookupTool, WeightCapacityTool

log = logging.getLogger("lease_agent")


class LeaseVettingAgent:

    def __init__(
        self,
        inventory_path: str | Path = "data/towers_inventory.json",
        policies_path: str | Path = "data/regional_policies.txt",
    ):
        self._tower_lookup = TowerLookupTool(inventory_path)
        self._policy_lookup = PolicyLookupTool(policies_path)
        self._weight_check = WeightCapacityTool()

    def vet(self, request_text: str) -> AgentJudgment:
        checks: list[CheckResult] = []
        trace: list[ToolCall] = []

        req: LeaseRequest = parse_lease_request(request_text)
        log.info(
            "Parsed request — operator=%s  weight=%.1fkg  height=%s  tower=%s",
            req.operator, req.equipment_weight_kg,
            f"{req.equipment_height_m}m" if req.equipment_height_m else "N/A",
            req.tower_id,
        )

        tower = self._tower_lookup(req.tower_id)
        trace.append(ToolCall(
            tool="tower_lookup",
            input={"tower_id": req.tower_id},
            output=f"Found: {tower}" if tower else "NOT FOUND",
        ))

        if tower is None:
            checks.append(CheckResult(
                check="tower_exists",
                passed=False,
                detail=f"Tower {req.tower_id} not found in inventory.",
            ))
            return self._build_judgment(req, checks, trace)

        checks.append(CheckResult(
            check="tower_exists",
            passed=True,
            detail=f"Tower {tower.tower_id} found in region {tower.region}.",
        ))
        log.info("Tower found — region=%s  load=%d/%d kg",
                 tower.region, tower.current_weight_kg, tower.max_allowed_weight_kg)

        fits, total = self._weight_check(
            tower.current_weight_kg, tower.max_allowed_weight_kg,
            req.equipment_weight_kg,
        )
        trace.append(ToolCall(
            tool="weight_capacity_check",
            input={
                "current_kg": tower.current_weight_kg,
                "max_kg": tower.max_allowed_weight_kg,
                "new_kg": req.equipment_weight_kg,
            },
            output=f"total={total}kg  fits={fits}",
        ))
        checks.append(CheckResult(
            check="weight_capacity",
            passed=fits,
            detail=(
                f"{tower.current_weight_kg}kg + {req.equipment_weight_kg}kg "
                f"= {total}kg  (max {tower.max_allowed_weight_kg}kg)"
            ),
        ))

        policy = self._policy_lookup(tower.region)
        trace.append(ToolCall(
            tool="policy_lookup",
            input={"region": tower.region},
            output=f"Found: {policy}" if policy else "No policy for this region.",
        ))

        if policy is None:
            checks.append(CheckResult(
                check="regional_policy",
                passed=True,
                detail=f"No regional restrictions for {tower.region}.",
            ))
        else:
            if policy.max_height_m is not None:
                if req.equipment_height_m is not None:
                    ok = req.equipment_height_m <= policy.max_height_m
                    checks.append(CheckResult(
                        check="regional_height_limit",
                        passed=ok,
                        detail=(
                            f"Requested {req.equipment_height_m}m vs "
                            f"region max {policy.max_height_m}m."
                        ),
                    ))
                else:
                    checks.append(CheckResult(
                        check="regional_height_limit",
                        passed=True,
                        detail="No height specified in request; height limit not applicable.",
                    ))

            if policy.max_single_asset_weight_kg is not None:
                ok = req.equipment_weight_kg <= policy.max_single_asset_weight_kg
                checks.append(CheckResult(
                    check="regional_asset_weight_limit",
                    passed=ok,
                    detail=(
                        f"Asset {req.equipment_weight_kg}kg vs "
                        f"region max {policy.max_single_asset_weight_kg}kg."
                    ),
                ))

        return self._build_judgment(req, checks, trace, tower.region)

    @staticmethod
    def _build_judgment(
        req: LeaseRequest,
        checks: list[CheckResult],
        trace: list[ToolCall],
        region: str | None = None,
    ) -> AgentJudgment:
        all_passed = all(c.passed for c in checks)
        failed = [c for c in checks if not c.passed]

        if all_passed:
            summary = (
                f"APPROVED — all {len(checks)} checks passed for "
                f"{req.operator}'s request on {req.tower_id}."
            )
        else:
            reasons = ", ".join(c.check for c in failed)
            summary = (
                f"REJECTED — {len(failed)} check(s) failed: {reasons}."
            )

        verdict = Verdict.APPROVED if all_passed else Verdict.REJECTED
        log.info("Verdict: %s — %s", verdict.value, summary)

        return AgentJudgment(
            verdict=verdict,
            operator=req.operator,
            tower_id=req.tower_id,
            region=region,
            checks=checks,
            tool_trace=trace,
            summary=summary,
        )
