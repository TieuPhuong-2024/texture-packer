#!/usr/bin/env python3
"""
Comprehensive scalability test for the improved sprite detection system.
Tests performance with various sprite sheet sizes and frame counts.
"""

import sys
import os
import time
import math
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageDraw
from src.sprite_sheet_processor import SpriteSheetProcessor, FrameData

def create_large_sprite_sheet(width: int, height: int, frame_size: int = 32, padding: int = 2) -> Image.Image:
    """Create a large sprite sheet with many frames for testing scalability."""
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # Generate many different colors
    colors = []
    for i in range(1000):  # Generate many colors
        r = (i * 37) % 256
        g = (i * 73) % 256  
        b = (i * 101) % 256
        colors.append((r, g, b, 255))
    
    frame_count = 0
    y = padding
    while y + frame_size <= height:
        x = padding
        while x + frame_size <= width:
            # Use cycling colors
            color = colors[frame_count % len(colors)]
            draw.rectangle([x, y, x + frame_size, y + frame_size], fill=color)
            
            # Add some variation (small shapes inside frames)
            if frame_count % 3 == 0:
                # Add a circle
                draw.ellipse([x+4, y+4, x+frame_size-4, y+frame_size-4], 
                           fill=(255, 255, 255, 200))
            elif frame_count % 3 == 1:
                # Add a smaller rectangle
                draw.rectangle([x+6, y+6, x+frame_size-6, y+frame_size-6], 
                             fill=(128, 128, 128, 200))
            
            x += frame_size + padding
            frame_count += 1
        y += frame_size + padding
    
    return image, frame_count

def create_grid_sprite_sheet(grid_size: int = 20, frame_size: int = 32) -> Image.Image:
    """Create a regular grid sprite sheet for testing grid detection."""
    width = height = grid_size * frame_size
    image = Image.new('RGB', (width, height), (128, 128, 128))  # Gray background
    draw = ImageDraw.Draw(image)
    
    frame_count = 0
    for row in range(grid_size):
        for col in range(grid_size):
            x = col * frame_size
            y = row * frame_size
            
            # Create different colored frames
            color = (
                (frame_count * 15) % 256,
                (frame_count * 37) % 256,
                (frame_count * 73) % 256
            )
            draw.rectangle([x, y, x + frame_size, y + frame_size], fill=color)
            frame_count += 1
    
    return image, frame_count

