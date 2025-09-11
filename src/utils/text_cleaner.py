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
        # Flatten all variations for section extraction regex
        self._all_section_variations = [h for v in self.section_headers.values() for h in v]
    
    def clean_text(self, text: str) -> str:
        """Comprehensive text cleaning pipeline."""
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
        
        # Replace smart / curly double quotes with standard
        text = re.sub(r'[“”]', '"', text)
        # Replace smart / curly single quotes / apostrophes with standard
        text = re.sub(r'[‘’´`]', "'", text)
        # Normalize any stray repeated quotes
        text = re.sub(r'"{2,}', '"', text)
        text = re.sub(r"'{2,}", "'", text)
        
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
        
        # Remove any remaining artifacts (allow common punctuation & bullet)
        text = re.sub(r"[^A-Za-z0-9\s\n\.,;:!\?\(\)\[\]\{@#\$%\^&\*\+=\|\\<>\'\"/\-•]", '', text)
        
        # Ensure consistent line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text
    
    def extract_clean_sections(self, text: str) -> Dict[str, str]:
        """Extract and clean individual sections from resume text."""
        sections = {}
        if not text:
            return sections
        
        # Build combined header regex once
        header_pattern = r'(?:' + '|'.join([re.escape(h) for h in self._all_section_variations]) + r')'
        for standard_name, variations in self.section_headers.items():
            for variation in variations:
                # Non-greedy capture until next header or end
                pattern = re.compile(rf'(?is)\b{re.escape(variation)}\b(.*?)(?=\b{header_pattern}\b|\Z)')
                match = pattern.search(text)
                if match:
                    section_text = match.group(1)
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
        """Mask personal information unless preservation requested.
        Args:
            text: Input resume text.
            preserve_contact: If True, leaves contact details intact.
        Returns:
            Text with personal identifiers masked.
        """
        if preserve_contact or not text:
            return text
        # Emails
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '[EMAIL]', text)
        # Phone numbers (various international/common US formats)
        phone_pattern = (r"""\b(?:\+?\d{1,3}[\s.-]*)?  # Country code
                           (?:\(?\d{3}\)?[\s.-]*)      # Area code
                           \d{3}[\s.-]*\d{4}\b""")
        text = re.sub(phone_pattern, '[PHONE]', text, flags=re.VERBOSE)
        # LinkedIn / GitHub profiles
        text = re.sub(r'\b(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+/?', '[LINKEDIN]', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_.-]+/?', '[GITHUB]', text, flags=re.IGNORECASE)
        # Simple street addresses
        text = re.sub(r'\b\d{1,5}\s+[A-ZaL
