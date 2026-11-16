"""
Explanation payload and prompt, verbatim from `llm_explanation_service.py:38-97` except the real
`solver_type` and the grey interval vectors (Settled Decision 8).
"""

import json
from typing import Any, Dict

from constants.solver_constants import SolverType
from models.solver_models import SolverOutput

PROMPT_TEMPLATE = """
You are an analytical thinker. Explain the following DEMATEL results in several clear academic-style paragraphs.

Your explanation should:
- describe the overall structure of the system,
- explain which factors belong to the cause group and which belong to the effect group,
- use the relation value (R-C) to determine causal direction,
- use prominence (R+C) only to describe overall importance or centrality,
- do not infer cause/effect from prominence or from high/low prominence scores,
- comment on the most influential factors by separating importance (prominence) from direction (relation),
- explain what the threshold means for interpreting the system,
- explain the total relation matrix and how factors affect each other,
- avoid bullet points,
- avoid repeating the raw numbers too much,
- stay grounded in the data only.

Method rules:
- Cause group means relation >= 0.
- Effect group means relation < 0.
- Prominence measures importance, not causal direction.
- If a factor has high prominence but negative relation, describe it as important but effect-oriented.
- If a factor has low prominence but positive relation, describe it as less central but cause-oriented.

Data:
{data}
"""


class ExplanationPromptFeature:
    """Builds the data payload and the prompt sent to the AI provider."""

    def build_payload(self, output: SolverOutput) -> Dict[str, Any]:
        """
        Build the result payload in Qt's key order.

        Args:
            output: Solver output

        Returns:
            Dict[str, Any]: Payload
        """
        payload: Dict[str, Any] = {
            "factors": output.factors,
            "cause_group": output.cause_group,
            "effect_group": output.effect_group,
            "threshold_method": output.threshold_method.value,
            "threshold_value": output.threshold_value,
            "prominence": [float(x) for x in output.prominence],
            "relation": [float(x) for x in output.relation],
            "metric_definitions": {
                "prominence": "R+C, used only for overall importance/centrality",
                "relation": "R-C, used for causal direction",
                "cause_rule": "relation >= 0",
                "effect_rule": "relation < 0",
            },
            "solver_type": output.solver_type.value,
        }
        if output.raw_prominence is not None:
            prefix = "grey" if output.solver_type == SolverType.GREY_DEMATEL else "fuzzy"
            payload[f"{prefix}_prominence"] = [[float(v) for v in row] for row in output.raw_prominence]
            payload[f"{prefix}_relation"] = [[float(v) for v in row] for row in output.raw_relation]
        return payload

    def build_prompt(self, payload: Dict[str, Any]) -> str:
        """
        Fill the prompt template.

        Args:
            payload: Result payload

        Returns:
            str: Prompt text
        """
        return PROMPT_TEMPLATE.format(data=json.dumps(payload, indent=2, ensure_ascii=False)).strip()


explanation_prompt_feature = ExplanationPromptFeature()
