"""
ZeX-ATS-AI Sentiment Analysis Utilities
Lightweight fallback version with optional dependencies.
If nltk / textblob / spacy not installed, uses simple heuristic.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from src.utils.system_logger import log_function

# Optional heavy deps --------------------------------------------------------
try:
    import nltk  # type: ignore
    from nltk.sentiment import SentimentIntensityAnalyzer  # type: ignore
except Exception:  # pragma: no cover
    nltk = None  # type: ignore
    SentimentIntensityAnalyzer = None  # type: ignore

try:
    from textblob import TextBlob  # type: ignore
except Exception:  # pragma: no cover
    TextBlob = None  # type: ignore

try:
    import spacy  # type: ignore
except Exception:  # pragma: no cover
    spacy = None  # type: ignore


@dataclass
class SentimentResult:
    overall_sentiment: str
    confidence_score: float
    positive_score: float
    negative_score: float
    neutral_score: float
    compound_score: float
    subjectivity: float
    def to_dict(self) -> Dict[str, float]:
        return {
            'overall_sentiment': self.overall_sentiment,
            'confidence_score': self.confidence_score,
            'positive_score': self.positive_score,
            'negative_score': self.negative_score,
            'neutral_score': self.neutral_score,
            'compound_score': self.compound_score,
            'subjectivity': self.subjectivity
        }


class SentimentAnalyzer:
    def __init__(self):
        self.vader = None
        if SentimentIntensityAnalyzer:
            try:
                self.vader = SentimentIntensityAnalyzer()
            except Exception:
                try:
                    if nltk:
                        nltk.download('vader_lexicon', quiet=True)  # type: ignore
                        self.vader = SentimentIntensityAnalyzer()
                except Exception:
                    self.vader = None
        # spaCy optional
        if spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")  # type: ignore
            except Exception:
                try:
                    self.nlp = spacy.blank("en")  # type: ignore
                except Exception:
                    self.nlp = None
        else:
            self.nlp = None
        self.positive_professional_words = {
            'achieved','accomplished','improved','increased','enhanced','optimized','streamlined','developed','implemented','delivered','successful','effective','innovative','strategic','collaborative','proactive','results-driven','experienced','skilled','proficient','expert','advanced'
        }
        self.negative_professional_words = {
            'failed','struggled','difficult','issues','unable','inexperienced','limited','basic','minimal','weak','poor'
        }
        self.power_words = {
            'accelerated','achieved','advanced','boosted','built','created','delivered','developed','directed','drove','enhanced','exceeded','executed','expanded','generated','implemented','improved','increased','influenced','initiated','launched','led','managed','maximized','optimized','organized','produced','reduced','resolved','spearheaded','strengthened','streamlined','transformed'
        }

    @log_function("INFO", "SENTIMENT_OK")
    def analyze_sentiment(self, text: str) -> SentimentResult:
        if not text.strip():
            return SentimentResult('neutral', 1.0,0,0,1,0,0)
        positive_score = negative_score = neutral_score = 0.0
        compound = 0.0
        subjectivity = 0.0
        if self.vader:
            try:
                vs = self.vader.polarity_scores(text)
                positive_score = vs.get('pos',0.0)
                negative_score = vs.get('neg',0.0)
                neutral_score = vs.get('neu',0.0)
                compound = vs.get('compound',0.0)
            except Exception:
                pass
        if TextBlob:
            try:
                blob = TextBlob(text)
                subjectivity = float(getattr(blob.sentiment,'subjectivity',0.0))
                if compound == 0.0:
                    compound = float(getattr(blob.sentiment,'polarity',0.0))
            except Exception:
                pass
        if compound >= 0.1:
            sentiment = 'positive'
            confidence = min(abs(compound)*1.5,1.0)
        elif compound <= -0.1:
            sentiment = 'negative'
            confidence = min(abs(compound)*1.5,1.0)
        else:
            sentiment = 'neutral'
            confidence = 1.0 - abs(compound)
        return SentimentResult(sentiment, confidence, positive_score, negative_score, neutral_score, compound, subjectivity)

    @log_function("DEBUG", "PRO_TONE_OK")
    def _analyze_professional_tone(self, text: str) -> Dict[str, float]:
        tl = text.lower(); words = tl.split(); total = len(words) or 1
        pos = sum(1 for w in words if w in self.positive_professional_words)
        neg = sum(1 for w in words if w in self.negative_professional_words)
        power = sum(1 for w in words if w in self.power_words)
        return {
            'professional_tone': (pos - neg)/total + power/total,
            'power_words_ratio': power/total,
            'positive_ratio': pos/total,
            'negative_ratio': neg/total
        }

    @log_function("DEBUG", "SECTION_SENTIMENTS_OK")
    def analyze_section_sentiments(self, sections: Dict[str, str]) -> Dict[str, SentimentResult]:
        out = {}
        for name, content in sections.items():
            if content and len(content.strip()) > 10:
                out[name] = self.analyze_sentiment(content)
        return out

    @log_function("REMARK", "TONE_RECS_OK")
    def get_tone_recommendations(self, sentiment_result: SentimentResult, text: str) -> List[str]:
        rec = []
        if sentiment_result.overall_sentiment == 'negative':
            rec.append('Use more positive, achievement-focused language.')
        if sentiment_result.subjectivity > 0.7:
            rec.append('Balance subjective statements with objective metrics.')
        if sentiment_result.subjectivity < 0.2:
            rec.append('Add more energetic language to avoid sounding too dry.')
        return rec

    @log_function("METRIC", "CONFIDENCE_METRICS_OK")
    def calculate_confidence_indicators(self, text: str) -> Dict[str, float]:
        tl = text.lower(); words = tl.split(); total = len(words) or 1
        confident = {'successfully','achieved','accomplished','exceeded','led','managed','implemented','developed','expert','proficient'}
        weak = {'helped','assisted','participated','involved','tried','attempted','maybe','possibly','somewhat'}
        return {
            'confidence_ratio': sum(1 for w in words if w in confident)/total,
            'weak_language_ratio': sum(1 for w in words if w in weak)/total
        }
