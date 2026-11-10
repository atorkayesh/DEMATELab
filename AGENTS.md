# Repository guidance

## Setup and launch
- The installable project is `DEMATELab/pyproject.toml`, not the repository root; Python must be >=3.10. From the root, install for development with `python3 -m pip install -e ./DEMATELab`.
- Launch from the outer `DEMATELab/` directory with `python3 -m DEMATELab` (or the installed `DEMATELab` command). Both call `DEMATELab.gui_app:main`; running `gui_app.py` directly is not the entrypoint.
- Keep that working directory: stepper icons and stylesheet URLs use relative `assets/icons/...` paths, while logos/fonts use package-relative `DEMATELab/DEMATELab/assets/`. These two asset directories are not interchangeable.
- `DEMATELab.app` is a launcher, not a standalone distribution: it executes `/opt/miniconda3/bin/python3` against the adjacent source checkout.

## Execution paths and editing traps
Paths below are relative to `DEMATELab/DEMATELab/`.

- **Duplicate definitions:** `gui_app.py` defines `StepperWidget`, `FloatStepperWidget`, `MainWindow`, and `main` twice. The later definitions override the earlier ones; locate the active definition before editing.
- Analysis flows from `gui_app.py` through `analysis_service.run_analysis(AnalysisInput)` into the numerical engines. This service is the GUI-independent entrypoint for focused solver checks.
- Fuzzy Z-DEMATEL only has a separate linguistic converter (`fuzzy_z_dematel_core.py`); it reuses `FuzzyExpertInput`, `FuzzyDematelEngine`, and `FuzzyDematelResult`, not a separate Z engine/result.
- Result matrices differ: classical uses `(n, n)` arrays and unprefixed fields; fuzzy/Z use `(n, n, 3)` arrays and `fuzzy_*` fields; grey uses `(n, n, 2)` arrays and `grey_*` fields. All expose scalar `r`, `c`, `prominence`, and `relation` vectors. The viewer resolves matrix fields via `_get_matrix_attr`.
- GUI XLSX/PNG exports are implemented in `results_viewer_widget.py`; they do not call `export_service.py`. Changing the latter alone will not change GUI exports.
- AI requests run through `ExplanationWorker` in a `QThread`, wired and cleaned up in `results_viewer_widget.py`; provider requests live in `llm_explanation_service.py`.

## Input contracts
- `constants.py` owns linguistic maps. Standard scales end in `Extreme influence`; Z uses `Very high influence` plus reliability. Labels are case-sensitive after trimming.
- `matrix_parsers.py` handles Excel imports: one sheet per expert for workbook imports, either an `n x n` body or an `(n+1) x (n+1)` labeled matrix. Named-import paths require matching row/column factor names and consistent names across sheets; comparisons are case-insensitive. Imported diagonals are forced to `No influence`.
- Engine weights must sum to 1; the GUI's three-decimal rounding/tolerance correction is in `_normalize_weight_inputs`, not in `analysis_service.run_analysis`.

## Verification
- No automated tests, CI workflows, lockfile, or lint/formatter/typecheck configuration is checked in. Do not assume `pytest` or other quality tools are installed.
- Minimum syntax check from the repository root: `python3 -m compileall -q DEMATELab/DEMATELab`. This does not verify numerical correctness or GUI behavior.
- For behavior changes, launch the GUI and exercise the affected solver/import/export flow. Sample workbooks are in `Example data/`; AI explanation additionally requires a provider API key and network access.
- `font_loader.ensure_inter_fonts` may download Inter from GitHub if the package's `assets/fonts/Inter-Regular.ttf` is missing; download failures silently fall back to available fonts.
