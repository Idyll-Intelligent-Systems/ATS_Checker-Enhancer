import importlib
import sys
from types import ModuleType

from src.core import ats_analyzer as original_ats_analyzer


def test_spacy_unavailable_warning(monkeypatch):
    # Force spacy unavailable branch
    monkeypatch.setattr(original_ats_analyzer, "spacy", None)
    analyzer = original_ats_analyzer.ATSAnalyzer()
    assert analyzer.nlp is None
    assert analyzer.nlp_mode == "unavailable"


def test_spacy_blank_fallback(monkeypatch):
    # Craft minimal dummy spacy module to trigger blank fallback
    dummy = ModuleType("spacy")

    def load(name):
        raise RuntimeError("model not installed")

    class DummyBlank:
        def __call__(self, text):
            return text  # Not used when nlp_mode == blank_en

    def blank(lang):
        return DummyBlank()

    dummy.load = load  # type: ignore
    dummy.blank = blank  # type: ignore

    # Inject dummy spacy into sys.modules and reload
    monkeypatch.setitem(sys.modules, "spacy", dummy)
    reloaded = importlib.reload(sys.modules[original_ats_analyzer.__name__])
    analyzer = reloaded.ATSAnalyzer()
    # Fallback should select blank_en mode
    assert analyzer.nlp is not None
    assert analyzer.nlp_mode == "blank_en"


def test_low_score_recommendations():
    # Extremely minimal resume vs rich JD to drive low overall score & keyword mismatch
    analyzer = original_ats_analyzer.ATSAnalyzer()
    resume = "Hi"  # no sections, no keywords, almost empty
    job_description = "Python AWS Docker Kubernetes SQL Leadership Communication Optimization Scaling"

    result = importlib.reload(sys.modules[original_ats_analyzer.__name__]).ATSAnalyzer()
    # Run analysis (async) using a helper
    import asyncio
    analysis = asyncio.run(result.analyze_resume(resume, job_description=job_description))
    assert any("Low ATS compatibility" in w for w in analysis.weaknesses)
    assert analysis.ats_score.overall_score < 60
    # Ensure standard missing sections suggestion appears
    assert any("Add standard sections" in s for s in analysis.suggestions)


def test_format_score_empty_input_branch():
    analyzer = original_ats_analyzer.ATSAnalyzer()
    # Directly call internal method to cover empty non_empty_lines branch
    score = analyzer._calculate_format_score("")  # noqa: SLF001
    # Should return minimal baseline (>= 0.1 due to neutral contribution path)
    assert score >= 0.1


def test_readability_score_branches(monkeypatch):
    analyzer = original_ats_analyzer.ATSAnalyzer()
    # Patch flesch_reading_ease in module for controlled branching
    target_values = [70, 50, 85, 30, 10]  # maps to 1.0, 0.8, 0.8, 0.6, 0.4
    expected = {70:1.0, 50:0.8, 85:0.8, 30:0.6, 10:0.4}
    for val in target_values:
        monkeypatch.setattr(original_ats_analyzer, "flesch_reading_ease", lambda _t, v=val: v)
        r = analyzer._calculate_readability_score("Dummy text.")  # noqa: SLF001
        assert r == expected[val]
