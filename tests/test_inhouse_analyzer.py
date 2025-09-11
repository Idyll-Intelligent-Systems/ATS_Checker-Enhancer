import asyncio
from src.core.ats_analyzer import ATSAnalyzer

TEST_RESUME = """John Doe\nEmail: john@example.com\nExperience\nLed optimization of data pipeline improving performance by 40%.\nImplemented Python microservices and Docker/Kubernetes deployment.\nEducation\nBachelor of Science in Computer Science\nSkills\nPython Java SQL AWS Docker Leadership Communication"""

async def run_analysis():
    analyzer = ATSAnalyzer()
    result = await analyzer.analyze_resume(TEST_RESUME, job_description="Looking for Python developer with AWS and Docker skills")
    assert result.ats_score.overall_score > 0
    assert 'insights' in result.ai_insights

def test_inhouse():
    asyncio.run(run_analysis())
