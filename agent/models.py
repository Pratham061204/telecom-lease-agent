from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Verdict(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class LeaseRequest(BaseModel):
    operator: str
    equipment_weight_kg: float
    equipment_height_m: Optional[float] = None
    tower_id: str
    raw_text: str


class TowerInfo(BaseModel):
    tower_id: str
    region: str
    max_allowed_weight_kg: float
    current_weight_kg: float


class RegionalPolicy(BaseModel):
    region: str
    max_height_m: Optional[float] = None
    max_single_asset_weight_kg: Optional[float] = None
    raw_rule: str


class CheckResult(BaseModel):
    check: str
    passed: bool
    detail: str


class ToolCall(BaseModel):
    tool: str
    input: dict
    output: str


class AgentJudgment(BaseModel):
    verdict: Verdict
    operator: str
    tower_id: str
    region: Optional[str] = None
    checks: list[CheckResult]
    tool_trace: list[ToolCall]
    summary: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
