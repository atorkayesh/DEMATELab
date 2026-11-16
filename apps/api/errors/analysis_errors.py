"""Analysis errors: invalid input to the solvers and failures while solving."""

from http import HTTPStatus

from errors.app_error import AppError


class InvalidAnalysisInputError(AppError):
    """The analysis input does not satisfy a solver rule (shape, weights, factors). Uses the Qt message."""

    code = "invalid_analysis_input"
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    public_message = "The analysis input is invalid."


class UnknownLinguisticTermError(AppError):
    """A matrix cell holds a label that is not on the solver's linguistic scale."""

    code = "unknown_linguistic_term"
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    public_message = "A matrix cell holds an unknown linguistic term."


class InvalidWeightsError(AppError):
    """The expert weights do not sum to 1 within the GUI tolerance."""

    code = "invalid_weights"
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    public_message = "Expert weights must sum to 1."


class AnalysisFailedError(AppError):
    """The solver could not produce a result (all cells "No influence", or (I - X) not invertible)."""

    code = "analysis_failed"
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    public_message = "The analysis could not be completed."


class ClusteringFailedError(AppError):
    """The total relation matrix cannot be split into the four cluster groups."""

    code = "clustering_failed"
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    public_message = "Could not generate cluster heatmap."
