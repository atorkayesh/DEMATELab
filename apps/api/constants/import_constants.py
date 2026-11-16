"""Upload limits for the Excel imports."""

IMPORT_SETTINGS = {
    "MAX_UPLOAD_BYTES": 5 * 1024 * 1024,
    "ALLOWED_EXTENSIONS": (".xlsx",),
    "SOURCE_LABEL": "Uploaded sheet",
}
