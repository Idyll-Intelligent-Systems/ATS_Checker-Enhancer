"""
ZeX-ATS-AI: Enterprise-Grade ATS Checker & Enhancer
Version: 1.0.0

This package provides advanced AI-powered resume analysis and optimization tools
for enterprise-level Applicant Tracking Systems.

Features:
- AI-powered resume analysis
- ATS compatibility scoring
- Skills gap analysis
- Job matching algorithms
- Real-time dashboard
- Enterprise security
- Multi-tenant support
"""

__version__ = "1.0.0"
__author__ = "Idyll Intelligent Systems"
__email__ = "support@zex-ats-ai.com"

from src.core.config import settings
from src.core.ats_analyzer import ATSAnalyzer
try:  # Optional during minimal in-house tests
    from src.core.resume_processor import ResumeProcessor  # type: ignore
except Exception:  # pragma: no cover
    class ResumeProcessor:  # minimal stub
        def __init__(self, *_, **__):
            raise RuntimeError("ResumeProcessor dependencies not installed in minimal mode")

__all__ = [
    "settings",
    "ATSAnalyzer", 
    "ResumeProcessor"
]
