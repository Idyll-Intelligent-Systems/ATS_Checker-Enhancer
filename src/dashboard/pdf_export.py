"""PDF export utilities for ATS Dashboard.

Generates HTML used for WeasyPrint PDF generation. Separated for testability.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Any
from src.utils.system_logger import log_function
import base64
import json

# Simple inline SVG logo (placeholder) -> base64 encode for <img src>
_SVG_LOGO = """<svg width='140' height='40' viewBox='0 0 140 40' xmlns='http://www.w3.org/2000/svg'>\n  <defs>\n    <linearGradient id='g' x1='0%' y1='0%' x2='100%' y2='0%'>\n      <stop stop-color='#6366f1' offset='0%'/>\n      <stop stop-color='#8b5cf6' offset='50%'/>\n      <stop stop-color='#ec4899' offset='100%'/>\n    </linearGradient>\n  </defs>\n  <rect rx='8' ry='8' x='0' y='0' width='140' height='40' fill='url(#g)'/>\n  <text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-family='Inter,Arial,sans-serif' font-size='16' fill='white'>ZeX ATS</text>\n</svg>"""
_LOGO_B64 = base64.b64encode(_SVG_LOGO.encode("utf-8")).decode("utf-8")

# Mapping of section keys to title + anchor id
SECTION_DEFS = {
    "scores": ("Scores", "scores"),
    "strengths": ("Strengths", "strengths"),
    "weaknesses": ("Areas for Improvement", "weaknesses"),
    "recommendations": ("Recommendations", "recommendations"),
    "keywords": ("Keyword Summary", "keywords"),
    "insights": ("In-House Insights", "insights"),
}

@log_function("REMARK", "PDF_HTML_OK")
def build_pdf_html(analysis_result: Any, selected_sections: List[str]) -> str:
    """Build full HTML for PDF generation.

    Args:
        analysis_result: Object returned from ATSAnalyzer (must expose attributes used).
        selected_sections: List of section keys to include (subset of SECTION_DEFS keys).

    Returns:
        Complete HTML string with anchors, logo, watermark, and table of contents.
    """
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html: List[str] = []
    html.append(
        "<html><head><meta charset='utf-8'><style>" \
        "body{font-family:Inter,Arial,sans-serif;margin:28px;color:#1f2341;}" \
        "h1,h2,h3{color:#333;margin:0.6em 0 0.35em;} ul,ol{margin:0.3em 0 0.9em 1.2em;} li{margin:0.25em 0;}" \
        "table{border-collapse:collapse;width:100%;margin:0.6em 0;} th,td{padding:6px 8px;border:1px solid #ddd;font-size:12px;}" \
        ".toc a{text-decoration:none;color:#6366f1;} .badge{display:inline-block;padding:2px 8px;margin:2px 4px 2px 0;border-radius:20px;font-size:11px;background:#eef2ff;color:#4338ca;}" \
        "#watermark{position:fixed;left:0;top:0;width:100%;height:100%;pointer-events:none;z-index:-1;}" \
        "#watermark:after{content:'ZeX ATS Confidential';position:absolute;top:40%;left:50%;transform:translate(-50%,-50%) rotate(-30deg);font-size:60px;color:rgba(99,102,241,0.08);font-weight:700;letter-spacing:4px;white-space:nowrap;}" \
        "footer{position:fixed;bottom:18px;left:0;right:0;text-align:center;font-size:10px;color:#6b7280;}" \
        "hr{border:none;border-top:1px solid #e5e7eb;margin:1.4em 0;}" \
        "</style></head><body><div id='watermark'></div>"
    )

    html.append(
        f"<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;'>"
        f"<div><img alt='logo' style='height:40px' src='data:image/svg+xml;base64,{_LOGO_B64}'/></div>"
        f"<div style='text-align:right;font-size:12px;color:#555'>Generated: {ts}<br/>Version: 1.0.0</div>"
        "</div>"
    )
    html.append("<h1>ATS Analysis Report</h1>")

    # Table of contents
    toc_items = []
    for key in selected_sections:
        if key in SECTION_DEFS:
            title, anchor = SECTION_DEFS[key]
            toc_items.append(f"<li><a href='#{anchor}'>{title}</a></li>")
    html.append("<h2>Table of Contents</h2><ul class='toc'>" + ''.join(toc_items) + "</ul><hr/>")

    # Helper to add section safely
    def add_section(key: str, content_builder):
        if key not in selected_sections:
            return
        title, anchor = SECTION_DEFS[key]
        html.append(f"<h2 id='{anchor}'>{title}</h2>")
        content_builder()
        html.append("<hr/>")

    # Scores
    def _scores():
        scores = {
            'Overall': analysis_result.ats_score.overall_score,
            'Keyword': analysis_result.ats_score.keyword_score,
            'Format': analysis_result.ats_score.format_score,
            'Readability': analysis_result.ats_score.readability_score,
            'Content': analysis_result.ats_score.content_score,
            'Contact': analysis_result.ats_score.contact_score,
            'Skills': analysis_result.ats_score.skills_score,
            'Experience': analysis_result.ats_score.experience_score,
            'Education': analysis_result.ats_score.education_score,
        }
        html.append("<table><thead><tr><th>Category</th><th>Score (%)</th></tr></thead><tbody>")
        for k,v in scores.items():
            html.append(f"<tr><td>{k}</td><td>{v:.1f}</td></tr>")
        html.append("</tbody></table>")

    # Strengths
    def _strengths():
        if getattr(analysis_result, 'strengths', None):
            html.append('<ul>')
            for s in analysis_result.strengths:
                html.append(f"<li>{s}</li>")
            html.append('</ul>')
        else:
            html.append('<p><em>No strengths detected.</em></p>')

    # Weaknesses
    def _weaknesses():
        if getattr(analysis_result, 'weaknesses', None):
            html.append('<ul>')
            for w in analysis_result.weaknesses:
                html.append(f"<li>{w}</li>")
            html.append('</ul>')
        else:
            html.append('<p><em>No critical weaknesses.</em></p>')

    # Recommendations
    def _recommendations():
        if getattr(analysis_result, 'suggestions', None):
            html.append('<ol>')
            for r in analysis_result.suggestions:
                html.append(f"<li>{r}</li>")
            html.append('</ol>')
        else:
            html.append('<p><em>No recommendations available.</em></p>')

    # Keywords
    def _keywords():
        ka = getattr(analysis_result, 'keyword_analysis', {}) or {}
        matched = ka.get('matched_keywords', [])
        missing = ka.get('missing_keywords', [])
        html.append(f"<p><strong>Matched:</strong> {len(matched)} | <strong>Missing:</strong> {len(missing)}</p>")
        if matched:
            html.append('<h3 style="margin-top:0.6em">Top Matched</h3>')
            html.append('<div>')
            for m in matched[:25]:
                html.append(f"<span class='badge'>{m}</span>")
            html.append('</div>')
        if missing:
            html.append('<h3 style="margin-top:0.6em">Top Missing</h3><div>')
            for m in missing[:25]:
                html.append(f"<span class='badge' style='background:#fee2e2;color:#991b1b'>{m}</span>")
            html.append('</div>')

    # Insights
    def _insights():
        ai_insights = getattr(analysis_result, 'ai_insights', None)
        if not isinstance(ai_insights, dict):
            html.append('<p><em>No insights available.</em></p>')
            return
        payload = ai_insights.get('insights')
        if not isinstance(payload, dict):
            html.append('<p><em>No insights available.</em></p>')
            return
        for k,v in payload.items():
            html.append(f"<h3>{k.replace('_',' ').title()}</h3>")
            if isinstance(v, list):
                html.append('<ul>')
                for item in v:
                    html.append(f"<li>{item}</li>")
                html.append('</ul>')
            else:
                html.append(f"<p>{v}</p>")

    add_section('scores', _scores)
    add_section('strengths', _strengths)
    add_section('weaknesses', _weaknesses)
    add_section('recommendations', _recommendations)
    add_section('keywords', _keywords)
    add_section('insights', _insights)

    # Footer
    html.append("<footer>ZeX ATS AI &mdash; Confidential Report &bull; Generated at " + ts + "</footer>")
    html.append("</body></html>")
    return ''.join(html)

__all__ = ["build_pdf_html", "SECTION_DEFS"]
