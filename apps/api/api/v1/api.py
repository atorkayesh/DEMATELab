"""
API v1 router aggregation.

This module serves as the central point for all API v1 routes. Every router is registered here and
mounted by main.py. All routes are public: the API is stateless and has no accounts.
"""

from fastapi import APIRouter

from routers.analysis import router as analysis_router
from routers.analysis_charts import router as analysis_charts_router
from routers.analysis_export import router as analysis_export_router
from routers.explanations import router as explanations_router
from routers.health import router as health_router
from routers.imports import router as imports_router
from routers.scales import router as scales_router
from routers.weights import router as weights_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(scales_router)
api_router.include_router(weights_router)
api_router.include_router(analysis_router)
api_router.include_router(analysis_export_router)
api_router.include_router(analysis_charts_router)
api_router.include_router(imports_router)
api_router.include_router(explanations_router)
