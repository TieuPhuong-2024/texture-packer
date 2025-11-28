"""
Sprite Sheet Processor Module
Core functionality for managing sprite sheets, frames, and data export.
"""

import json
import csv
import xml.etree.ElementTree as ET
import os
from PIL import Image, ImageDraw, ImageTk
from typing import List, Dict, Tuple, Optional
import tkinter as tk
from tkinter import messagebox


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