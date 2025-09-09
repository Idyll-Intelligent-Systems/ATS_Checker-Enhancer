"""
ZeX-ATS-AI File Validator
Enterprise-grade file validation and security checks.
"""

import io
import magic
from typing import BinaryIO, Optional, List, Dict, Tuple
from dataclasses import dataclass
from pathlib import Path
import hashlib

from src.core.config import settings


@dataclass
class ValidationResult:
    """File validation result."""
    is_valid: bool
    file_type: str
    file_size: int
    mime_type: str
    error_message: Optional[str] = None
    warnings: List[str] = None
    security_score: float = 1.0
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class FileValidator:
    """Enterprise file validation with security checks."""
    
    def __init__(self):
        """Initialize file validator with security rules."""
        self.max_file_size = settings.max_file_size_mb * 1024 * 1024  # Convert to bytes
        self.allowed_extensions = set(settings.supported_formats)
        
        # MIME type mappings for security
        self.safe_mime_types = {
            '.pdf': ['application/pdf'],
            '.doc': ['application/msword'],
            '.docx': [
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            ],
            '.txt': ['text/plain'],
            '.rtf': ['application/rtf', 'text/rtf']
        }
        
        # Security patterns to check for
        self.security_patterns = [
            b'<script',  # JavaScript
            b'javascript:',  # JavaScript protocol
            b'vbscript:',  # VBScript
            b'onload=',  # Event handlers
            b'onclick=',  # Event handlers
            b'<?php',  # PHP code
            b'<%',  # ASP code
            b'<object',  # Object embedding
            b'<embed',  # Embed tags
            b'<iframe',  # Iframe tags
        ]
        
        # Suspicious file patterns
        self.suspicious_patterns = [
            b'\x00' * 100,  # Null byte padding
            b'\xFF' * 100,  # FF byte padding
            b'JFIF' + b'\x00' * 50,  # Image headers in documents
            b'PNG' + b'\x00' * 50,   # Image headers in documents
        ]
    
    async def validate_file(
        self, 
        file_content: BinaryIO, 
        filename: str
    ) -> ValidationResult:
        """
        Comprehensive file validation with security checks.
        
        Args:
            file_content: Binary file content
            filename: Original filename
            
        Returns:
            ValidationResult with validation details and security assessment
        """
        # Reset file pointer
        file_content.seek(0)
        
        # Basic validation
        file_extension = Path(filename).suffix.lower()
        file_data = file_content.read()
        file_size = len(file_data)
        
        # Reset file pointer
        file_content.seek(0)
        
        # Check file extension
        if file_extension not in self.allowed_extensions:
            return ValidationResult(
                is_valid=False,
                file_type=file_extension,
                file_size=file_size,
                mime_type='unknown',
                error_message=f"Unsupported file type: {file_extension}"
            )
        
        # Check file size
        if file_size > self.max_file_size:
            return ValidationResult(
                is_valid=False,
                file_type=file_extension,
                file_size=file_size,
                mime_type='unknown',
                error_message=f"File too large: {file_size / 1024 / 1024:.1f}MB (max: {settings.max_file_size_mb}MB)"
            )
        
        # Check minimum file size
        if file_size < 100:  # Less than 100 bytes
            return ValidationResult(
                is_valid=False,
                file_type=file_extension,
                file_size=file_size,
                mime_type='unknown',
                error_message="File is too small or empty"
            )
        
        # Detect MIME type
        mime_type = await self._detect_mime_type(file_data)
        
        # Validate MIME type
        mime_validation = self._validate_mime_type(file_extension, mime_type)
        if not mime_validation['is_valid']:
            return ValidationResult(
                is_valid=False,
                file_type=file_extension,
                file_size=file_size,
                mime_type=mime_type,
                error_message=mime_validation['error']
            )
        
        # Security checks
        security_result = await self._perform_security_checks(file_data, file_extension)
        
        # File structure validation
        structure_result = await self._validate_file_structure(file_data, file_extension)
        
        # Combine validation results
        warnings = []
        warnings.extend(security_result.get('warnings', []))
        warnings.extend(structure_result.get('warnings', []))
        
        is_valid = (
            security_result['is_secure'] and 
            structure_result['is_valid'] and
            security_result['security_score'] > 0.5
        )
        
        error_message = None
        if not is_valid:
            if not security_result['is_secure']:
                error_message = "Security validation failed"
            elif not structure_result['is_valid']:
                error_message = structure_result.get('error', "File structure validation failed")
            else:
                error_message = "File failed security assessment"
        
        return ValidationResult(
            is_valid=is_valid,
            file_type=file_extension,
            file_size=file_size,
            mime_type=mime_type,
            error_message=error_message,
            warnings=warnings,
            security_score=security_result['security_score']
        )
    
    async def _detect_mime_type(self, file_data: bytes) -> str:
        """Detect MIME type using python-magic."""
        try:
            # Use python-magic to detect MIME type
            mime_type = magic.from_buffer(file_data, mime=True)
            return mime_type
        except Exception:
            # Fallback to basic detection based on file signature
            return self._detect_mime_by_signature(file_data)
    
    def _detect_mime_by_signature(self, file_data: bytes) -> str:
        """Detect MIME type by file signature (magic bytes)."""
        if file_data.startswith(b'%PDF'):
            return 'application/pdf'
        elif file_data.startswith(b'PK\x03\x04'):  # ZIP-based formats (DOCX, etc.)
            # Check for DOCX
            if b'word/' in file_data[:1000]:
                return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            return 'application/zip'
        elif file_data.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):  # OLE2 (DOC)
            return 'application/msword'
        elif file_data.startswith((b'{\rtf', b'{\\rtf')):  # RTF
            return 'application/rtf'
        else:
            # Try to detect if it's plain text
            try:
                file_data.decode('utf-8')
                return 'text/plain'
            except UnicodeDecodeError:
                try:
                    file_data.decode('latin-1')
                    return 'text/plain'
                except UnicodeDecodeError:
                    return 'application/octet-stream'
    
    def _validate_mime_type(self, file_extension: str, mime_type: str) -> Dict[str, any]:
        """Validate MIME type matches file extension."""
        expected_mimes = self.safe_mime_types.get(file_extension, [])
        
        if not expected_mimes:
            return {'is_valid': True, 'warning': f"No MIME validation for {file_extension}"}
        
        if mime_type in expected_mimes:
            return {'is_valid': True}
        
        # Some tolerance for common variations
        tolerance_map = {
            'application/octet-stream': ['application/pdf', 'application/msword'],
            'text/plain': ['application/rtf'],
        }
        
        if mime_type in tolerance_map:
            for expected in expected_mimes:
                if expected in tolerance_map[mime_type]:
                    return {'is_valid': True, 'warning': f"MIME type tolerance applied: {mime_type}"}
        
        return {
            'is_valid': False,
            'error': f"MIME type {mime_type} doesn't match extension {file_extension}"
        }
    
    async def _perform_security_checks(self, file_data: bytes, file_extension: str) -> Dict[str, any]:
        """Perform comprehensive security checks on file content."""
        security_score = 1.0
        warnings = []
        is_secure = True
        
        # Check for malicious patterns
        for pattern in self.security_patterns:
            if pattern in file_data:
                security_score -= 0.3
                warnings.append(f"Suspicious content pattern detected")
                if security_score < 0.5:
                    is_secure = False
        
        # Check for suspicious file structure patterns
        for pattern in self.suspicious_patterns:
            if pattern in file_data:
                security_score -= 0.2
                warnings.append("Suspicious file structure detected")
        
        # Check file entropy (detect encrypted/compressed malware)
        entropy = self._calculate_entropy(file_data)
        if entropy > 7.5:  # High entropy might indicate encryption/compression
            security_score -= 0.1
            warnings.append("High file entropy detected")
        
        # PDF-specific security checks
        if file_extension == '.pdf':
            pdf_checks = self._check_pdf_security(file_data)
            security_score *= pdf_checks['score']
            warnings.extend(pdf_checks['warnings'])
            if not pdf_checks['is_safe']:
                is_secure = False
        
        # Office document security checks
        elif file_extension in ['.doc', '.docx']:
            office_checks = self._check_office_security(file_data)
            security_score *= office_checks['score']
            warnings.extend(office_checks['warnings'])
            if not office_checks['is_safe']:
                is_secure = False
        
        return {
            'is_secure': is_secure,
            'security_score': max(0.0, security_score),
            'warnings': warnings
        }
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of file data."""
        if not data:
            return 0
        
        # Count byte frequencies
        frequencies = {}
        for byte in data:
            frequencies[byte] = frequencies.get(byte, 0) + 1
        
        # Calculate entropy
        import math
        entropy = 0.0
        data_len = len(data)
        
        for count in frequencies.values():
            probability = count / data_len
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _check_pdf_security(self, file_data: bytes) -> Dict[str, any]:
        """PDF-specific security checks."""
        score = 1.0
        warnings = []
        is_safe = True
        
        # Check for JavaScript in PDF
        if b'/JS' in file_data or b'/JavaScript' in file_data:
            score -= 0.5
            warnings.append("PDF contains JavaScript")
            is_safe = False
        
        # Check for embedded files
        if b'/EmbeddedFile' in file_data:
            score -= 0.3
            warnings.append("PDF contains embedded files")
        
        # Check for forms
        if b'/AcroForm' in file_data:
            score -= 0.1
            warnings.append("PDF contains forms")
        
        # Check for actions
        if b'/OpenAction' in file_data or b'/AA' in file_data:
            score -= 0.3
            warnings.append("PDF contains automatic actions")
        
        return {
            'score': max(0.0, score),
            'warnings': warnings,
            'is_safe': is_safe
        }
    
    def _check_office_security(self, file_data: bytes) -> Dict[str, any]:
        """Office document security checks."""
        score = 1.0
        warnings = []
        is_safe = True
        
        # Check for macros in Office documents
        if b'macros' in file_data.lower() or b'vba' in file_data.lower():
            score -= 0.5
            warnings.append("Document may contain macros")
            is_safe = False
        
        # Check for external links
        if b'http://' in file_data or b'https://' in file_data:
            count = file_data.count(b'http://') + file_data.count(b'https://')
            if count > 5:  # Many external links
                score -= 0.2
                warnings.append("Document contains many external links")
        
        # Check for embedded objects
        if b'oleObject' in file_data or b'OLE' in file_data:
            score -= 0.3
            warnings.append("Document contains embedded objects")
        
        return {
            'score': max(0.0, score),
            'warnings': warnings,
            'is_safe': is_safe
        }
    
    async def _validate_file_structure(self, file_data: bytes, file_extension: str) -> Dict[str, any]:
        """Validate file structure integrity."""
        warnings = []
        is_valid = True
        error = None
        
        try:
            if file_extension == '.pdf':
                is_valid = self._validate_pdf_structure(file_data)
                if not is_valid:
                    error = "Invalid PDF structure"
            
            elif file_extension == '.docx':
                is_valid = self._validate_docx_structure(file_data)
                if not is_valid:
                    error = "Invalid DOCX structure"
            
            elif file_extension == '.doc':
                is_valid = self._validate_doc_structure(file_data)
                if not is_valid:
                    error = "Invalid DOC structure"
            
            elif file_extension == '.txt':
                is_valid = self._validate_text_structure(file_data)
                if not is_valid:
                    error = "Invalid text encoding"
        
        except Exception as e:
            is_valid = False
            error = f"Structure validation error: {str(e)}"
        
        return {
            'is_valid': is_valid,
            'warnings': warnings,
            'error': error
        }
    
    def _validate_pdf_structure(self, file_data: bytes) -> bool:
        """Validate PDF file structure."""
        # Check PDF header
        if not file_data.startswith(b'%PDF-'):
            return False
        
        # Check for EOF marker
        if b'%%EOF' not in file_data[-100:]:
            return False
        
        # Basic structure check
        if b'/Catalog' not in file_data:
            return False
        
        return True
    
    def _validate_docx_structure(self, file_data: bytes) -> bool:
        """Validate DOCX file structure."""
        # DOCX is a ZIP file
        if not file_data.startswith(b'PK'):
            return False
        
        # Should contain Word-specific files
        required_parts = [b'word/document.xml', b'[Content_Types].xml']
        for part in required_parts:
            if part not in file_data:
                return False
        
        return True
    
    def _validate_doc_structure(self, file_data: bytes) -> bool:
        """Validate DOC file structure."""
        # Check OLE2 signature
        if not file_data.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'):
            return False
        
        # Check for Word-specific structures
        if b'Microsoft Office Word' not in file_data and b'WordDocument' not in file_data:
            return False
        
        return True
    
    def _validate_text_structure(self, file_data: bytes) -> bool:
        """Validate text file encoding."""
        # Try to decode as UTF-8
        try:
            file_data.decode('utf-8')
            return True
        except UnicodeDecodeError:
            pass
        
        # Try common encodings
        for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
            try:
                file_data.decode(encoding)
                return True
            except UnicodeDecodeError:
                continue
        
        return False
    
    def calculate_file_hash(self, file_data: bytes) -> str:
        """Calculate SHA-256 hash of file for integrity checking."""
        return hashlib.sha256(file_data).hexdigest()
    
    def is_duplicate_file(self, file_hash: str, existing_hashes: List[str]) -> bool:
        """Check if file is a duplicate based on hash."""
        return file_hash in existing_hashes
