"""
Health check router.

- `/health`: API status (the API has no dependencies to check).
- `/is-alive`: liveness only, used by the Docker health check.
"""

from fastapi import APIRouter
from starlette.responses import Response

from features.health_feature import health_feature
from models.health_models import AliveData, HealthCheckData
from models.response_model import ApiResponseModel
from utils.response_utils import response_builder

router = APIRouter(tags=["health"])


@router.get("/health", response_model=ApiResponseModel[HealthCheckData])
async def health_check() -> Response:
    """
    Health check endpoint: API status and response time.

    Returns:
        Response: ApiResponseModel[HealthCheckData]
    """
    return response_builder.ok(await health_feature.get_health(), "System is healthy")


@router.get("/is-alive", response_model=ApiResponseModel[AliveData])
async def is_alive() -> Response:
    """
    Simple liveness check endpoint.

    Returns:
        Response: ApiResponseModel[AliveData] with the liveness status
    """
    return response_builder.ok(AliveData(status="alive"), "Service is alive")
