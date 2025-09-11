import asyncio
import types
import pytest

from src.core.ats_analyzer import ATSAnalyzer, ATSScore
from src.ai.inhouse.base import registry as inhouse_registry


def make_score(overall, keyword=0.5, format_=0.5, readability=0.5, content=0.5, contact=0.5, skills=0.5, exp=0.5, edu=0.5):
    return ATSScore(
        overall_score=overall,
        keyword_score=keyword*100,
        format_score=format_*100,
        readability_score=readability*100,
        content_score=content*100,
        contact_score=contact*100,
        skills_score=skills*100,
        experience_score=exp*100,
        education_score=edu*100,
    )


def test_generate_recommendations_high_score():
    analyzer = ATSAnalyzer()
    ats = make_score(85, keyword=0.8, format_=0.8, contact=0.8)
    keyword_analysis = {'match_percentage': 70, 'missing_keywords': []}
    skills_analysis = {'skill_count': 12}
    content_analysis = {'readability_score': 65}
    format_analysis = {'section_count': 5}
    strengths, weaknesses, suggestions = analyzer._generate_recommendations(
        ats, keyword_analysis, skills_analysis, content_analysis, format_analysis, {}
    )
    assert any('Excellent ATS compatibility' in s for s in strengths)
    assert not any('Low ATS compatibility' in w for w in weaknesses)
    assert len(strengths) > 1


def test_generate_recommendations_low_score():
    analyzer = ATSAnalyzer()
    ats = make_score(40, keyword=0.3, format_=0.3, contact=0.2, skills=0.1)
    keyword_analysis = {'match_percentage': 10, 'missing_keywords': ['python','api','sql','docker']}
    skills_analysis = {'skill_count': 2}
    content_analysis = {'readability_score': 30}
    format_analysis = {'section_count': 1}
    strengths, weaknesses, suggestions = analyzer._generate_recommendations(
        ats, keyword_analysis, skills_analysis, content_analysis, format_analysis, {}
    )
    assert any('Low ATS compatibility' in w for w in weaknesses)
    assert any('Include missing keywords' in s for s in suggestions)
    assert any('Limited skills representation' in w for w in weaknesses)


def test_inhouse_insights_error_path(monkeypatch):
    analyzer = ATSAnalyzer()
    def boom(name):
        raise RuntimeError('forced-error')
    monkeypatch.setattr(inhouse_registry, 'get', boom)
    res = asyncio.run(analyzer._get_inhouse_insights_wrapper('sample text'))
    assert 'insights' in res and 'error' in res['insights']


def test_content_and_skills_with_and_without_nlp():
    analyzer = ATSAnalyzer()
    text = "Python Java AWS leadership communication achieved improved increased reduced implemented data science"
    # Force NLP unavailable branch
    analyzer.nlp = None
    analyzer.nlp_mode = 'unavailable'
    skills_no_nlp = asyncio.run(analyzer._analyze_skills(text))
    content_no_nlp = asyncio.run(analyzer._analyze_content_quality(text))
    # Create fake NLP pipeline
    class FakeToken:
        def __init__(self, text, pos='VERB'):
            self.text = text
            self.lemma_ = text.lower()
            self.pos_ = pos
            self.is_alpha = text.isalpha()
    class FakeDoc(list):
        @property
        def sents(self):
            return [types.SimpleNamespace(text=text)]
    class FakeNLP:
        def __call__(self, _t):
            return FakeDoc([FakeToken('Achieved'), FakeToken('Improved'), FakeToken('Python','NOUN')])
    analyzer.nlp = FakeNLP()
    analyzer.nlp_mode = 'fake'
    skills_with_nlp = asyncio.run(analyzer._analyze_skills(text))
    content_with_nlp = asyncio.run(analyzer._analyze_content_quality(text))
    assert skills_no_nlp['skill_count'] == skills_with_nlp['skill_count']  # extraction stable
    assert content_with_nlp['nlp_mode'] == 'fake'
