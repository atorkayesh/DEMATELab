"""Excel import errors."""

from http import HTTPStatus

from errors.app_error import AppError


class InvalidImportError(AppError):
    """The workbook was read but does not hold a valid matrix (Qt parser or editor message)."""

    code = "invalid_import"
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    public_message = "The uploaded workbook could not be imported."


class UnsupportedFileError(AppError):
    """The upload is not an `.xlsx` workbook."""

    code = "unsupported_file"
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    public_message = "Only .xlsx workbooks can be imported."


class UploadTooLargeError(AppError):
    """The upload exceeds the size limit."""

    code = "upload_too_large"
    status_code = HTTPStatus.REQUEST_ENTITY_TOO_LARGE
    public_message = "The uploaded file is larger than 5 MB."
