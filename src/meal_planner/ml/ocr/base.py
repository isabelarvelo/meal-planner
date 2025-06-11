"""Base OCR engine interface."""

import abc
from pathlib import Path
from typing import List, Set

from meal_planner.core.models import OCRResult


class BaseOCREngine(abc.ABC):
    """Base class for OCR engines."""
    
    @abc.abstractmethod
    async def extract_text(self, file_path: Path) -> OCRResult:
        """Extract text from a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            OCR result
        """
        pass
    
    @abc.abstractmethod
    def get_name(self) -> str:
        """Get the name of the OCR engine.
        
        Returns:
            Name of the OCR engine
        """
        pass
    
    @abc.abstractmethod
    def get_version(self) -> str:
        """Get the version of the OCR engine.
        
        Returns:
            Version of the OCR engine
        """
        pass
    
    @abc.abstractmethod
    def get_supported_formats(self) -> Set[str]:
        """Get the supported file formats.
        
        Returns:
            Set of supported file extensions
        """
        pass
    
    def supports_format(self, file_path: Path) -> bool:
        """Check if the engine supports the given file format.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the format is supported, False otherwise
        """
        extension = file_path.suffix.lower()
        return extension in self.get_supported_formats()