def test_detection_performance():
    """Test detection performance with various sprite sheet configurations."""
    print("=" * 80)
    print("SPRITE DETECTION SCALABILITY TEST")
    print("=" * 80)
    
    processor = SpriteSheetProcessor()
    test_results = []
    
    # Test configurations
    test_configs = [
        # (description, sheet_creator, max_frames, performance_mode)
        ("Small Grid (8x8)", lambda: create_grid_sprite_sheet(8, 32), 100, "fast"),
        ("Medium Grid (12x12)", lambda: create_grid_sprite_sheet(12, 32), 100, "balanced"),
        ("Large Grid (16x16)", lambda: create_grid_sprite_sheet(16, 32), 100, "thorough"),
        ("Large Sheet (100 frames)", lambda: create_large_sprite_sheet(512, 512, 32, 2), 100, "balanced"),
        ("Very Large Sheet (200 frames)", lambda: create_large_sprite_sheet(800, 600, 32, 2), 200, "balanced"),
        ("Huge Sheet (500+ frames)", lambda: create_large_sprite_sheet(1200, 800, 24, 2), 500, "fast"),
    ]
    
    for desc, sheet_creator, max_frames, mode in test_configs:
        print(f"\n--- Testing {desc} ---")
        
        # Create sprite sheet
        start_time = time.time()
        sheet, actual_frame_count = sheet_creator()
        creation_time = time.time() - start_time
        print(f"Created sprite sheet: {sheet.size[0]}x{sheet.size[1]} pixels")
        print(f"Expected frames: ~{actual_frame_count}")
        print(f"Creation time: {creation_time:.2f}s")
        
        # Set up processor
        processor.image = sheet
        processor.sheet_width, processor.sheet_height = sheet.size
        
        # Test detection with different modes
        for test_mode in ["fast", "balanced", "thorough"]:
            print(f"\n  Testing {test_mode} mode:")
            
            # Clear previous results
            processor.frames = []
            
            # Run detection
            detection_start = time.time()
            try:
                detected_frames = processor.detect_frames_automatically(
                    max_frames=max_frames, 
                    performance_mode=test_mode
                )
                detection_time = time.time() - detection_start
                
                detection_rate = len(detected_frames) / detection_time if detection_time > 0 else 0
                
                print(f"    Detected frames: {len(detected_frames)}")
                print(f"    Detection time: {detection_time:.2f}s")
                print(f"    Detection rate: {detection_rate:.1f} frames/sec")
                print(f"    Accuracy: {len(detected_frames)/actual_frame_count*100:.1f}%")
                
                # Store results
                test_results.append({
                    'test': f"{desc}_{test_mode}",
                    'sheet_size': sheet.size,
                    'actual_frames': actual_frame_count,
                    'detected_frames': len(detected_frames),
                    'detection_time': detection_time,
                    'detection_rate': detection_rate,
                    'accuracy': len(detected_frames)/actual_frame_count,
                    'mode': test_mode
                })
                
            except Exception as e:
                print(f"    ERROR: {e}")
                test_results.append({
                    'test': f"{desc}_{test_mode}",
                    'sheet_size': sheet.size,
                    'actual_frames': actual_frame_count,
                    'detected_frames': 0,
                    'detection_time': 0,
                    'detection_rate': 0,
                    'accuracy': 0,
                    'mode': test_mode,
                    'error': str(e)
                })
    
    # Print summary
    print("\n" + "=" * 80)
    print("PERFORMANCE SUMMARY")
    print("=" * 80)
    
    print(f"{'Test':<25} {'Mode':<10} {'Detected':<9} {'Time(s)':<8} {'Rate(f/s)':<10} {'Accuracy':<10}")
    print("-" * 80)
    
    for result in test_results:
        if 'error' not in result:
            print(f"{result['test'][:24]:<25} {result['mode']:<10} "
                  f"{result['detected_frames']:<9} {result['detection_time']:<8.2f} "
                  f"{result['detection_rate']:<10.1f} {result['accuracy']*100:<10.1f}%")
        else:
            print(f"{result['test'][:24]:<25} {result['mode']:<10} ERROR")
    
    # Performance analysis
    print("\n" + "=" * 80)
    print("SCALABILITY ANALYSIS")
    print("=" * 80)
    
    # Calculate performance metrics
    total_tests = len([r for r in test_results if 'error' not in r])
    
    if total_tests == 0:
        print("No tests completed successfully. Please check the errors above.")
        return test_results
        
    avg_detection_time = sum(r['detection_time'] for r in test_results if 'error' not in r) / total_tests
    avg_rate = sum(r['detection_rate'] for r in test_results if 'error' not in r) / total_tests
    avg_accuracy = sum(r['accuracy'] for r in test_results if 'error' not in r) / total_tests
    
    print(f"Total tests completed: {total_tests}")
    print(f"Average detection time: {avg_detection_time:.2f}s")
    print(f"Average detection rate: {avg_rate:.1f} frames/second")
    print(f"Average accuracy: {avg_accuracy*100:.1f}%")
    
    # Performance by mode
    for mode in ["fast", "balanced", "thorough"]:
        mode_results = [r for r in test_results if r['mode'] == mode and 'error' not in r]
        if mode_results:
            mode_avg_time = sum(r['detection_time'] for r in mode_results) / len(mode_results)
            mode_avg_rate = sum(r['detection_rate'] for r in mode_results) / len(mode_results)
            mode_avg_accuracy = sum(r['accuracy'] for r in mode_results) / len(mode_results)
            
            print(f"\n{mode.upper()} mode:")
            print(f"  Average time: {mode_avg_time:.2f}s")
            print(f"  Average rate: {mode_avg_rate:.1f} frames/sec")
            print(f"  Average accuracy: {mode_avg_accuracy*100:.1f}%")
    
    # Scalability insights
    print("\n" + "=" * 80)
    print("SCALABILITY INSIGHTS")
    print("=" * 80)
    
    if total_tests > 0:
        # Check if the system can handle large sprite sheets
        large_sheet_tests = [r for r in test_results if r['sheet_size'][0] * r['sheet_size'][1] > 500000]
        if large_sheet_tests:
            large_sheet_success = len([r for r in large_sheet_tests if r['detection_time'] > 0]) / len(large_sheet_tests)
            print(f"Large sheet processing success rate: {large_sheet_success*100:.1f}%")
        
        # Check frame count scalability
        high_frame_tests = [r for r in test_results if r['actual_frames'] > 100]
        if high_frame_tests:
            high_frame_success = len([r for r in high_frame_tests if r['detection_time'] > 0]) / len(high_frame_tests)
            print(f"High frame count processing success rate: {high_frame_success*100:.1f}%")
        
        # Best performing configuration
        best_result = max([r for r in test_results if 'error' not in r], 
                         key=lambda x: x['detection_rate'] * x['accuracy'])
        print(f"Best performance: {best_result['test']} ({best_result['detection_rate']:.1f} frames/sec, {best_result['accuracy']*100:.1f}% accuracy)")
    
    return test_results

def test_gui_import():
    """Test that the GUI imports correctly with new functionality."""
    print("\n" + "=" * 80)
    print("GUI INTEGRATION TEST")
    print("=" * 80)
    
    try:
        from gui.main_application import MainApplication
        print("PASS: GUI imports successfully")
        
        # Test that the performance mode combobox exists
        app = MainApplication()
        if hasattr(app, 'performance_mode'):
            print("PASS: Performance mode selector available")
            print(f"  Available modes: {app.performance_mode['values']}")
        else:
            print("FAIL: Performance mode selector not found")
        
        app.destroy()
        
    except Exception as e:
        print(f"FAIL: GUI import failed: {e}")

if __name__ == "__main__":
    try:
        # Run scalability tests
        results = test_detection_performance()
        
        # Test GUI integration
        test_gui_import()
        
        print("\n" + "=" * 80)
        print("SCALABILITY TEST COMPLETED")
        print("=" * 80)
        print("The sprite detection system has been optimized for:")
        print("• Large sprite sheets (1000+ pixels)")
        print("• High frame counts (100+ frames)")
        print("• Multiple performance modes")
        print("• Spatial partitioning for very large images")
        print("• Adaptive sampling and early termination")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()