"""
File handling utilities for Sprite Sheet Manager
"""

import os
import json
import csv
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PIL import Image
from utils.config import SUPPORTED_IMAGE_FORMATS


class FileHandler:
    """Utility class for handling file operations."""
    
    @staticmethod
    def get_supported_image_formats() -> List[str]:
        """Get list of supported image format extensions."""
        return list(SUPPORTED_IMAGE_FORMATS.keys())
    
    @staticmethod
    def is_image_file(file_path: str) -> bool:
        """Check if file is a supported image format."""
        file_ext = Path(file_path).suffix.lower()
        return file_ext in SUPPORTED_IMAGE_FORMATS
    
    @staticmethod
    def validate_image_file(file_path: str) -> Tuple[bool, str]:
        """
        Validate if file is a readable image.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not os.path.exists(file_path):
                return False, "File does not exist"
            
            if not FileHandler.is_image_file(file_path):
                return False, "Unsupported file format"
            
            # Try to open the image
            with Image.open(file_path) as img:
                img.verify()  # Verify it's a valid image
            
            return True, ""
            
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    @staticmethod
    def ensure_directory(directory_path: str) -> bool:
        """
        Ensure directory exists, create if it doesn't.
        
        Returns:
            bool: True if directory exists or was created successfully
        """
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def save_json(data: Dict, file_path: str) -> bool:
        """Save data to JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    @staticmethod
    def load_json(file_path: str) -> Optional[Dict]:
        """Load data from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    @staticmethod
    def save_csv(data: List[List], file_path: str) -> bool:
        """Save data to CSV file."""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_unique_filename(base_path: str) -> str:
        """
        Get a unique filename by adding numbers if file exists.
        
        Args:
            base_path: Base file path
            
        Returns:
            str: Unique file path
        """
        path = Path(base_path)
        if not path.exists():
            return base_path
        
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        
        counter = 1
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return str(new_path)
            counter += 1
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict:
        """
        Get comprehensive file information.
        
        Returns:
            Dict containing file information
        """
        path = Path(file_path)
        stat = path.stat()
        
        return {
            'name': path.name,
            'stem': path.stem,
            'suffix': path.suffix.lower(),
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'is_image': FileHandler.is_image_file(file_path)
        }
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """
        Clean filename by removing invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            str: Cleaned filename
        """
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Ensure not empty
        if not filename:
            filename = 'untitled'
        
        return filename