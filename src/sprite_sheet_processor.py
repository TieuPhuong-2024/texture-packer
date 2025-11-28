"""
Sprite Sheet Processor Module
Core functionality for managing sprite sheets, frames, and data export.
"""

import json
import csv
import xml.etree.ElementTree as ET
import os
from PIL import Image, ImageDraw, ImageTk, ImageFilter
from typing import List, Dict, Tuple, Optional
import tkinter as tk
from tkinter import messagebox
from collections import Counter


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

    def detect_frames_automatically(self, max_frames: int = 20) -> List[FrameData]:
        """
        Automatically detect potential sprite frames in the sprite sheet.
        Uses comprehensive multi-strategy detection to work with any sprite sheet type.

        Args:
            max_frames: Maximum number of frames to suggest (to avoid UI clutter)

        Returns:
            List of detected FrameData objects that can be selected
        """
        if self.image is None:
            return []

        # Try comprehensive sprite detection first
        sprite_bounds = self.detect_sprites_comprehensive(self.image, max_frames)
        
        if sprite_bounds:
            # Convert bounds to FrameData objects
            detected_frames = []
            for i, (x, y, width, height) in enumerate(sprite_bounds):
                frame_name = f"detected_sprite_{i+1:02d}"
                detected_frames.append(FrameData(frame_name, x, y, width, height))
            
            if len(detected_frames) > 0:
                print(f"Comprehensive detection found {len(detected_frames)} sprites")
                return detected_frames[:max_frames]

        # Fallback to grid-based detection if comprehensive detection fails
        print("Falling back to grid-based detection...")
        return self._detect_frames_grid_fallback(max_frames)

    def _detect_frames_grid_fallback(self, max_frames: int) -> List[FrameData]:
        """Fallback grid-based frame detection."""
        detected_frames = []

        # Common sprite sizes to try (from largest to smallest)
        common_sizes = [
            (64, 64), (32, 32), (48, 48), (96, 96), (128, 128),
            (64, 32), (32, 64), (64, 128), (128, 64), (32, 48), (48, 32)
        ]

        for width, height in common_sizes:
            if len(detected_frames) >= max_frames:
                break

            # Skip sizes that don't fit
            if width > self.sheet_width or height > self.sheet_height:
                continue

            # Calculate grid dimensions
            cols = self.sheet_width // width
            rows = self.sheet_height // height

            # Only consider reasonable grids (at least 2x2, but not too many)
            if cols >= 2 and rows >= 2 and cols * rows <= 16:  # Limit to avoid too many frames
                for row in range(min(rows, 4)):  # Limit rows to avoid clutter
                    for col in range(min(cols, 4)):  # Limit cols to avoid clutter
                        if len(detected_frames) >= max_frames:
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

        # If no frames detected with the grid approach, try a simpler approach
        if not detected_frames:
            # Try to create frames based on dividing the sheet into equal parts
            for i in range(min(4, max_frames)):  # Up to 4 frames
                if self.sheet_width > self.sheet_height:
                    # Wide sheet - divide horizontally
                    width = self.sheet_width // 4
                    height = self.sheet_height
                    x = i * width
                    y = 0
                else:
                    # Tall sheet - divide vertically
                    width = self.sheet_width
                    height = self.sheet_height // 4
                    x = 0
                    y = i * height

                # Check bounds
                if x + width <= self.sheet_width and y + height <= self.sheet_height:
                    frame_name = f"region_{i+1}"
                    detected_frames.append(FrameData(frame_name, x, y, width, height))

        return detected_frames

    def get_sprite_detection_info(self) -> Dict:
        """
        Get information about the sprite detection capabilities.
        
        Returns:
            Dictionary with detection method information
        """
        return {
            "supported_methods": [
                "Alpha Transparency Detection",
                "Solid Color Background Detection", 
                "Color-based Cluster Detection",
                "Edge Detection for Connected Sprites",
                "Grid-based Fallback Detection"
            ],
            "description": "Comprehensive detection system that automatically tries multiple strategies to work with any sprite sheet type",
            "legacy_method": "detect_pixel_clusters (alpha-only)",
            "improved_method": "detect_sprites_comprehensive",
            "auto_method": "detect_frames_automatically (uses comprehensive detection)"
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

    def detect_sprites_comprehensive(self, image, max_sprites: int = 50) -> List[Tuple[int, int, int, int]]:
        """
        Comprehensive sprite detection that tries multiple strategies to work with any sprite sheet.
        
        Args:
            image: PIL Image object
            max_sprites: Maximum number of sprites to detect
            
        Returns:
            List of tuples (x, y, width, height) for detected sprites
        """
        if image is None:
            return []
        
        # Strategy 1: Try alpha transparency detection
        sprites = self._detect_sprites_alpha(image, max_sprites)
        if len(sprites) > 0:
            print(f"Detected {len(sprites)} sprites using alpha transparency")
            return sprites[:max_sprites]
        
        # Strategy 2: Try solid color background detection
        sprites = self._detect_sprites_background(image, max_sprites)
        if len(sprites) > 0:
            print(f"Detected {len(sprites)} sprites using background detection")
            return sprites[:max_sprites]
        
        # Strategy 3: Try color-based cluster detection
        sprites = self._detect_sprites_color_clusters(image, max_sprites)
        if len(sprites) > 0:
            print(f"Detected {len(sprites)} sprites using color clustering")
            return sprites[:max_sprites]
        
        # Strategy 4: Try edge detection for connected sprites
        sprites = self._detect_sprites_edges(image, max_sprites)
        if len(sprites) > 0:
            print(f"Detected {len(sprites)} sprites using edge detection")
            return sprites[:max_sprites]
        
        # Strategy 5: Fallback to grid-based detection
        sprites = self._detect_sprites_grid(image, max_sprites)
        print(f"Detected {len(sprites)} sprites using grid-based fallback")
        return sprites[:max_sprites]

    def _detect_sprites_alpha(self, image, max_sprites: int) -> List[Tuple[int, int, int, int]]:
        """Detect sprites using alpha transparency."""
        if image.mode != 'RGBA':
            return []
            
        width, height = image.size
        visited = set()
        sprites = []

        for y in range(height):
            for x in range(width):
                if len(sprites) >= max_sprites:
                    break
                    
                if (x, y) not in visited:
                    pixel = image.getpixel((x, y))
                    if len(pixel) == 4 and pixel[3] > 0:  # Non-transparent pixel
                        sprite_bounds = self._flood_fill_bounds(image, x, y, visited, 
                                                              lambda px: len(px) == 4 and px[3] > 0)
                        if sprite_bounds:
                            sprites.append(sprite_bounds)
        
        return sprites

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