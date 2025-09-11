"""
ZeX-ATS-AI Text Processing Utilities
Advanced text cleaning, normalization, and preprocessing.
"""

import re
import string
from typing import List, Dict, Optional, Set
import unicodedata

# Optional imports with graceful fallback
try:
    import nltk  # type: ignore
    from nltk.corpus import stopwords  # type: ignore
    from nltk.tokenize import word_tokenize, sent_tokenize  # type: ignore
    from nltk.stem import WordNetLemmatizer  # type: ignore
except Exception:  # If NLTK missing, define simple fallbacks
    nltk = None  # type: ignore
    stopwords = None  # type: ignore
    WordNetLemmatizer = object  # type: ignore
    def word_tokenize(text):
        return re.findall(r"[A-Za-z']+", text)
    def sent_tokenize(text):
        return re.split(r'[.!?]\s+', text)

try:
    import spacy  # type: ignore
except Exception:
    spacy = None  # type: ignore

class TextProcessor:
    """Advanced text processing for resume analysis (degrades gracefully)."""
    
    def __init__(self):
        self._download_nltk_data()
        self.lemmatizer = WordNetLemmatizer() if nltk else None
        # spaCy optional
        if spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                try:
                    self.nlp = spacy.blank("en")
                except Exception:
                    self.nlp = None
        else:
            self.nlp = None
        if stopwords:
            try:
                self.stop_words = set(stopwords.words('english'))
            except Exception:
                self.stop_words = set()
        else:
            self.stop_words = set()
        self.resume_stopwords = {'resume','cv','curriculum','vitae','page','pages','references','available','upon','request'}
        self.all_stopwords = self.stop_words.union(self.resume_stopwords)
    
    def _download_nltk_data(self):
        if not nltk:
            return
        required = ['punkt','stopwords','wordnet','averaged_perceptron_tagger']
        for data in required:
            try:
                nltk.data.find(f'tokenizers/{data}')
            except LookupError:
                try:
                    nltk.download(data, quiet=True)
                except Exception:
                    pass
    
    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = unicodedata.normalize('NFKD', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        text = self._fix_encoding_issues(text)
        text = self._remove_pdf_artifacts(text)
        text = self._standardize_formatting(text)
        return text.strip()
    
    def _fix_encoding_issues(self, text: str) -> str:
        encoding_fixes = {
            'â€™': "'", 'â€œ': '"', 'â€': '"', 'â€¢': '•', 'â€"': '–', 'Â': '',
            'â\x80\x99': "'", 'â\x80\x9c': '"', 'â\x80\x9d': '"'
        }
        for bad, good in encoding_fixes.items():
            text = text.replace(bad, good)
        return text
    
    def _remove_pdf_artifacts(self, text: str) -> str:
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        text = re.sub(r'\n\s*Page\s+\d+\s*\n', '\n', text, re.IGNORECASE)
        text = re.sub(r'\n\s*[A-Z\s]{10,}\s*\n', '\n', text)
        text = re.sub(r'\n\s*_{3,}\s*\n', '\n', text)
        text = re.sub(r'\n\s*-{3,}\s*\n', '\n', text)
        text = re.sub(r'[•·‣⁃]\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
        return text
    
    def _standardize_formatting(self, text: str) -> str:
        text = re.sub(r'[•·‣⁃▪▫◦‣⁃]', '•', text)
        text = re.sub(r'[–—]', '-', text)
        text = re.sub(r'[“”"]', '"', text)
        text = re.sub(r"[‘’']", "'", text)  # fixed regex quoting issue
        text = re.sub(r'\s+([,.;:!?])', r'\1', text)
        text = re.sub(r'([,.;:!?])\s*([a-zA-Z])', r'\1 \2', text)
        text = re.sub(r'\s+@\s+', '@', text)
        text = re.sub(r'www\s*\.\s*', 'www.', text)
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        sentences = sent_tokenize(text)
        return [s.strip() for s in sentences if len(s.strip()) > 10 and not s.strip().isupper()]
    
    def extract_words(self, text: str, remove_stopwords: bool = True) -> List[str]:
        words = word_tokenize(text.lower())
        clean = []
        for w in words:
            if w.isalpha() and len(w) > 2 and (not remove_stopwords or w not in self.all_stopwords):
                clean.append(w)
        return clean
    
    def lemmatize_text(self, text: str) -> str:
        if not self.lemmatizer:
            return text.lower()
        words = word_tokenize(text.lower())
        return ' '.join(self.lemmatizer.lemmatize(w) for w in words if w.isalpha())
    
    def extract_phrases(self, text: str, min_length: int = 2, max_length: int = 4) -> List[str]:
        if not self.nlp or getattr(self.nlp, 'pipe_names', []) == []:
            return []
        doc = self.nlp(text)
        phrases = []
        for chunk in getattr(doc, 'noun_chunks', []):
            phrase = chunk.text.lower().strip()
            wc = len(phrase.split())
            if min_length <= wc <= max_length:
                phrases.append(phrase)
        for ent in getattr(doc, 'ents', []):
            if ent.label_ in ['ORG','PRODUCT','SKILL','TECHNOLOGY']:
                phrase = ent.text.lower().strip()
                wc = len(phrase.split())
                if min_length <= wc <= max_length:
                    phrases.append(phrase)
        return list(set(phrases))
    
    def calculate_text_stats(self, text: str) -> Dict[str, int]:
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        return {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'paragraph_count': len(text.split('\n\n')),
            'avg_words_per_sentence': len(words)/len(sentences) if sentences else 0,
            'avg_characters_per_word': len(text)/len(words) if words else 0,
            'unique_words': len(set(w.lower() for w in words if w.isalpha())),
            'vocabulary_richness': len(set(w.lower() for w in words if w.isalpha()))/len(words) if words else 0
        }
    
    def extract_technical_terms(self, text: str) -> List[str]:
        technical_terms = []
        acronyms = re.findall(r'\b[A-Z]{2,5}\b', text)
        technical_terms.extend(acronyms)
        tech_patterns = [
            r'\b(python|java|javascript|c\+\+|c#|php|ruby|go|rust|swift|kotlin)\b',
            r'\b(html|css|sql|nosql|mongodb|postgresql|mysql|redis)\b',
            r'\b(react|angular|vue|node\.js|django|flask|spring|laravel)\b',
            r'\b(aws|azure|gcp|docker|kubernetes|jenkins|git|ci/cd)\b',
            r'\b(machine learning|deep learning|ai|ml|nlp|cv|computer vision)\b',
            r'\b(agile|scrum|devops|microservices|api|rest|graphql)\b'
        ]
        for pattern in tech_patterns:
            technical_terms.extend(re.findall(pattern, text, re.IGNORECASE))
        return list(set(t.lower() for t in technical_terms))
    
    def normalize_job_titles(self, text: str) -> List[str]:
        title_patterns = [
            r'\b(senior|lead|principal|staff)\s+(engineer|developer|analyst|manager)\b',
            r'\b(software|data|systems|network|security)\s+(engineer|developer|analyst)\b',
            r'\b(project|product|engineering|technical)\s+manager\b',
            r'\b(full\s+stack|front\s+end|back\s+end)\s+(developer|engineer)\b',
            r'\b(data|business|systems|security)\s+analyst\b',
            r'\b(devops|site reliability)\s+engineer\b'
        ]
        job_titles = []
        for pattern in title_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            job_titles.extend([m if isinstance(m, str) else ' '.join(m) for m in matches])
        return list(set(j.lower().strip() for j in job_titles))
    
    def extract_contact_patterns(self, text: str) -> Dict[str, List[str]]:
        patterns = {
            'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phones': r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'linkedin': r'(?:linkedin\.com/in/|in/)[A-Za-z0-9-]+',
            'github': r'(?:github\.com/)[A-Za-z0-9-]+',
            'websites': r'https?://[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[^\s]*)?'
        }
        extracted = {}
        for key, pattern in patterns.items():
            extracted[key] = list(set(re.findall(pattern, text, re.IGNORECASE)))
        return extracted
