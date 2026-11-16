"""Health check errors."""

from http import HTTPStatus

from errors.app_error import AppError


class ServiceUnhealthyError(AppError):
    """A dependency is down. Carries the health details as `data`."""

    code = "service_unhealthy"
    status_code = HTTPStatus.SERVICE_UNAVAILABLE
    public_message = "System is unhealthy"
