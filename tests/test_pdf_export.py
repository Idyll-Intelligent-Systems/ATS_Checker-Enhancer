import types
from src.dashboard.pdf_export import build_pdf_html, SECTION_DEFS

class DummyScore:
    def __init__(self):
        self.overall_score = 85.2
        self.keyword_score = 70.5
        self.format_score = 90.1
        self.readability_score = 78.3
        self.content_score = 80.0
        self.contact_score = 88.0
        self.skills_score = 75.0
        self.experience_score = 82.0
        self.education_score = 77.0

class DummyResult:
    def __init__(self):
        self.ats_score = DummyScore()
        self.strengths = ["Good formatting", "Strong experience section"]
        self.weaknesses = ["Missing certification details"]
        self.suggestions = ["Add more quantified achievements", "Include recent training"]
        self.keyword_analysis = {
            'matched_keywords': ['python','api','cloud'],
            'missing_keywords': ['docker','kubernetes']
        }
        self.ai_insights = {
            'insights': {
                'top_strengths': ['Clear structure','Relevant tech stack'],
                'critical_improvements': ['Add leadership examples'],
                'overall_impression': 'Well-rounded technical profile.'
            }
        }


def test_build_pdf_html_all_sections():
    dr = DummyResult()
    html = build_pdf_html(dr, list(SECTION_DEFS.keys()))
    # Basic presence checks
    assert 'ATS Analysis Report' in html
    for title, anchor in SECTION_DEFS.values():
        assert f"id='{anchor}'" in html or anchor in html
    assert 'ZeX ATS Confidential' in html  # watermark text


def test_build_pdf_html_subset():
    dr = DummyResult()
    subset = ['scores','insights']
    html = build_pdf_html(dr, subset)
    # Only subset anchors appear
    assert 'id="scores"' in html or '#scores' in html
    assert 'id="insights"' in html or '#insights' in html
    # Absent section title shouldn't be present
    assert 'Recommendations' not in html

