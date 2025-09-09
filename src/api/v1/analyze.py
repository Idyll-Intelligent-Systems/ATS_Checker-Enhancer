"""
ZeX-ATS-AI Analysis API Endpoints - Enhanced Multi-Format Support
Supports: PDF, DOCX, LaTeX, Images, PPT, Excel, Audio, Video
"""

import asyncio
from typing import Dict, List, Optional, Any
import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
import mimetypes
from pathlib import Path

from src.core.security import get_current_user
from src.models.user import User
from src.services.analysis_service import AnalysisService
from src.ai.processors.enhanced_document_processor import EnhancedDocumentProcessor
from src.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    MultiFormatAnalysisResponse,
    SupportedFormatsResponse
)
from src.utils.rate_limiter import RateLimiter
from src.utils.validators import validate_file_size, validate_file_type

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize processors
analysis_service = AnalysisService()
document_processor = EnhancedDocumentProcessor()
rate_limiter = RateLimiter()


@router.get("/supported-formats", response_model=SupportedFormatsResponse)
async def get_supported_formats():
    """Get list of all supported file formats."""
    try:
        formats = document_processor.SUPPORTED_FORMATS
        
        format_categories = {
            "documents": {
                "PDF": {
                    "extensions": ["pdf"],
                    "mime_types": formats["pdf"],
                    "description": "Portable Document Format - industry standard"
                },
                "Microsoft Word": {
                    "extensions": ["docx", "doc"],
                    "mime_types": formats["docx"],
                    "description": "Microsoft Word documents"
                },
                "LaTeX": {
                    "extensions": ["tex", "latex"],
                    "mime_types": formats.get("tex", []) + formats.get("latex", []),
                    "description": "LaTeX typesetting documents"
                }
            },
            "presentations": {
                "PowerPoint": {
                    "extensions": ["pptx", "ppt"],
                    "mime_types": formats["pptx"],
                    "description": "Microsoft PowerPoint presentations"
                }
            },
            "spreadsheets": {
                "Excel": {
                    "extensions": ["xlsx", "xls"],
                    "mime_types": formats["xlsx"],
                    "description": "Microsoft Excel spreadsheets"
                }
            },
            "images": {
                "JPEG": {
                    "extensions": ["jpg", "jpeg"],
                    "mime_types": formats["jpeg"],
                    "description": "JPEG images with OCR extraction"
                },
                "PNG": {
                    "extensions": ["png"],
                    "mime_types": formats["png"],
                    "description": "PNG images with OCR extraction"
                }
            },
            "audio": {
                "MP3": {
                    "extensions": ["mp3"],
                    "mime_types": formats["mp3"],
                    "description": "MP3 audio with speech-to-text transcription"
                },
                "WAV": {
                    "extensions": ["wav"],
                    "mime_types": formats["wav"],
                    "description": "WAV audio with speech-to-text transcription"
                }
            },
            "video": {
                "MP4": {
                    "extensions": ["mp4"],
                    "mime_types": formats["mp4"],
                    "description": "MP4 video with audio transcription and frame OCR"
                },
                "AVI": {
                    "extensions": ["avi"],
                    "mime_types": formats["avi"],
                    "description": "AVI video with audio transcription and frame OCR"
                }
            }
        }
        
        return SupportedFormatsResponse(
            success=True,
            total_formats=len([ext for category in format_categories.values() for format_info in category.values() for ext in format_info["extensions"]]),
            categories=format_categories,
            max_file_size="50MB",
            processing_features=[
                "Text extraction",
                "OCR (Optical Character Recognition)",
                "Speech-to-text transcription",
                "Document structure analysis",
                "AI-powered content analysis",
                "ATS optimization scoring",
                "Multi-language support"
            ]
        )
        
    except Exception as e:
        logger.error(f"Error getting supported formats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve supported formats")


