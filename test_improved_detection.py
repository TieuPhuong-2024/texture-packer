#!/usr/bin/env python3
"""
Test script for improved sprite detection system.
Tests different sprite sheet types to verify comprehensive detection works.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw
from src.sprite_sheet_processor import SpriteSheetProcessor, FrameData

def create_test_sprite_sheets():
    """Create various types of test sprite sheets."""
    test_sheets = {}
    
    # Test 1: Alpha transparency sprites (original working case)
    print("Creating alpha transparency sprite sheet...")
    alpha_sheet = Image.new('RGBA', (200, 200), (255, 255, 255, 0))  # Transparent background
    draw = ImageDraw.Draw(alpha_sheet)
    
    # Draw some colored rectangles with transparency
    colors = [(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255), (255, 255, 0, 255)]
    positions = [(10, 10), (80, 10), (150, 10), (10, 80)]
    
    for i, (color, (x, y)) in enumerate(zip(colors, positions)):
        draw.rectangle([x, y, x+50, y+50], fill=color)
    
    test_sheets['alpha_transparency'] = alpha_sheet
    
    # Test 2: Solid color background sprites
    print("Creating solid background sprite sheet...")
    bg_sheet = Image.new('RGB', (200, 200), (128, 128, 128))  # Gray background
    draw = ImageDraw.Draw(bg_sheet)
    
    # Draw colored rectangles on gray background
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    positions = [(10, 10), (80, 10), (150, 10), (10, 80)]
    
    for i, (color, (x, y)) in enumerate(zip(colors, positions)):
        draw.rectangle([x, y, x+50, y+50], fill=color)
    
    test_sheets['solid_background'] = bg_sheet
    
    # Test 3: Grid-based sprite sheet
    print("Creating grid-based sprite sheet...")
    grid_sheet = Image.new('RGB', (192, 192), (255, 255, 255))  # White background
    draw = ImageDraw.Draw(grid_sheet)
    
    # Draw 3x3 grid of different colored sprites
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255),
        (255, 255, 0), (255, 0, 255), (0, 255, 255),
        (128, 128, 128), (255, 128, 0), (128, 0, 255)
    ]
    
    sprite_size = 48
    padding = 16
    
    for i, color in enumerate(colors):
        row = i // 3
        col = i % 3
        x = col * (sprite_size + padding) + padding
        y = row * (sprite_size + padding) + padding
        draw.rectangle([x, y, x + sprite_size, y + sprite_size], fill=color)
    
    test_sheets['grid_based'] = grid_sheet
    
    return test_sheets

def test_detection_methods():
    """Test the improved detection system."""
    print("Testing Improved Sprite Detection System")
    print("=" * 50)
    
    # Create test sprite sheets
    test_sheets = create_test_sprite_sheets()
    
    # Create processor instance
    processor = SpriteSheetProcessor()
    
    # Test each sprite sheet
    for sheet_name, image in test_sheets.items():
        print(f"\n--- Testing {sheet_name.replace('_', ' ').title()} ---")
        
        # Set the image for the processor
        processor.image = image
        processor.sheet_width, processor.sheet_height = image.size
        
        print(f"Image size: {image.size}")
        print(f"Image mode: {image.mode}")
        
        # Test comprehensive detection
        detected_sprites = processor.detect_sprites_comprehensive(image, max_sprites=20)
        
        print(f"Detected {len(detected_sprites)} sprites:")
        for i, (x, y, width, height) in enumerate(detected_sprites):
            print(f"  Sprite {i+1}: ({x}, {y}) {width}x{height}")
        
        # Test automatic frame detection
        frames = processor.detect_frames_automatically(max_frames=20)
        print(f"Auto-detected {len(frames)} frames")
        for frame in frames[:5]:  # Show first 5 frames
            print(f"  Frame: {frame.name} at ({frame.x}, {frame.y}) {frame.width}x{frame.height}")
        
        # Test legacy method for comparison
        legacy_sprites = processor.detect_pixel_clusters(image)
        print(f"Legacy method detected {len(legacy_sprites)} sprites")
        
        print("-" * 30)
    
    # Show detection info
    print("\n--- Detection System Information ---")
    info = processor.get_sprite_detection_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    try:
        test_detection_methods()
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()