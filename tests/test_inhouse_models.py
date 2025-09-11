from src.ai.inhouse.base import registry
from src.ai.inhouse.keyword_model import KeywordScorer
from src.ai.inhouse.insight_generator import InsightGenerator

def test_keyword_scorer_basic():
    km: KeywordScorer = registry.get("keyword_scorer")  # type: ignore
    km.add_document("python data pipeline optimization")
    top = km.top_n("Python improved pipeline reliability")
    assert 'python' in top


def test_insight_generator_contract():
    ig: InsightGenerator = registry.get("insight_generator")  # type: ignore
    out = ig.predict({
        'ats_score': {'overall_score':80,'keyword_score':70,'format_score':70,'readability_score':70,'content_score':70,'contact_score':70,'skills_score':70,'experience_score':70,'education_score':70},
        'keyword_analysis': {'match_percentage':65,'missing_keywords':['kubernetes','cloud','api']},
        'skills_analysis': {'skill_count':12},
        'content_analysis': {'readability_score':65},
        'format_analysis': {'section_count':4}
    })
    assert 'top_strengths' in out and 'critical_improvements' in out
