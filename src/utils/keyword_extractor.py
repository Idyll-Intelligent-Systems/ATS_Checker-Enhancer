"""
ZeX-ATS-AI Keyword Extraction Utilities
Advanced keyword and skill extraction using NLP and machine learning.
"""

import re
from typing import List, Dict, Set, Optional, Tuple
from collections import Counter, defaultdict
import asyncio

import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag
from sklearn.feature_extraction.text import TfidfVectorizer
import requests

from src.core.config import settings


class KeywordExtractor:
    """Advanced keyword extraction for resume and job description analysis."""
    
    def __init__(self):
        """Initialize keyword extractor with NLP models and skill databases."""
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except OSError:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: No spaCy model found. Install with: python -m spacy download en_core_web_sm")
                self.nlp = None
        
        # Initialize TF-IDF vectorizer
        self.tfidf = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=1,
            max_df=0.8
        )
        
        # Skill databases
        self.technical_skills = self._load_technical_skills()
        self.soft_skills = self._load_soft_skills()
        self.industry_keywords = self._load_industry_keywords()
        
        # Stop words
        self.stop_words = set(stopwords.words('english'))
        
        # Resume-specific stop words
        self.resume_stop_words = {
            'resume', 'cv', 'experience', 'education', 'skills', 'objective',
            'summary', 'references', 'available', 'upon', 'request', 'page'
        }
        
        self.all_stop_words = self.stop_words.union(self.resume_stop_words)
    
    def _load_technical_skills(self) -> Dict[str, List[str]]:
        """Load comprehensive technical skills database."""
        return {
            'programming_languages': [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'c',
                'go', 'rust', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'php',
                'ruby', 'perl', 'shell', 'bash', 'powershell'
            ],
            'web_technologies': [
                'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express',
                'django', 'flask', 'spring boot', 'laravel', 'asp.net', 'jquery',
                'bootstrap', 'sass', 'less', 'webpack', 'gulp', 'grunt'
            ],
            'databases': [
                'sql', 'mysql', 'postgresql', 'mongodb', 'cassandra', 'redis',
                'elasticsearch', 'oracle', 'sql server', 'sqlite', 'nosql',
                'dynamodb', 'neo4j', 'couchbase', 'influxdb'
            ],
            'cloud_platforms': [
                'aws', 'azure', 'gcp', 'google cloud', 'heroku', 'digitalocean',
                's3', 'ec2', 'lambda', 'cloudformation', 'terraform', 'ansible'
            ],
            'devops_tools': [
                'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab',
                'ci/cd', 'travis ci', 'circle ci', 'nagios', 'prometheus',
                'grafana', 'elk stack', 'splunk'
            ],
            'data_science': [
                'machine learning', 'deep learning', 'artificial intelligence',
                'data science', 'data analysis', 'statistics', 'pandas', 'numpy',
                'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'jupyter',
                'tableau', 'power bi', 'spark', 'hadoop'
            ],
            'mobile_development': [
                'ios', 'android', 'react native', 'flutter', 'xamarin',
                'swift', 'objective-c', 'kotlin', 'java'
            ],
            'methodologies': [
                'agile', 'scrum', 'kanban', 'waterfall', 'devops', 'tdd',
                'bdd', 'microservices', 'restful', 'soap', 'graphql'
            ]
        }
    
    def _load_soft_skills(self) -> List[str]:
        """Load comprehensive soft skills database."""
        return [
            'leadership', 'communication', 'teamwork', 'collaboration',
            'problem solving', 'analytical thinking', 'critical thinking',
            'creativity', 'innovation', 'adaptability', 'flexibility',
            'time management', 'project management', 'organization',
            'attention to detail', 'multitasking', 'decision making',
            'negotiation', 'presentation', 'public speaking', 'mentoring',
            'conflict resolution', 'emotional intelligence', 'empathy',
            'customer service', 'sales', 'marketing', 'research',
            'strategic planning', 'business analysis', 'process improvement'
        ]
    
    def _load_industry_keywords(self) -> Dict[str, List[str]]:
        """Load industry-specific keywords."""
        return {
            'technology': [
                'software development', 'system architecture', 'scalability',
                'performance optimization', 'security', 'debugging', 'testing',
                'code review', 'api development', 'integration', 'automation'
            ],
            'finance': [
                'financial analysis', 'risk management', 'portfolio management',
                'trading', 'derivatives', 'quantitative analysis', 'modeling',
                'compliance', 'audit', 'investment', 'banking'
            ],
            'healthcare': [
                'patient care', 'medical records', 'healthcare administration',
                'clinical research', 'regulatory compliance', 'hipaa',
                'electronic health records', 'telemedicine'
            ],
            'marketing': [
                'digital marketing', 'seo', 'sem', 'social media marketing',
                'content marketing', 'email marketing', 'analytics',
                'conversion optimization', 'brand management', 'campaign management'
            ],
            'sales': [
                'lead generation', 'customer acquisition', 'account management',
                'business development', 'crm', 'sales forecasting',
                'territory management', 'client relationships'
            ]
        }
    
    async def extract_keywords(
        self, 
        text: str, 
        method: str = 'hybrid',
        top_n: int = 50
    ) -> List[str]:
        """
        Extract keywords from text using various methods.
        
        Args:
            text: Input text
            method: Extraction method ('tfidf', 'spacy', 'pattern', 'hybrid')
            top_n: Number of top keywords to return
            
        Returns:
            List of extracted keywords
        """
        if method == 'tfidf':
            return await self._extract_tfidf_keywords(text, top_n)
        elif method == 'spacy':
            return await self._extract_spacy_keywords(text, top_n)
        elif method == 'pattern':
            return await self._extract_pattern_keywords(text, top_n)
        else:  # hybrid
            return await self._extract_hybrid_keywords(text, top_n)
    
    async def _extract_tfidf_keywords(self, text: str, top_n: int) -> List[str]:
        """Extract keywords using TF-IDF scoring."""
        try:
            # Fit TF-IDF on the text
            tfidf_matrix = self.tfidf.fit_transform([text])
            feature_names = self.tfidf.get_feature_names_out()
            
            # Get TF-IDF scores
            scores = tfidf_matrix.toarray()[0]
            
            # Create keyword-score pairs and sort
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Return top keywords
            return [keyword for keyword, score in keyword_scores[:top_n] if score > 0]
        
        except Exception as e:
            print(f"TF-IDF extraction error: {e}")
            return await self._extract_pattern_keywords(text, top_n)
    
    async def _extract_spacy_keywords(self, text: str, top_n: int) -> List[str]:
        """Extract keywords using spaCy NLP."""
        if not self.nlp:
            return await self._extract_pattern_keywords(text, top_n)
        
        try:
            doc = self.nlp(text)
            keywords = []
            
            # Extract named entities
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PRODUCT', 'TECHNOLOGY', 'SKILL']:
                    keywords.append(ent.text.lower())
            
            # Extract noun phrases
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) <= 3:  # Limit phrase length
                    keywords.append(chunk.text.lower())
            
            # Extract important individual tokens
            for token in doc:
                if (token.pos_ in ['NOUN', 'PROPN'] and 
                    not token.is_stop and 
                    not token.is_punct and 
                    len(token.text) > 2):
                    keywords.append(token.lemma_.lower())
            
            # Count occurrences and return most frequent
            keyword_counts = Counter(keywords)
            return [keyword for keyword, count in keyword_counts.most_common(top_n)]
        
        except Exception as e:
            print(f"spaCy extraction error: {e}")
            return await self._extract_pattern_keywords(text, top_n)
    
    async def _extract_pattern_keywords(self, text: str, top_n: int) -> List[str]:
        """Extract keywords using regex patterns and skill databases."""
        keywords = []
        text_lower = text.lower()
        
        # Extract technical skills
        for category, skills in self.technical_skills.items():
            for skill in skills:
                if skill in text_lower:
                    keywords.append(skill)
        
        # Extract soft skills
        for skill in self.soft_skills:
            if skill in text_lower:
                keywords.append(skill)
        
        # Extract programming language specific patterns
        prog_patterns = [
            r'\b(python|java|javascript|typescript|c\+\+|c#)\s*(3\.\d+|1[0-9]|2[0-9])?\b',
            r'\b(sql|mysql|postgresql|mongodb)\s*(server|database)?\b',
            r'\b(react|angular|vue)\s*(js|\.js)?\b',
            r'\b(aws|azure|gcp)\s*(ec2|s3|lambda|functions)?\b'
        ]
        
        for pattern in prog_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    keyword = ' '.join(filter(None, match)).strip()
                else:
                    keyword = match.strip()
                if keyword:
                    keywords.append(keyword)
        
        # Extract acronyms (potential technical terms)
        acronyms = re.findall(r'\b[A-Z]{2,6}\b', text)
        keywords.extend([acronym.lower() for acronym in acronyms])
        
        # Extract version numbers with technologies
        version_patterns = [
            r'\b(python|java|node|php|ruby)\s*(\d+\.?\d*)\b',
            r'\b(version|v\.?)\s*(\d+\.?\d*)\b'
        ]
        
        for pattern in version_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    keyword = ' '.join(match).strip()
                    keywords.append(keyword)
        
        # Count and return most frequent
        keyword_counts = Counter(keywords)
        return [keyword for keyword, count in keyword_counts.most_common(top_n)]
    
    async def _extract_hybrid_keywords(self, text: str, top_n: int) -> List[str]:
        """Extract keywords using hybrid approach combining all methods."""
        # Get keywords from all methods
        tfidf_keywords = await self._extract_tfidf_keywords(text, top_n//2)
        spacy_keywords = await self._extract_spacy_keywords(text, top_n//2)
        pattern_keywords = await self._extract_pattern_keywords(text, top_n//2)
        
        # Combine and score keywords
        all_keywords = tfidf_keywords + spacy_keywords + pattern_keywords
        keyword_counts = Counter(all_keywords)
        
        # Prioritize keywords that appear in multiple methods
        scored_keywords = []
        for keyword, count in keyword_counts.most_common():
            # Boost score for keywords found in multiple methods
            score = count
            if count > 1:
                score *= 1.5  # Boost for appearing in multiple methods
            
            # Boost technical skills
            if any(keyword in skills for skills in self.technical_skills.values()):
                score *= 1.3
            
            scored_keywords.append((keyword, score))
        
        # Sort by score and return top keywords
        scored_keywords.sort(key=lambda x: x[1], reverse=True)
        return [keyword for keyword, score in scored_keywords[:top_n]]
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract categorized skills from text."""
        text_lower = text.lower()
        categorized_skills = defaultdict(list)
        
        # Extract technical skills by category
        for category, skills in self.technical_skills.items():
            for skill in skills:
                if skill in text_lower:
                    categorized_skills[category].append(skill)
        
        # Extract soft skills
        for skill in self.soft_skills:
            if skill in text_lower:
                categorized_skills['soft_skills'].append(skill)
        
        # Convert defaultdict to regular dict
        return dict(categorized_skills)
    
    def calculate_skill_match(
        self, 
        resume_text: str, 
        job_description: str
    ) -> Dict[str, float]:
        """Calculate skill matching scores between resume and job description."""
        resume_skills = self.extract_skills(resume_text)
        job_skills = self.extract_skills(job_description)
        
        match_scores = {}
        
        for category in set(resume_skills.keys()) | set(job_skills.keys()):
            resume_cat_skills = set(resume_skills.get(category, []))
            job_cat_skills = set(job_skills.get(category, []))
            
            if not job_cat_skills:
                match_scores[category] = 0.0
            else:
                matches = resume_cat_skills & job_cat_skills
                match_scores[category] = len(matches) / len(job_cat_skills)
        
        return match_scores
    
    def extract_experience_keywords(self, text: str) -> Dict[str, List[str]]:
        """Extract experience-related keywords and metrics."""
        experience_keywords = {
            'action_verbs': [],
            'achievements': [],
            'technologies': [],
            'metrics': []
        }
        
        # Action verbs commonly used in resumes
        action_verbs = [
            'achieved', 'developed', 'implemented', 'managed', 'led', 'created',
            'improved', 'increased', 'reduced', 'optimized', 'delivered',
            'designed', 'built', 'established', 'launched', 'streamlined'
        ]
        
        text_lower = text.lower()
        
        # Extract action verbs
        for verb in action_verbs:
            if verb in text_lower:
                experience_keywords['action_verbs'].append(verb)
        
        # Extract metrics and achievements
        metric_patterns = [
            r'(\d+(?:\.\d+)?)\s*%',  # Percentages
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',  # Money amounts
            r'(\d+(?:,\d{3})*)\s*(users|customers|clients|people|employees)',  # Scale
            r'(\d+(?:\.\d+)?)\s*(million|billion|thousand|k|m|b)',  # Large numbers
            r'(\d+(?:\.\d+)?)\s*(years?|months?|weeks?)\s*(?:of\s*)?experience'  # Time
        ]
        
        for pattern in metric_patterns:
            matches = re.findall(pattern, text_lower)
            experience_keywords['metrics'].extend(matches)
        
        return experience_keywords
    
    def extract_job_requirements(self, job_description: str) -> Dict[str, List[str]]:
        """Extract structured requirements from job description."""
        requirements = {
            'required_skills': [],
            'preferred_skills': [],
            'experience_level': [],
            'education': [],
            'certifications': []
        }
        
        text_lower = job_description.lower()
        
        # Extract required vs preferred skills
        required_section = re.search(
            r'(required|must have|essential).*?(?=preferred|nice to have|plus|\Z)', 
            text_lower, re.DOTALL
        )
        
        if required_section:
            required_text = required_section.group()
            requirements['required_skills'] = await self.extract_keywords(required_text, top_n=20)
        
        preferred_section = re.search(
            r'(preferred|nice to have|plus|bonus).*?(?=required|must have|\Z)',
            text_lower, re.DOTALL
        )
        
        if preferred_section:
            preferred_text = preferred_section.group()
            requirements['preferred_skills'] = await self.extract_keywords(preferred_text, top_n=15)
        
        # Extract experience level
        exp_patterns = [
            r'(\d+)\+?\s*(?:to\s*\d+\s*)?years?\s*(?:of\s*)?experience',
            r'(entry|junior|senior|lead|principal|staff)\s*(?:level)?',
            r'(beginner|intermediate|advanced|expert)\s*level'
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, text_lower)
            requirements['experience_level'].extend(matches)
        
        # Extract education requirements
        education_patterns = [
            r'(bachelor|master|phd|doctorate|associate)\s*(?:degree|\'s)?',
            r'(bs|ba|ms|ma|mba|phd)\s*(?:in|degree)',
            r'college\s*(?:degree|graduate)'
        ]
        
        for pattern in education_patterns:
            matches = re.findall(pattern, text_lower)
            requirements['education'].extend(matches)
        
        return requirements
    
    def extract_generic_keywords(self) -> List[str]:
        """Return generic keywords when no job description is provided."""
        generic_keywords = []
        
        # Add common technical skills
        for category, skills in self.technical_skills.items():
            generic_keywords.extend(skills[:5])  # Top 5 from each category
        
        # Add common soft skills
        generic_keywords.extend(self.soft_skills[:10])
        
        # Add common business terms
        business_terms = [
            'project management', 'team leadership', 'problem solving',
            'communication', 'analysis', 'planning', 'strategy',
            'process improvement', 'customer service', 'quality assurance'
        ]
        generic_keywords.extend(business_terms)
        
        return generic_keywords[:30]  # Return top 30 generic keywords
