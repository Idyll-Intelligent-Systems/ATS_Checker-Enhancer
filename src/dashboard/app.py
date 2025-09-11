"""
ZeX-ATS-AI Streamlit Dashboard
Interactive dashboard for resume analysis with advanced visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import asyncio
from datetime import datetime, timedelta
import json
import io
from typing import Dict, List, Optional
from src.utils.system_logger import init_system_logger, log_function
from src.core.config import (
    load_user_preferences,
    set_user_preference,
    get_user_preference,
    get_user_scoped_preference,
    set_user_scoped_preference,
    get_user_roles,
)
from io import BytesIO
from src.dashboard.pdf_export import build_pdf_html, SECTION_DEFS
try:
    from weasyprint import HTML  # type: ignore
    _PDF_AVAILABLE = True
except Exception:  # graceful fallback
    _PDF_AVAILABLE = False

# Initialize structured logger for Streamlit runtime (idempotent)
init_system_logger()

# Set page configuration
st.set_page_config(
    page_title="ZeX-ATS-AI Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme / UI Phase 3: dynamic futuristic styling is injected at runtime (see inject_theme)

# Import local modules (these would need to be adjusted based on actual structure)
try:
    from src.core.ats_analyzer import ATSAnalyzer
    from src.core.resume_processor import ResumeProcessor
    from src.database.connection import get_database_session
    from src.database.models import User, Analysis
except ImportError:
    st.error("Unable to import required modules. Please ensure the application is properly installed.")
    st.stop()

class StreamlitDashboard:
    """Streamlit dashboard for ZeX-ATS-AI."""
    
    def __init__(self):
        """Initialize dashboard components."""
        self.ats_analyzer = ATSAnalyzer()
        self.resume_processor = ResumeProcessor()
        # Session defaults
        prefs = load_user_preferences()
        if 'dark_mode' not in st.session_state:
            st.session_state.dark_mode = bool(prefs.get('dark_mode', False))
        if 'primary_color' not in st.session_state:
            st.session_state.primary_color = prefs.get('primary_color', '#6366f1')
        # Simulated user id (placeholder: integrate real auth later)
        if 'current_user_id' not in st.session_state:
            st.session_state.current_user_id = 'demo-user'
        
        # Initialize session state
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
        if 'processed_resume' not in st.session_state:
            st.session_state.processed_resume = None
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []

    # ------------------------------------------------------------------
    # THEME & STYLING
    # ------------------------------------------------------------------
    @log_function("DEBUG", "DASHBOARD_THEME_INJECT_OK")
    def inject_theme(self):
        """Inject dynamic glassmorphism theme based on dark/light mode."""
        dark = st.session_state.dark_mode
        # Light / Dark palettes (CSS variables)
        palette = {
            'bg': '#0f1115' if dark else '#f5f7fb',
            'panel': 'rgba(255,255,255,0.08)' if dark else 'rgba(255,255,255,0.65)',
            'panel_border': 'rgba(255,255,255,0.18)' if dark else 'rgba(0,0,0,0.08)',
            'text': '#f5f7fb' if dark else '#1f2341',
            'subtext': '#c3c9d4' if dark else '#4b5563',
            'accent': st.session_state.primary_color,
            'gradient': 'linear-gradient(135deg,#6366f1 0%,#8b5cf6 50%,#ec4899 100%)',
            'shadow': '0 8px 24px -6px rgba(0,0,0,0.55)' if dark else '0 8px 24px -6px rgba(0,0,0,0.15)',
            'badge_bg': 'rgba(99,102,241,0.15)' if dark else 'rgba(99,102,241,0.08)',
            'scroll_thumb': '#374151' if dark else '#d1d5db'
        }
        st.markdown(f"""
        <style>
            :root {{
                --bg: {palette['bg']};
                --panel: {palette['panel']};
                --panel-border: {palette['panel_border']};
                --text: {palette['text']};
                --subtext: {palette['subtext']};
                --accent: {palette['accent']};
                --shadow-elevation: {palette['shadow']};
                --badge-bg: {palette['badge_bg']};
            }}
            html, body, .stApp {{
                background: var(--bg) !important;
                color: var(--text) !important;
                font-family: 'Inter', system-ui, sans-serif;
                scroll-behavior: smooth;
            }}
            /* Scrollbar */
            ::-webkit-scrollbar {{ width: 10px; }}
            ::-webkit-scrollbar-track {{ background: transparent; }}
            ::-webkit-scrollbar-thumb {{ background: {palette['scroll_thumb']}; border-radius: 20px; }}
            /* Header */
            .main-header {{
                background: {palette['gradient']};
                color: white;
                padding: 1.2rem 1.5rem;
                border-radius: 22px;
                position: relative;
                overflow: hidden;
                box-shadow: var(--shadow-elevation);
            }}
            .main-header:before {{
                content: '';
                position: absolute; inset:0;
                background: radial-gradient(circle at 30% 20%,rgba(255,255,255,0.25),transparent 60%);
                mix-blend-mode: overlay; pointer-events:none;
            }}
            /* Glass panels */
            .glass-panel {{
                background: var(--panel);
                backdrop-filter: blur(18px) saturate(1.6);
                -webkit-backdrop-filter: blur(18px) saturate(1.6);
                border: 1px solid var(--panel-border);
                border-radius: 20px;
                padding: 1.25rem 1.4rem 1.4rem 1.4rem;
                margin-bottom: 1.2rem;
                box-shadow: var(--shadow-elevation);
                position: relative;
                overflow: hidden;
            }}
            .glass-panel h2, .glass-panel h3, .glass-panel h4 {{
                font-weight:600; letter-spacing: .5px; margin-top:0.2rem;
            }}
            /* Metric ring container */
            .metric-grid {{ display:grid; gap:1.2rem; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); margin-bottom:1.5rem; }}
            .metric-card {{
                background: var(--panel);
                border:1px solid var(--panel-border);
                border-radius:18px;
                padding:1rem 1.1rem;
                position:relative;
                overflow:hidden;
                transition: all .35s ease;
            }}
            .metric-card:hover {{ transform:translateY(-4px); box-shadow:0 12px 30px -10px rgba(0,0,0,.35); }}
            .metric-title {{ font-size:.85rem; text-transform:uppercase; letter-spacing:.08em; color:var(--subtext); margin:0 0 .35rem 0; }}
            .metric-value {{ font-size:2.05rem; font-weight:600; line-height:1; margin:0; background:linear-gradient(90deg,var(--accent),#a855f7); -webkit-background-clip:text; color:transparent; }}
            /* Recommendations */
            .recommendation-box {{
                background: var(--panel);
                backdrop-filter: blur(14px) saturate(1.4);
                border:1px solid var(--panel-border);
                border-radius:16px;
                padding:.85rem 1rem;
                margin:.55rem 0;
                font-size:.92rem;
            }}
            /* Badges */
            .neo-badge {{
                display:inline-block; padding:.35rem .65rem; margin:.25rem .35rem .25rem 0;
                background:var(--badge-bg); color:var(--text); font-size:.70rem; font-weight:500;
                letter-spacing:.5px; border:1px solid var(--panel-border); border-radius:40px;
                backdrop-filter: blur(12px) saturate(1.6);
            }}
            .neo-badge.success {{ background:rgba(16,185,129,0.18); border-color:rgba(16,185,129,0.35);}} 
            .neo-badge.danger {{ background:rgba(239,68,68,0.18); border-color:rgba(239,68,68,0.40);}} 
            .neo-badge.warn {{ background:rgba(245,158,11,0.20); border-color:rgba(245,158,11,0.45);}} 
            /* Separator */
            .section-separator {{ height:1px; background:linear-gradient(90deg,transparent,var(--panel-border),transparent); margin:1.6rem 0 1.1rem; }}
            /* Glow pulse */
            @keyframes glowPulse {{ 0%{{box-shadow:0 0 0 0 rgba(99,102,241,.4);}} 70%{{box-shadow:0 0 0 18px rgba(99,102,241,0);}} 100%{{box-shadow:0 0 0 0 rgba(99,102,241,0);}} }}
            .pulse-accent {{ animation: glowPulse 3.8s ease-in-out infinite; }}
            .insight-block {{
                background:var(--panel); border:1px solid var(--panel-border); border-radius:18px; padding:1rem 1.1rem; margin-bottom:.9rem;
            }}
            .insight-block h4 {{ margin:.2rem 0 .6rem; font-size:1rem; }}
        </style>
        """, unsafe_allow_html=True)
    
    @log_function("INFO", "DASHBOARD_RUN_OK")
    def run(self):
        """Run the main dashboard."""
        # Inject theme each run (supports dark mode toggle)
        self.inject_theme()
        # Header
        st.markdown("""
        <div class="main-header">
            <h1>🎯 ZeX-ATS-AI Dashboard</h1>
            <p>Enterprise-Grade Resume Analysis & ATS Optimization</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar
        self.render_sidebar()
        
        # Main content based on selected page
        page = st.session_state.get('current_page', 'analyze')
        
        if page == 'analyze':
            self.render_analysis_page()
        elif page == 'history':
            self.render_history_page()
        elif page == 'insights':
            self.render_insights_page()
        elif page == 'settings':
            self.render_settings_page()
    
    @log_function("INFO", "DASHBOARD_SIDEBAR_OK")
    def render_sidebar(self):
        """Render the sidebar navigation."""
        with st.sidebar:
            st.image("https://via.placeholder.com/200x80/667eea/white?text=ZeX-ATS-AI", 
                    use_column_width=True)
            
            st.markdown("---")
            # Dark mode toggle
            dm = st.checkbox("🌙 Dark Mode", value=st.session_state.dark_mode, key="dark_mode_toggle")
            if dm != st.session_state.dark_mode:
                st.session_state.dark_mode = dm
                set_user_preference('dark_mode', dm)
                st.rerun()
            # Accent color picker
            accent = st.color_picker("🎨 Accent", value=st.session_state.primary_color, key="accent_picker")
            if accent != st.session_state.primary_color:
                st.session_state.primary_color = accent
                set_user_preference('primary_color', accent)
                st.rerun()
            # Per-user stored note preference (sample) 
            user_note = st.text_input("Personal Note (saved)", value=get_user_scoped_preference(st.session_state.current_user_id, 'note', ''), key='user_note_box')
            if st.button("💾 Save Note", key='save_note_btn'):
                set_user_scoped_preference(st.session_state.current_user_id, 'note', user_note)
                st.success("Saved.")
            st.markdown("<div style='margin-top:.4rem;'></div>", unsafe_allow_html=True)
            
            # Navigation
            pages = {
                'analyze': '📊 Analyze Resume',
                'history': '📈 Analysis History', 
                'insights': '💡 Insights & Trends',
                'settings': '⚙️ Settings'
            }
            
            for page_key, page_name in pages.items():
                if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                    st.session_state.current_page = page_key
                    st.rerun()
            
            st.markdown("---")
            
            # User info (placeholder)
            with st.expander("👤 User Profile"):
                st.info("**Demo User**\nFree Tier\n5/10 analyses used")
                st.progress(0.5)
            
            # Quick stats
            with st.expander("📊 Quick Stats"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Analyses", "47")
                    st.metric("Avg Score", "78.5")
                with col2:
                    st.metric("This Month", "12")
                    st.metric("Best Score", "94.2")
    
    @log_function("INFO", "DASHBOARD_ANALYZE_PAGE_OK")
    def render_analysis_page(self):
        """Render the main analysis page."""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("📄 Resume Analysis")
            
            # File upload or text input
            input_method = st.radio("Input Method:", ["Upload File", "Paste Text"], horizontal=True)
            
            resume_content = None
            filename = "manual_input"
            
            if input_method == "Upload File":
                uploaded_file = st.file_uploader(
                    "Choose a resume file",
                    type=['pdf', 'docx', 'doc', 'txt'],
                    help="Upload your resume in PDF, Word, or text format"
                )
                
                if uploaded_file is not None:
                    filename = uploaded_file.name
                    resume_content = uploaded_file
            
            else:  # Paste Text
                resume_text = st.text_area(
                    "Paste your resume text here:",
                    height=200,
                    placeholder="Copy and paste your resume content here..."
                )
                
                if resume_text.strip():
                    resume_content = resume_text
            
            # Analysis options
            st.subheader("Analysis Options")
            
            col_opt1, col_opt2 = st.columns(2)
            
            with col_opt1:
                job_description = st.text_area(
                    "Job Description (optional):",
                    height=150,
                    help="Paste the job description to get targeted keyword analysis"
                )
            
            with col_opt2:
                target_role = st.text_input("Target Role (optional):", 
                                          help="e.g., Software Engineer, Data Scientist")
                
                analysis_options = st.multiselect(
                    "Analysis Features:",
                    ["AI Insights", "Detailed Keywords", "Sentiment Analysis", "Industry Benchmarking"],
                    default=["AI Insights", "Detailed Keywords"]
                )
            
            # Analyze button
            if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
                if resume_content is not None:
                    with st.spinner("Analyzing resume... This may take a few moments."):
                        try:
                            # Process resume
                            if input_method == "Upload File":
                                processed_resume = asyncio.run(
                                    self.resume_processor.process_resume_file(
                                        resume_content, filename
                                    )
                                )
                            else:
                                processed_resume = asyncio.run(
                                    self.resume_processor.process_resume_text(resume_content, filename)
                                )
                            
                            # Perform analysis
                            analysis_result = asyncio.run(
                                self.ats_analyzer.analyze_resume(
                                    processed_resume.cleaned_text,
                                    job_description if job_description.strip() else None,
                                    target_role if target_role.strip() else None
                                )
                            )
                            
                            # Store in session state
                            st.session_state.analysis_results = analysis_result
                            st.session_state.processed_resume = processed_resume
                            
                            st.success("✅ Analysis completed successfully!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Analysis failed: {str(e)}")
                else:
                    st.warning("Please upload a file or paste resume text to analyze.")
        
        with col2:
            st.header("🎯 Quick Tips")
            
            tips = [
                "📝 Use action verbs like 'achieved', 'developed', 'managed'",
                "📊 Include quantifiable metrics and achievements",
                "🔍 Match keywords from the job description",
                "📋 Use standard section headings",
                "📱 Keep contact information up to date",
                "🎨 Use consistent formatting throughout"
            ]
            
            for tip in tips:
                st.info(tip)
        
        # Display results if available
        if st.session_state.analysis_results is not None:
            st.markdown("---")
            self.render_analysis_results(st.session_state.analysis_results)
    
    @log_function("DEBUG", "DASHBOARD_RESULTS_OK")
    def render_analysis_results(self, analysis_result):
        """Render the analysis results with visualizations."""
        st.header("📊 Analysis Results")
        overall_score = analysis_result.ats_score.overall_score
        keyword_score = analysis_result.ats_score.keyword_score
        format_score = analysis_result.ats_score.format_score
        readability_score = analysis_result.ats_score.readability_score

        # Futuristic metric grid
        st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin-top:0;'>Performance Snapshot</h3>", unsafe_allow_html=True)
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        # Radial gauge helper
        def radial_gauge(label: str, value: float, accent: str, animate: bool = True, steps: int = 15):
            target = float(f"{value:.1f}")
            if not animate or target <= 0:
                frames = []
                vals = [target]
            else:
                vals = np.linspace(0, target, steps)
                frames = [
                    go.Frame(data=[go.Indicator(
                        mode="gauge+number",
                        value=v,
                        number={'suffix': '%', 'font': {'size': 26}},
                        title={'text': label, 'font': {'size': 14}},
                        gauge={
                            'axis': {'range': [0,100], 'tickwidth': 1, 'tickcolor': '#888'},
                            'bar': {'color': accent},
                            'bgcolor': 'rgba(0,0,0,0)',
                            'borderwidth': 1,
                            'bordercolor': 'rgba(255,255,255,0.15)',
                            'steps': [
                                {'range':[0,40],'color':'rgba(239,68,68,0.25)'},
                                {'range':[40,70],'color':'rgba(245,158,11,0.25)'},
                                {'range':[70,100],'color':'rgba(16,185,129,0.25)'}
                            ]
                        }
                    )]) for v in vals
                ]
            # Initial figure
            fig = go.Figure(
                data=[go.Indicator(
                    mode="gauge+number",
                    value=vals[0],
                    number={'suffix': '%', 'font': {'size': 26}},
                    title={'text': label, 'font': {'size': 14}},
                    gauge={
                        'axis': {'range': [0,100], 'tickwidth': 1, 'tickcolor': '#888'},
                        'bar': {'color': accent},
                        'bgcolor': 'rgba(0,0,0,0)',
                        'borderwidth': 1,
                        'bordercolor': 'rgba(255,255,255,0.15)',
                        'steps': [
                            {'range':[0,40],'color':'rgba(239,68,68,0.25)'},
                            {'range':[40,70],'color':'rgba(245,158,11,0.25)'},
                            {'range':[70,100],'color':'rgba(16,185,129,0.25)'}
                        ]
                    }
                )],
                frames=frames
            )
            if animate and len(frames) > 1:
                fig.update_layout(
                    updatemenus=[{
                        'type': 'buttons',
                        'buttons': [{
                            'label': '▶',
                            'method': 'animate',
                            'args': [None, {'frame': {'duration': 60, 'redraw': True}, 'fromcurrent': True}]
                        }],
                        'x': 0.85,
                        'y': 0.05,
                        'showactive': False
                    }]
                )
            fig.update_layout(
                height=250,
                margin=dict(l=15,r=15,t=40,b=15),
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color':'white' if st.session_state.dark_mode else '#1f2341'}
            )
            st.plotly_chart(fig, use_container_width=True)
        with mcol1: radial_gauge('Overall ATS', overall_score, st.session_state.primary_color)
        with mcol2: radial_gauge('Keyword Match', keyword_score, st.session_state.primary_color)
        with mcol3: radial_gauge('Format Score', format_score, st.session_state.primary_color)
        with mcol4: radial_gauge('Readability', readability_score, st.session_state.primary_color)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Detailed score breakdown
        st.markdown("<div class='section-separator'></div>", unsafe_allow_html=True)
        st.subheader("📋 Score Breakdown")
        
        scores_df = pd.DataFrame({
            'Category': ['Keywords', 'Format', 'Readability', 'Content', 'Contact', 'Skills', 'Experience', 'Education'],
            'Score': [
                analysis_result.ats_score.keyword_score,
                analysis_result.ats_score.format_score,
                analysis_result.ats_score.readability_score,
                analysis_result.ats_score.content_score,
                analysis_result.ats_score.contact_score,
                analysis_result.ats_score.skills_score,
                analysis_result.ats_score.experience_score,
                analysis_result.ats_score.education_score
            ]
        })
        
        # Create radar chart
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=scores_df['Score'],
            theta=scores_df['Category'],
            fill='toself',
            name='Your Resume',
            line=dict(color='#667eea')
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            title="ATS Score Breakdown",
            height=400
        )
        
        col_r1, col_r2 = st.columns([2, 1])
        with col_r1:
            st.plotly_chart(fig_radar, use_container_width=True)
        with col_r2:
            st.dataframe(
                scores_df.style.format({'Score': '{:.1f}%'}).background_gradient(
                    subset=['Score'], cmap='RdYlGn', vmin=0, vmax=100
                ),
                use_container_width=True
            )
        
        # Strengths and Weaknesses
        st.markdown("<div class='section-separator'></div>", unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.subheader("💪 Strengths")
            if analysis_result.strengths:
                for s in analysis_result.strengths:
                    st.markdown(f"<span class='neo-badge success'>{s}</span>", unsafe_allow_html=True)
            else:
                st.info("No strengths identified.")
        with col_s2:
            st.subheader("⚠️ Areas for Improvement")
            if analysis_result.weaknesses:
                for w in analysis_result.weaknesses:
                    st.markdown(f"<span class='neo-badge danger'>{w}</span>", unsafe_allow_html=True)
            else:
                st.success("No critical weaknesses detected.")
        
        # Recommendations
        st.markdown("<div class='section-separator'></div>", unsafe_allow_html=True)
        st.subheader("🎯 Recommendations")
        for i, suggestion in enumerate(analysis_result.suggestions):
            st.markdown(f"<div class='recommendation-box'><strong>{i+1}.</strong> {suggestion}</div>", unsafe_allow_html=True)
        
        # Keyword Analysis
        if analysis_result.keyword_analysis:
            st.subheader("🔍 Keyword Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Matched Keywords:**")
                matched_keywords = analysis_result.keyword_analysis.get('matched_keywords', [])
                if matched_keywords:
                    for keyword in matched_keywords[:10]:  # Show top 10
                        st.badge(keyword, color='success')
                else:
                    st.info("No job description provided for keyword matching")
            
            with col2:
                st.write("**Missing Keywords:**")
                missing_keywords = analysis_result.keyword_analysis.get('missing_keywords', [])
                if missing_keywords:
                    for keyword in missing_keywords[:10]:  # Show top 10
                        st.badge(keyword, color='danger')
                else:
                    st.info("No missing keywords identified")
        
        # AI Insights (if available)
        if hasattr(analysis_result, 'ai_insights') and analysis_result.ai_insights:
            st.subheader("🤖 In-House Insight Engine")
            insights_payload = analysis_result.ai_insights.get('insights') if isinstance(analysis_result.ai_insights, dict) else None
            if insights_payload and isinstance(insights_payload, dict):
                # Display structured insight blocks
                for section_key, section_value in insights_payload.items():
                    with st.expander(section_key.replace('_',' ').title()):
                        if isinstance(section_value, list):
                            for item in section_value:
                                st.markdown(f"<div class='insight-block'>{item}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='insight-block'>{section_value}</div>", unsafe_allow_html=True)
            else:
                st.info("Insight data not available.")
        
        # Export options
        st.markdown("<div class='section-separator'></div>", unsafe_allow_html=True)
        st.subheader("📤 Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Section selector
            with st.expander("Select Export Sections", expanded=False):
                default_sections = list(SECTION_DEFS.keys())
                chosen_sections = st.multiselect(
                    "Sections", default_sections, default=default_sections, key="pdf_sections_select"
                )
            if st.button("📊 Export as PDF Report", key="export_pdf_btn"):
                if not _PDF_AVAILABLE:
                    st.error("PDF engine (WeasyPrint) not available. Ensure dependency installed.")
                else:
                    full_html = build_pdf_html(analysis_result, chosen_sections or list(SECTION_DEFS.keys()))
                    try:
                        pdf_bytes = HTML(string=full_html).write_pdf()
                        st.download_button(
                            label="⬇️ Download PDF",
                            data=pdf_bytes,
                            file_name=f"ats_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime='application/pdf'
                        )
                        st.success("PDF generated.")
                    except Exception as e:
                        st.error(f"PDF generation failed: {e}")
        
        with col2:
            if st.button("📋 Copy Results to Clipboard", key="copy_clip_btn"):
                payload = json.dumps(analysis_result.to_dict(), indent=2)
                st.markdown("""
                <style>
                .toast-copy-success { position:fixed; top:85px; right:25px; background:var(--panel); backdrop-filter:blur(12px); border:1px solid var(--panel-border); padding:.65rem 1rem; border-radius:14px; box-shadow:0 6px 20px -4px rgba(0,0,0,.35); animation:f-pop .35s ease; font-size:.85rem; }
                @keyframes f-pop { 0%{transform:translateY(-6px);opacity:0;} 100%{transform:translateY(0);opacity:1;} }
                </style>
                <div id="copy-toast" style="display:none" class="toast-copy-success">✅ Copied to clipboard</div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                <script>
                (function() {{
                   const txt = {json.dumps(payload)};
                   function showToast() {{
                       const el = window.parent.document.getElementById('copy-toast');
                       if(!el) return; el.style.display='block'; setTimeout(()=>el.style.display='none', 2600);
                   }}
                   try {{ navigator.clipboard.writeText(txt).then(showToast).catch(showToast); }} catch(e) {{ showToast(); }}
                }})();
                </script>
                """, unsafe_allow_html=True)
                st.info("Clipboard attempted (browser permission required).")
        
        with col3:
            # Download JSON
            json_results = json.dumps(analysis_result.to_dict(), indent=2)
            st.download_button(
                "💾 Download JSON",
                json_results,
                file_name=f"ats_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

        # Admin-only diagnostics panel
        roles = get_user_roles(st.session_state.current_user_id)
        if 'admin' in roles:
            with st.expander("🛠 Admin Diagnostics"):
                st.write("User Roles:", roles)
                st.write("Session State Keys:", list(st.session_state.keys()))
                if st.button("Grant Admin Again (noop)"):
                    st.info("Role already present.")
    
    @log_function("INFO", "DASHBOARD_HISTORY_OK")
    def render_history_page(self):
        """Render analysis history page."""
        st.header("📈 Analysis History")
        
        # Mock data for demonstration
        history_data = {
            'Date': pd.date_range(start='2024-01-01', periods=20, freq='W'),
            'Filename': [f"resume_v{i}.pdf" for i in range(1, 21)],
            'Overall Score': np.random.uniform(60, 95, 20),
            'Keyword Score': np.random.uniform(50, 90, 20),
            'Format Score': np.random.uniform(70, 95, 20)
        }
        
        history_df = pd.DataFrame(history_data)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_range = st.date_input(
                "Date Range:",
                value=(history_df['Date'].min().date(), history_df['Date'].max().date()),
                min_value=history_df['Date'].min().date(),
                max_value=history_df['Date'].max().date()
            )
        
        with col2:
            score_filter = st.slider("Minimum Score:", 0, 100, 0)
        
        with col3:
            file_filter = st.multiselect(
                "Files:",
                history_df['Filename'].unique(),
                default=[]
            )
        
        # Filter data
        filtered_df = history_df.copy()
        
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_df = filtered_df[
                (filtered_df['Date'].dt.date >= start_date) & 
                (filtered_df['Date'].dt.date <= end_date)
            ]
        
        if score_filter > 0:
            filtered_df = filtered_df[filtered_df['Overall Score'] >= score_filter]
        
        if file_filter:
            filtered_df = filtered_df[filtered_df['Filename'].isin(file_filter)]
        
        # Display charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Score trend
            fig_trend = px.line(
                filtered_df, 
                x='Date', 
                y=['Overall Score', 'Keyword Score', 'Format Score'],
                title="Score Trends Over Time"
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            # Score distribution
            fig_dist = px.histogram(
                filtered_df,
                x='Overall Score',
                bins=10,
                title="Score Distribution"
            )
            st.plotly_chart(fig_dist, use_container_width=True)
        
        # Data table
        st.subheader("Analysis Records")
        
        st.dataframe(
            filtered_df.style.format({
                'Overall Score': '{:.1f}%',
                'Keyword Score': '{:.1f}%', 
                'Format Score': '{:.1f}%'
            }).background_gradient(
                subset=['Overall Score', 'Keyword Score', 'Format Score'],
                cmap='RdYlGn',
                vmin=0,
                vmax=100
            ),
            use_container_width=True
        )
    
    @log_function("INFO", "DASHBOARD_INSIGHTS_OK")
    def render_insights_page(self):
        """Render insights and trends page."""
        st.header("💡 Insights & Trends")
        
        # Industry benchmarks
        st.subheader("📊 Industry Benchmarks")
        
        benchmark_data = {
            'Industry': ['Technology', 'Finance', 'Healthcare', 'Education', 'Marketing'],
            'Avg Score': [82.5, 78.3, 75.2, 73.8, 79.1],
            'Top Keyword': ['Python', 'Excel', 'Patient Care', 'Curriculum', 'SEO']
        }
        
        benchmark_df = pd.DataFrame(benchmark_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_benchmark = px.bar(
                benchmark_df,
                x='Industry',
                y='Avg Score',
                title="Average ATS Scores by Industry",
                color='Avg Score',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_benchmark, use_container_width=True)
        
        with col2:
            st.dataframe(benchmark_df, use_container_width=True)
        
        # Trending keywords
        st.subheader("🔥 Trending Keywords")
        
        trending_keywords = {
            'Keyword': ['AI/Machine Learning', 'Cloud Computing', 'Data Analysis', 'Agile', 'Python', 'Leadership'],
            'Trend': ['↗️ +15%', '↗️ +12%', '↗️ +8%', '→ +2%', '→ 0%', '↘️ -3%'],
            'Category': ['Technical', 'Technical', 'Technical', 'Methodology', 'Programming', 'Soft Skill']
        }
        
        trending_df = pd.DataFrame(trending_keywords)
        st.dataframe(trending_df, use_container_width=True)
        
        # Tips and best practices
        st.subheader("💡 Best Practices")
        
        best_practices = [
            "**Use specific metrics**: Include numbers, percentages, and measurable achievements",
            "**Tailor for each job**: Customize your resume for specific job descriptions",
            "**Use standard sections**: Include Summary, Experience, Education, and Skills",
            "**Choose the right format**: Use clean, ATS-friendly templates",
            "**Proofread carefully**: Ensure there are no spelling or grammar errors",
            "**Update regularly**: Keep your resume current with latest achievements"
        ]
        
        for practice in best_practices:
            st.markdown(f"• {practice}")
    
    @log_function("INFO", "DASHBOARD_SETTINGS_OK")
    def render_settings_page(self):
        """Render settings and preferences page."""
        st.header("⚙️ Settings & Preferences")
        
        # Analysis preferences
        st.subheader("🎯 Analysis Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.selectbox("Default Analysis Type:", ["Comprehensive", "Quick", "Detailed"])
            st.multiselect("Default Features:", 
                         ["AI Insights", "Keyword Analysis", "Sentiment Analysis", "Industry Benchmarking"],
                         default=["AI Insights", "Keyword Analysis"])
        
        with col2:
            st.selectbox("Industry Focus:", ["Technology", "Finance", "Healthcare", "General"])
            st.slider("Analysis Detail Level:", 1, 5, 3)
        
        # Notification preferences
        st.subheader("🔔 Notifications")
        
        st.checkbox("Email notifications for completed analyses")
        st.checkbox("Weekly summary reports")
        st.checkbox("Industry trend alerts")
        
        # Data and privacy
        st.subheader("🔒 Data & Privacy")
        
        st.checkbox("Store analysis history")
        st.checkbox("Allow anonymous usage analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export All Data"):
                st.info("Data export feature coming soon!")
        
        with col2:
            if st.button("🗑️ Delete All History"):
                st.warning("Data deletion feature coming soon!")
        
        # Account information
        st.subheader("👤 Account Information")
        
        with st.expander("Account Details"):
            st.text_input("Full Name:", value="Demo User")
            st.text_input("Email:", value="demo@example.com")
            st.selectbox("Subscription:", ["Free", "Pro", "Enterprise"], index=0)
            
            if st.button("Update Profile"):
                st.success("Profile updated successfully!")
    
    @log_function("DEBUG", "DASHBOARD_SCORE_COLOR_OK")
    def get_score_color(self, score):
        """Get color based on score value."""
        if score >= 80:
            return "#28a745"  # Green
        elif score >= 60:
            return "#ffc107"  # Yellow
        else:
            return "#dc3545"  # Red

# Custom components
def st_badge(text, color='primary'):
    """Create a colored badge."""
    colors = {
        'primary': '#0d6efd',
        'success': '#198754',
        'danger': '#dc3545',
        'warning': '#fd7e14',
        'info': '#0dcaf0'
    }
    
    bg_color = colors.get(color, colors['primary'])
    
    st.markdown(f"""
    <span style="
        background-color: {bg_color};
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.375rem;
        font-size: 0.75rem;
        font-weight: 500;
        margin-right: 0.25rem;
        margin-bottom: 0.25rem;
        display: inline-block;
    ">{text}</span>
    """, unsafe_allow_html=True)

# Monkey patch the badge function
st.badge = st_badge

# Main execution
if __name__ == "__main__":
    dashboard = StreamlitDashboard()
    dashboard.run()