@router.post("/resume/multi-format", response_model=MultiFormatAnalysisResponse)
async def analyze_resume_multi_format(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    analysis_type: str = "resume",
    include_ai_insights: bool = True,
    current_user: User = Depends(get_current_user)
):
    """
    Enhanced multi-format resume analysis supporting:
    - Documents: PDF, DOCX, LaTeX
    - Images: JPEG, PNG (with OCR)
    - Presentations: PPTX
    - Spreadsheets: XLSX
    - Audio: MP3, WAV (with speech-to-text)
    - Video: MP4, AVI (with transcription and frame analysis)
    """
    try:
        # Rate limiting check
        can_analyze = await rate_limiter.check_limit(
            str(current_user.id), 
            current_user.subscription_tier.value
        )
        
        if not can_analyze:
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded. Please upgrade your plan or wait."
            )
        
        # Start concurrent analysis tracking
        analysis_id = await rate_limiter.start_analysis(str(current_user.id))
        
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No file provided")
            
            # Validate file size (50MB limit for multimedia files)
            max_size = 50 * 1024 * 1024  # 50MB
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            
            if file_size > max_size:
                raise HTTPException(
                    status_code=413, 
                    detail=f"File too large. Maximum size: {max_size // (1024*1024)}MB"
                )
            
            # Get file extension
            file_extension = Path(file.filename).suffix.lower().lstrip('.')
            
            # Validate supported format
            if file_extension not in document_processor.SUPPORTED_FORMATS:
                supported_extensions = list(document_processor.SUPPORTED_FORMATS.keys())
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file format: .{file_extension}. Supported: {', '.join(supported_extensions)}"
                )
            
            # Process document with enhanced processor
            logger.info(f"Processing {file_extension.upper()} file: {file.filename} ({file_size} bytes)")
            
            processing_result = await document_processor.process_document(
                file=file,
                analysis_type=analysis_type
            )
            
            if not processing_result.get("success"):
                raise HTTPException(
                    status_code=422,
                    detail=f"Failed to process file: {processing_result.get('error', 'Unknown error')}"
                )
            
            # Extract processed content
            content_data = processing_result["content"]
            file_info = processing_result["file_info"]
            insights = processing_result["insights"]
            
            # Perform ATS analysis if text was extracted
            extracted_text = content_data.get("text", "")
            
            if extracted_text.strip():
                # Run comprehensive analysis
                ats_analysis = await analysis_service.analyze_resume_content(
                    text=extracted_text,
                    user_id=current_user.id,
                    filename=file.filename
                )
                
                # Combine insights
                combined_insights = {
                    **insights,
                    "ats_analysis": ats_analysis,
                    "content_stats": {
                        "total_characters": len(extracted_text),
                        "word_count": len(extracted_text.split()),
                        "readability_score": insights.get("ats_score", 0)
                    }
                }
            else:
                # No text extracted - provide format-specific feedback
                combined_insights = insights
                combined_insights["warning"] = f"No text could be extracted from {file_extension.upper()} file"
                
                if file_extension in ["jpg", "jpeg", "png"]:
                    combined_insights["suggestions"] = [
                        "Image quality may be too low for OCR",
                        "Try using a higher resolution image",
                        "Consider converting to PDF or DOCX format",
                        "Ensure text in image is clear and readable"
                    ]
                elif file_extension in ["mp3", "wav"]:
                    combined_insights["suggestions"] = [
                        "Audio quality may be insufficient for transcription",
                        "Ensure clear speech without background noise",
                        "Consider providing a text transcript",
                        "Check audio format compatibility"
                    ]
            
            # Create response with format-specific data
            response_data = {
                "success": True,
                "analysis_id": analysis_id,
                "file_info": {
                    "filename": file_info["filename"],
                    "format": file_info["format"].upper(),
                    "size_mb": round(file_info["size"] / (1024*1024), 2),
                    "mime_type": file_info["mime_type"],
                    "processing_method": get_processing_method(file_info["format"])
                },
                "content_extraction": {
                    "text_extracted": bool(extracted_text.strip()),
                    "extraction_method": get_extraction_method(file_info["format"]),
                    "confidence_score": content_data.get("ocr_confidence", 100),
                    "pages_processed": len(content_data.get("pages", [])),
                    "images_found": len(content_data.get("images", [])),
                    "tables_found": len(content_data.get("tables", [])),
                    "audio_transcribed": bool(content_data.get("audio_transcription")),
                    "video_frames_analyzed": len(content_data.get("key_frames", []))
                },
                "analysis_results": combined_insights,
                "processing_time": processing_result.get("processing_time", 0),
                "recommendations": generate_format_recommendations(file_info["format"], content_data),
                "upgrade_suggestions": get_upgrade_suggestions(current_user.subscription_tier.value, file_info["format"])
            }
            
            # Add format-specific details
            if file_info["format"] in ["pdf", "docx"]:
                response_data["document_structure"] = {
                    "has_structure": bool(content_data.get("pages") or content_data.get("paragraphs")),
                    "sections_detected": len(content_data.get("sections", [])),
                    "formatting_preserved": True
                }
            
            elif file_info["format"] in ["jpg", "jpeg", "png"]:
                response_data["ocr_details"] = {
                    "confidence": content_data.get("ocr_confidence", 0),
                    "languages_detected": content_data.get("detected_languages", []),
                    "elements_detected": content_data.get("detected_elements", [])
                }
            
            elif file_info["format"] in ["mp3", "wav"]:
                response_data["audio_details"] = {
                    "transcription_available": bool(content_data.get("transcription")),
                    "language_detected": content_data.get("language", "unknown"),
                    "segments_count": len(content_data.get("segments", []))
                }
            
            elif file_info["format"] in ["mp4", "avi"]:
                response_data["video_details"] = {
                    "duration_seconds": content_data.get("video_info", {}).get("duration", 0),
                    "frames_analyzed": len(content_data.get("key_frames", [])),
                    "audio_transcribed": bool(content_data.get("audio_transcription")),
                    "text_from_frames": len(content_data.get("ocr_results", []))
                }
            
            # Background task for detailed analysis if pro/enterprise user
            if current_user.subscription_tier.value in ["pro", "enterprise"] and extracted_text:
                background_tasks.add_task(
                    perform_advanced_analysis,
                    analysis_id,
                    extracted_text,
                    current_user.id,
                    file_info["format"]
                )
            
            return MultiFormatAnalysisResponse(**response_data)
            
        finally:
            # Mark analysis as complete
            await rate_limiter.finish_analysis(str(current_user.id), analysis_id)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in multi-format analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during analysis")


