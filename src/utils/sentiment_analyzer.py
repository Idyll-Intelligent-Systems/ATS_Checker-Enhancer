"""
ZeX-ATS-AI Sentiment Analysis Utilities
Advanced sentiment and tone analysis for resume content.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import spacy


@dataclass
class SentimentResult:
    """Sentiment analysis result."""
    overall_sentiment: str  # positive, negative, neutral
    confidence_score: float  # 0.0 to 1.0
    positive_score: float
    negative_score: float
    neutral_score: float
    compound_score: float  # -1.0 to 1.0
    subjectivity: float  # 0.0 to 1.0
    
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
    """Advanced sentiment analysis for resume content."""
    
    def __init__(self):
        """Initialize sentiment analyzer with multiple models."""
        # Download VADER lexicon if not available
        try:
            self.vader = SentimentIntensityAnalyzer()
        except LookupError:
            nltk.download('vader_lexicon', quiet=True)
            self.vader = SentimentIntensityAnalyzer()
        
        # Load spaCy model if available
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = None
        
        # Professional tone keywords
        self.positive_professional_words = {
            'achieved', 'accomplished', 'improved', 'increased', 'enhanced',
            'optimized', 'streamlined', 'developed', 'implemented', 'delivered',
            'successful', 'effective', 'efficient', 'innovative', 'strategic',
            'collaborative', 'proactive', 'results-driven', 'experienced',
            'skilled', 'proficient', 'expert', 'advanced', 'comprehensive'
        }
        
        self.negative_professional_words = {
            'failed', 'struggled', 'difficult', 'challenging', 'problems',
            'issues', 'unable', 'inexperienced', 'unfamiliar', 'limited',
            'basic', 'minimal', 'weak', 'poor', 'inadequate', 'insufficient'
        }
        
        # Power words that indicate strong performance
        self.power_words = {
            'accelerated', 'achieved', 'advanced', 'boosted', 'built',
            'created', 'delivered', 'developed', 'directed', 'drove',
            'enhanced', 'exceeded', 'executed', 'expanded', 'generated',
            'implemented', 'improved', 'increased', 'influenced', 'initiated',
            'launched', 'led', 'managed', 'maximized', 'optimized',
            'organized', 'produced', 'reduced', 'resolved', 'spearheaded',
            'strengthened', 'streamlined', 'succeeded', 'supervised', 'transformed'
        }
    
    def analyze_sentiment(self, text: str) -> SentimentResult:
        """
        Comprehensive sentiment analysis of resume text.
        
        Args:
            text: Resume text to analyze
            
        Returns:
            SentimentResult with detailed sentiment scores
        """
        # VADER sentiment analysis
        vader_scores = self.vader.polarity_scores(text)
        
        # TextBlob sentiment analysis
        blob = TextBlob(text)
        blob_sentiment = blob.sentiment
        
        # Professional tone analysis
        professional_scores = self._analyze_professional_tone(text)
        
        # Combine scores with weights
        # VADER compound score: 40%
        # TextBlob polarity: 30%
        # Professional tone: 30%
        compound_score = (
            vader_scores['compound'] * 0.4 +
            blob_sentiment.polarity * 0.3 +
            professional_scores['professional_tone'] * 0.3
        )
        
        # Determine overall sentiment
        if compound_score >= 0.1:
            overall_sentiment = 'positive'
            confidence_score = min(abs(compound_score) * 2, 1.0)
        elif compound_score <= -0.1:
            overall_sentiment = 'negative'
            confidence_score = min(abs(compound_score) * 2, 1.0)
        else:
            overall_sentiment = 'neutral'
            confidence_score = 1.0 - abs(compound_score) * 2
        
        return SentimentResult(
            overall_sentiment=overall_sentiment,
            confidence_score=confidence_score,
            positive_score=vader_scores['pos'],
            negative_score=vader_scores['neg'],
            neutral_score=vader_scores['neu'],
            compound_score=compound_score,
            subjectivity=blob_sentiment.subjectivity
        )
    
    def _analyze_professional_tone(self, text: str) -> Dict[str, float]:
        """Analyze professional tone specific to resumes."""
        text_lower = text.lower()
        words = text_lower.split()
        
        # Count professional words
        positive_count = sum(1 for word in words if word in self.positive_professional_words)
        negative_count = sum(1 for word in words if word in self.negative_professional_words)
        power_word_count = sum(1 for word in words if word in self.power_words)
        
        total_words = len(words)
        
        if total_words == 0:
            return {'professional_tone': 0.0, 'power_words_ratio': 0.0}
        
        # Calculate professional tone score
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        power_words_ratio = power_word_count / total_words
        
        # Professional tone score (-1 to 1)
        professional_tone = (positive_ratio - negative_ratio) * 2 + power_words_ratio
        professional_tone = max(-1.0, min(1.0, professional_tone))
        
        return {
            'professional_tone': professional_tone,
            'power_words_ratio': power_words_ratio,
            'positive_ratio': positive_ratio,
            'negative_ratio': negative_ratio
        }
    
    def analyze_section_sentiments(self, sections: Dict[str, str]) -> Dict[str, SentimentResult]:
        """Analyze sentiment for individual resume sections."""
        section_sentiments = {}
        
        for section_name, section_text in sections.items():
            if section_text and len(section_text.strip()) > 10:
                section_sentiments[section_name] = self.analyze_sentiment(section_text)
        
        return section_sentiments
    
    def get_tone_recommendations(self, sentiment_result: SentimentResult, text: str) -> List[str]:
        """Generate recommendations based on sentiment analysis."""
        recommendations = []
        
        # Overall sentiment recommendations
        if sentiment_result.overall_sentiment == 'negative':
            recommendations.append(
                "Consider using more positive and confident language to describe your achievements"
            )
        elif sentiment_result.confidence_score < 0.3:
            recommendations.append(
                "Strengthen your language with more decisive and impactful words"
            )
        
        # Subjectivity recommendations
        if sentiment_result.subjectivity > 0.7:
            recommendations.append(
                "Balance subjective statements with objective facts and measurable achievements"
            )
        elif sentiment_result.subjectivity < 0.3:
            recommendations.append(
                "Add some personality and enthusiasm to make your resume more engaging"
            )
        
        # Power words recommendations
        professional_scores = self._analyze_professional_tone(text)
        if professional_scores['power_words_ratio'] < 0.02:  # Less than 2% power words
            recommendations.append(
                "Include more action verbs and power words to demonstrate impact and leadership"
            )
        
        # Positive/negative balance
        if sentiment_result.negative_score > 0.15:
            recommendations.append(
                "Minimize negative language and focus on achievements and solutions"
            )
        
        if sentiment_result.positive_score < 0.3:
            recommendations.append(
                "Incorporate more positive language to highlight your accomplishments"
            )
        
        return recommendations
    
    def calculate_confidence_indicators(self, text: str) -> Dict[str, float]:
        """Calculate indicators of confidence and assertiveness in resume text."""
        text_lower = text.lower()
        words = text_lower.split()
        total_words = len(words)
        
        if total_words == 0:
            return {}
        
        # Confidence indicators
        confident_phrases = {
            'successfully', 'achieved', 'accomplished', 'exceeded', 'led',
            'managed', 'directed', 'implemented', 'developed', 'created',
            'expertise', 'expert', 'proficient', 'skilled', 'experienced'
        }
        
        # Weak language indicators
        weak_phrases = {
            'helped', 'assisted', 'participated', 'involved', 'tried',
            'attempted', 'hoped', 'wished', 'maybe', 'possibly',
            'somewhat', 'fairly', 'quite', 'pretty', 'rather'
        }
        
        # Uncertainty indicators
        uncertainty_phrases = {
            'might', 'could', 'would', 'should', 'perhaps', 'probably',
            'possibly', 'maybe', 'seems', 'appears', 'tends'
        }
        
        confident_count = sum(1 for word in words if word in confident_phrases)
        weak_count = sum(1 for word in words if word in weak_phrases)
        uncertainty_count = sum(1 for word in words if word in uncertainty_phrases)
        
        return {
            'confidence_ratio': confident_count / total_words,
            'weak_language_ratio': weak_count / total_words,
            'uncertainty_ratio': uncertainty_count / total_words,
            'confidence_score': max(0, confident_count - weak_count - uncertainty_count) / total_words
        }
    
    def analyze_readability_tone(self, text: str) -> Dict[str, float]:
        """Analyze tone factors that affect readability."""
        sentences = text.split('.')
        words = text.split()
        
        if not sentences or not words:
            return {}
        
        # Calculate average sentence length
        avg_sentence_length = len(words) / len(sentences)
        
        # Calculate complexity indicators
        complex_words = [word for word in words if len(word) > 7]
        complexity_ratio = len(complex_words) / len(words)
        
        # Check for jargon and technical terms
        technical_patterns = [
            r'\b[A-Z]{2,}\b',  # Acronyms
            r'\b\w+[-]\w+\b',  # Hyphenated terms
            r'\b\w+[/]\w+\b'   # Slash terms
        ]
        
        import re
        jargon_count = 0
        for pattern in technical_patterns:
            jargon_count += len(re.findall(pattern, text))
        
        jargon_ratio = jargon_count / len(words) if words else 0
        
        return {
            'avg_sentence_length': avg_sentence_length,
            'complexity_ratio': complexity_ratio,
            'jargon_ratio': jargon_ratio,
            'readability_score': 1.0 - min(1.0, (avg_sentence_length/20 + complexity_ratio + jargon_ratio)/3)
        }
    
    def get_emotional_keywords(self, text: str) -> Dict[str, List[str]]:
        """Extract emotional and tonal keywords from text."""
        text_lower = text.lower()
        words = set(text_lower.split())
        
        emotional_categories = {
            'enthusiasm': ['excited', 'passionate', 'motivated', 'eager', 'enthusiastic', 'driven'],
            'confidence': ['confident', 'assured', 'certain', 'convinced', 'determined'],
            'achievement': ['achieved', 'accomplished', 'succeeded', 'exceeded', 'surpassed'],
            'leadership': ['led', 'directed', 'managed', 'guided', 'supervised', 'coordinated'],
            'innovation': ['innovative', 'creative', 'pioneered', 'developed', 'designed'],
            'collaboration': ['collaborated', 'teamwork', 'partnered', 'cooperated', 'coordinated']
        }
        
        found_keywords = {}
        for category, keywords in emotional_categories.items():
            found = [word for word in keywords if word in words]
            if found:
                found_keywords[category] = found
        
        return found_keywords
