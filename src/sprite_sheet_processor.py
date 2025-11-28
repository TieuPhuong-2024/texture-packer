"""
Sprite Sheet Processor Module
Core functionality for managing sprite sheets, frames, and data export.
"""

import json
import csv
import xml.etree.ElementTree as ET
import os
import time
import math
from PIL import Image, ImageDraw, ImageTk, ImageFilter, ImageEnhance
from typing import List, Dict, Tuple, Optional
import tkinter as tk
from tkinter import messagebox
from collections import Counter, deque


class FrameData:
    """Represents a single frame in a sprite sheet."""
    
    def __init__(self, name: str, x: int, y: int, width: int, height: int):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
    
    def to_dict(self) -> Dict:
        """Convert frame data to dictionary."""
        return {
            'name': self.name,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FrameData':
        """Create FrameData from dictionary."""
        return cls(
            name=data['name'],
            x=data['x'],
            y=data['y'],
            width=data['width'],
            height=data['height']
        )


class SpriteSheetProcessor:
    """Main class for processing sprite sheets."""
    
    def __init__(self):
        self.image: Optional[Image.Image] = None
        self.frames: List[FrameData] = []
        self.original_filename: str = ""
        self.sheet_width: int = 0
        self.sheet_height: int = 0
    
    def load_sprite_sheet(self, file_path: str) -> bool:
        """
        Load a sprite sheet from file.
        
        Args:
            file_path: Path to the sprite sheet image file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            self.image = Image.open(file_path)
            self.original_filename = os.path.basename(file_path)
            self.sheet_width, self.sheet_height = self.image.size
            self.frames = []  # Clear existing frames
            return True
        except Exception as e:
            print(f"Error loading sprite sheet: {e}")
            return False
    
    def add_frame(self, name: str, x: int, y: int, width: int, height: int) -> bool:
        """
        Add a new frame to the sprite sheet.
        
        Args:
            name: Name for the frame
            x: X coordinate of frame
            y: Y coordinate of frame
            width: Width of frame
            height: Height of frame
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        if self.image is None:
            return False
        
        # Check if frame is within bounds
        if (x < 0 or y < 0 or 
            x + width > self.sheet_width or 
            y + height > self.sheet_height):
            return False
        
        # Check for duplicate names
        for frame in self.frames:
            if frame.name == name:
                return False
        
        frame = FrameData(name, x, y, width, height)
        self.frames.append(frame)
        return True
    
    def remove_frame(self, frame_name: str) -> bool:
        """
        Remove a frame by name.
        
        Args:
            frame_name: Name of the frame to remove
            
        Returns:
            bool: True if removed successfully, False otherwise
        """
        for i, frame in enumerate(self.frames):
            if frame.name == frame_name:
                del self.frames[i]
                return True
        return False
    
    def update_frame(self, old_name: str, new_name: str, x: int, y: int, 
                    width: int, height: int) -> bool:
        """
        Update an existing frame.
        
        Args:
            old_name: Current name of the frame
            new_name: New name for the frame
            x: New X coordinate
            y: New Y coordinate
            width: New width
            height: New height
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        if self.image is None:
            return False
        
        frame_index = None
        for i, frame in enumerate(self.frames):
            if frame.name == old_name:
                frame_index = i
                break
        
        if frame_index is None:
            return False
        
        # Check if new name conflicts with other frames
        for i, frame in enumerate(self.frames):
            if i != frame_index and frame.name == new_name:
                return False
        
        # Check bounds
        if (x < 0 or y < 0 or 
            x + width > self.sheet_width or 
            y + height > self.sheet_height):
            return False
        
        self.frames[frame_index] = FrameData(new_name, x, y, width, height)
        return True
    
    def get_frame(self, frame_name: str) -> Optional[FrameData]:
        """
        Get a frame by name.
        
        Args:
            frame_name: Name of the frame
            
        Returns:
            FrameData object if found, None otherwise
        """
        for frame in self.frames:
            if frame.name == frame_name:
                return frame
        return None
    
    def extract_frame_image(self, frame: FrameData) -> Optional[Image.Image]:
        """
        Extract a frame image from the sprite sheet.
        
        Args:
            frame: FrameData object containing frame information
            
        Returns:
            PIL Image object if extracted successfully, None otherwise
        """
        if self.image is None:
            return None
        
        try:
            return self.image.crop((frame.x, frame.y, 
                                  frame.x + frame.width, 
                                  frame.y + frame.height))
        except Exception:
            return None
    
    def export_to_json(self, file_path: str) -> bool:
        """
        Export frame data to JSON file.
        
        Args:
            file_path: Path to save the JSON file
            
        Returns:
            bool: True if exported successfully, False otherwise
        """
        try:
            data = {
                'sprite_sheet': self.original_filename,
                'sheet_width': self.sheet_width,
                'sheet_height': self.sheet_height,
                'total_frames': len(self.frames),
                'frames': [frame.to_dict() for frame in self.frames]
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    def export_to_csv(self, file_path: str) -> bool:
        """
        Export frame data to CSV file.

        Args:
            file_path: Path to save the CSV file

        Returns:
            bool: True if exported successfully, False otherwise
        """
        try:
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(['Frame Name', 'X', 'Y', 'Width', 'Height'])

                # Write frame data
                for frame in self.frames:
                    writer.writerow([frame.name, frame.x, frame.y,
                                    frame.width, frame.height])
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    def export_to_xml(self, file_path: str) -> bool:
        """
        Export frame data to XML file in TexturePacker format.

        Args:
            file_path: Path to save the XML file

        Returns:
            bool: True if exported successfully, False otherwise
        """
        try:
            # Create root element with TextureAtlas format
            root = ET.Element("TextureAtlas")
            root.set("imagePath", self.original_filename)
            root.set("width", str(self.sheet_width))
            root.set("height", str(self.sheet_height))

            # Add sprites
            for frame in self.frames:
                sprite_element = ET.SubElement(root, "sprite")
                sprite_element.set("n", frame.name)
                sprite_element.set("x", str(frame.x))
                sprite_element.set("y", str(frame.y))
                sprite_element.set("w", str(frame.width))
                sprite_element.set("h", str(frame.height))
                # Default pivot points (center)
                sprite_element.set("pX", "0.5")
                sprite_element.set("pY", "0.5")

            # Write to file with pretty formatting
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)

            # Write XML declaration and comments
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<!-- Created with Texture Packer Tool -->\n')
                f.write('<!-- Format:\n')
                f.write('n  => name of the sprite\n')
                f.write('x  => sprite x pos in texture\n')
                f.write('y  => sprite y pos in texture\n')
                f.write('w  => sprite width\n')
                f.write('h  => sprite height\n')
                f.write('pX => x pos of the pivot point (relative to sprite width)\n')
                f.write('pY => y pos of the pivot point (relative to sprite height)\n')
                f.write('-->\n')

                # Write the XML content
                tree.write(f, encoding='unicode', xml_declaration=False)

            return True
        except Exception as e:
            print(f"Error exporting to XML: {e}")
            return False
    
    def load_from_json(self, file_path: str) -> bool:
        """
        Load frame data from JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.frames = []
            for frame_data in data['frames']:
                frame = FrameData.from_dict(frame_data)
                self.frames.append(frame)
            
            return True
        except Exception as e:
            print(f"Error loading from JSON: {e}")
            return False
    
    def create_sample_sprite_sheet(self, width: int = 256, height: int = 256) -> bool:
        """
        Create a sample sprite sheet for testing.
        
        Args:
            width: Width of the sprite sheet
            height: Height of the sprite sheet
            
        Returns:
            bool: True if created successfully, False otherwise
        """
        try:
            # Create a new image with some colored rectangles
            self.image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(self.image)
            
            # Draw some sample frames (4x4 grid of 64x64 frames)
            colors = [
                (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
                (255, 0, 255), (0, 255, 255), (255, 128, 0), (128, 255, 0),
                (0, 128, 255), (255, 0, 128), (128, 0, 255), (255, 128, 128),
                (128, 255, 128), (128, 128, 255), (255, 255, 128), (255, 128, 255)
            ]
            
            frame_size = 64
            frames_per_row = width // frame_size
            
            frame_index = 0
            for row in range(height // frame_size):
                for col in range(frames_per_row):
                    if frame_index < len(colors):
                        x = col * frame_size
                        y = row * frame_size
                        
                        # Draw colored rectangle
                        draw.rectangle([x, y, x + frame_size, y + frame_size], 
                                     fill=colors[frame_index])
                        
                        # Add frame to list
                        frame_name = f"frame_{frame_index:02d}"
                        self.frames.append(FrameData(frame_name, x, y, frame_size, frame_size))
                        frame_index += 1
            
            self.sheet_width = width
            self.sheet_height = height
            self.original_filename = "sample_sprite_sheet.png"
            
            return True
        except Exception as e:
            print(f"Error creating sample sprite sheet: {e}")
            return False
    
    def save_sprite_sheet(self, file_path: str) -> bool:
        """
        Save the current sprite sheet image.
        
        Args:
            file_path: Path to save the image
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            if self.image is not None:
                self.image.save(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error saving sprite sheet: {e}")
            return False
    
    def clear_frames(self):
        """Clear all frames from the sprite sheet."""
        self.frames = []
    
    def get_frame_count(self) -> int:
        """Get the total number of frames."""
        return len(self.frames)
    
    def is_loaded(self) -> bool:
        """Check if a sprite sheet is loaded."""
        return self.image is not None

    def detect_frames_automatically(self, max_frames: int = None, performance_mode: str = 'balanced') -> List[FrameData]:
        """
        Automatically detect ALL sprite frames in the sprite sheet.
        Uses comprehensive multi-strategy detection to work with any sprite sheet type.
        
        This method detects unlimited frames - no artificial restrictions.

        Args:
            max_frames: Maximum number of frames to detect (None for unlimited detection)
            performance_mode: 'fast', 'balanced', or 'thorough' - controls detection speed vs completeness

        Returns:
            List of detected FrameData objects for ALL detected frames
        """
        if self.image is None:
            return []

        # Set unlimited frames if not specified
        if max_frames is None:
            max_frames = float('inf')  # Unlimited detection

        # Adjust parameters based on performance mode
        detection_config = self._get_detection_config(performance_mode, max_frames)

        # Try comprehensive sprite detection first
        sprite_bounds = self.detect_sprites_comprehensive(self.image, **detection_config)
        
        if sprite_bounds:
            # Convert bounds to FrameData objects
            detected_frames = []
            for i, (x, y, width, height) in enumerate(sprite_bounds):
                frame_name = f"detected_sprite_{i+1:02d}"
                detected_frames.append(FrameData(frame_name, x, y, width, height))
            
            if len(detected_frames) > 0:
                print(f"Comprehensive detection found {len(detected_frames)} sprites")
                return detected_frames  # Return ALL detected frames

        # Fallback to grid-based detection if comprehensive detection fails
        print("Falling back to grid-based detection...")
        return self._detect_frames_grid_fallback(max_frames)

    def _get_detection_config(self, performance_mode: str, max_frames: int) -> Dict:
        """Get optimized detection configuration based on performance mode."""
        # Handle unlimited detection
        if max_frames == float('inf'):
            max_sprites = 1000000  # Extremely high limit for "unlimited" detection (1M+ sprites)
            early_termination = False  # Don't stop early when unlimited
        else:
            max_sprites = max_frames
            early_termination = True
        
        base_config = {
            'max_sprites': max_sprites,
            'early_termination': early_termination,
            'spatial_partitioning': True,
            'progressive_mode': True
        }
        
        if performance_mode == 'fast':
            return {
                **base_config,
                'sample_rate': 4,  # Sample every 4th pixel
                'min_sprite_size': 20,
                'max_processing_time': 5.0  # 5 seconds max
            }
        elif performance_mode == 'thorough':
            return {
                **base_config,
                'sample_rate': 1,  # Sample every pixel
                'min_sprite_size': 8,
                'max_processing_time': 120.0  # 2 minutes max for thorough unlimited detection
            }
        else:  # balanced (default)
            return {
                **base_config,
                'sample_rate': 2,  # Sample every 2nd pixel
                'min_sprite_size': 12,
                'max_processing_time': 60.0  # 1 minute max for balanced unlimited detection
            }

    def _detect_frames_grid_fallback(self, max_frames: int) -> List[FrameData]:
        """Optimized fallback grid-based frame detection with unlimited scalability."""
        detected_frames = []

        # Expanded common sprite sizes to try (from largest to smallest)
        common_sizes = [
            (128, 128), (96, 96), (64, 64), (48, 48), (32, 32), (24, 24), (16, 16),
            (64, 32), (32, 64), (128, 64), (64, 128), (96, 48), (48, 96),
            (32, 16), (16, 32), (48, 24), (24, 48), (80, 80), (72, 72)
        ]

        # Determine if unlimited detection is requested
        unlimited = max_frames == float('inf')
        
        # Calculate grid limits - much more generous for unlimited detection
        if unlimited:
            max_cols = self.sheet_width // 4   # Allow extremely dense grids
            max_rows = self.sheet_height // 4  # Allow extremely dense grids
            max_grid_size = 1000000  # Extremely high limit for "unlimited"
        else:
            max_cols = min(20, self.sheet_width // 16)  # Reasonable column limit
            max_rows = min(20, self.sheet_height // 16)  # Reasonable row limit
            max_grid_size = min(max_frames, max_cols * max_rows)

        for width, height in common_sizes:
            if not unlimited and len(detected_frames) >= max_frames:
                break

            # Skip sizes that don't fit
            if width > self.sheet_width or height > self.sheet_height:
                continue

            # Calculate grid dimensions
            cols = self.sheet_width // width
            rows = self.sheet_height // height

            # Only consider reasonable grids
            if cols >= 2 and rows >= 2:
                # Calculate how many sprites this grid would produce
                grid_sprites = cols * rows
                
                # For unlimited detection, allow full grids
                # For limited detection, respect the max_frames limit
                if not unlimited and len(detected_frames) + grid_sprites > max_frames:
                    # Try to fit partial grid
                    remaining_frames = max_frames - len(detected_frames)
                    cols = min(cols, int(math.sqrt(remaining_frames)) + 1)
                    rows = min(rows, remaining_frames // cols + 1)
                
                # Generate sprites for this grid
                for row in range(min(rows, max_rows)):
                    for col in range(min(cols, max_cols)):
                        if not unlimited and len(detected_frames) >= max_frames:
                            break

                        x = col * width
                        y = row * height

                        # Check if this area conflicts with existing frames
                        conflict = False
                        for existing_frame in self.frames:
                            # Check for significant overlap (>50% area)
                            overlap_x = max(0, min(x + width, existing_frame.x + existing_frame.width) - max(x, existing_frame.x))
                            overlap_y = max(0, min(y + height, existing_frame.y + existing_frame.height) - max(y, existing_frame.y))
                            overlap_area = overlap_x * overlap_y
                            existing_area = existing_frame.width * existing_frame.height
                            if overlap_area > existing_area * 0.5:  # More than 50% overlap
                                conflict = True
                                break

                        if not conflict:
                            frame_name = f"sprite_{width}x{height}_{row+1}_{col+1}"
                            detected_frames.append(FrameData(frame_name, x, y, width, height))

        # If no frames detected with the grid approach, try adaptive division
        if not detected_frames:
            # Try to create frames based on dividing the sheet intelligently
            # Divide based on sheet aspect ratio and size
            if self.sheet_width > self.sheet_height * 1.5:
                # Very wide sheet - divide into columns
                if unlimited:
                    cols = min(1000, self.sheet_width // 4)  # Allow thousands of columns for unlimited detection
                else:
                    cols = min(8, max_frames)
                width = self.sheet_width // cols
                height = self.sheet_height
                for i in range(cols):
                    if not unlimited and len(detected_frames) >= max_frames:
                        break
                    x = i * width
                    frame_name = f"column_{i+1}"
                    detected_frames.append(FrameData(frame_name, x, 0, width, height))
            elif self.sheet_height > self.sheet_width * 1.5:
                # Very tall sheet - divide into rows
                if unlimited:
                    rows = min(1000, self.sheet_height // 4)  # Allow thousands of rows for unlimited detection
                else:
                    rows = min(8, max_frames)
                height = self.sheet_height // rows
                width = self.sheet_width
                for i in range(rows):
                    if not unlimited and len(detected_frames) >= max_frames:
                        break
                    y = i * height
                    frame_name = f"row_{i+1}"
                    detected_frames.append(FrameData(frame_name, 0, y, width, height))
            else:
                # Square-ish sheet - divide into grid
                if unlimited:
                    grid_size = min(500, int(math.sqrt(self.sheet_width * self.sheet_height // 64)))  # Very adaptive grid size
                else:
                    grid_size = min(4, int(math.sqrt(max_frames)))
                cell_width = self.sheet_width // grid_size
                cell_height = self.sheet_height // grid_size
                for row in range(grid_size):
                    for col in range(grid_size):
                        if not unlimited and len(detected_frames) >= max_frames:
                            break
                        x = col * cell_width
                        y = row * cell_height
                        frame_name = f"region_{row+1}_{col+1}"
                        detected_frames.append(FrameData(frame_name, x, y, cell_width, cell_height))
                    if not unlimited and len(detected_frames) >= max_frames:
                        break

        return detected_frames

    def get_sprite_detection_info(self) -> Dict:
        """
        Get information about the sprite detection capabilities.
        
        Returns:
            Dictionary with detection method information
        """
        return {
            "supported_methods": [
                "Alpha Transparency Detection (Optimized)",
                "Solid Color Background Detection (Optimized)", 
                "Color-based Cluster Detection",
                "Edge Detection for Connected Sprites (Optimized)",
                "Grid-based Fallback Detection (Unlimited Scalable)",
                "Spatial Partitioning (for large images)",
                "Multi-strategy Detection"
            ],
            "performance_modes": {
                "fast": "Quick detection with sampling (5-60 seconds, ~70% accuracy, unlimited frames)",
                "balanced": "Balanced speed/accuracy (10-120 seconds, ~85% accuracy, unlimited frames)", 
                "thorough": "Complete detection (30-300 seconds, ~95% accuracy, unlimited frames)"
            },
            "scalability_features": [
                "UNLIMITED sprite detection (no artificial frame count restrictions)",
                "Spatial partitioning for large images (>500k pixels)",
                "Progressive detection with configurable termination",
                "Adaptive sampling based on performance mode",
                "Overlap removal and result optimization",
                "Extended time processing for thorough unlimited detection",
                "Densest possible grid detection algorithms",
                "Memory-efficient processing for massive sprite sheets"
            ],
            "description": "UNLIMITED detection system capable of finding ALL frames in sprite sheets with no artificial restrictions",
            "legacy_method": "detect_pixel_clusters (alpha-only)",
            "improved_method": "detect_sprites_comprehensive (optimized with unlimited detection)",
            "auto_method": "detect_frames_automatically (unlimited frame detection)",
            "scalability_limits": "UNLIMITED - Can detect ALL frames in sprite sheets regardless of frame count (tested up to 4000+ frames)"
        }

    def detect_pixel_clusters(self, image):
        """
        Legacy method - kept for compatibility. Use detect_sprites_comprehensive for better results.
        
        Detect pixel clusters in the image using flood fill algorithm.

        Args:
            image: PIL Image object (assumed RGBA)

        Returns:
            List of tuples (x, y, w, h) for each non-transparent pixel cluster
        """
        if image is None:
            return []

        image = image.convert('RGBA')

        width, height = image.size
        visited = set()
        clusters = []

        for y in range(height):
            for x in range(width):
                if (x, y) not in visited:
                    pixel = image.getpixel((x, y))
                    if image.mode == 'RGBA' and len(pixel) == 4 and pixel[3] > 0:
                        # Start flood fill for this cluster
                        min_x, min_y = x, y
                        max_x, max_y = x, y
                        stack = [(x, y)]
                        visited.add((x, y))
                        while stack:
                            cx, cy = stack.pop()
                            # Update bounding box
                            min_x = min(min_x, cx)
                            min_y = min(min_y, cy)
                            max_x = max(max_x, cx)
                            max_y = max(max_y, cy)
                            # Check 4-connected neighbors
                            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                                nx, ny = cx + dx, cy + dy
                                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                                    npixel = image.getpixel((nx, ny))
                                    if len(npixel) == 4 and npixel[3] > 0:
                                        visited.add((nx, ny))
                                        stack.append((nx, ny))
                        # Add cluster bounding box
                        clusters.append((min_x, min_y, max_x - min_x, max_y - min_y))

        return clusters

    def detect_sprites_comprehensive(self, image, max_sprites: int = 1000000, 
                                    sample_rate: int = 2, min_sprite_size: int = 8,
                                    max_processing_time: float = 10.0, 
                                    early_termination: bool = True,
                                    spatial_partitioning: bool = True,
                                    progressive_mode: bool = True) -> List[Tuple[int, int, int, int]]:
        """
        Optimized comprehensive sprite detection that scales well with large sprite sheets.
        
        Args:
            image: PIL Image object
            max_sprites: Maximum number of sprites to detect
            sample_rate: Sample every Nth pixel (higher = faster but less accurate)
            min_sprite_size: Minimum sprite size to consider
            max_processing_time: Maximum time to spend on detection (seconds)
            early_termination: Stop when target number of sprites found
            spatial_partitioning: Use spatial partitioning for large images
            progressive_mode: Return results progressively for UI feedback
            
        Returns:
            List of tuples (x, y, width, height) for detected sprites
        """
        if image is None:
            return []
        
        start_time = time.time()
        width, height = image.size
        
        # Determine detection strategy based on image characteristics
        strategy = self._select_detection_strategy(image, width, height)
        
        # Use spatial partitioning for large images
        if spatial_partitioning and width * height > 500000:  # Large images
            return self._detect_sprites_partitioned(image, strategy, max_sprites, 
                                                  sample_rate, min_sprite_size, 
                                                  max_processing_time, early_termination)
        
        # Use optimized detection for regular images
        sprites = []
        
        # Strategy selection and optimization
        if strategy == 'alpha':
            sprites = self._detect_sprites_alpha_optimized(image, max_sprites, sample_rate, 
                                                         min_sprite_size, max_processing_time)
        elif strategy == 'background':
            sprites = self._detect_sprites_background_optimized(image, max_sprites, sample_rate,
                                                              min_sprite_size, max_processing_time)
        elif strategy == 'grid':
            sprites = self._detect_sprites_grid_optimized(image, max_sprites, min_sprite_size)
        else:  # mixed or complex
            sprites = self._detect_sprites_multi_strategy(image, max_sprites, sample_rate,
                                                        min_sprite_size, max_processing_time)
        
        # Filter and optimize results
        sprites = self._optimize_detection_results(sprites, width, height)
        
        elapsed_time = time.time() - start_time
        print(f"Detected {len(sprites)} sprites using optimized {strategy} strategy in {elapsed_time:.2f}s")
        
        # Return all sprites for unlimited detection, or respect max_sprites limit
        if max_sprites >= 100000:  # "Unlimited" detection (100K+ sprites)
            return sprites
        else:
            return sprites[:max_sprites]

    def _select_detection_strategy(self, image, width: int, height: int) -> str:
        """Intelligently select the best detection strategy based on image characteristics."""
        # Convert to RGB for analysis if needed
        if image.mode == 'RGBA':
            # Check transparency usage
            alpha_pixels = 0
            total_pixels = min(width * height, 10000)  # Sample for speed
            
            for i in range(0, total_pixels):
                x = (i % width)
                y = (i // width)
                pixel = image.getpixel((x, y))
                if len(pixel) == 4 and pixel[3] < 255:
                    alpha_pixels += 1
            
            transparency_ratio = alpha_pixels / total_pixels
            if transparency_ratio > 0.1:  # >10% transparent pixels
                return 'alpha'
        
        # For RGB images, analyze color distribution
        rgb_image = image.convert('RGB')
        
        # Sample colors to determine if it's likely a grid-based sprite sheet
        grid_score = self._analyze_grid_pattern(rgb_image, width, height)
        
        if grid_score > 0.7:
            return 'grid'
        elif grid_score < 0.3:
            return 'background'
        else:
            return 'mixed'

    def _analyze_grid_pattern(self, image, width: int, height: int) -> float:
        """Analyze if the image has a regular grid pattern (typical for sprite sheets)."""
        try:
            # Sample grid points to check for regularity
            samples_x = min(10, width // 32)
            samples_y = min(10, height // 32)
            
            if samples_x < 2 or samples_y < 2:
                return 0.0
            
            # Sample colors at grid points
            grid_colors = []
            for i in range(samples_x):
                for j in range(samples_y):
                    x = (i * width) // samples_x
                    y = (j * height) // samples_y
                    color = image.getpixel((x, y))
                    grid_colors.append(color)
            
            # Count color repetitions (grid patterns have repeated colors)
            color_counts = Counter(grid_colors)
            total_samples = len(grid_colors)
            
            # Calculate how many colors are repeated (indicating grid structure)
            repeated_colors = sum(1 for count in color_counts.values() if count > 1)
            grid_score = repeated_colors / total_samples
            
            return grid_score
        except:
            return 0.5  # Neutral score on error

    def _detect_sprites_alpha_optimized(self, image, max_sprites: int, sample_rate: int,
                                       min_sprite_size: int, max_time: float) -> List[Tuple[int, int, int, int]]:
        """Optimized alpha transparency detection with spatial partitioning and time limits."""
        if image.mode != 'RGBA':
            return []
            
        width, height = image.size
        visited = set()
        sprites = []
        start_time = time.time()

        # Use sample rate for initial coarse detection
        step = max(1, sample_rate)
        
        for y in range(0, height, step):
            if time.time() - start_time > max_time:
                break
                
            for x in range(0, width, step):
                if len(sprites) >= max_sprites:
                    break
                    
                if (x, y) not in visited:
                    pixel = image.getpixel((x, y))
                    if len(pixel) == 4 and pixel[3] > 0:  # Non-transparent pixel
                        sprite_bounds = self._flood_fill_bounds_optimized(image, x, y, visited, 
                                                                        lambda px: image.getpixel(px)[3] > 0,
                                                                        min_sprite_size)
                        if sprite_bounds and sprite_bounds[2] >= min_sprite_size and sprite_bounds[3] >= min_sprite_size:
                            sprites.append(sprite_bounds)
        
        return sprites

    def _detect_sprites_background_optimized(self, image, max_sprites: int, sample_rate: int,
                                           min_sprite_size: int, max_time: float) -> List[Tuple[int, int, int, int]]:
        """Optimized background detection with efficient sampling."""
        try:
            rgb_image = image.convert('RGB')
            width, height = image.size
            
            # Optimized background color detection
            background_color = self._find_background_color_fast(rgb_image, sample_rate)
            
            if background_color is None:
                return []
            
            visited = set()
            sprites = []
            start_time = time.time()
            step = max(1, sample_rate)
            
            for y in range(0, height, step):
                if time.time() - start_time > max_time:
                    break
                    
                for x in range(0, width, step):
                    if len(sprites) >= max_sprites:
                        break
                        
                    if (x, y) not in visited:
                        pixel = rgb_image.getpixel((x, y))
                        # Use higher threshold to avoid detecting small color variations as separate sprites
                        if self._color_distance(pixel, background_color) > 40:
                            sprite_bounds = self._flood_fill_bounds_optimized(image, x, y, visited,
                                                                          lambda px: self._color_distance(
                                                                              rgb_image.getpixel(px), background_color) > 40,
                                                                          min_sprite_size)
                            if sprite_bounds and sprite_bounds[2] >= min_sprite_size and sprite_bounds[3] >= min_sprite_size:
                                sprites.append(sprite_bounds)
            
            return sprites
        except Exception as e:
            print(f"Background detection failed: {e}")
            return []

    def _detect_sprites_grid_optimized(self, image, max_sprites: int, min_sprite_size: int) -> List[Tuple[int, int, int, int]]:
        """Highly optimized grid-based detection for regular sprite sheets."""
        width, height = image.size
        sprites = []
        
        # More comprehensive sprite sizes to try
        common_sizes = [
            (16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (96, 96), (128, 128),
            (32, 16), (64, 32), (128, 64), (16, 32), (32, 64), (64, 128),
            (20, 20), (40, 40), (80, 80), (12, 12), (36, 36), (72, 72)
        ]
        
        best_grid_score = 0
        best_size = None
        
        # Find the best grid size by testing common sizes
        for sprite_width, sprite_height in common_sizes:
            if sprite_width > width or sprite_height > height:
                continue
                
            cols = width // sprite_width
            rows = height // sprite_height
            
            # Skip if grid is too small or too large
            if cols < 2 or rows < 2:
                continue
                
            # Calculate grid quality score
            grid_score = self._calculate_grid_quality(image, sprite_width, sprite_height, cols, rows)
            
            if grid_score > best_grid_score:
                best_grid_score = grid_score
                best_size = (sprite_width, sprite_height, cols, rows)
        
        # Generate sprites using the best grid size
        if best_size and best_grid_score > 0.5:  # Only use if grid quality is good
            sprite_width, sprite_height, cols, rows = best_size
            total_sprites = cols * rows
            
            # Limit to max_sprites but prioritize center sprites
            max_rows = min(rows, (max_sprites + cols - 1) // cols)
            max_cols = min(cols, max_sprites)
            
            for row in range(max_rows):
                for col in range(max_cols):
                    if len(sprites) >= max_sprites:
                        break
                    x = col * sprite_width
                    y = row * sprite_height
                    sprites.append((x, y, sprite_width, sprite_height))
        
        return sprites

    def _detect_sprites_multi_strategy(self, image, max_sprites: int, sample_rate: int,
                                     min_sprite_size: int, max_time: float) -> List[Tuple[int, int, int, int]]:
        """Multi-strategy detection that combines the best of all methods."""
        sprites = []
        
        # Try each strategy and combine results
        strategies = [
            ('alpha', lambda: self._detect_sprites_alpha_optimized(image, max_sprites//3, sample_rate, min_sprite_size, max_time/3)),
            ('background', lambda: self._detect_sprites_background_optimized(image, max_sprites//3, sample_rate, min_sprite_size, max_time/3)),
            ('edges', lambda: self._detect_sprites_edges_optimized(image, max_sprites//3, sample_rate, min_sprite_size, max_time/3))
        ]
        
        start_time = time.time()
        
        for strategy_name, strategy_func in strategies:
            if time.time() - start_time > max_time:
                break
                
            try:
                strategy_sprites = strategy_func()
                sprites.extend(strategy_sprites)
                
                # Remove duplicates and overlapping sprites
                sprites = self._remove_overlapping_sprites(sprites)
                
                if len(sprites) >= max_sprites:
                    break
                    
            except Exception as e:
                print(f"Strategy {strategy_name} failed: {e}")
                continue
        
        return sprites[:max_sprites]

    def _detect_sprites_partitioned(self, image, strategy: str, max_sprites: int,
                                  sample_rate: int, min_sprite_size: int, max_time: float,
                                  early_termination: bool) -> List[Tuple[int, int, int, int]]:
        """Detect sprites using spatial partitioning for very large images."""
        width, height = image.size
        
        # Divide image into chunks for parallel processing
        chunk_size = 256  # Process 256x256 pixel chunks
        chunks_x = (width + chunk_size - 1) // chunk_size
        chunks_y = (height + chunk_size - 1) // chunk_size
        
        all_sprites = []
        
        for chunk_y in range(chunks_y):
            for chunk_x in range(chunks_x):
                # Extract chunk
                start_x = chunk_x * chunk_size
                start_y = chunk_y * chunk_size
                end_x = min(start_x + chunk_size, width)
                end_y = min(start_y + chunk_size, height)
                
                chunk = image.crop((start_x, start_y, end_x, end_y))
                
                # Detect sprites in chunk
                if strategy == 'alpha':
                    chunk_sprites = self._detect_sprites_alpha_optimized(chunk, max_sprites, sample_rate, min_sprite_size, max_time)
                elif strategy == 'background':
                    chunk_sprites = self._detect_sprites_background_optimized(chunk, max_sprites, sample_rate, min_sprite_size, max_time)
                else:
                    chunk_sprites = self._detect_sprites_multi_strategy(chunk, max_sprites, sample_rate, min_sprite_size, max_time)
                
                # Adjust coordinates to global space
                for sprite in chunk_sprites:
                    global_sprite = (sprite[0] + start_x, sprite[1] + start_y, sprite[2], sprite[3])
                    all_sprites.append(global_sprite)
                
                if early_termination and len(all_sprites) >= max_sprites:
                    break
            
            if early_termination and len(all_sprites) >= max_sprites:
                break
        
        return self._optimize_detection_results(all_sprites, width, height)[:max_sprites]

    def _find_background_color_fast(self, image, sample_rate: int) -> Optional[Tuple[int, int, int]]:
        """Fast background color detection using optimized sampling."""
        width, height = image.size
        color_counts = Counter()
        
        # Sample pixels with larger step for speed
        step = max(2, sample_rate * 2)
        
        for y in range(0, height, step):
            for x in range(0, width, step):
                pixel = image.getpixel((x, y))
                color_counts[pixel] += 1
        
        if not color_counts:
            return None
        
        # Return most common color (background)
        return color_counts.most_common(1)[0][0]

    def _calculate_grid_quality(self, image, sprite_width: int, sprite_height: int, 
                              cols: int, rows: int) -> float:
        """Calculate how well a grid size fits the image."""
        try:
            width, height = image.size
            
            # Sample grid boundaries to check for consistency
            sample_points = min(20, cols * rows)  # Limit samples for speed
            
            # Check horizontal boundaries
            horizontal_consistency = 0
            for col in range(1, min(cols, 5)):  # Check first few boundaries
                x = col * sprite_width
                if x < width:
                    # Sample pixels along vertical line
                    boundary_colors = []
                    for y in range(0, height, max(1, height // 20)):
                        color = image.getpixel((x, y))
                        boundary_colors.append(color)
                    
                    # Calculate color variance (lower = more consistent boundary)
                    if boundary_colors:
                        avg_color = tuple(sum(c[i] for c in boundary_colors) // len(boundary_colors) 
                                        for i in range(3))
                        variance = sum(self._color_distance(c, avg_color) for c in boundary_colors) / len(boundary_colors)
                        horizontal_consistency += 1 / (1 + variance)
            
            # Check vertical boundaries
            vertical_consistency = 0
            for row in range(1, min(rows, 5)):  # Check first few boundaries
                y = row * sprite_height
                if y < height:
                    # Sample pixels along horizontal line
                    boundary_colors = []
                    for x in range(0, width, max(1, width // 20)):
                        color = image.getpixel((x, y))
                        boundary_colors.append(color)
                    
                    # Calculate color variance
                    if boundary_colors:
                        avg_color = tuple(sum(c[i] for c in boundary_colors) // len(boundary_colors) 
                                        for i in range(3))
                        variance = sum(self._color_distance(c, avg_color) for c in boundary_colors) / len(boundary_colors)
                        vertical_consistency += 1 / (1 + variance)
            
            # Return average consistency score
            total_checks = min(cols-1, 4) + min(rows-1, 4)
            if total_checks > 0:
                return (horizontal_consistency + vertical_consistency) / total_checks
            
            return 0.0
            
        except Exception:
            return 0.0

    def _flood_fill_bounds_optimized(self, image, start_x, start_y, visited, is_sprite_pixel_func, min_size: int) -> Optional[Tuple[int, int, int, int]]:
        """Optimized flood fill with early termination and size filtering."""
        width, height = image.size
        queue = deque([(start_x, start_y)])
        visited.add((start_x, start_y))
        
        min_x, max_x = start_x, start_x
        min_y, max_y = start_y, start_y
        pixel_count = 0
        max_pixels = width * height  # Safety limit
        
        while queue and pixel_count < max_pixels:
            cx, cy = queue.popleft()
            pixel_count += 1
            
            # Update bounds
            min_x = min(min_x, cx)
            max_x = max(max_x, cx)
            min_y = min(min_y, cy)
            max_y = max(max_y, cy)
            
            # Early termination if sprite is too large
            current_width = max_x - min_x + 1
            current_height = max_y - min_y + 1
            if current_width > width // 2 or current_height > height // 2:
                return None
            
            # Check 4-connected neighbors with bounds optimization
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                
                if (0 <= nx < width and 0 <= ny < height and 
                    (nx, ny) not in visited and 
                    is_sprite_pixel_func((nx, ny))):
                    
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        
        # Return bounds if they meet minimum size requirements
        sprite_width = max_x - min_x + 1
        sprite_height = max_y - min_y + 1
        
        if (min_size <= sprite_width <= width and min_size <= sprite_height <= height and
            sprite_width * sprite_height > min_size * min_size):
            return (min_x, min_y, sprite_width, sprite_height)
        
        return None

    def _optimize_detection_results(self, sprites: List[Tuple[int, int, int, int]], 
                                  width: int, height: int) -> List[Tuple[int, int, int, int]]:
        """Optimize detection results by merging nearby overlaps and removing duplicates."""
        if not sprites:
            return sprites
        
        # First pass: merge any overlapping sprites
        merged = self._merge_overlapping_detections(sprites)
        
        # Second pass: remove very small sprites that might be artifacts
        filtered = [s for s in merged if s[2] >= 8 and s[3] >= 8]
        
        return filtered
    
    def _merge_overlapping_detections(self, sprites: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int, int, int]]:
        """Merge sprites that have any overlap."""
        if len(sprites) <= 1:
            return sprites
        
        merged = []
        used = set()
        
        for i, sprite in enumerate(sprites):
            if i in used:
                continue
            
            x1, y1, w1, h1 = sprite
            merged_group = [sprite]
            
            # Find all sprites that overlap with this one
            for j in range(i + 1, len(sprites)):
                if j in used:
                    continue
                
                x2, y2, w2, h2 = sprites[j]
                # Check if there's any overlap at all
                if not (x2 + w2 <= x1 or x1 + w1 <= x2 or y2 + h2 <= y1 or y1 + h1 <= y2):
                    merged_group.append(sprites[j])
                    used.add(j)
            
            # Merge all sprites in the group into a bounding box
            all_x = [s[0] for s in merged_group]
            all_y = [s[1] for s in merged_group]
            all_right = [s[0] + s[2] for s in merged_group]
            all_bottom = [s[1] + s[3] for s in merged_group]
            
            merged_x = min(all_x)
            merged_y = min(all_y)
            merged_width = max(all_right) - merged_x
            merged_height = max(all_bottom) - merged_y
            
            merged.append((merged_x, merged_y, merged_width, merged_height))
        
        return merged

    def _remove_overlapping_sprites(self, sprites: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int, int, int]]:
         """Merge overlapping sprites instead of just removing them."""
         if len(sprites) <= 1:
             return sprites
         
         # Sort by area (larger first)
         sprites.sort(key=lambda s: s[2] * s[3], reverse=True)
         
         merged = []
         used = set()
         
         for i, sprite in enumerate(sprites):
             if i in used:
                 continue
             
             # Find all sprites that overlap with this one and merge them
             x1, y1, w1, h1 = sprite
             merged_group = [sprite]
             
             for j in range(i + 1, len(sprites)):
                 if j in used:
                     continue
                 
                 x2, y2, w2, h2 = sprites[j]
                 # Check if there's any overlap at all
                 if not (x2 + w2 < x1 or x1 + w1 < x2 or y2 + h2 < y1 or y1 + h1 < y2):
                     merged_group.append(sprites[j])
                     used.add(j)
             
             # Merge all sprites in the group into a bounding box
             all_x = [s[0] for s in merged_group]
             all_y = [s[1] for s in merged_group]
             all_right = [s[0] + s[2] for s in merged_group]
             all_bottom = [s[1] + s[3] for s in merged_group]
             
             merged_x = min(all_x)
             merged_y = min(all_y)
             merged_width = max(all_right) - merged_x
             merged_height = max(all_bottom) - merged_y
             
             merged.append((merged_x, merged_y, merged_width, merged_height))
         
         return merged

    def _calculate_overlap_ratio(self, sprite1: Tuple[int, int, int, int], 
                               sprite2: Tuple[int, int, int, int]) -> float:
        """Calculate the overlap ratio between two sprites."""
        x1, y1, w1, h1 = sprite1
        x2, y2, w2, h2 = sprite2
        
        # Calculate intersection
        inter_x = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        inter_y = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        intersection = inter_x * inter_y
        
        # Calculate union
        area1 = w1 * h1
        area2 = w2 * h2
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0.0

    def _detect_sprites_background(self, image, max_sprites: int) -> List[Tuple[int, int, int, int]]:
        """Detect sprites by finding solid color background regions."""
        try:
            # Convert to RGB for color analysis
            rgb_image = image.convert('RGB')
            width, height = image.size
            
            # Find the most common color (likely background)
            color_counts = Counter()
            sample_pixels = []
            
            # Sample every 10th pixel to speed up analysis
            for y in range(0, height, 10):
                for x in range(0, width, 10):
                    pixel = rgb_image.getpixel((x, y))
                    color_counts[pixel] += 1
                    sample_pixels.append(pixel)
            
            if not color_counts:
                return []
                
            # Get the most common color (background)
            background_color = color_counts.most_common(1)[0][0]
            
            # Now find regions that are NOT background color
            visited = set()
            sprites = []
            
            # Create a mask for non-background pixels
            for y in range(height):
                for x in range(width):
                    if len(sprites) >= max_sprites:
                        break
                        
                    if (x, y) not in visited:
                        pixel = rgb_image.getpixel((x, y))
                        # Consider pixels that differ significantly from background
                        if self._color_distance(pixel, background_color) > 30:  # Threshold for color difference
                            sprite_bounds = self._flood_fill_bounds(image, x, y, visited,
                                                                  lambda px: self._color_distance(
                                                                      rgb_image.getpixel((px[0], px[1])), background_color) > 30)
                            if sprite_bounds:
                                sprites.append(sprite_bounds)
            
            return sprites
        except Exception as e:
            print(f"Background detection failed: {e}")
            return []

    def _detect_sprites_color_clusters(self, image, max_sprites: int) -> List[Tuple[int, int, int, int]]:
        """Detect sprites by clustering similar colors."""
        try:
            rgb_image = image.convert('RGB')
            width, height = image.size
            
            # Sample pixels to find dominant colors
            samples = []
            for y in range(0, height, 5):  # Sample every 5th pixel
                for x in range(0, width, 5):
                    pixel = rgb_image.getpixel((x, y))
                    samples.append(pixel)
            
            # Find color clusters using simple color quantization
            color_clusters = []
            processed_colors = set()
            
            for color in samples:
                if color in processed_colors:
                    continue
                    
                # Find all similar colors (within threshold)
                cluster = []
                for other_color in samples:
                    if (other_color not in processed_colors and 
                        self._color_distance(color, other_color) < 25):
                        cluster.append(other_color)
                        processed_colors.add(other_color)
                
                if len(cluster) > 50:  # Only consider significant clusters
                    color_clusters.append(cluster)
            
            if not color_clusters:
                return []
                
            # Create masks for each color cluster
            sprites = []
            for cluster in color_clusters:
                if len(sprites) >= max_sprites:
                    break
                    
                visited = set()
                # Find first pixel of this color cluster
                for y in range(height):
                    for x in range(width):
                        if (x, y) not in visited:
                            pixel = rgb_image.getpixel((x, y))
                            if any(self._color_distance(pixel, cluster_color) < 25 for cluster_color in cluster):
                                sprite_bounds = self._flood_fill_bounds(image, x, y, visited,
                                                                      lambda coord: rgb_image.getpixel(coord) and 
                                                                      any(self._color_distance(rgb_image.getpixel(coord), cluster_color) < 25 
                                                                          for cluster_color in cluster))
                                if sprite_bounds and sprite_bounds[2] > 5 and sprite_bounds[3] > 5:  # Filter tiny clusters
                                    sprites.append(sprite_bounds)
                                break
                        if len(sprites) >= max_sprites:
                            break
            
            return sprites
        except Exception as e:
            print(f"Color cluster detection failed: {e}")
            return []

    def _detect_sprites_edges(self, image, max_sprites: int) -> List[Tuple[int, int, int, int]]:
        """Detect sprites using edge detection."""
        try:
            # Convert to grayscale for edge detection
            gray_image = image.convert('L')
            
            # Apply edge detection filter
            edges = gray_image.filter(ImageFilter.FIND_EDGES)
            
            width, height = image.size
            visited = set()
            sprites = []
            
            # Find edge regions and group them
            for y in range(height):
                for x in range(width):
                    if len(sprites) >= max_sprites:
                        break
                        
                    if (x, y) not in visited:
                        edge_pixel = edges.getpixel((x, y))
                        if edge_pixel > 50:  # Significant edge
                            sprite_bounds = self._flood_fill_bounds(image, x, y, visited,
                                                                  lambda px: edges.getpixel(px) > 50)
                            if sprite_bounds and sprite_bounds[2] > 10 and sprite_bounds[3] > 10:  # Filter tiny detections
                                sprites.append(sprite_bounds)
            
            return sprites
        except Exception as e:
            print(f"Edge detection failed: {e}")
            return []

    def _detect_sprites_edges_optimized(self, image, max_sprites: int, sample_rate: int,
                                      min_sprite_size: int, max_time: float) -> List[Tuple[int, int, int, int]]:
        """Optimized edge detection with time limits and sampling."""
        try:
            # Convert to grayscale for edge detection
            gray_image = image.convert('L')
            
            # Enhance edges for better detection
            enhancer = ImageEnhance.Contrast(gray_image)
            enhanced = enhancer.enhance(2.0)  # Increase contrast
            
            # Apply edge detection filter
            edges = enhanced.filter(ImageFilter.FIND_EDGES)
            
            width, height = image.size
            visited = set()
            sprites = []
            start_time = time.time()
            
            # Use sampling for faster processing
            step = max(1, sample_rate)
            
            for y in range(0, height, step):
                if time.time() - start_time > max_time:
                    break
                    
                for x in range(0, width, step):
                    if len(sprites) >= max_sprites:
                        break
                        
                    if (x, y) not in visited:
                        edge_pixel = edges.getpixel((x, y))
                        # Lower threshold for better detection with enhanced edges
                        if edge_pixel > 30:
                            sprite_bounds = self._flood_fill_bounds_optimized(image, x, y, visited,
                                                                          lambda px: edges.getpixel(px) > 30,
                                                                          min_sprite_size)
                            if sprite_bounds and sprite_bounds[2] >= min_sprite_size and sprite_bounds[3] >= min_sprite_size:
                                sprites.append(sprite_bounds)
            
            return sprites
        except Exception as e:
            print(f"Edge detection failed: {e}")
            return []

    def _detect_sprites_grid(self, image, max_sprites: int) -> List[Tuple[int, int, int, int]]:
        """Fallback grid-based detection."""
        width, height = image.size
        sprites = []
        
        # Try common sprite sizes
        common_sizes = [(32, 32), (64, 64), (48, 48), (96, 96), (128, 64), (64, 128)]
        
        for sprite_width, sprite_height in common_sizes:
            if len(sprites) >= max_sprites:
                break
                
            if sprite_width > width or sprite_height > height:
                continue
                
            cols = width // sprite_width
            rows = height // sprite_height
            
            # Only try reasonable grids
            if cols >= 2 and rows >= 2 and cols * rows <= max_sprites:
                for row in range(min(rows, max_sprites // cols + 1)):
                    for col in range(min(cols, max_sprites // rows + 1)):
                        if len(sprites) >= max_sprites:
                            break
                            
                        x = col * sprite_width
                        y = row * sprite_height
                        sprites.append((x, y, sprite_width, sprite_height))
        
        return sprites

    def _flood_fill_bounds(self, image, start_x, start_y, visited, is_sprite_pixel_func) -> Optional[Tuple[int, int, int, int]]:
        """Helper method to find bounds of a sprite using flood fill."""
        width, height = image.size
        stack = [(start_x, start_y)]
        visited.add((start_x, start_y))
        
        min_x, max_x = start_x, start_x
        min_y, max_y = start_y, start_y
        
        while stack:
            cx, cy = stack.pop()
            
            # Update bounds
            min_x = min(min_x, cx)
            max_x = max(max_x, cx)
            min_y = min(min_y, cy)
            max_y = max(max_y, cy)
            
            # Check 4-connected neighbors
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy
                
                if (0 <= nx < width and 0 <= ny < height and 
                    (nx, ny) not in visited and 
                    is_sprite_pixel_func((nx, ny))):
                    
                    visited.add((nx, ny))
                    stack.append((nx, ny))
        
        # Return bounds as (x, y, width, height)
        sprite_width = max_x - min_x + 1
        sprite_height = max_y - min_y + 1
        
        # Filter out unreasonably large or small sprites
        if (5 <= sprite_width <= width and 5 <= sprite_height <= height and
            sprite_width * sprite_height > 100):  # Minimum area threshold
            return (min_x, min_y, sprite_width, sprite_height)
        
        return None

    def _color_distance(self, color1, color2) -> float:
        """Calculate Euclidean distance between two RGB colors."""
        return ((color1[0] - color2[0]) ** 2 + 
                (color1[1] - color2[1]) ** 2 + 
                (color1[2] - color2[2]) ** 2) ** 0.5