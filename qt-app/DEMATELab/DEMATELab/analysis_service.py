# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 13:42:10 2026

@author: Ali
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .constants import ThresholdMethod
from .dematel_core import DematelEngine, ExpertInput, linguistic_to_numeric_matrix
from .fuzzy_dematel_core import (
    FuzzyDematelEngine,
    FuzzyExpertInput,
    linguistic_to_fuzzy_matrix,
)
from .grey_dematel_core import (
    GreyDematelEngine,
    GreyExpertInput,
    linguistic_to_grey_matrix,
)
from .fuzzy_z_dematel_core import z_linguistic_to_fuzzy_matrix


SolverType = Literal["dematel", "fuzzy_dematel", "grey_dematel", "fuzzy_z_dematel"]


@dataclass(slots=True)
class ExpertFormData:
    name: str
    weight: float
    matrix: list[list[str]]


@dataclass(slots=True)
class AnalysisInput:
    solver_type: str
    factors: list[str]
    experts: list[ExpertFormData]
    threshold_method: str | None = None


def _normalize_solver_type(value: str) -> str:
    normalized = value.strip().lower().replace(" ", "_").replace("-", "_")

    if normalized == "dematel":
        return "dematel"

    if normalized in {"fuzzy_dematel", "fuzzydematel"}:
        return "fuzzy_dematel"

    if normalized in {"grey_dematel", "greydematel"}:
        return "grey_dematel"

    if normalized in {"fuzzy_z_dematel", "fuzzyzdematel", "z_dematel", "fz_dematel"}:
        return "fuzzy_z_dematel"

    raise ValueError(f"Unsupported solver type: {value}")


def _normalize_threshold_method(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip().lower().replace(" ", "_").replace("-", "_")
    if normalized == "":
        return None

    mapping = {
        "average": "average",
        "first_quartile": "first_quartile",
        "median": "median",
        "third_quartile": "third_quartile",
        "mmde": "mmde",
        "maximum_mean_de_entropy": "mmde",
    }

    if normalized not in mapping:
        raise ValueError(f"Unsupported threshold method: {value}")

    return mapping[normalized]


def _parse_threshold_method(threshold_method: str | None) -> ThresholdMethod | None:
    normalized = _normalize_threshold_method(threshold_method)
    if normalized is None:
        return None
    return ThresholdMethod(normalized)


def run_analysis(payload: AnalysisInput):
    solver_type = _normalize_solver_type(payload.solver_type)
    threshold = _parse_threshold_method(payload.threshold_method)

    # ----------------------------
    # DEMATEL
    # ----------------------------
    if solver_type == "dematel":
        experts = [
            ExpertInput(
                name=expert.name,
                weight=expert.weight,
                matrix=linguistic_to_numeric_matrix(expert.matrix),
            )
            for expert in payload.experts
        ]
        engine = DematelEngine(factors=payload.factors, experts=experts)
        return engine.solve(threshold_method=threshold)

    # ----------------------------
    # FUZZY DEMATEL
    # ----------------------------
    if solver_type == "fuzzy_dematel":
        experts = [
            FuzzyExpertInput(
                name=expert.name,
                weight=expert.weight,
                matrix=linguistic_to_fuzzy_matrix(expert.matrix),
            )
            for expert in payload.experts
        ]
        engine = FuzzyDematelEngine(factors=payload.factors, experts=experts)
        return engine.solve(threshold_method=threshold)

    # ----------------------------
    # GREY DEMATEL
    # ----------------------------
    if solver_type == "grey_dematel":
        experts = [
            GreyExpertInput(
                name=expert.name,
                weight=expert.weight,
                matrix=linguistic_to_grey_matrix(expert.matrix),
            )
            for expert in payload.experts
        ]
        engine = GreyDematelEngine(factors=payload.factors, experts=experts)
        return engine.solve(threshold_method=threshold)

    # ----------------------------
    # FUZZY Z-DEMATEL
    # ----------------------------
    if solver_type == "fuzzy_z_dematel":
        experts = [
            FuzzyExpertInput(
                name=expert.name,
                weight=expert.weight,
                matrix=z_linguistic_to_fuzzy_matrix(expert.matrix),
            )
            for expert in payload.experts
        ]
        engine = FuzzyDematelEngine(factors=payload.factors, experts=experts)
        return engine.solve(threshold_method=threshold)

    raise ValueError(f"Unsupported solver type: {payload.solver_type}")