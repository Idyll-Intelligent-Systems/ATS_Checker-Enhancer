import asyncio
from src.core.ats_analyzer import ATSAnalyzer


def test_empty_resume_analysis():
    analyzer = ATSAnalyzer()
    result = asyncio.run(analyzer.analyze_resume(""))
    assert result.ats_score.overall_score >= 0
    assert isinstance(result.strengths, list)
    assert isinstance(result.weaknesses, list)
    assert isinstance(result.suggestions, list)


def test_minimal_keyword_job_description():
    analyzer = ATSAnalyzer()
    resume = "Python developer with API experience"
    jd = "Python API SQL"
    result = asyncio.run(analyzer.analyze_resume(resume, jd))
    ka = result.keyword_analysis
    assert ka['match_percentage'] >= 0
    assert 'matched_keywords' in ka


def test_low_content_scores_trigger_suggestions():
    analyzer = ATSAnalyzer()
    resume = "Intern"
    result = asyncio.run(analyzer.analyze_resume(resume))
    assert len(result.suggestions) >= 3

