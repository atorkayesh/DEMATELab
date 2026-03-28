# -*- coding: utf-8 -*-
"""
Created on Tue Mar 17 14:01:05 2026

@author: Ali
"""

# -*- coding: utf-8 -*-

from __future__ import annotations

from PySide6.QtCore import QObject, Signal, Slot

from .llm_explanation_service import generate_dematel_explanation


class ExplanationWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, result, engine: str, api_key: str, model: str | None = None):
        super().__init__()
        self.result = result
        self.engine = engine
        self.api_key = api_key
        self.model = model or self._default_model(engine)

    def _default_model(self, engine: str) -> str:
        defaults = {
            "Gemini": "gemini-1.5-flash",
            "OpenAI": "gpt-4o-mini",
            "OpenRouter": "openai/gpt-4o-mini",
            "Groq": "llama3-8b-8192",
        }
        return defaults.get(engine, "")

    @Slot()
    def run(self) -> None:
        try:
            explanation = generate_dematel_explanation(
                result=self.result,
                engine=self.engine,
                api_key=self.api_key,
                model=self.model,
            )
            self.finished.emit(explanation)
        except Exception as exc:
            self.error.emit(str(exc))