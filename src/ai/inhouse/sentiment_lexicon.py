"""Lexicon-based sentiment model (offline).
Combines simple positive/negative word lists with heuristic scoring.
"""
from __future__ import annotations
from .base import BaseModel, ModelMetadata, registry
from typing import Dict
import re

POS = {"great","excellent","improved","increased","optimized","successful","achieved","delivered","enhanced","positive","robust","scalable","reliable"}
NEG = {"issue","problem","failed","delay","error","bug","negative","poor","bottleneck"}

class LexiconSentiment(BaseModel):
    def __init__(self):
        super().__init__(ModelMetadata(name="lexicon_sentiment", description="Offline lexicon sentiment"))

    def _predict(self, input_data):
        if not isinstance(input_data,str):
            raise TypeError("LexiconSentiment expects string input")
        words = [w.lower() for w in re.findall(r"[A-Za-z']+", input_data)]
        total = len(words) or 1
        pos = sum(1 for w in words if w in POS)
        neg = sum(1 for w in words if w in NEG)
        score = (pos - neg)/total
        label = "positive" if score>0.01 else "negative" if score<-0.01 else "neutral"
        return {"label": label, "score": round(score,4), "pos_ratio": pos/total, "neg_ratio": neg/total}

registry.register("lexicon_sentiment", lambda: LexiconSentiment())
