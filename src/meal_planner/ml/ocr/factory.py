"""Factory for creating OCR engines."""

from loguru import logger

from meal_planner.core.models import OCREngine
from meal_planner.ml.ocr.base import BaseOCREngine
from meal_planner.ml.ocr.marker_engine import MarkerEngine
from meal_planner.ml.ocr.pymupdf_engine import PyMuPDFEngine


def create_ocr_engine(engine_type: OCREngine) -> BaseOCREngine:
    """Create an OCR engine.
    
    Args:
        engine_type: Type of OCR engine to create
        
    Returns:
        OCR engine
        
    Raises:
        ValueError: If the engine type is not supported
    """
    logger.info(f"Creating OCR engine: {engine_type}")
    
    if engine_type == OCREngine.PYMUPDF:
        return PyMuPDFEngine()
    elif engine_type == OCREngine.MARKER:
        return MarkerEngine()
    else:
        raise ValueError(f"Unsupported OCR engine: {engine_type}")
