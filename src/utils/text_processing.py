"""
ZeX-ATS-AI Text Processing Utilities
Advanced text cleaning, normalization, and preprocessing.
"""

import re
import string
from typing import List, Dict, Optional, Set
import unicodedata

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
import spacy


class TextProcessor:
    """Advanced text processing for resume analysis."""
    
    def __init__(self):
        """Initialize text processor with NLP tools."""
        # Download required NLTK data
        self._download_nltk_data()
        
        # Initialize lemmatizer
        self.lemmatizer = WordNetLemmatizer()
        
        # Load spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Some features may be limited.")
            self.nlp = None
        
        # English stopwords
        self.stop_words = set(stopwords.words('english'))
        
        # Common resume stopwords to remove
        self.resume_stopwords = {
            'resume', 'cv', 'curriculum', 'vitae', 'page', 'pages',
            'references', 'available', 'upon', 'request'
        }
        
        # Combine stopwords
        self.all_stopwords = self.stop_words.union(self.resume_stopwords)
    
    def _download_nltk_data(self):
        """Download required NLTK data."""
        required_data = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger']
        for data in required_data:
            try:
                nltk.data.find(f'tokenizers/{data}')
            except LookupError:
                try:
                    nltk.download(data, quiet=True)
                except:
                    pass
    
    def clean_text(self, text: str) -> str:
        """
        Comprehensive text cleaning for resume analysis.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        # Fix common encoding issues
        text = self._fix_encoding_issues(text)
        
        # Remove PDF artifacts and OCR errors
        text = self._remove_pdf_artifacts(text)
        
        # Standardize formatting
        text = self._standardize_formatting(text)
        
        return text.strip()
    
    def _fix_encoding_issues(self, text: str) -> str:
        """Fix common encoding issues in extracted text."""
        # Common encoding fixes
        encoding_fixes = {
            'â€™': "'",  # Right single quotation mark
            'â€œ': '"',  # Left double quotation mark
            'â€': '"',   # Right double quotation mark
            'â€¢': '•',  # Bullet point
            'â€"': '–',  # En dash
            'â€"': '—',  # Em dash
            'Â': '',     # Non-breaking space artifacts
            'â\x80\x99': "'",  # Another apostrophe variant
            'â\x80\x9c': '"',  # Left quote variant
            'â\x80\x9d': '"',  # Right quote variant
        }
        
        for bad, good in encoding_fixes.items():
            text = text.replace(bad, good)
        
        return text
    
    def _remove_pdf_artifacts(self, text: str) -> str:
        """Remove common PDF extraction artifacts."""
        # Remove page numbers
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        text = re.sub(r'\n\s*Page\s+\d+\s*\n', '\n', text, re.IGNORECASE)
        
        # Remove header/footer artifacts
        text = re.sub(r'\n\s*[A-Z\s]{10,}\s*\n', '\n', text)  # All caps headers
        text = re.sub(r'\n\s*_{3,}\s*\n', '\n', text)  # Underline separators
        text = re.sub(r'\n\s*-{3,}\s*\n', '\n', text)  # Dash separators
        
        # Remove extra bullet point artifacts
        text = re.sub(r'[•·‣⁃]\s*$', '', text, flags=re.MULTILINE)
        
        # Fix broken words (common in PDF extraction)
        text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
        
        return text
    
    def _standardize_formatting(self, text: str) -> str:
        """Standardize text formatting."""
        # Standardize bullet points
        text = re.sub(r'[•·‣⁃▪▫◦‣⁃]', '•', text)
        
        # Standardize dashes
        text = re.sub(r'[–—]', '-', text)
        
        # Standardize quotes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r'[''']', "'", text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([,.;:!?])', r'\1', text)
        text = re.sub(r'([,.;:!?])\s*([a-zA-Z])', r'\1 \2', text)
        
        # Standardize email and URL formatting
        text = re.sub(r'\s+@\s+', '@', text)
        text = re.sub(r'www\s*\.\s*', 'www.', text)
        
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """Extract clean sentences from text."""
        sentences = sent_tokenize(text)
        
        # Clean sentences
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and not sentence.isupper():  # Filter out headers
                clean_sentences.append(sentence)
        
        return clean_sentences
    
    def extract_words(self, text: str, remove_stopwords: bool = True) -> List[str]:
        """Extract and clean words from text."""
        # Tokenize
        words = word_tokenize(text.lower())
        
        # Filter words
        clean_words = []
        for word in words:
            # Keep only alphabetic words with length > 2
            if (word.isalpha() and 
                len(word) > 2 and 
                (not remove_stopwords or word not in self.all_stopwords)):
                clean_words.append(word)
        
        return clean_words
    
    def lemmatize_text(self, text: str) -> str:
        """Lemmatize text for better analysis."""
        words = word_tokenize(text.lower())
        lemmatized = [self.lemmatizer.lemmatize(word) for word in words if word.isalpha()]
        return ' '.join(lemmatized)
    
    def extract_phrases(self, text: str, min_length: int = 2, max_length: int = 4) -> List[str]:
        """Extract meaningful phrases using NLP."""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        phrases = []
        
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            phrase = chunk.text.lower().strip()
            word_count = len(phrase.split())
            if min_length <= word_count <= max_length:
                phrases.append(phrase)
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'SKILL', 'TECHNOLOGY']:
                phrase = ent.text.lower().strip()
                if min_length <= len(phrase.split()) <= max_length:
                    phrases.append(phrase)
        
        return list(set(phrases))  # Remove duplicates
    
    def calculate_text_stats(self, text: str) -> Dict[str, int]:
        """Calculate comprehensive text statistics."""
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        
        return {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'paragraph_count': len(text.split('\n\n')),
            'avg_words_per_sentence': len(words) / len(sentences) if sentences else 0,
            'avg_characters_per_word': len(text) / len(words) if words else 0,
            'unique_words': len(set(word.lower() for word in words if word.isalpha())),
            'vocabulary_richness': len(set(word.lower() for word in words if word.isalpha())) / len(words) if words else 0
        }
    
    def extract_technical_terms(self, text: str) -> List[str]:
        """Extract technical terms and acronyms."""
        technical_terms = []
        
        # Extract acronyms (2-5 uppercase letters)
        acronyms = re.findall(r'\b[A-Z]{2,5}\b', text)
        technical_terms.extend(acronyms)
        
        # Extract programming languages and technologies
        tech_patterns = [
            r'\b(python|java|javascript|c\+\+|c#|php|ruby|go|rust|swift|kotlin)\b',
            r'\b(html|css|sql|nosql|mongodb|postgresql|mysql|redis)\b',
            r'\b(react|angular|vue|node\.js|django|flask|spring|laravel)\b',
            r'\b(aws|azure|gcp|docker|kubernetes|jenkins|git|ci/cd)\b',
            r'\b(machine learning|deep learning|ai|ml|nlp|cv|computer vision)\b',
            r'\b(agile|scrum|devops|microservices|api|rest|graphql)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            technical_terms.extend(matches)
        
        # Remove duplicates and return
        return list(set([term.lower() for term in technical_terms]))
    
    def normalize_job_titles(self, text: str) -> List[str]:
        """Extract and normalize job titles."""
        # Common job title patterns
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
            job_titles.extend([match if isinstance(match, str) else ' '.join(match) for match in matches])
        
        return list(set([title.lower().strip() for title in job_titles]))
    
    def extract_contact_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract various contact information patterns."""
        patterns = {
            'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phones': r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'linkedin': r'(?:linkedin\.com/in/|in/)[A-Za-z0-9-]+',
            'github': r'(?:github\.com/)[A-Za-z0-9-]+',
            'websites': r'https?://[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[^\s]*)?'
        }
        
        extracted = {}
        for key, pattern in patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            extracted[key] = list(set(matches))
        
        return extracted
