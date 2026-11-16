"""Analysis export router: `POST /analysis/export/xlsx` (the Qt GUI's XLSX export)."""

from fastapi import APIRouter
from starlette.responses import Response

from features.xlsx_export_feature import XLSX_FILENAME, XLSX_MEDIA_TYPE, xlsx_export_feature
from models.analysis_request_models import AnalysisRequest
from utils.response_utils import response_builder

router = APIRouter(prefix="/analysis/export", tags=["analysis"])


@router.post("/xlsx", response_class=Response, responses={200: {"content": {XLSX_MEDIA_TYPE: {}}}})
async def export_xlsx(body: AnalysisRequest) -> Response:
    """
    Download `dematel_results.xlsx`.

    Returns:
        Response: The workbook as an attachment
    """
    return response_builder.download_bytes(await xlsx_export_feature.export(body), XLSX_FILENAME, XLSX_MEDIA_TYPE)
