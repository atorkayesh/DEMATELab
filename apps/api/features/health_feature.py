"""
Health check logic.

The API is stateless and has no dependencies (no database, no stored AI provider), so the health check
reports the API itself.
"""

from models.health_models import HealthCheckData, ServiceStatus


class HealthFeature:
    """API health check."""

    async def get_health(self) -> HealthCheckData:
        """
        Report the API status.

        Returns:
            HealthCheckData: `healthy`, with the API `up`
        """
        return HealthCheckData(status="healthy", services={"api": ServiceStatus(status="up")})


health_feature = HealthFeature()
