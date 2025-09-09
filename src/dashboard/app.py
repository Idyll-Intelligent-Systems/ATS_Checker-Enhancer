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

# Set page configuration
st.set_page_config(
    page_title="ZeX-ATS-AI Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .score-excellent { color: #28a745; }
    .score-good { color: #ffc107; }
    .score-poor { color: #dc3545; }
    .recommendation-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

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
        
        # Initialize session state
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
        if 'processed_resume' not in st.session_state:
            st.session_state.processed_resume = None
        if 'analysis_history' not in st.session_state:
            st.session_state.analysis_history = []
    
    def run(self):
        """Run the main dashboard."""
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
    
    def render_sidebar(self):
        """Render the sidebar navigation."""
        with st.sidebar:
            st.image("https://via.placeholder.com/200x80/667eea/white?text=ZeX-ATS-AI", 
                    use_column_width=True)
            
            st.markdown("---")
            
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
    
    def render_analysis_results(self, analysis_result):
        """Render the analysis results with visualizations."""
        st.header("📊 Analysis Results")
        
        # Overall score
        overall_score = analysis_result.ats_score.overall_score
        score_color = self.get_score_color(overall_score)
        
        # Score display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h2 style="color: {score_color}; margin: 0;">{overall_score:.1f}%</h2>
                <p style="margin: 0;">Overall ATS Score</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            keyword_score = analysis_result.ats_score.keyword_score
            st.metric("Keyword Match", f"{keyword_score:.1f}%")
        
        with col3:
            format_score = analysis_result.ats_score.format_score
            st.metric("Format Score", f"{format_score:.1f}%")
        
        with col4:
            readability_score = analysis_result.ats_score.readability_score
            st.metric("Readability", f"{readability_score:.1f}%")
        
        # Detailed score breakdown
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
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            st.dataframe(
                scores_df.style.format({'Score': '{:.1f}%'}).background_gradient(
                    subset=['Score'], cmap='RdYlGn', vmin=0, vmax=100
                ),
                use_container_width=True
            )
        
        # Strengths and Weaknesses
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💪 Strengths")
            for strength in analysis_result.strengths:
                st.success(f"✅ {strength}")
        
        with col2:
            st.subheader("⚠️ Areas for Improvement")
            for weakness in analysis_result.weaknesses:
                st.warning(f"⚠️ {weakness}")
        
        # Recommendations
        st.subheader("🎯 Recommendations")
        
        for i, suggestion in enumerate(analysis_result.suggestions):
            st.markdown(f"""
            <div class="recommendation-box">
                <strong>Recommendation {i+1}:</strong> {suggestion}
            </div>
            """, unsafe_allow_html=True)
        
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
            st.subheader("🤖 AI-Powered Insights")
            
            with st.expander("View AI Analysis", expanded=False):
                if 'openai_insights' in analysis_result.ai_insights:
                    st.json(analysis_result.ai_insights['openai_insights'])
                elif 'anthropic_insights' in analysis_result.ai_insights:
                    st.write(analysis_result.ai_insights['anthropic_insights'])
                else:
                    st.info("AI insights not available for this analysis")
        
        # Export options
        st.subheader("📤 Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export as PDF Report"):
                # This would generate a PDF report
                st.info("PDF export feature coming soon!")
        
        with col2:
            if st.button("📋 Copy Results to Clipboard"):
                # This would copy results to clipboard
                st.info("Copy to clipboard feature coming soon!")
        
        with col3:
            # Download JSON
            json_results = json.dumps(analysis_result.to_dict(), indent=2)
            st.download_button(
                "💾 Download JSON",
                json_results,
                file_name=f"ats_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
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
