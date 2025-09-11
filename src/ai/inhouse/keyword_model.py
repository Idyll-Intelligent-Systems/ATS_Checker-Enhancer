"""Lightweight TF-IDF style keyword scorer (pure Python / no sklearn).
Provides simple term scoring for similarity & extraction.
"""
from __future__ import annotations
from .base import BaseModel, ModelMetadata, registry
from typing import List, Dict
import math
import re

class KeywordScorer(BaseModel):
    def __init__(self):
        super().__init__(ModelMetadata(name="keyword_scorer", description="Pure Python TF-IDF like scorer"))
        self.doc_freq: Dict[str,int] = {}
        self.num_docs = 0

    def _tokenize(self, text: str) -> List[str]:
        return [t.lower() for t in re.findall(r"[A-Za-z][A-Za-z0-9_+#.-]{1,30}", text)]

    def add_document(self, text: str):
        tokens = set(self._tokenize(text))
        for tok in tokens:
            self.doc_freq[tok] = self.doc_freq.get(tok,0)+1
        self.num_docs += 1

    def score(self, text: str) -> Dict[str,float]:
        tokens = self._tokenize(text)
        tf: Dict[str,int] = {}
        for t in tokens:
            tf[t] = tf.get(t,0)+1
        scores: Dict[str,float] = {}
        for t,c in tf.items():
            df = self.doc_freq.get(t,1)
            idf = math.log((1 + self.num_docs)/(1+df)) + 1
            scores[t] = (c/len(tokens))*idf
        return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

    def top_n(self, text: str, n: int = 20) -> List[str]:
        return list(self.score(text).keys())[:n]

    def _predict(self, input_data):
        if isinstance(input_data, str):
            return self.top_n(input_data)
        raise TypeError("KeywordScorer expects string input")

# Register
registry.register("keyword_scorer", lambda: KeywordScorer())
