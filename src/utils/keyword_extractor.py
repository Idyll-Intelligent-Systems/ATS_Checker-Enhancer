"""
ZeX-ATS-AI Keyword Extraction Utilities
Advanced keyword and skill extraction using NLP and machine learning.
Lightweight fallback version: all heavy dependencies (spaCy, NLTK, scikit-learn)
are optional. If missing, the extractor degrades gracefully to simple pattern
and dictionary based extraction so the unified API can run in low-resource
environments.
"""

import re
from typing import List, Dict, Set, Optional, Tuple
from collections import Counter, defaultdict

# Optional imports -----------------------------------------------------------
try:  # spaCy
    import spacy  # type: ignore
except Exception:  # pragma: no cover
    spacy = None  # type: ignore

try:  # NLTK stopwords
    import nltk  # type: ignore
    from nltk.corpus import stopwords  # type: ignore
except Exception:  # pragma: no cover
    nltk = None  # type: ignore
    stopwords = None  # type: ignore

try:  # scikit-learn TF-IDF
    from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
except Exception:  # pragma: no cover
    TfidfVectorizer = None  # type: ignore

try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore

from src.core.config import settings


class KeywordExtractor:
    """Advanced keyword extraction for resume and job description analysis (with graceful fallback)."""

    def __init__(self):
        # spaCy model (optional)
        self.nlp = None
        if spacy:
            for model in ["en_core_web_lg", "en_core_web_sm"]:
                try:
                    self.nlp = spacy.load(model)  # type: ignore
                    break
                except Exception:
                    continue
            if self.nlp is None:
                try:
                    self.nlp = spacy.blank("en")  # type: ignore
                except Exception:
                    pass
        # TF-IDF (optional)
        if TfidfVectorizer:
            self.tfidf = TfidfVectorizer(
                max_features=500,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.85
            )
        else:
            self.tfidf = None
        # Skill databases
        self.technical_skills = self._load_technical_skills()
        self.soft_skills = self._load_soft_skills()
        self.industry_keywords = self._load_industry_keywords()
        # Stop words
        if stopwords:
            try:
                # Ensure resource downloaded
                try:
                    stopwords.words('english')
                except Exception:
                    nltk.download('stopwords')  # type: ignore
                sw = set(stopwords.words('english'))  # type: ignore
            except Exception:
                sw = set()
        else:
            sw = {"the","and","for","with","from","that","this","your","have","has","are","was","were","will","can"}
        self.resume_stop_words = {
            'resume', 'cv', 'experience', 'education', 'skills', 'objective',
            'summary', 'references', 'available', 'upon', 'request', 'page'
        }
        self.all_stop_words = sw.union(self.resume_stop_words)

    # ------------------------------ Loaders ---------------------------------
    def _load_technical_skills(self) -> Dict[str, List[str]]:
        return {
            'programming_languages': ['python','java','javascript','typescript','c++','c#','go','rust','swift','kotlin','scala','r','php','ruby'],
            'web_technologies': ['html','css','react','angular','vue','node.js','express','django','flask','spring','jquery'],
            'databases': ['sql','mysql','postgresql','mongodb','redis','sqlite','dynamodb'],
            'cloud_platforms': ['aws','azure','gcp','google cloud','heroku','digitalocean','terraform','ansible'],
            'devops_tools': ['docker','kubernetes','jenkins','git','github','gitlab','ci/cd','prometheus','grafana'],
            'data_science': ['machine learning','deep learning','data science','data analysis','pandas','numpy','scikit-learn','tensorflow','pytorch','spark'],
            'methodologies': ['agile','scrum','kanban','devops','microservices']
        }

    def _load_soft_skills(self) -> List[str]:
        return ['leadership','communication','teamwork','collaboration','problem solving','analytical thinking','creativity','adaptability','time management','mentoring','presentation','strategic planning']

    def _load_industry_keywords(self) -> Dict[str, List[str]]:
        return {
            'technology': ['software development','system architecture','security','testing','integration','automation'],
            'finance': ['financial analysis','risk management','portfolio','trading','compliance'],
            'healthcare': ['patient care','medical records','hipaa','telemedicine'],
        }

    # --------------------------- Public Methods -----------------------------
    async def extract_keywords(self, text: str, method: str = 'hybrid', top_n: int = 50) -> List[str]:
        if not text.strip():
            return []
        if method == 'tfidf':
            return await self._extract_tfidf_keywords(text, top_n)
        if method == 'spacy':
            return await self._extract_spacy_keywords(text, top_n)
        if method == 'pattern':
            return await self._extract_pattern_keywords(text, top_n)
        return await self._extract_hybrid_keywords(text, top_n)

    async def _extract_tfidf_keywords(self, text: str, top_n: int) -> List[str]:
        if not self.tfidf:
            return await self._extract_pattern_keywords(text, top_n)
        try:
            matrix = self.tfidf.fit_transform([text])
            feats = self.tfidf.get_feature_names_out()
            scores = matrix.toarray()[0]
            pairs = sorted(zip(feats, scores), key=lambda x: x[1], reverse=True)
            return [k for k,s in pairs[:top_n] if s > 0]
        except Exception:
            return await self._extract_pattern_keywords(text, top_n)

    async def _extract_spacy_keywords(self, text: str, top_n: int) -> List[str]:
        if not self.nlp:
            return await self._extract_pattern_keywords(text, top_n)
        try:
            doc = self.nlp(text)
            kws = []
            for ent in getattr(doc, 'ents', []):
                if ent.label_ in ['ORG','PRODUCT','TECHNOLOGY']:
                    kws.append(ent.text.lower())
            for chunk in getattr(doc, 'noun_chunks', []):
                if len(chunk.text.split()) <= 3:
                    kws.append(chunk.text.lower())
            for token in doc:
                if token.is_alpha and not token.is_stop and token.pos_ in ['NOUN','PROPN']:
                    kws.append(token.lemma_.lower())
            counts = Counter(kws)
            return [k for k,_ in counts.most_common(top_n)]
        except Exception:
            return await self._extract_pattern_keywords(text, top_n)

    async def _extract_pattern_keywords(self, text: str, top_n: int) -> List[str]:
        text_lower = text.lower()
        kws = []
        for skills in self.technical_skills.values():
            for s in skills:
                if s in text_lower:
                    kws.append(s)
        for s in self.soft_skills:
            if s in text_lower:
                kws.append(s)
        prog_patterns = [
            r'\b(python|java|javascript|typescript|c\+\+|c#)\b',
            r'\b(sql|mysql|postgresql|mongodb)\b',
            r'\b(react|angular|vue)\b',
            r'\b(aws|azure|gcp)\b'
        ]
        for p in prog_patterns:
            for m in re.findall(p, text_lower, re.IGNORECASE):
                if isinstance(m, tuple):
                    for part in m:
                        if part:
                            kws.append(part.lower())
                else:
                    kws.append(m.lower())
        acronyms = re.findall(r'\b[A-Z]{2,5}\b', text)
        kws.extend([a.lower() for a in acronyms])
        counts = Counter(kws)
        return [k for k,_ in counts.most_common(top_n)]

    async def _extract_hybrid_keywords(self, text: str, top_n: int) -> List[str]:
        part = max(5, top_n // 3)
        combined = (
            await self._extract_tfidf_keywords(text, part) +
            await self._extract_spacy_keywords(text, part) +
            await self._extract_pattern_keywords(text, part)
        )
        counts = Counter(combined)
        return [k for k,_ in counts.most_common(top_n)]

    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        text_lower = text.lower()
        out = defaultdict(list)
        for cat, skills in self.technical_skills.items():
            for s in skills:
                if s in text_lower:
                    out[cat].append(s)
        for s in self.soft_skills:
            if s in text_lower:
                out['soft_skills'].append(s)
        return dict(out)

    def calculate_skill_match(self, resume_text: str, job_description: str) -> Dict[str, float]:
        resume = self.extract_skills(resume_text)
        job = self.extract_skills(job_description)
        scores = {}
        for cat in set(resume.keys()) | set(job.keys()):
            r = set(resume.get(cat, []))
            j = set(job.get(cat, []))
            scores[cat] = len(r & j) / len(j) if j else 0.0
        return scores

    def extract_experience_keywords(self, text: str) -> Dict[str, List[str]]:
        out = {'action_verbs': [], 'achievements': [], 'technologies': [], 'metrics': []}
        verbs = ['achieved','developed','implemented','managed','led','created','improved','increased','optimized','delivered']
        tl = text.lower()
        for v in verbs:
            if v in tl:
                out['action_verbs'].append(v)
        metric_patterns = [r'(\d+(?:\.\d+)?)\s*%', r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)']
        for p in metric_patterns:
            for m in re.findall(p, tl):
                out['metrics'].append(m if isinstance(m, str) else ' '.join(m))
        return out

    def extract_job_requirements(self, job_description: str) -> Dict[str, List[str]]:
        """Lightweight extraction of job requirements (synchronous, no awaits)."""
        req = {'required_skills': [], 'preferred_skills': [], 'experience_level': [], 'education': [], 'certifications': []}
        text_lower = job_description.lower()
        # Simple segmentation
        required_match = re.search(r'(required|must have|essential)(.*?)(preferred|nice to have|plus|bonus|$)', text_lower, re.DOTALL)
        if required_match:
            segment = required_match.group(2)
            req['required_skills'] = [w for w in set(segment.split()) if len(w) > 4][:20]
        preferred_match = re.search(r'(preferred|nice to have|plus|bonus)(.*)$', text_lower, re.DOTALL)
        if preferred_match:
            seg = preferred_match.group(2)
            req['preferred_skills'] = [w for w in set(seg.split()) if len(w) > 4][:15]
        exp_patterns = [r'(\d+)\+?\s*years?', r'(entry|junior|senior|lead|principal|staff)']
        for p in exp_patterns:
            req['experience_level'].extend([m if isinstance(m, str) else ' '.join(m) for m in re.findall(p, text_lower)])
        edu_patterns = [r'(bachelor|master|phd|doctorate|associate)', r'(bs|ba|ms|ma|mba|phd)']
        for p in edu_patterns:
            req['education'].extend([m if isinstance(m, str) else ' '.join(m) for m in re.findall(p, text_lower)])
        return req

    def extract_generic_keywords(self) -> List[str]:
        generic = []
        for _, skills in self.technical_skills.items():
            generic.extend(skills[:3])
        generic.extend(self.soft_skills[:8])
        business_terms = ['project management','team leadership','problem solving','communication','analysis','planning','strategy']
        generic.extend(business_terms)
        # Deduplicate preserve order
        seen = set(); ordered = []
        for k in generic:
            if k not in seen:
                seen.add(k); ordered.append(k)
        return ordered[:30]
