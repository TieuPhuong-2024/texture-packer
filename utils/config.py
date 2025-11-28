"""
Configuration settings for Sprite Sheet Manager
"""

import os
from pathlib import Path

# Application settings
APP_NAME = "Sprite Sheet Manager"
APP_VERSION = "1.0"
APP_AUTHOR = "Developer"

# File paths
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_SAMPLES_DIR = PROJECT_ROOT / "samples"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "output"

# Supported image formats
SUPPORTED_IMAGE_FORMATS = {
    '.png': 'PNG',
    '.jpg': 'JPEG', 
    '.jpeg': 'JPEG',
    '.bmp': 'BMP',
    '.gif': 'GIF'
}

# Default settings
DEFAULT_SPRITE_SHEET_WIDTH = 512
DEFAULT_SPRITE_SHEET_HEIGHT = 512
DEFAULT_FRAME_SIZE = 64

# GUI settings
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

# Export settings
EXPORT_FORMATS = ['JSON', 'CSV']
JSON_INDENT = 2

# Color settings for UI
COLORS = {
    'background': '#f0f0f0',
    'foreground': '#000000',
    'accent': '#007acc',
    'warning': '#ff9500',
    'error': '#ff3b30',
    'success': '#34c759'
}