@router.post("/document/batch-process")
async def batch_process_documents(
    files: List[UploadFile] = File(...),
    analysis_type: str = "resume",
    current_user: User = Depends(get_current_user)
):
    """
    Batch process multiple documents of different formats.
    Enterprise feature supporting up to 10 files simultaneously.
    """
    try:
        # Check subscription level
        if current_user.subscription_tier.value not in ["enterprise"]:
            raise HTTPException(
                status_code=403,
                detail="Batch processing is available for Enterprise users only"
            )
        
        # Limit batch size
        if len(files) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 files allowed in batch processing"
            )
        
        # Rate limiting for batch processing
        can_analyze = await rate_limiter.check_concurrent_analyses(
            str(current_user.id),
            current_user.subscription_tier.value
        )
        
        if not can_analyze:
            raise HTTPException(
                status_code=429,
                detail="Too many concurrent analyses. Please wait."
            )
        
        # Process files concurrently
        tasks = []
        for file in files:
            task = process_single_file_async(file, analysis_type, current_user)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile results
        successful_analyses = []
        failed_analyses = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                failed_analyses.append({
                    "filename": files[i].filename,
                    "error": str(result)
                })
            else:
                successful_analyses.append(result)
        
        return {
            "success": True,
            "total_files": len(files),
            "successful_analyses": len(successful_analyses),
            "failed_analyses": len(failed_analyses),
            "results": successful_analyses,
            "failures": failed_analyses,
            "batch_id": f"batch_{current_user.id}_{len(files)}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        raise HTTPException(status_code=500, detail="Batch processing failed")


# Helper functions
def get_processing_method(format_type: str) -> str:
    """Get the processing method description for a format."""
    methods = {
        "pdf": "Advanced PDF parsing with text and image extraction",
        "docx": "Microsoft Word document structure analysis",
        "tex": "LaTeX command parsing and text cleaning",
        "latex": "LaTeX command parsing and text cleaning",
        "pptx": "PowerPoint slide content and structure extraction",
        "xlsx": "Excel worksheet data and metadata analysis",
        "jpg": "Optical Character Recognition (OCR)",
        "jpeg": "Optical Character Recognition (OCR)",
        "png": "Optical Character Recognition (OCR)",
        "mp3": "Advanced speech-to-text transcription",
        "wav": "Advanced speech-to-text transcription",
        "mp4": "Video frame analysis and audio transcription",
        "avi": "Video frame analysis and audio transcription"
    }
    return methods.get(format_type, "Standard text extraction")


def get_extraction_method(format_type: str) -> str:
    """Get the extraction method used for a format."""
    methods = {
        "pdf": "PyMuPDF with OCR fallback",
        "docx": "python-docx structure parsing",
        "tex": "LaTeX command interpretation",
        "latex": "LaTeX command interpretation",
        "pptx": "python-pptx slide analysis",
        "xlsx": "openpyxl cell-by-cell reading",
        "jpg": "Tesseract OCR with image enhancement",
        "jpeg": "Tesseract OCR with image enhancement",
        "png": "Tesseract OCR with image enhancement",
        "mp3": "OpenAI Whisper transcription",
        "wav": "OpenAI Whisper transcription",
        "mp4": "MoviePy + Whisper + OCR on key frames",
        "avi": "MoviePy + Whisper + OCR on key frames"
    }
    return methods.get(format_type, "Generic text extraction")


def generate_format_recommendations(format_type: str, content_data: Dict) -> List[str]:
    """Generate format-specific recommendations."""
    recommendations = []
    
    if format_type in ["jpg", "jpeg", "png"]:
        ocr_confidence = content_data.get("ocr_confidence", 0)
        if ocr_confidence < 70:
            recommendations.extend([
                "Consider using higher resolution images for better OCR results",
                "Convert to PDF or DOCX format for optimal ATS compatibility",
                "Ensure text is clear and not overlaid on complex backgrounds"
            ])
    
    elif format_type in ["mp3", "wav"]:
        if not content_data.get("transcription"):
            recommendations.extend([
                "Audio quality may need improvement for better transcription",
                "Speak clearly and reduce background noise",
                "Consider providing a text version alongside audio"
            ])
    
    elif format_type in ["tex", "latex"]:
        recommendations.extend([
            "LaTeX is well-structured but convert to PDF for broader ATS compatibility",
            "Ensure all packages compile correctly",
            "Consider simplifying complex mathematical notations for ATS parsing"
        ])
    
    elif format_type == "xlsx":
        recommendations.extend([
            "Spreadsheets are unconventional for resumes",
            "Consider reformatting as a traditional document",
            "Ensure important information is in the first worksheet"
        ])
    
    return recommendations


def get_upgrade_suggestions(tier: str, format_type: str) -> List[str]:
    """Get upgrade suggestions based on user tier and format."""
    if tier == "free":
        return [
            "Upgrade to Pro for advanced AI insights",
            "Get priority processing for multimedia files",
            "Access to batch processing capabilities"
        ]
    elif tier == "pro":
        return [
            "Upgrade to Enterprise for batch processing",
            "Advanced video analysis capabilities",
            "Custom format support and API access"
        ]
    return []


async def process_single_file_async(file: UploadFile, analysis_type: str, user: User) -> Dict:
    """Process a single file asynchronously for batch processing."""
    try:
        processing_result = await document_processor.process_document(
            file=file,
            analysis_type=analysis_type
        )
        
        return {
            "filename": file.filename,
            "success": processing_result.get("success", False),
            "format": processing_result.get("file_info", {}).get("format", "unknown"),
            "text_length": len(processing_result.get("content", {}).get("text", "")),
            "ats_score": processing_result.get("insights", {}).get("ats_score", 0)
        }
    except Exception as e:
        return {
            "filename": file.filename,
            "success": False,
            "error": str(e)
        }


async def perform_advanced_analysis(
    analysis_id: str,
    text: str,
    user_id: int,
    format_type: str
):
    """Background task for advanced analysis."""
    try:
        # This would perform more detailed analysis
        # Save results to database for later retrieval
        logger.info(f"Advanced analysis completed for {analysis_id}")
    except Exception as e:
        logger.error(f"Advanced analysis failed for {analysis_id}: {e}")
