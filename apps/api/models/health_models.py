"""Health check models."""

from typing import Dict, Literal, Optional

from pydantic import BaseModel

ServiceState = Literal["up", "down"]
HealthState = Literal["healthy", "unhealthy"]


class ServiceStatus(BaseModel):
    """Health status of one service."""

    status: ServiceState
    response_time_ms: Optional[float] = None
    error: Optional[str] = None


class HealthCheckData(BaseModel):
    """Health check response data."""

    status: HealthState
    services: Dict[str, ServiceStatus]


class AliveData(BaseModel):
    """Liveness check response data."""

    status: Literal["alive"]
