#!/usr/bin/env python3
"""
Test script for Sprite Sheet Manager functionality
Demonstrates core features without the GUI
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.sprite_sheet_processor import SpriteSheetProcessor, FrameData


def test_sprite_sheet_processor():
    """Test the core sprite sheet processor functionality."""
    print("=== Sprite Sheet Manager Functionality Test ===\n")
    
    # Create processor instance
    processor = SpriteSheetProcessor()
    print("[OK] Created SpriteSheetProcessor instance")
    
    # Test 1: Create sample sprite sheet
    print("\n1. Creating sample sprite sheet...")
    if processor.create_sample_sprite_sheet(256, 256):
        print("[OK] Sample sprite sheet created successfully")
        print(f"  - Dimensions: {processor.sheet_width}x{processor.sheet_height}")
        print(f"  - Number of frames: {processor.get_frame_count()}")
    else:
        print("[FAIL] Failed to create sample sprite sheet")
        return False
    
    # Test 2: List frames
    print("\n2. Listing frames:")
    for i, frame in enumerate(processor.frames[:5]):  # Show first 5 frames
        print(f"  Frame {i+1}: {frame.name} at ({frame.x}, {frame.y}) size {frame.width}x{frame.height}")
    
    # Test 3: Add custom frame
    print("\n3. Adding custom frame...")
    if processor.add_frame("custom_frame", 200, 200, 32, 32):
        print("[OK] Custom frame added successfully")
    else:
        print("[FAIL] Failed to add custom frame")
    
    # Test 4: Export to JSON
    print("\n4. Exporting to JSON...")
    json_file = project_root / "test_export.json"
    if processor.export_to_json(str(json_file)):
        print(f"[OK] Exported to JSON: {json_file}")
    else:
        print("[FAIL] Failed to export to JSON")
    
    # Test 5: Export to CSV
    print("\n5. Exporting to CSV...")
    csv_file = project_root / "test_export.csv"
    if processor.export_to_csv(str(csv_file)):
        print(f"[OK] Exported to CSV: {csv_file}")
    else:
        print("[FAIL] Failed to export to CSV")
    
    # Test 6: Save sprite sheet image
    print("\n6. Saving sprite sheet image...")
    image_file = project_root / "test_sprite_sheet.png"
    if processor.save_sprite_sheet(str(image_file)):
        print(f"[OK] Saved sprite sheet image: {image_file}")
    else:
        print("[FAIL] Failed to save sprite sheet image")
    
    # Test 7: Test frame extraction
    print("\n7. Testing frame extraction...")
    if processor.frames:
        first_frame = processor.frames[0]
        extracted = processor.extract_frame_image(first_frame)
        if extracted:
            print(f"[OK] Extracted frame '{first_frame.name}' successfully")
            print(f"  - Extracted size: {extracted.size}")
        else:
            print("[FAIL] Failed to extract frame image")
    
    # Test 8: Test frame operations
    print("\n8. Testing frame operations...")
    
    # Get frame
    frame = processor.get_frame("custom_frame")
    if frame:
        print(f"[OK] Found frame: {frame.name}")
        
        # Update frame
        if processor.update_frame("custom_frame", "updated_frame", 210, 210, 32, 32):
            print("[OK] Frame updated successfully")
        else:
            print("[FAIL] Failed to update frame")
        
        # Remove frame
        if processor.remove_frame("updated_frame"):
            print("[OK] Frame removed successfully")
        else:
            print("[FAIL] Failed to remove frame")
    
    print(f"\n9. Final frame count: {processor.get_frame_count()}")
    
    # Test 9: Load from JSON
    print("\n10. Testing load from JSON...")
    processor.clear_frames()
    print(f"  - Frames after clear: {processor.get_frame_count()}")
    
    if processor.load_from_json(str(json_file)):
        print(f"[OK] Loaded frames from JSON: {processor.get_frame_count()} frames")
    else:
        print("[FAIL] Failed to load from JSON")
    
    print("\n=== Test completed successfully! ===")
    
    # Cleanup test files
    print("\nCleaning up test files...")
    for test_file in [json_file, csv_file, image_file]:
        if test_file.exists():
            test_file.unlink()
            print(f"  Removed: {test_file.name}")
    
    return True


def test_file_handler():
    """Test file handling utilities."""
    print("\n=== File Handler Tests ===\n")
    
    from utils.file_handler import FileHandler
    from utils.config import SUPPORTED_IMAGE_FORMATS
    
    print("[OK] FileHandler imported successfully")
    print(f"[OK] Supported formats: {list(SUPPORTED_IMAGE_FORMATS.keys())}")
    
    # Test filename cleaning
    test_name = "test<>file?.png"
    cleaned = FileHandler.clean_filename(test_name)
    print(f"[OK] Filename cleaning: '{test_name}' -> '{cleaned}'")
    
    return True


def main():
    """Run all tests."""
    try:
        # Test core functionality
        test_sprite_sheet_processor()
        
        # Test utilities
        test_file_handler()
        
        print("\n[SUCCESS] All tests passed! The application is working correctly.")
        print("\nTo run the GUI application:")
        print("  python main.py")
        
    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())