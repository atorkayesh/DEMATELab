"""
Loader for the fixtures generated from `qt-app/` by `scripts/generate_parity_fixtures.py`.

Never edit the fixtures by hand: regenerate them from the Qt app.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

from constants.solver_constants import SolverType
from features.linguistic_conversion_feature import linguistic_conversion_feature
from models.solver_models import SolverExpert

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class ParityFixtures:
    """Reads parity, import, and XLSX fixtures."""

    def parity(self) -> List[Tuple[str, Dict]]:
        """Return (name, fixture) for every analysis fixture, sorted by name."""
        return [(path.stem, self._load(path)) for path in sorted((FIXTURES_DIR / "parity").glob("*.json"))]

    def parity_case(self, name: str) -> Dict:
        """Return one analysis fixture by name (`<case>__<solver>__<threshold>`)."""
        return self._load(FIXTURES_DIR / "parity" / f"{name}.json")

    def solver_experts(self, name: str, solver: SolverType) -> Tuple[Dict, List[str], List[SolverExpert]]:
        """Return (fixture, factors, engine experts) built from a fixture as the GUI passes them."""
        fixture = self.parity_case(name)
        request = fixture["request"]
        convert = linguistic_conversion_feature
        experts = [
            SolverExpert(
                expert["name"],
                weight,
                convert.convert(
                    solver, convert.force_diagonal(expert["matrix"], solver), expert["name"], request["factors"]
                ),
            )
            for expert, weight in zip(request["experts"], fixture["corrected_weights"], strict=True)
        ]
        return fixture, request["factors"], experts

    def imports(self) -> List[Tuple[str, Dict, bytes]]:
        """Return (name, fixture, workbook bytes) for every import fixture."""
        folder = FIXTURES_DIR / "imports"
        return [
            (path.stem, fixture, (folder / fixture["file"]).read_bytes())
            for path in sorted(folder.glob("*.json"))
            for fixture in [self._load(path)]
        ]

    def xlsx_path(self, name: str) -> Path:
        """Return the path of a Qt-exported workbook."""
        return FIXTURES_DIR / "xlsx" / f"{name}.xlsx"

    def _load(self, path: Path) -> Dict:
        return json.loads(path.read_text(encoding="utf-8"))


parity_fixtures = ParityFixtures()
