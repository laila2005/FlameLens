"""Request models shared by the engine and the API."""
from typing import Literal, Optional

from pydantic import BaseModel, Field

FuelState = Literal["solid", "liquid", "gas", "any"]


class Target(BaseModel):
    """A habitat design the engineer wants evidence for."""
    o2_pct: float = Field(ge=0, le=100, description="oxygen percent by volume")
    pressure_psi: float = Field(gt=0, le=200, description="total pressure in psi")
    airflow_cm_s: Optional[float] = Field(default=None, ge=0, le=500, description="airflow in cm/s, None if unknown")
    gravity_g: float = Field(default=0, ge=0, le=1, description="0 = microgravity, 0.16 lunar, 0.38 Mars, 1 Earth")
    fuel_state: FuelState = "any"


class RankRequest(BaseModel):
    target: Target
    weights: Optional[dict] = None  # keys o2, psi, flow, fuel, grav
    k: int = Field(default=10, ge=1, le=50)


class TargetRequest(BaseModel):
    target: Target


class AlternativesRequest(BaseModel):
    target: Target
    k: int = Field(default=3, ge=1, le=10)


class CampaignRequest(BaseModel):
    n: int = Field(default=3, ge=1, le=10)
    targets: list[Target]


class VerifyRequest(BaseModel):
    """Claims to check against the evidence retrieved for a habitat (same rules as /api/explain)."""
    target: Target
    claims: list[dict]
