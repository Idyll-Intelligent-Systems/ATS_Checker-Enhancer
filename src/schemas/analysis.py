"""
ZeX-ATS-AI Analysis Schemas - Enhanced Multi-Format Support
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum


class AnalysisType(str, Enum):
    """Supported analysis types."""
    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"
    COMPARISON = "comparison"
    BULK = "bulk"


class FileFormat(str, Enum):
    """Supported file formats."""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TEX = "tex"
    LATEX = "latex"
    PPTX = "pptx"
    PPT = "ppt"
    XLSX = "xlsx"
    XLS = "xls"
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    MP3 = "mp3"
    WAV = "wav"
    MP4 = "mp4"
    AVI = "avi"


class ProcessingStatus(str, Enum):
    """Processing status options."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Request Schemas
class AnalysisRequest(BaseModel):
    """Standard analysis request."""
    analysis_type: AnalysisType
    include_ai_insights: bool = True
    target_job_description: Optional[str] = None
    custom_keywords: Optional[List[str]] = None
    
    class Config:
        example = {
            "analysis_type": "resume",
            "include_ai_insights": True,
            "target_job_description": "Software Engineer position requiring Python, React, and AWS experience",
            "custom_keywords": ["Python", "React", "AWS", "Docker"]
        }


class MultiFormatAnalysisRequest(BaseModel):
    """Multi-format analysis request."""
    analysis_type: AnalysisType = AnalysisType.RESUME
    include_ai_insights: bool = True
    extract_images: bool = False
    perform_ocr: bool = True
    transcribe_audio: bool = True
    analyze_video_frames: bool = True
    target_keywords: Optional[List[str]] = None
    
    class Config:
        example = {
            "analysis_type": "resume",
            "include_ai_insights": True,
            "extract_images": False,
            "perform_ocr": True,
            "transcribe_audio": True,
            "analyze_video_frames": True,
            "target_keywords": ["Python", "Data Science", "Machine Learning"]
        }


class BulkAnalysisRequest(BaseModel):
    """Bulk analysis request for enterprise users."""
    file_urls: List[str] = Field(..., max_items=100)
    analysis_type: AnalysisType = AnalysisType.RESUME
    comparison_job_description: Optional[str] = None
    include_rankings: bool = True
    export_format: str = "json"
    
    @validator("file_urls")
    def validate_file_urls(cls, v):
        if len(v) == 0:
            raise ValueError("At least one file URL is required")
        return v
    
    class Config:
        example = {
            "file_urls": [
                "https://storage.example.com/resume1.pdf",
                "https://storage.example.com/resume2.docx"
            ],
            "analysis_type": "resume",
            "comparison_job_description": "Senior Python Developer",
            "include_rankings": True,
            "export_format": "json"
        }


# Response Schemas
class FileInfo(BaseModel):
    """File information schema."""
    filename: str
    format: str
    size_mb: float
    mime_type: str
    processing_method: str
    upload_time: Optional[datetime] = None


class ContentExtraction(BaseModel):
    """Content extraction results."""
    text_extracted: bool
    extraction_method: str
    confidence_score: float = Field(ge=0, le=100)
    pages_processed: int = 0
    images_found: int = 0
    tables_found: int = 0
    audio_transcribed: bool = False
    video_frames_analyzed: int = 0
    detected_languages: Optional[List[str]] = None


class DocumentStructure(BaseModel):
    """Document structure analysis."""
    has_structure: bool
    sections_detected: int
    formatting_preserved: bool
    headers_found: List[str] = []
    bullet_points: int = 0
    contact_info_detected: bool = False


class OCRDetails(BaseModel):
    """OCR processing details."""
    confidence: float = Field(ge=0, le=100)
    languages_detected: List[str] = []
    elements_detected: List[str] = []
    text_regions: int = 0
    image_quality_score: Optional[float] = None


class AudioDetails(BaseModel):
    """Audio processing details."""
    transcription_available: bool
    language_detected: str = "unknown"
    segments_count: int = 0
    speaker_count: Optional[int] = None
    audio_quality_score: Optional[float] = None
    duration_seconds: Optional[float] = None


class VideoDetails(BaseModel):
    """Video processing details."""
    duration_seconds: float
    frames_analyzed: int
    audio_transcribed: bool
    text_from_frames: int
    key_frames_extracted: int = 0
    video_quality_score: Optional[float] = None


class ATSScore(BaseModel):
    """ATS compatibility scoring."""
    overall_score: float = Field(ge=0, le=100)
    keyword_match_score: float = Field(ge=0, le=100)
    format_score: float = Field(ge=0, le=100)
    readability_score: float = Field(ge=0, le=100)
    structure_score: float = Field(ge=0, le=100)
    improvement_potential: float = Field(ge=0, le=100)


class AIInsights(BaseModel):
    """AI-generated insights."""
    strengths: List[str] = []
    weaknesses: List[str] = []
    suggestions: List[str] = []
    missing_keywords: List[str] = []
    skill_gaps: List[str] = []
    industry_alignment: Optional[str] = None
    experience_level: Optional[str] = None
    career_stage: Optional[str] = None


