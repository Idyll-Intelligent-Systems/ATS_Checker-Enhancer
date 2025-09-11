import importlib, sys, asyncio, types
from src.ai.inhouse import sentiment_lexicon
from src.core import ats_analyzer as analyzer_mod


def test_lexicon_sentiment_positive_negative_neutral():
    model = sentiment_lexicon.registry.get("lexicon_sentiment")
    pos = model.predict("Achieved excellent optimized scalable solution")
    neg = model.predict("Problem error bug failure bottleneck issue")
    neu = model.predict("This sentence has none of those words present")
    assert pos["label"] == "positive" and pos["score"] > 0
    assert neg["label"] == "negative" and neg["score"] < 0
    assert neu["label"] == "neutral"


def test_lexicon_sentiment_type_error():
    model = sentiment_lexicon.registry.get("lexicon_sentiment")
    try:
        model.predict(123)  # type: ignore[arg-type]
    except TypeError as e:
        assert "expects string" in str(e)
    else:
        raise AssertionError("TypeError not raised for non-string input")


def test_nlp_exception_branch(monkeypatch):
    # Force spacy present but load always raising, blank also raising to hit error log branch
    dummy_spacy = types.SimpleNamespace()

    def load(_name):
        raise RuntimeError("load failure")

    def blank(_lang):
        raise RuntimeError("blank failure")

    dummy_spacy.load = load  # type: ignore
    dummy_spacy.blank = blank  # type: ignore
    monkeypatch.setitem(sys.modules, "spacy", dummy_spacy)
    reloaded = importlib.reload(sys.modules[analyzer_mod.__name__])
    inst = reloaded.ATSAnalyzer()
    # Expect nlp remains None and mode 'unavailable'
    assert inst.nlp is None
    assert inst.nlp_mode in ("unavailable", "blank_en")


def test_nlp_happy_blank_branch(monkeypatch):
    # Force spacy load fail but blank succeeds
    dummy_spacy = types.SimpleNamespace()

    def load(_name):
        raise RuntimeError("load missing")

    class Blank:
        def __call__(self, text):
            return text

    def blank(_lang):
        return Blank()

    dummy_spacy.load = load  # type: ignore
    dummy_spacy.blank = blank  # type: ignore
    monkeypatch.setitem(sys.modules, "spacy", dummy_spacy)
    reloaded = importlib.reload(sys.modules[analyzer_mod.__name__])
    inst = reloaded.ATSAnalyzer()
    assert inst.nlp is not None
    assert inst.nlp_mode == "blank_en"
