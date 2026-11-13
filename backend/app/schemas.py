"""Request models shared by the engine and the API."""
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

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
    weights: Optional[dict[Literal["o2", "psi", "flow", "fuel", "grav"], float]] = None  # each weight >= 0, see validator
    k: int = Field(default=10, ge=1, le=50)

    @field_validator("weights")
    @classmethod
    def _weights_ok(cls, w):
        return _check_weights(w)


def _check_weights(w):
    if w is not None and any((v is None) or v < 0 or v > 10 for v in w.values()):
        raise ValueError("weights must be numbers between 0 and 10")
    return w


class TargetRequest(BaseModel):
    target: Target


class AlternativesRequest(BaseModel):
    target: Target
    k: int = Field(default=3, ge=1, le=10)


class NamedTarget(BaseModel):
    """A habitat design with a display name, for the campaign planner."""
    id: str = Field(max_length=40)
    name: str = Field(max_length=60)
    target: Target


class CampaignRequest(BaseModel):
    """How many experiments NASA can fly (n) and which designs they should serve (default: the presets)."""
    n: int = Field(default=3, ge=1, le=10)
    targets: Optional[list[NamedTarget]] = Field(default=None, max_length=12)


class VerifyRequest(BaseModel):
    """Claims to check against the evidence retrieved for a habitat (same rules as /api/explain)."""
    target: Target
    claims: list[dict]
