"""Heuristic Insight Generator replacing external LLM calls.
Produces structured recommendations from analysis components.
"""
from __future__ import annotations
from .base import BaseModel, ModelMetadata, registry
from typing import Dict, Any, List
import random

class InsightGenerator(BaseModel):
    def __init__(self):
        super().__init__(ModelMetadata(name="insight_generator", description="Deterministic heuristic resume insight engine"))

    def _pick(self, items: List[str], k: int) -> List[str]:
        uniq = []
        for i in items:
            if i not in uniq:
                uniq.append(i)
        random.seed(0)  # stable across runs
        random.shuffle(uniq)
        return uniq[:k]

    def _predict(self, input_data: Dict[str, Any]):
        # input_data expects dict with keys: ats_score, keyword_analysis, skills_analysis, content_analysis, format_analysis
        ats = input_data.get('ats_score', {})
        kw = input_data.get('keyword_analysis', {})
        skills = input_data.get('skills_analysis', {})
        content = input_data.get('content_analysis', {})
        fmt = input_data.get('format_analysis', {})
        strengths: List[str] = []
        improvements: List[str] = []
        kw_pct = kw.get('match_percentage',0)
        if kw_pct>60: strengths.append(f"Keyword alignment strong ({kw_pct:.1f}%).")
        else: improvements.append("Increase alignment with role-specific keywords.")
        if ats.get('format_score',0) > 70: strengths.append("Good structural formatting.")
        else: improvements.append("Refine section headers & bullet consistency.")
        if content.get('readability_score',0) > 60: strengths.append("Readable professional tone.")
        else: improvements.append("Simplify long sentences & clarify impact metrics.")
        if skills.get('skill_count',0) >= 10: strengths.append("Comprehensive skill set showcased.")
        else: improvements.append("Add more targeted tech & soft skills.")
        suggestions = [
            "Quantify achievements with metrics (%, $, time saved).",
            "Front-load impact verbs (led, built, optimized).",
            "Group related tools to save space.",
            "Ensure consistent tense in experience section.",
            "Balance technical depth with business outcomes."
        ]
        return {
            "top_strengths": self._pick(strengths, min(3,len(strengths))) or ["Foundational content present."],
            "critical_improvements": self._pick(improvements, min(3,len(improvements))) or ["Refine clarity and keyword focus."],
            "keyword_suggestions": kw.get('missing_keywords', [])[:5],
            "ats_optimization_tips": suggestions[:3],
            "overall_impression": "Resume analyzed offline using heuristic engine; focus on measurable impact and tighter keyword targeting for higher ATS scores."}

registry.register("insight_generator", lambda: InsightGenerator())
