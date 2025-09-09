"""
ZeX-ATS-AI Text Cleaner Utilities
Advanced text cleaning and normalization for document processing.
"""

import re
import unicodedata
from typing import List, Dict, Optional, Set
import html


class TextCleaner:
    """Advanced text cleaning for resume processing."""
    
    def __init__(self):
        """Initialize text cleaner with patterns and rules."""
        # Common PDF artifacts patterns
        self.pdf_artifacts = [
            r'\f',  # Form feed characters
            r'[^\x00-\x7F]+',  # Non-ASCII artifacts (optional)
            r'(?m)^\s*Page\s+\d+\s*$',  # Page numbers
            r'(?m)^\s*\d+\s*$',  # Standalone numbers
            r'(?m)^\s*[_-]{3,}\s*$',  # Separator lines
        ]
        
        # Encoding fixes for common issues
        self.encoding_fixes = {
            'â€™': "'",  # Right single quotation mark
            'â€œ': '"',  # Left double quotation mark  
            'â€': '"',   # Right double quotation mark
            'â€¢': '•',  # Bullet point
            'â€"': '–',  # En dash
            'â€"': '—',  # Em dash
            'â€¦': '…',  # Ellipsis
            'Â': '',     # Non-breaking space artifacts
            'Ã¢â‚¬â„¢': "'",  # Another apostrophe variant
            'Ã¢â‚¬Å"': '"',  # Left quote variant
            'Ã¢â‚¬Â': '"',   # Right quote variant
        }
        
        # Bullet point standardization
        self.bullet_points = ['•', '·', '‣', '⁃', '▪', '▫', '◦', '‣', '⁃', '*', '-']
        
        # Common resume section headers for normalization
        self.section_headers = {
            'experience': ['experience', 'work experience', 'employment', 'work history', 'professional experience'],
            'education': ['education', 'educational background', 'academic background', 'qualifications'],
            'skills': ['skills', 'technical skills', 'core competencies', 'competencies', 'expertise'],
            'summary': ['summary', 'profile', 'professional summary', 'objective', 'career objective'],
            'projects': ['projects', 'key projects', 'notable projects', 'project experience'],
            'certifications': ['certifications', 'certificates', 'licenses', 'professional certifications']
        }
    
    def clean_text(self, text: str) -> str:
        """
        Comprehensive text cleaning pipeline.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Step 1: HTML entity decoding
        text = html.unescape(text)
        
        # Step 2: Unicode normalization
        text = unicodedata.normalize('NFKD', text)
        
        # Step 3: Fix encoding issues
        text = self._fix_encoding_issues(text)
        
        # Step 4: Remove PDF artifacts
        text = self._remove_pdf_artifacts(text)
        
        # Step 5: Normalize whitespace
        text = self._normalize_whitespace(text)
        
        # Step 6: Standardize punctuation
        text = self._standardize_punctuation(text)
        
        # Step 7: Fix broken words
        text = self._fix_broken_words(text)
        
        # Step 8: Normalize bullet points
        text = self._normalize_bullet_points(text)
        
        # Step 9: Clean up contact information
        text = self._clean_contact_info(text)
        
        # Step 10: Final cleanup
        text = self._final_cleanup(text)
        
        return text.strip()
    
    def _fix_encoding_issues(self, text: str) -> str:
        """Fix common encoding issues from PDF extraction."""
        for bad, good in self.encoding_fixes.items():
            text = text.replace(bad, good)
        
        # Fix smart quotes and apostrophes
        text = re.sub(r'["""]', '"', text)
        text = re.sub(r'[''']', "'", text)
        
        # Fix em and en dashes
        text = re.sub(r'[–—]', '-', text)
        
        # Fix ellipsis
        text = re.sub(r'…', '...', text)
        
        return text
    
    def _remove_pdf_artifacts(self, text: str) -> str:
        """Remove common PDF extraction artifacts."""
        # Remove form feed and other control characters
        text = re.sub(r'[\f\v\x0b\x0c]', '', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'(?m)^\s*Page\s+\d+(?:\s+of\s+\d+)?\s*$', '', text, re.IGNORECASE)
        text = re.sub(r'(?m)^\s*\d+\s*$', '', text)
        
        # Remove horizontal separators
        text = re.sub(r'(?m)^\s*[_-]{3,}\s*$', '', text)
        text = re.sub(r'(?m)^\s*[.]{3,}\s*$', '', text)
        
        # Remove repeated underscores or dashes used as lines
        text = re.sub(r'_{5,}', '', text)
        text = re.sub(r'-{5,}', '', text)
        
        # Remove standalone punctuation lines
        text = re.sub(r'(?m)^\s*[^\w\s]{1,5}\s*$', '', text)
        
        return text
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize all types of whitespace."""
        # Replace tabs with spaces
        text = text.replace('\t', ' ')
        
        # Normalize line breaks
        text = re.sub(r'\r\n|\r', '\n', text)
        
        # Remove excessive line breaks (more than 2)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove excessive spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove trailing spaces from lines
        text = re.sub(r' +$', '', text, flags=re.MULTILINE)
        
        # Remove leading spaces from lines (except for intentional indentation)
        text = re.sub(r'^[ ]{1,3}(?=\w)', '', text, flags=re.MULTILINE)
        
        return text
    
    def _standardize_punctuation(self, text: str) -> str:
        """Standardize punctuation marks."""
        # Fix spacing around punctuation
        text = re.sub(r'\s+([,.;:!?])', r'\1', text)
        text = re.sub(r'([,.;:!?])([a-zA-Z])', r'\1 \2', text)
        
        # Fix spacing around parentheses
        text = re.sub(r'\s+([)])', r'\1', text)
        text = re.sub(r'([(\[])\s+', r'\1', text)
        
        # Fix multiple punctuation marks
        text = re.sub(r'([.!?]){2,}', r'\1', text)
        text = re.sub(r'([,;:]){2,}', r'\1', text)
        
        # Standardize email and URL formatting
        text = re.sub(r'\s+@\s+', '@', text)
        text = re.sub(r'www\s*\.\s*', 'www.', text)
        
        return text
    
    def _fix_broken_words(self, text: str) -> str:
        """Fix words broken by line breaks during PDF extraction."""
        # Fix hyphenated words broken across lines
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # Fix words broken without hyphens
        text = re.sub(r'(\w{2,})\s*\n\s*([a-z]{2,})', r'\1\2', text)
        
        # Fix common broken technical terms
        broken_terms = {
            'Java Script': 'JavaScript',
            'Type Script': 'TypeScript', 
            'Post greSQL': 'PostgreSQL',
            'My SQL': 'MySQL',
            'Mongo DB': 'MongoDB',
            'Node js': 'Node.js',
            'React js': 'React.js',
            'Angular js': 'AngularJS'
        }
        
        for broken, fixed in broken_terms.items():
            text = re.sub(re.escape(broken), fixed, text, flags=re.IGNORECASE)
        
        return text
    
    def _normalize_bullet_points(self, text: str) -> str:
        """Normalize all bullet points to a standard format."""
        # Replace all variations of bullet points with standard bullet
        for bullet in self.bullet_points[1:]:  # Skip first (standard) bullet
            text = text.replace(bullet, '•')
        
        # Ensure proper spacing after bullet points
        text = re.sub(r'•\s*', '• ', text)
        
        # Fix bullet points at start of lines
        text = re.sub(r'(?m)^\s*•', '• ', text)
        
        return text
    
    def _clean_contact_info(self, text: str) -> str:
        """Clean and standardize contact information."""
        # Standardize phone numbers
        text = re.sub(r'[^\d\s\+\(\)-]', '', text)  # Keep only valid phone chars
        text = re.sub(r'(\d{3})\s*[-.]?\s*(\d{3})\s*[-.]?\s*(\d{4})', 
                     r'\1-\2-\3', text)
        
        # Clean email addresses
        text = re.sub(r'(\w+)\s*@\s*(\w+)', r'\1@\2', text)
        
        # Clean LinkedIn URLs
        text = re.sub(r'linkedin\s*\.\s*com\s*/\s*in\s*/\s*', 
                     'linkedin.com/in/', text, flags=re.IGNORECASE)
        
        return text
    
    def _final_cleanup(self, text: str) -> str:
        """Final cleanup pass."""
        # Remove empty lines at start and end
        text = text.strip()
        
        # Ensure single space between words
        text = re.sub(r'(\w)\s+(\w)', r'\1 \2', text)
        
        # Remove any remaining artifacts
        text = re.sub(r'[^\w\s\n.,;:!?()[\]{}@#$%^&*+=|\\<>"\'-/]', '', text)
        
        # Ensure consistent line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text
    
    def extract_clean_sections(self, text: str) -> Dict[str, str]:
        """Extract and clean individual sections from resume text."""
        sections = {}
        text_lower = text.lower()
        
        for standard_name, variations in self.section_headers.items():
            for variation in variations:
                pattern = rf'(?i)\b{re.escape(variation)}\b.*?(?=(?:\b(?:{")|(?:".join([re.escape(h) for headers in self.section_headers.values() for h in headers])}))\b|\Z)'
                match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                
                if match:
                    section_text = match.group()
                    # Remove the header itself
                    section_text = re.sub(rf'(?i)^.*?\b{re.escape(variation)}\b[^\n]*\n?', '', section_text)
                    sections[standard_name] = self._clean_section_text(section_text.strip())
                    break
        
        return sections
    
    def _clean_section_text(self, section_text: str) -> str:
        """Clean individual section text."""
        if not section_text:
            return ""
        
        # Remove excessive bullet points
        section_text = re.sub(r'•\s*•+', '•', section_text)
        
        # Clean up spacing in lists
        section_text = re.sub(r'(?m)^•\s*$', '', section_text)
        
        # Remove empty bullet points
        section_text = re.sub(r'(?m)^•\s*\n', '', section_text)
        
        # Ensure proper paragraph separation
        section_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', section_text)
        
        return section_text.strip()
    
    def remove_personal_info(self, text: str, preserve_contact: bool = False) -> str:
        """Remove or mask personal information for privacy."""
        if preserve_contact:
            return text
        
        # Mask email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                     '[EMAIL]', text)
        
        # Mask phone numbers
        text = re.sub(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', 
                     '[PHONE]', text)
        
        # Mask addresses (basic pattern)
        text = re.sub(r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Boulevard|Blvd)', 
                     '[ADDRESS]', text, flags=re.IGNORECASE)
        
        return text
    
    def validate_cleaned_text(self, original: str, cleaned: str) -> Dict[str, any]:
        """Validate that text cleaning preserved important information."""
        original_words = len(original.split())
        cleaned_words = len(cleaned.split())
        
        # Calculate preservation ratio
        preservation_ratio = cleaned_words / original_words if original_words > 0 else 0
        
        # Check for important sections
        important_keywords = ['experience', 'education', 'skills', 'summary']
        preserved_keywords = sum(1 for keyword in important_keywords 
                               if keyword in cleaned.lower())
        
        return {
            'original_length': len(original),
            'cleaned_length': len(cleaned),
            'word_preservation_ratio': preservation_ratio,
            'preserved_sections': preserved_keywords,
            'is_valid': preservation_ratio > 0.7 and preserved_keywords >= 2,
            'warnings': self._generate_cleaning_warnings(original, cleaned)
        }
    
    def _generate_cleaning_warnings(self, original: str, cleaned: str) -> List[str]:
        """Generate warnings about potential issues in cleaning."""
        warnings = []
        
        original_words = len(original.split())
        cleaned_words = len(cleaned.split())
        
        if cleaned_words < original_words * 0.5:
            warnings.append("Significant text loss detected during cleaning")
        
        if len(cleaned) < 100:
            warnings.append("Cleaned text is very short, may indicate extraction issues")
        
        # Check for missing email/phone after cleaning
        if '@' in original and '@' not in cleaned:
            warnings.append("Email address may have been removed during cleaning")
        
        # Check for excessive line breaks
        if cleaned.count('\n') > original.count('\n') * 1.5:
            warnings.append("Excessive line breaks in cleaned text")
        
        return warnings
