"""
ZeX-ATS-AI Core ATS Analyzer
Advanced AI-powered resume analysis and ATS compatibility scoring.
"""

import re
import json
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime

import spacy
import nltk
from textstat import flesch_reading_ease, syllable_count
from textblob import TextBlob
import openai
import anthropic

from src.core.config import settings
from src.utils.text_processing import TextProcessor
from src.utils.keyword_extractor import KeywordExtractor
from src.utils.sentiment_analyzer import SentimentAnalyzer


@dataclass
class ATSScore:
    """ATS compatibility score breakdown."""
    overall_score: float
    keyword_score: float
    format_score: float
    readability_score: float
    content_score: float
    contact_score: float
    skills_score: float
    experience_score: float
    education_score: float
    
    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class ResumeAnalysis:
    """Comprehensive resume analysis results."""
    ats_score: ATSScore
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    keyword_analysis: Dict[str, Any]
    skills_analysis: Dict[str, Any]
    content_analysis: Dict[str, Any]
    format_analysis: Dict[str, Any]
    ai_insights: Dict[str, Any]
    processing_time: float
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        return result


class ATSAnalyzer:
    """Enterprise-grade ATS compatibility analyzer."""
    
    def __init__(self):
        """Initialize the ATS analyzer with AI models and processors."""
        self.text_processor = TextProcessor()
        self.keyword_extractor = KeywordExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize AI clients
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
        
        if settings.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(
                api_key=settings.anthropic_api_key
            )
    
    async def analyze_resume(
        self, 
        resume_text: str, 
        job_description: Optional[str] = None,
        target_role: Optional[str] = None
    ) -> ResumeAnalysis:
        """
        Comprehensive resume analysis with AI-powered insights.
        
        Args:
            resume_text: The resume text to analyze
            job_description: Optional job description for matching
            target_role: Optional target role for optimization
            
        Returns:
            ResumeAnalysis object with detailed results
        """
        start_time = datetime.now()
        
        # Parallel processing of different analysis components
        tasks = [
            self._analyze_ats_compatibility(resume_text, job_description),
            self._analyze_keywords(resume_text, job_description),
            self._analyze_skills(resume_text),
            self._analyze_content_quality(resume_text),
            self._analyze_format_structure(resume_text),
        ]
        
        if settings.openai_api_key or settings.anthropic_api_key:
            tasks.append(self._get_ai_insights(resume_text, job_description, target_role))
        
        results = await asyncio.gather(*tasks)
        
        # Unpack results
        ats_score = results[0]
        keyword_analysis = results[1] 
        skills_analysis = results[2]
        content_analysis = results[3]
        format_analysis = results[4]
        ai_insights = results[5] if len(results) > 5 else {}
        
        # Generate suggestions and insights
        strengths, weaknesses, suggestions = self._generate_recommendations(
            ats_score, keyword_analysis, skills_analysis, 
            content_analysis, format_analysis, ai_insights
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ResumeAnalysis(
            ats_score=ats_score,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            keyword_analysis=keyword_analysis,
            skills_analysis=skills_analysis,
            content_analysis=content_analysis,
            format_analysis=format_analysis,
            ai_insights=ai_insights,
            processing_time=processing_time,
            timestamp=start_time
        )
    
    async def _analyze_ats_compatibility(
        self, 
        resume_text: str, 
        job_description: Optional[str] = None
    ) -> ATSScore:
        """Analyze ATS compatibility and generate detailed score."""
        
        # Keyword matching score
        keyword_score = await self._calculate_keyword_score(resume_text, job_description)
        
        # Format compatibility score
        format_score = self._calculate_format_score(resume_text)
        
        # Readability score
        readability_score = self._calculate_readability_score(resume_text)
        
        # Content quality score
        content_score = self._calculate_content_score(resume_text)
        
        # Contact information score
        contact_score = self._calculate_contact_score(resume_text)
        
        # Skills presentation score
        skills_score = self._calculate_skills_score(resume_text)
        
        # Experience presentation score
        experience_score = self._calculate_experience_score(resume_text)
        
        # Education presentation score
        education_score = self._calculate_education_score(resume_text)
        
        # Calculate overall weighted score
        weights = {
            'keyword': 0.25,
            'format': 0.15,
            'readability': 0.10,
            'content': 0.15,
            'contact': 0.10,
            'skills': 0.10,
            'experience': 0.10,
            'education': 0.05
        }
        
        overall_score = (
            keyword_score * weights['keyword'] +
            format_score * weights['format'] +
            readability_score * weights['readability'] +
            content_score * weights['content'] +
            contact_score * weights['contact'] +
            skills_score * weights['skills'] +
            experience_score * weights['experience'] +
            education_score * weights['education']
        ) * 100
        
        return ATSScore(
            overall_score=round(overall_score, 1),
            keyword_score=round(keyword_score * 100, 1),
            format_score=round(format_score * 100, 1),
            readability_score=round(readability_score * 100, 1),
            content_score=round(content_score * 100, 1),
            contact_score=round(contact_score * 100, 1),
            skills_score=round(skills_score * 100, 1),
            experience_score=round(experience_score * 100, 1),
            education_score=round(education_score * 100, 1)
        )
    
    async def _calculate_keyword_score(
        self, 
        resume_text: str, 
        job_description: Optional[str] = None
    ) -> float:
        """Calculate keyword matching score."""
        if not job_description:
            # Use generic tech keywords if no job description provided
            job_keywords = self.keyword_extractor.extract_generic_keywords()
        else:
            job_keywords = await self.keyword_extractor.extract_keywords(job_description)
        
        resume_keywords = await self.keyword_extractor.extract_keywords(resume_text)
        
        if not job_keywords:
            return 0.7  # Neutral score if no keywords to match
        
        matches = len(set(job_keywords) & set(resume_keywords))
        return min(matches / len(job_keywords), 1.0)
    
    def _calculate_format_score(self, resume_text: str) -> float:
        """Calculate format compatibility score."""
        score = 0.0
        
        # Check for proper sections
        sections = ['experience', 'education', 'skills', 'summary', 'objective']
        found_sections = sum(1 for section in sections if section in resume_text.lower())
        score += (found_sections / len(sections)) * 0.3
        
        # Check for bullet points
        if '•' in resume_text or '*' in resume_text or '-' in resume_text:
            score += 0.2
        
        # Check for consistent formatting patterns
        lines = resume_text.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        # Check for consistent capitalization
        proper_caps = sum(1 for line in non_empty_lines if line[0].isupper()) / len(non_empty_lines)
        score += proper_caps * 0.2
        
        # Check for appropriate length
        word_count = len(resume_text.split())
        if 300 <= word_count <= 800:
            score += 0.3
        elif 200 <= word_count < 300 or 800 < word_count <= 1200:
            score += 0.2
        else:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_readability_score(self, resume_text: str) -> float:
        """Calculate readability score using various metrics."""
        try:
            flesch_score = flesch_reading_ease(resume_text)
            
            # Normalize Flesch score (0-100) to 0-1
            # Target range: 60-80 (standard reading level)
            if 60 <= flesch_score <= 80:
                readability = 1.0
            elif 40 <= flesch_score < 60 or 80 < flesch_score <= 90:
                readability = 0.8
            elif 20 <= flesch_score < 40 or 90 < flesch_score <= 100:
                readability = 0.6
            else:
                readability = 0.4
            
            return readability
        except:
            return 0.7  # Neutral score if calculation fails
    
    def _calculate_content_score(self, resume_text: str) -> float:
        """Calculate content quality score."""
        score = 0.0
        
        # Check for quantifiable achievements
        numbers = re.findall(r'\d+[%]?|\$\d+', resume_text)
        if len(numbers) >= 5:
            score += 0.3
        elif len(numbers) >= 2:
            score += 0.2
        else:
            score += 0.1
        
        # Check for action verbs
        doc = self.nlp(resume_text)
        verbs = [token.lemma_ for token in doc if token.pos_ == 'VERB']
        strong_verbs = ['achieve', 'develop', 'implement', 'manage', 'lead', 
                       'create', 'improve', 'increase', 'optimize', 'deliver']
        strong_verb_count = sum(1 for verb in verbs if verb in strong_verbs)
        score += min(strong_verb_count / 10, 0.25)
        
        # Check for industry-relevant keywords
        score += min(len(set(resume_text.lower().split()) & 
                    set(['python', 'java', 'sql', 'aws', 'docker', 'kubernetes'])) / 20, 0.2)
        
        # Check against clichés
        cliches = ['team player', 'hard worker', 'detail-oriented', 'self-motivated']
        cliche_count = sum(1 for cliche in cliches if cliche in resume_text.lower())
        score += max(0.25 - (cliche_count * 0.1), 0)
        
        return min(score, 1.0)
    
    def _calculate_contact_score(self, resume_text: str) -> float:
        """Calculate contact information completeness score."""
        score = 0.0
        
        # Email
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text):
            score += 0.3
        
        # Phone
        if re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', resume_text):
            score += 0.3
        
        # LinkedIn
        if 'linkedin' in resume_text.lower():
            score += 0.2
        
        # Location/Address
        if re.search(r'\b(street|st\.|avenue|ave\.|road|rd\.|city|state)\b', resume_text.lower()):
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_skills_score(self, resume_text: str) -> float:
        """Calculate skills section quality score."""
        score = 0.0
        
        # Check for dedicated skills section
        if 'skills' in resume_text.lower():
            score += 0.4
        
        # Check for technical skills
        tech_skills = ['python', 'java', 'javascript', 'sql', 'aws', 'docker', 'git']
        found_tech = sum(1 for skill in tech_skills if skill in resume_text.lower())
        score += min(found_tech / len(tech_skills), 0.3)
        
        # Check for soft skills
        soft_skills = ['leadership', 'communication', 'problem-solving', 'analytical']
        found_soft = sum(1 for skill in soft_skills if skill in resume_text.lower())
        score += min(found_soft / len(soft_skills), 0.3)
        
        return min(score, 1.0)
    
    def _calculate_experience_score(self, resume_text: str) -> float:
        """Calculate experience section quality score."""
        score = 0.0
        
        # Check for experience section
        if any(keyword in resume_text.lower() for keyword in ['experience', 'work', 'employment']):
            score += 0.3
        
        # Check for company names and dates
        date_patterns = [
            r'\d{4}[-/]\d{4}',  # 2020-2021
            r'\d{4}\s*[-–]\s*\d{4}',  # 2020 - 2021
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*\d{4}',  # Month Year
        ]
        
        dates_found = sum(1 for pattern in date_patterns 
                         if re.search(pattern, resume_text, re.IGNORECASE))
        score += min(dates_found / 3, 0.4)
        
        # Check for achievement-oriented descriptions
        achievement_words = ['achieved', 'improved', 'increased', 'reduced', 'implemented']
        achievements = sum(1 for word in achievement_words if word in resume_text.lower())
        score += min(achievements / 5, 0.3)
        
        return min(score, 1.0)
    
    def _calculate_education_score(self, resume_text: str) -> float:
        """Calculate education section quality score."""
        score = 0.0
        
        # Check for education section
        if 'education' in resume_text.lower():
            score += 0.4
        
        # Check for degree mentions
        degrees = ['bachelor', 'master', 'phd', 'doctorate', 'associate', 'diploma']
        found_degrees = sum(1 for degree in degrees if degree in resume_text.lower())
        score += min(found_degrees / 2, 0.3)
        
        # Check for institutions
        if any(word in resume_text.lower() for word in ['university', 'college', 'institute']):
            score += 0.3
        
        return min(score, 1.0)
    
    async def _analyze_keywords(
        self, 
        resume_text: str, 
        job_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze keyword usage and relevance."""
        resume_keywords = await self.keyword_extractor.extract_keywords(resume_text)
        
        if job_description:
            job_keywords = await self.keyword_extractor.extract_keywords(job_description)
            matched_keywords = set(resume_keywords) & set(job_keywords)
            missing_keywords = set(job_keywords) - set(resume_keywords)
        else:
            job_keywords = []
            matched_keywords = set()
            missing_keywords = set()
        
        return {
            'resume_keywords': resume_keywords[:20],  # Top 20
            'job_keywords': job_keywords[:20] if job_keywords else [],
            'matched_keywords': list(matched_keywords)[:15],
            'missing_keywords': list(missing_keywords)[:10],
            'keyword_density': len(resume_keywords) / len(resume_text.split()) * 100,
            'match_percentage': len(matched_keywords) / len(job_keywords) * 100 if job_keywords else 0
        }
    
    async def _analyze_skills(self, resume_text: str) -> Dict[str, Any]:
        """Analyze skills mentioned in the resume."""
        doc = self.nlp(resume_text)
        
        # Extract technical skills
        technical_skills = []
        skill_patterns = [
            r'\b(python|java|javascript|c\+\+|sql|html|css|react|node\.js|aws|docker|kubernetes)\b',
            r'\b(machine learning|data science|artificial intelligence|deep learning)\b',
            r'\b(agile|scrum|devops|ci/cd|git|jenkins|terraform)\b'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            technical_skills.extend(matches)
        
        # Extract soft skills using NLP
        soft_skill_keywords = ['leadership', 'communication', 'teamwork', 'problem-solving']
        soft_skills = [skill for skill in soft_skill_keywords if skill in resume_text.lower()]
        
        return {
            'technical_skills': list(set(technical_skills)),
            'soft_skills': soft_skills,
            'skill_count': len(set(technical_skills + soft_skills)),
            'skills_by_category': {
                'programming': [s for s in technical_skills if s in ['python', 'java', 'javascript', 'c++']],
                'cloud': [s for s in technical_skills if s in ['aws', 'docker', 'kubernetes']],
                'data': [s for s in technical_skills if 'data' in s or 'machine learning' in s]
            }
        }
    
    async def _analyze_content_quality(self, resume_text: str) -> Dict[str, Any]:
        """Analyze overall content quality."""
        doc = self.nlp(resume_text)
        
        # Sentiment analysis
        sentiment = self.sentiment_analyzer.analyze_sentiment(resume_text)
        
        # Grammar and language analysis
        sentences = [sent.text for sent in doc.sents]
        avg_sentence_length = sum(len(sent.split()) for sent in sentences) / len(sentences)
        
        # Vocabulary complexity
        unique_words = len(set(token.lemma_.lower() for token in doc if token.is_alpha))
        total_words = len([token for token in doc if token.is_alpha])
        vocabulary_richness = unique_words / total_words if total_words > 0 else 0
        
        return {
            'sentiment': sentiment,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'vocabulary_richness': round(vocabulary_richness, 3),
            'readability_score': flesch_reading_ease(resume_text),
            'word_count': total_words,
            'sentence_count': len(sentences),
            'paragraph_count': len(resume_text.split('\n\n'))
        }
    
    async def _analyze_format_structure(self, resume_text: str) -> Dict[str, Any]:
        """Analyze document structure and formatting."""
        lines = resume_text.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        # Detect sections
        section_headers = []
        potential_headers = ['summary', 'experience', 'education', 'skills', 'projects', 'certifications']
        
        for line in non_empty_lines:
            if any(header in line.lower() for header in potential_headers):
                section_headers.append(line.strip())
        
        # Analyze formatting consistency
        bullet_points = len(re.findall(r'[•*-]\s', resume_text))
        date_formats = len(re.findall(r'\d{4}', resume_text))
        
        return {
            'sections_detected': section_headers,
            'section_count': len(section_headers),
            'line_count': len(non_empty_lines),
            'bullet_points': bullet_points,
            'date_formats_found': date_formats,
            'has_consistent_formatting': len(section_headers) >= 3,
            'estimated_pages': len(resume_text) // 3000 + 1  # Rough estimate
        }
    
    async def _get_ai_insights(
        self, 
        resume_text: str, 
        job_description: Optional[str] = None,
        target_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get AI-powered insights and recommendations."""
        insights = {}
        
        try:
            if settings.openai_api_key:
                insights.update(await self._get_openai_insights(resume_text, job_description, target_role))
        except Exception as e:
            insights['openai_error'] = str(e)
        
        try:
            if settings.anthropic_api_key:
                insights.update(await self._get_anthropic_insights(resume_text, job_description, target_role))
        except Exception as e:
            insights['anthropic_error'] = str(e)
        
        return insights
    
    async def _get_openai_insights(
        self, 
        resume_text: str, 
        job_description: Optional[str] = None,
        target_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get insights from OpenAI GPT models."""
        prompt = f"""Analyze this resume for ATS optimization and provide specific recommendations:

RESUME:
{resume_text[:2000]}  # Limit for token constraints

JOB DESCRIPTION: {job_description[:1000] if job_description else 'Not provided'}
TARGET ROLE: {target_role if target_role else 'Not specified'}

Provide a JSON response with:
1. top_strengths (3 items)
2. critical_improvements (3 items)  
3. keyword_suggestions (5 items)
4. ats_optimization_tips (3 items)
5. overall_impression (1 paragraph)
"""
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        
        try:
            content = response.choices[0].message.content
            return {"openai_insights": json.loads(content)}
        except:
            return {"openai_insights": {"raw_response": content}}
    
    async def _get_anthropic_insights(
        self, 
        resume_text: str, 
        job_description: Optional[str] = None,
        target_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get insights from Anthropic Claude."""
        prompt = f"""Please analyze this resume for ATS compatibility and career advancement:

<resume>
{resume_text[:2000]}
</resume>

<job_description>
{job_description[:1000] if job_description else 'Not provided'}
</job_description>

<target_role>
{target_role if target_role else 'General optimization'}
</target_role>

Provide specific, actionable feedback focusing on:
1. ATS scanning optimization
2. Keyword alignment  
3. Content structure improvements
4. Professional presentation enhancement
"""
        
        message = await self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {"anthropic_insights": message.content[0].text}
    
    def _generate_recommendations(
        self,
        ats_score: ATSScore,
        keyword_analysis: Dict[str, Any],
        skills_analysis: Dict[str, Any], 
        content_analysis: Dict[str, Any],
        format_analysis: Dict[str, Any],
        ai_insights: Dict[str, Any]
    ) -> Tuple[List[str], List[str], List[str]]:
        """Generate strengths, weaknesses, and suggestions based on analysis."""
        
        strengths = []
        weaknesses = []
        suggestions = []
        
        # Analyze scores and generate insights
        if ats_score.overall_score >= 80:
            strengths.append(f"Excellent ATS compatibility with {ats_score.overall_score}% overall score")
        elif ats_score.overall_score >= 60:
            strengths.append(f"Good ATS compatibility with {ats_score.overall_score}% overall score")
        else:
            weaknesses.append(f"Low ATS compatibility at {ats_score.overall_score}% - needs improvement")
        
        # Keyword analysis insights
        if keyword_analysis.get('match_percentage', 0) >= 60:
            strengths.append(f"Strong keyword alignment at {keyword_analysis['match_percentage']:.1f}%")
        else:
            weaknesses.append("Low keyword matching with job requirements")
            suggestions.append(f"Include missing keywords: {', '.join(keyword_analysis.get('missing_keywords', [])[:5])}")
        
        # Skills analysis insights
        if skills_analysis.get('skill_count', 0) >= 10:
            strengths.append(f"Comprehensive skills list with {skills_analysis['skill_count']} identified skills")
        else:
            weaknesses.append("Limited skills representation")
            suggestions.append("Add more technical and soft skills relevant to your field")
        
        # Content quality insights
        if content_analysis.get('readability_score', 0) >= 60:
            strengths.append("Good readability and content clarity")
        else:
            weaknesses.append("Content clarity could be improved")
            suggestions.append("Simplify sentence structure and use active voice")
        
        # Format analysis insights
        if format_analysis.get('section_count', 0) >= 4:
            strengths.append("Well-structured with clear sections")
        else:
            weaknesses.append("Missing standard resume sections")
            suggestions.append("Add standard sections: Summary, Experience, Education, Skills")
        
        # Score-based suggestions
        if ats_score.contact_score < 70:
            suggestions.append("Complete contact information including email, phone, and LinkedIn")
        
        if ats_score.keyword_score < 60:
            suggestions.append("Optimize keyword usage based on job descriptions")
        
        if ats_score.format_score < 70:
            suggestions.append("Improve formatting with consistent bullet points and section headers")
        
        # Ensure we have balanced feedback
        if len(strengths) < 2:
            strengths.append("Resume shows professional experience and qualifications")
        
        if len(suggestions) < 3:
            suggestions.extend([
                "Quantify achievements with specific metrics and numbers",
                "Use strong action verbs to describe accomplishments", 
                "Tailor content to specific job opportunities"
            ])
        
        return strengths[:5], weaknesses[:5], suggestions[:8]
