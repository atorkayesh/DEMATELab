# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 19:05:03 2026

@author: Ali
"""

from __future__ import annotations

import json

import httpx
from google import genai

from .constants import LLM_MODEL


SUPPORTED_ENGINES = {
    "Groq",
    "OpenRouter",
    "Gemini",
    "OpenAI",
}


DEFAULT_MODELS = {
    "Groq": "llama-3.3-70b-versatile",
    "OpenRouter": "openai/gpt-4o-mini",
    "Gemini": LLM_MODEL,
    "OpenAI": "gpt-4o-mini",
}


def build_result_payload(result) -> dict:
    payload = {
        "factors": result.factors,
        "cause_group": result.cause_group,
        "effect_group": result.effect_group,
        "threshold_method": result.threshold_method,
        "threshold_value": result.threshold_value,
        "prominence": [float(x) for x in result.prominence],
        "relation": [float(x) for x in result.relation],
        "metric_definitions": {
            "prominence": "R+C, used only for overall importance/centrality",
            "relation": "R-C, used for causal direction",
            "cause_rule": "relation >= 0",
            "effect_rule": "relation < 0",
        },
    }

    if hasattr(result, "fuzzy_direct_matrix"):
        payload["solver_type"] = "fuzzy_dematel"
        payload["fuzzy_prominence"] = [
            [float(v[0]), float(v[1]), float(v[2])]
            for v in result.fuzzy_prominence
        ]
        payload["fuzzy_relation"] = [
            [float(v[0]), float(v[1]), float(v[2])]
            for v in result.fuzzy_relation
        ]
    else:
        payload["solver_type"] = "dematel"

    return payload


def build_prompt(payload: dict) -> str:
    return f"""
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
{json.dumps(payload, indent=2, ensure_ascii=False)}
""".strip()


def _generate_with_openai_compatible(
    *,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    referer: str | None = None,
    title: str | None = None,
) -> str:
    headers = {
        "Authorization": f"Bearer {api_key.strip()}",
        "Content-Type": "application/json",
    }

    if referer:
        headers["HTTP-Referer"] = referer
    if title:
        headers["X-Title"] = title

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are an expert academic analyst interpreting DEMATEL results.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": 0.4,
    }

    with httpx.Client(timeout=120.0) as client:
        response = client.post(base_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    try:
        return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        raise ValueError("Unexpected response format from the selected LLM provider.") from exc


def _generate_with_gemini(
    *,
    api_key: str,
    model: str,
    prompt: str,
) -> str:
    client = genai.Client(api_key=api_key.strip())

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    if not getattr(response, "text", None):
        raise ValueError("No explanation was returned by Gemini.")

    return response.text.strip()


def generate_dematel_explanation(
    *,
    result,
    engine: str,
    api_key: str,
    model: str | None = None,
) -> str:
    if not engine or engine not in SUPPORTED_ENGINES:
        raise ValueError(f"Unsupported engine: {engine}")

    if not api_key or not api_key.strip():
        raise ValueError(f"API key is required for {engine}.")

    payload = build_result_payload(result)
    prompt = build_prompt(payload)
    selected_model = (model or DEFAULT_MODELS[engine]).strip()

    if engine == "Gemini":
        return _generate_with_gemini(
            api_key=api_key,
            model=selected_model,
            prompt=prompt,
        )

    if engine == "Groq":
        return _generate_with_openai_compatible(
            base_url="https://api.groq.com/openai/v1/chat/completions",
            api_key=api_key,
            model=selected_model,
            prompt=prompt,
        )

    if engine == "OpenRouter":
        return _generate_with_openai_compatible(
            base_url="https://openrouter.ai/api/v1/chat/completions",
            api_key=api_key,
            model=selected_model,
            prompt=prompt,
            referer="http://localhost",
            title="DEMATELab",
        )

    if engine == "OpenAI":
        return _generate_with_openai_compatible(
            base_url="https://api.openai.com/v1/chat/completions",
            api_key=api_key,
            model=selected_model,
            prompt=prompt,
        )

    raise ValueError(f"Unsupported engine: {engine}")
