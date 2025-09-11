# ATS Checker Enhancer – In-House AI Architecture (Phase 1–2)

## Overview
The legacy external AI/LLM stack (OpenAI, Anthropic, Transformers, Whisper, Torch, Sentence-Transformers, spaCy, NLTK, TextBlob) has been removed and replaced by deterministic, lightweight, in-house heuristic + classical components designed for extensibility, reliability, and offline operation.

## Goals
- Zero external AI API dependency
- Fast cold start, low memory
- Deterministic testable outputs
- Clear extension points for future custom ML/DL models
- Maintain ATS scoring & insights parity with simplified heuristic logic

## Component Layers
1. In-House Model Core (`src/ai/inhouse`)
   - `base.py`: Registry + `BaseModel` + metadata contracts.
   - `keyword_model.py`: Pure Python TF-IDF style scorer with incremental corpus updates.
   - `sentiment_lexicon.py`: Lexicon-based polarity estimator (expandable).
   - `insight_generator.py`: Heuristic resume insight synthesizer replacing GPT calls.
2. Analyzer (`src/core/ats_analyzer.py`)
   - Now calls `_get_inhouse_insights_wrapper` instead of external LLMs.
   - Legacy OpenAI/Anthropic methods deleted.
3. Document Processor (`src/ai/processors/enhanced_document_processor.py`)
   - Removed OpenAIClient, Whisper, Transformers pipeline, MoviePy audio usage.
   - Video processing switched to OpenCV frame sampling + OCR only.
   - Audio transcription: currently simple speech_recognition + stub mode (replaceable).
4. Dashboard (`src/dashboard/app.py`)
   - Displays "In-House Insights" JSON; Anthropic branch removed.

## Extensibility Strategy
- Add new model: implement subclass of `BaseModel`, register via `registry.register(key, ctor)`.
- Swap heuristic insight engine with a learned model by returning identical JSON contract.
- Future embeddings: add `embedding_model.py` with caching; feed into keyword/semantic scoring.

## Reliability & Determinism
- Randomness in `InsightGenerator` seeded to 0 for stable outputs.
- No network-required model downloads.
- Fallback configuration avoids hard pydantic dependency for minimal mode.

## Testing
- `tests/test_inhouse_analyzer.py`: end-to-end analyzer smoke test.
- `tests/test_inhouse_models.py`: model contract tests (keyword scorer + insight generator).

## Migration Notes
- Heavy deps commented in `requirements.txt`; `slim_requirements.txt` added for lean deploy.
- Remove commented lines permanently once operational stability confirmed across environments.
- If reintroducing advanced NLP: wrap behind feature flags and maintain offline default.

## Next Phases (Planned)
- Phase 3: Futuristic dashboard UI redesign (glassmorphism + dark neon theme).
- Phase 4: Pluggable training CLI for custom keyword / section classifier models.
- Phase 5: Lightweight embedding generator (character n-gram + hashing) for semantic similarity.

## SLA & Ops Considerations
- All model loads are O(1) initialization—no large downloads.
- Health endpoint (future) can enumerate `registry.list()` for live model status.
- Deterministic outputs -> easier regression baselines and audit logs.

## Security
- Removed external API keys usage for analysis path (minimizes leakage surface).
- Future model artifact signing recommended before introducing learned weights.

## Performance
- Keyword scoring: linear in token count; no matrix builds.
- Insight generation: constant-time heuristic evaluation.

---
For questions or extension proposals, add design docs under `docs/` and update this file upon architectural changes.
