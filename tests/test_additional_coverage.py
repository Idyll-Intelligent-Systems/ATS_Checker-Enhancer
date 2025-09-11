import pytest
import importlib
from src.core import ats_analyzer as analyzer_mod
from src.ai.inhouse import keyword_model


def test_readability_fallback_exception(monkeypatch):
    # Force flesch_reading_ease to raise to exercise except path returning 0.7 neutral
    monkeypatch.setattr(analyzer_mod, 'flesch_reading_ease', lambda _t: (_ for _ in ()).throw(RuntimeError('boom')))  # generator trick to raise
    a = analyzer_mod.ATSAnalyzer()
    val = a._calculate_readability_score("Some arbitrary text for readability scoring")  # noqa: SLF001
    assert val == 0.7


def test_keyword_scorer_type_error():
    scorer = keyword_model.registry.get('keyword_scorer')
    with pytest.raises(TypeError):
        scorer.predict(123)  # type: ignore[arg-type]


def test_keyword_scorer_add_and_score():
    scorer = keyword_model.registry.get('keyword_scorer')
    scorer.add_document("Python optimization scaling delivery")
    scorer.add_document("Python reliability robust systems")
    top = scorer.predict("Python robust scalable delivery")
    assert 'python' in top[:5]
