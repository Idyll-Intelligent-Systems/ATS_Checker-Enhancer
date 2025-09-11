from src.dashboard.pdf_export import build_pdf_html

class MinimalScore:
    def __init__(self):
        self.overall_score = 0.0
        self.keyword_score = 0.0
        self.format_score = 0.0
        self.readability_score = 0.0
        self.content_score = 0.0
        self.contact_score = 0.0
        self.skills_score = 0.0
        self.experience_score = 0.0
        self.education_score = 0.0

class MinimalResult:
    def __init__(self):
        self.ats_score = MinimalScore()
        self.strengths = []
        self.weaknesses = []
        self.suggestions = []
        self.keyword_analysis = {'matched_keywords': [], 'missing_keywords': []}
        self.ai_insights = {'insights': {}}


def test_build_pdf_html_missing_sections():
    res = MinimalResult()
    html = build_pdf_html(res, ['scores','insights'])
    # Ensure absent strengths section not rendered (no anchor)
    assert 'id="strengths"' not in html
    assert 'ATS Analysis Report' in html
