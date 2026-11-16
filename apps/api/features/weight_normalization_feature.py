"""
Expert weight defaults and correction, ported verbatim from the Qt GUI (`gui_app.py:55-101`).

Weights are rounded to thousandths; a total within ±0.005 of 1 is corrected by moving the remaining
thousandths onto the experts from the last one backwards.
"""

from typing import List, Optional

from constants.weight_constants import WEIGHT_SETTINGS
from errors.analysis_errors import InvalidWeightsError


class WeightNormalizationFeature:
    """Default weights and the GUI's weight correction."""

    def __init__(
        self, decimals: int = WEIGHT_SETTINGS["DECIMALS"], tolerance: float = WEIGHT_SETTINGS["SUM_TOLERANCE"]
    ):
        """
        Create the feature.

        Args:
            decimals: Decimals weights are rounded to
            tolerance: Largest accepted distance of the total from 1
        """
        self._units = 10**decimals
        self._tolerance = tolerance

    def default_weights(self, expert_count: int) -> List[float]:
        """
        Equal weights in thousandths, the remainder going to the first experts one by one.

        Args:
            expert_count: Number of experts (at least 1)

        Returns:
            List[float]: Weights summing to 1
        """
        base, remainder = divmod(self._units, expert_count)
        return [(base + (1 if index < remainder else 0)) / self._units for index in range(expert_count)]

    def normalize(self, weights: List[float]) -> List[float]:
        """
        Correct weights whose total is within the tolerance of 1.

        Args:
            weights: Entered weights

        Returns:
            List[float]: Corrected weights in thousandths, summing to 1

        Raises:
            InvalidWeightsError: When the total is outside the tolerance or cannot be corrected
        """
        corrected = self._correct(weights)
        if corrected is None:
            raise InvalidWeightsError(f"Weights {weights} cannot be corrected to sum to 1")
        return corrected

    def _correct(self, weights: List[float]) -> Optional[List[float]]:
        """Return the corrected weights, or `None` when the GUI would reject them."""
        if not weights:
            return []
        total = sum(weights)
        if total <= 0 or abs(total - 1.0) > self._tolerance:
            return None
        units = [int(round(weight * self._units)) for weight in weights]
        remainder = self._units - sum(units)
        if remainder > 0:
            remainder = self._shift(units, remainder, add=True)
        elif remainder < 0:
            remainder = self._shift(units, -remainder, add=False)
        if remainder != 0:
            return None
        return [value / self._units for value in units]

    def _shift(self, units: List[int], remainder: int, add: bool) -> int:
        """Move `remainder` thousandths onto (or off) the experts from the last one backwards; return what is left."""
        for index in range(len(units) - 1, -1, -1):
            available = self._units - units[index] if add else units[index]
            if available <= 0:
                continue
            adjustment = min(remainder, available)
            units[index] += adjustment if add else -adjustment
            remainder -= adjustment
            if remainder == 0:
                break
        return remainder


weight_normalization_feature = WeightNormalizationFeature()
