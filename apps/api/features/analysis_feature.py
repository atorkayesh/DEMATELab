"""
Analysis orchestration: the API's `run_analysis` (`analysis_service.py:94-157`) plus the GUI steps before it.

Request → weight correction (`gui_app._normalize_weight_inputs`) → diagonal forced to the solver's
no-influence label (matrix editor) → linguistic conversion → engine → result model and summary. Fuzzy
Z-DEMATEL is the Z converter plus the fuzzy engine. CPU work runs in a worker thread.
"""

import asyncio
from typing import Optional, Union

from constants.solver_constants import SolverType
from features.crisp_dematel_feature import CrispDematelFeature, crisp_dematel_feature
from features.fuzzy_dematel_feature import FuzzyDematelFeature, fuzzy_dematel_feature
from features.grey_dematel_feature import GreyDematelFeature, grey_dematel_feature
from features.linguistic_conversion_feature import LinguisticConversionFeature, linguistic_conversion_feature
from features.result_summary_feature import ResultSummaryFeature, result_summary_feature
from features.weight_normalization_feature import WeightNormalizationFeature, weight_normalization_feature
from models.analysis_request_models import AnalysisRequest
from models.analysis_response_models import AnalysisResponseData
from models.analysis_result_models import CrispAnalysisResult, FuzzyAnalysisResult, GreyAnalysisResult
from models.solver_models import SolverExpert, SolverOutput
from utils.matrix_utils import MatrixConverter, matrix_converter


class AnalysisFeature:
    """Runs an analysis request through the solvers."""

    def __init__(
        self,
        weights: Optional[WeightNormalizationFeature] = None,
        conversion: Optional[LinguisticConversionFeature] = None,
        crisp: Optional[CrispDematelFeature] = None,
        fuzzy: Optional[FuzzyDematelFeature] = None,
        grey: Optional[GreyDematelFeature] = None,
        summary: Optional[ResultSummaryFeature] = None,
        converter: Optional[MatrixConverter] = None,
    ):
        """
        Create the feature.

        Args:
            weights: Weight correction; defaults to the shared instance
            conversion: Linguistic conversion; defaults to the shared instance
            crisp: Classical engine; defaults to the shared instance
            fuzzy: Fuzzy engine (also fuzzy Z); defaults to the shared instance
            grey: Grey engine; defaults to the shared instance
            summary: Summary feature; defaults to the shared instance
            converter: Array conversions; defaults to the shared instance
        """
        self._weights = weights or weight_normalization_feature
        self._conversion = conversion or linguistic_conversion_feature
        self._crisp = crisp or crisp_dematel_feature
        self._fuzzy = fuzzy or fuzzy_dematel_feature
        self._grey = grey or grey_dematel_feature
        self._summary = summary or result_summary_feature
        self._converter = converter or matrix_converter

    async def analyze(self, request: AnalysisRequest) -> AnalysisResponseData:
        """
        Run the analysis in a worker thread.

        Args:
            request: Validated analysis request

        Returns:
            AnalysisResponseData: Result, summary, and corrected weights
        """
        return await asyncio.to_thread(self.analyze_sync, request)

    def analyze_sync(self, request: AnalysisRequest) -> AnalysisResponseData:
        """
        Run the analysis in the calling thread.

        Args:
            request: Validated analysis request

        Returns:
            AnalysisResponseData: Result, summary, and corrected weights
        """
        output = self.solve(request)
        return AnalysisResponseData(
            result=self.to_result_model(output),
            summary=self._summary.summarize(output),
            corrected_weights=output.expert_weights,
        )

    def solve(self, request: AnalysisRequest) -> SolverOutput:
        """
        Correct the weights, convert the matrices, and run the solver.

        Args:
            request: Validated analysis request

        Returns:
            SolverOutput: Engine output (numpy arrays)

        Raises:
            InvalidWeightsError: When the weights do not sum to 1 within the tolerance
            UnknownLinguisticTermError: When a cell is not on the solver's scale
            AnalysisFailedError: When the solver cannot produce a result
        """
        solver = request.solver_type
        weights = self._weights.normalize([expert.weight for expert in request.experts])
        experts = [
            SolverExpert(
                name=expert.name,
                weight=weight,
                matrix=self._conversion.convert(
                    solver, self._conversion.force_diagonal(expert.matrix, solver), expert.name, request.factors
                ),
            )
            for expert, weight in zip(request.experts, weights, strict=True)
        ]
        if solver == SolverType.DEMATEL:
            return self._crisp.solve(request.factors, experts, request.threshold_method)
        if solver == SolverType.GREY_DEMATEL:
            return self._grey.solve(request.factors, experts, request.threshold_method)
        return self._fuzzy.solve(request.factors, experts, request.threshold_method, solver)

    def to_result_model(
        self, output: SolverOutput
    ) -> Union[CrispAnalysisResult, FuzzyAnalysisResult, GreyAnalysisResult]:
        """
        Convert an engine output into the response model with the Qt field names.

        Args:
            output: Engine output

        Returns:
            Union[CrispAnalysisResult, FuzzyAnalysisResult, GreyAnalysisResult]: Result for the solver type
        """
        lists = self._converter.to_lists
        common = {
            "factors": output.factors,
            "expert_weights": output.expert_weights,
            "r": lists(output.r),
            "c": lists(output.c),
            "prominence": lists(output.prominence),
            "relation": lists(output.relation),
            "cause_group": output.cause_group,
            "effect_group": output.effect_group,
            "threshold_method": output.threshold_method,
            "threshold_value": output.threshold_value,
            "crisp_total_matrix": lists(output.crisp_total_matrix),
        }
        if output.solver_type == SolverType.DEMATEL:
            return CrispAnalysisResult(
                **common,
                direct_matrix=lists(output.direct_matrix),
                normalized_matrix=lists(output.normalized_matrix),
                total_matrix=lists(output.total_matrix),
            )
        prefix = "grey" if output.solver_type == SolverType.GREY_DEMATEL else "fuzzy"
        prefixed = {
            f"{prefix}_direct_matrix": lists(output.direct_matrix),
            f"{prefix}_normalized_matrix": lists(output.normalized_matrix),
            f"{prefix}_total_matrix": lists(output.total_matrix),
            f"{prefix}_r": lists(output.raw_r),
            f"{prefix}_c": lists(output.raw_c),
            f"{prefix}_prominence": lists(output.raw_prominence),
            f"{prefix}_relation": lists(output.raw_relation),
        }
        if prefix == "grey":
            return GreyAnalysisResult(**common, **prefixed)
        return FuzzyAnalysisResult(solver_type=output.solver_type.value, **common, **prefixed)


analysis_feature = AnalysisFeature()