class AnalysisResults(BaseModel):
    """Comprehensive analysis results."""
    ats_score: ATSScore
    ai_insights: AIInsights
    content_stats: Dict[str, Any] = {}
    keyword_analysis: Dict[str, Any] = {}
    competitive_analysis: Optional[Dict[str, Any]] = None
    sentiment_analysis: Optional[Dict[str, Any]] = None


class AnalysisResponse(BaseModel):
    """Standard analysis response."""
    success: bool
    analysis_id: str
    file_info: FileInfo
    analysis_results: AnalysisResults
    processing_time: float = 0.0
    recommendations: List[str] = []
    upgrade_suggestions: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MultiFormatAnalysisResponse(BaseModel):
    """Enhanced multi-format analysis response."""
    success: bool
    analysis_id: str
    file_info: FileInfo
    content_extraction: ContentExtraction
    analysis_results: Dict[str, Any]  # Flexible for different analysis types
    processing_time: float = 0.0
    recommendations: List[str] = []
    upgrade_suggestions: List[str] = []
    
    # Optional format-specific details
    document_structure: Optional[DocumentStructure] = None
    ocr_details: Optional[OCRDetails] = None
    audio_details: Optional[AudioDetails] = None
    video_details: Optional[VideoDetails] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    format_category: Optional[str] = None
    processing_warnings: List[str] = []
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FormatInfo(BaseModel):
    """Format information schema."""
    extensions: List[str]
    mime_types: List[str]
    description: str
    max_size_mb: Optional[int] = None
    processing_features: Optional[List[str]] = None


class SupportedFormatsResponse(BaseModel):
    """Supported formats response."""
    success: bool
    total_formats: int
    categories: Dict[str, Dict[str, FormatInfo]]
    max_file_size: str
    processing_features: List[str]
    limitations: Optional[Dict[str, List[str]]] = None
    
    class Config:
        example = {
            "success": True,
            "total_formats": 16,
            "categories": {
                "documents": {
                    "PDF": {
                        "extensions": ["pdf"],
                        "mime_types": ["application/pdf"],
                        "description": "Portable Document Format - industry standard"
                    }
                }
            },
            "max_file_size": "50MB",
            "processing_features": [
                "Text extraction",
                "OCR (Optical Character Recognition)",
                "Speech-to-text transcription"
            ]
        }


class BatchProcessingResult(BaseModel):
    """Individual file result in batch processing."""
    filename: str
    success: bool
    format: str
    text_length: int = 0
    ats_score: float = 0.0
    processing_time: float = 0.0
    error: Optional[str] = None


class BulkAnalysisResponse(BaseModel):
    """Bulk analysis response."""
    success: bool
    batch_id: str
    total_files: int
    successful_analyses: int
    failed_analyses: int
    results: List[BatchProcessingResult]
    failures: List[Dict[str, str]] = []
    processing_time: float = 0.0
    export_url: Optional[str] = None
    rankings: Optional[List[Dict[str, Any]]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ComparisonResult(BaseModel):
    """Resume-job comparison result."""
    match_percentage: float = Field(ge=0, le=100)
    keyword_matches: List[str] = []
    missing_keywords: List[str] = []
    skill_alignment: Dict[str, float] = {}
    experience_match: Optional[str] = None
    recommendations: List[str] = []
    compatibility_score: float = Field(ge=0, le=100)


class ComparisonResponse(BaseModel):
    """Comparison analysis response."""
    success: bool
    comparison_id: str
    resume_info: FileInfo
    job_info: FileInfo
    comparison_result: ComparisonResult
    detailed_analysis: AnalysisResults
    processing_time: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AnalysisHistory(BaseModel):
    """Analysis history entry."""
    analysis_id: str
    analysis_type: AnalysisType
    filename: str
    file_format: FileFormat
    ats_score: float = 0.0
    status: ProcessingStatus
    created_at: datetime
    processing_time: float = 0.0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserAnalytics(BaseModel):
    """User analytics data."""
    total_analyses: int = 0
    analyses_by_format: Dict[str, int] = {}
    average_ats_score: float = 0.0
    improvement_trend: List[float] = []
    most_used_features: List[str] = []
    time_saved_hours: float = 0.0
    period_days: int = 30


class ErrorResponse(BaseModel):
    """Error response schema."""
    success: bool = False
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Validation schemas
class FileValidation(BaseModel):
    """File validation result."""
    is_valid: bool
    file_size_mb: float
    format: FileFormat
    mime_type: str
    validation_errors: List[str] = []
    warnings: List[str] = []


class ProcessingCapabilities(BaseModel):
    """Processing capabilities for different subscription tiers."""
    max_file_size_mb: int
    max_concurrent_analyses: int
    supported_formats: List[FileFormat]
    advanced_features: List[str] = []
    batch_processing: bool = False
    priority_processing: bool = False
    api_access: bool = False
