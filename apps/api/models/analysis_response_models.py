"""Response of `POST /analysis`."""

from typing import List

from pydantic import BaseModel

from models.analysis_result_models import AnalysisResult
from models.summary_models import ResultSummary


class AnalysisResponseData(BaseModel):
    """The result, its summary, and the weights the analysis used after the GUI correction."""

    result: AnalysisResult
    summary: ResultSummary
    corrected_weights: List[float]
