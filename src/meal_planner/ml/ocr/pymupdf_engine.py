"""PyMuPDF OCR engine."""

import time
from pathlib import Path
from typing import Set

import fitz  # PyMuPDF
from loguru import logger

from meal_planner.core.models import OCREngine, OCRResult
from meal_planner.ml.ocr.base import BaseOCREngine


class PyMuPDFEngine(BaseOCREngine):
    """OCR engine using PyMuPDF."""
    
    def __init__(self):
        """Initialize the PyMuPDF engine."""
        logger.info("Initializing PyMuPDF engine")
    
    async def extract_text(self, file_path: Path) -> OCRResult:
        """Extract text from a file using PyMuPDF.
        
        Args:
            file_path: Path to the file
            
        Returns:
            OCR result
        """
        start_time = time.time()
        warnings = []
        
        try:
            # Check if file exists
            if not file_path.exists():
                warnings.append(f"File not found: {file_path}")
                return OCRResult(
                    text="",
                    confidence=0.0,
                    engine_used=OCREngine.PYMUPDF,
                    processing_time=time.time() - start_time,
                    warnings=warnings
                )
            
            # Check if file format is supported
            if not self.supports_format(file_path):
                warnings.append(f"Unsupported file format: {file_path.suffix}")
                return OCRResult(
                    text="",
                    confidence=0.0,
                    engine_used=OCREngine.PYMUPDF,
                    processing_time=time.time() - start_time,
                    warnings=warnings
                )
            
            # Open document
            doc = fitz.open(file_path)
            
            # Extract text from all pages
            text = ""
            for page in doc:
                text += page.get_text()
            
            # Close document
            doc.close()
            
            # Calculate confidence (PyMuPDF doesn't provide confidence scores)
            # We'll use a simple heuristic based on text length
            confidence = min(1.0, len(text) / 1000) if text else 0.0
            
            # Create result
            result = OCRResult(
                text=text,
                confidence=confidence,
                engine_used=OCREngine.PYMUPDF,
                processing_time=time.time() - start_time,
                page_count=len(doc),
                warnings=warnings
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Error extracting text with PyMuPDF: {e}")
            warnings.append(f"Error extracting text: {str(e)}")
            
            return OCRResult(
                text="",
                confidence=0.0,
                engine_used=OCREngine.PYMUPDF,
                processing_time=time.time() - start_time,
                warnings=warnings
            )
    
    def get_name(self) -> str:
        """Get the name of the OCR engine.
        
        Returns:
            Name of the OCR engine
        """
        return "PyMuPDF"
    
    def get_version(self) -> str:
        """Get the version of the OCR engine.
        
        Returns:
            Version of the OCR engine
        """
        return fitz.version[0]
    
    def get_supported_formats(self) -> Set[str]:
        """Get the supported file formats.
        
        Returns:
            Set of supported file extensions
        """
        return {
            ".pdf", ".xps", ".oxps", ".epub", ".mobi", ".fb2", ".cbz", ".svg"
        }
