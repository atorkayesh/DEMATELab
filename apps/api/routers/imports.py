"""Import router: one matrix from a sheet, or every expert's matrix from a workbook (`.xlsx`, ≤ 5 MB)."""

from typing import Annotated, List

from fastapi import APIRouter, File, Form, UploadFile
from starlette.responses import Response

from constants.solver_constants import INPUT_LIMITS
from features.matrix_import_feature import matrix_import_feature
from models.import_models import MatrixImportData, WorkbookImportData
from models.response_model import ApiResponseModel
from utils.response_utils import response_builder

router = APIRouter(prefix="/imports", tags=["imports"])

FactorCount = Annotated[int, Form(ge=INPUT_LIMITS["FACTORS_MIN"], le=INPUT_LIMITS["FACTORS_MAX"])]
UploadedFile = Annotated[UploadFile, File()]
ExpertNames = Annotated[List[str], Form(min_length=INPUT_LIMITS["EXPERTS_MIN"], max_length=INPUT_LIMITS["EXPERTS_MAX"])]


@router.post("/matrix", response_model=ApiResponseModel[MatrixImportData])
async def import_matrix(file: UploadedFile, factor_count: FactorCount) -> Response:
    """
    Import the first sheet as one matrix (plain `n x n` or labelled `(n+1) x (n+1)`).

    Returns:
        Response: ApiResponseModel[MatrixImportData]
    """
    return response_builder.ok(await matrix_import_feature.import_matrix(file, factor_count), "Matrix imported")


@router.post("/workbook", response_model=ApiResponseModel[WorkbookImportData])
async def import_workbook(file: UploadedFile, factor_count: FactorCount, expert_names: ExpertNames) -> Response:
    """
    Import one sheet per expert, matched by name (all names match) or by order.

    Returns:
        Response: ApiResponseModel[WorkbookImportData]
    """
    return response_builder.ok(
        await matrix_import_feature.import_workbook(file, factor_count, expert_names), "Workbook imported"
    )
