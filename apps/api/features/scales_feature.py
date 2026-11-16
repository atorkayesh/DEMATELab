"""Static input metadata: scales, solver and threshold options, limits, and weight rules."""

from constants.linguistic_constants import (
    LINGUISTIC_TERMS,
    NO_INFLUENCE_LABEL,
    Z_INFLUENCE_TERMS,
    Z_LINGUISTIC_TERMS,
    Z_NO_INFLUENCE_DEFAULT,
    Z_RELIABILITY_TERMS,
)
from constants.solver_constants import INPUT_LIMITS, SOLVER_LABELS, THRESHOLD_LABELS, SolverType
from constants.weight_constants import DEFAULT_WEIGHTS_RULE, WEIGHT_SETTINGS
from models.scale_models import InputLimits, Option, ScaleFamily, ScalesData, WeightRules


class ScalesFeature:
    """Describes what the GUI lets users enter."""

    def get_scales(self) -> ScalesData:
        """
        Return the scales and options.

        Returns:
            ScalesData: Terms per solver family, options, limits, and weight rules
        """
        return ScalesData(
            standard=ScaleFamily(
                solvers=[SolverType.DEMATEL.value, SolverType.FUZZY_DEMATEL.value, SolverType.GREY_DEMATEL.value],
                terms=LINGUISTIC_TERMS,
                default_label=NO_INFLUENCE_LABEL,
                diagonal_label=NO_INFLUENCE_LABEL,
            ),
            fuzzy_z=ScaleFamily(
                solvers=[SolverType.FUZZY_Z_DEMATEL.value],
                terms=Z_LINGUISTIC_TERMS,
                default_label=Z_NO_INFLUENCE_DEFAULT,
                diagonal_label=Z_NO_INFLUENCE_DEFAULT,
                influence_terms=Z_INFLUENCE_TERMS,
                reliability_terms=Z_RELIABILITY_TERMS,
            ),
            solvers=[Option(key=key.value, label=label) for key, label in SOLVER_LABELS.items()],
            thresholds=[Option(key=key.value, label=label) for key, label in THRESHOLD_LABELS.items()],
            limits=InputLimits(**{key.lower(): value for key, value in INPUT_LIMITS.items()}),
            weights=WeightRules(
                decimals=WEIGHT_SETTINGS["DECIMALS"],
                step=WEIGHT_SETTINGS["STEP"],
                sum_tolerance=WEIGHT_SETTINGS["SUM_TOLERANCE"],
                default_rule=DEFAULT_WEIGHTS_RULE,
            ),
        )


scales_feature = ScalesFeature()
