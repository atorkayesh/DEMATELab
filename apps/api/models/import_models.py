"""Excel import response models."""

from typing import List, Literal, Optional

from pydantic import BaseModel


class MatrixImportData(BaseModel):
    """One imported matrix; `factor_names` is set when the sheet had a header row and column."""

    factor_names: Optional[List[str]] = None
    matrix: List[List[str]]


class ExpertMatrix(BaseModel):
    """The matrix assigned to one expert."""

    expert_name: str
    matrix: List[List[str]]


class WorkbookImportData(BaseModel):
    """All experts' matrices from one workbook, and how sheets were matched to experts."""

    factor_names: Optional[List[str]] = None
    matrices: List[ExpertMatrix]
    matched_by: Literal["name", "order"]
