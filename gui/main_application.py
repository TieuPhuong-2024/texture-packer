"""
Main GUI Application for Sprite Sheet Manager
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from PIL import Image, ImageTk
from src.sprite_sheet_processor import SpriteSheetProcessor, FrameData


class MainApplication(tk.Tk):
    """Main application window for sprite sheet management."""
    
    def __init__(self):
        super().__init__()
        self.processor = SpriteSheetProcessor()
        self.zoom_level = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        self.detected_frames = []  # Store automatically detected frames
        self.detected_boxes = []
        self.selected_detected_index = None
        self.setup_ui()
        self.setup_menu()
        self.current_frame_name = None
        
    def setup_ui(self):
        """Set up the user interface."""
        self.title("Sprite Sheet Manager")
        self.geometry("1200x800")
        self.minsize(1000, 600)
        
        # Create main container
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Sprite sheet tab
        self.sprite_sheet_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.sprite_sheet_frame, text="Sprite Sheet")
        self.setup_sprite_sheet_tab()
        
        # Frame manager tab
        self.frame_manager_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_manager_frame, text="Frame Manager")
        self.setup_frame_manager_tab()
        
        # Export tab
        self.export_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.export_frame, text="Export")
        self.setup_export_tab()
        
        # Status bar
        self.status_bar = ttk.Label(self, text="Ready", relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_menu(self):
        """Set up the application menu."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Sprite Sheet...", command=self.load_sprite_sheet, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Sprite Sheet...", command=self.save_sprite_sheet, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Load Frame Data...", command=self.load_frame_data)
        file_menu.add_separator()
        file_menu.add_command(label="Create Sample Sheet", command=self.create_sample_sheet)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Clear All Frames", command=self.clear_frames)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Bind keyboard shortcuts
        self.bind('<Control-o>', lambda e: self.load_sprite_sheet())
        self.bind('<Control-s>', lambda e: self.save_sprite_sheet())
        
    def setup_sprite_sheet_tab(self):
        """Set up the sprite sheet viewer tab."""
        # Create a frame for the sprite sheet viewer
        viewer_frame = ttk.LabelFrame(self.sprite_sheet_frame, text="Sprite Sheet Viewer")
        viewer_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas for image display
        self.canvas = tk.Canvas(viewer_frame, bg="white", scrollregion=(0, 0, 800, 600))
        
        # Scrollbars
        h_scrollbar = ttk.Scrollbar(viewer_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scrollbar = ttk.Scrollbar(viewer_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        
        self.canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        viewer_frame.grid_rowconfigure(0, weight=1)
        viewer_frame.grid_columnconfigure(0, weight=1)
        
        # Frame selection tools
        selection_frame = ttk.LabelFrame(self.sprite_sheet_frame, text="Frame Selection & Zoom")
        selection_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(selection_frame, text="Frame Name:").grid(row=0, column=0, padx=5, pady=5)
        self.frame_name_entry = ttk.Entry(selection_frame, width=20)
        self.frame_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(selection_frame, text="Add Frame", command=self.add_frame_from_selection).grid(row=0, column=2, padx=5, pady=5)
        
        # Performance mode selection
        ttk.Label(selection_frame, text="Performance:").grid(row=0, column=3, padx=(20,5), pady=5)
        self.performance_mode = ttk.Combobox(selection_frame, values=["Fast", "Balanced", "Thorough"], width=10, state="readonly")
        self.performance_mode.set("Balanced")
        self.performance_mode.grid(row=0, column=4, padx=5, pady=5)
        
        ttk.Button(selection_frame, text="Auto Detect", command=self.auto_detect_frames).grid(row=0, column=5, padx=5, pady=5)
        ttk.Button(selection_frame, text="Clear Detected", command=self.clear_detected_frames).grid(row=0, column=6, padx=5, pady=5)

        # Zoom controls on row 1
        ttk.Label(selection_frame, text="Zoom:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Button(selection_frame, text="−", width=3, command=self.zoom_out).grid(row=1, column=1, padx=2, pady=5)
        self.zoom_label = ttk.Label(selection_frame, text="100%", width=6)
        self.zoom_label.grid(row=1, column=2, padx=2, pady=5)
        ttk.Button(selection_frame, text="+", width=3, command=self.zoom_in).grid(row=1, column=3, padx=2, pady=5)
        ttk.Button(selection_frame, text="Fit", width=4, command=self.zoom_fit).grid(row=1, column=4, padx=2, pady=5)
        
        # Mouse interaction
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        # Mouse wheel zoom
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)    # Linux scroll down
        
        self.selecting_frame = False
        self.start_x = 0
        self.start_y = 0
        self.current_rect = None
        
    def setup_frame_manager_tab(self):
        """Set up the frame manager tab."""
        # List of frames
        list_frame = ttk.LabelFrame(self.frame_manager_frame, text="Frames")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for frame list
        columns = ('Name', 'X', 'Y', 'Width', 'Height')
        self.frame_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.frame_tree.heading(col, text=col)
            self.frame_tree.column(col, width=80)
        
        # Scrollbars for treeview
        tree_v_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.frame_tree.yview)
        tree_h_scrollbar = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.frame_tree.xview)
        self.frame_tree.configure(yscrollcommand=tree_v_scrollbar.set, xscrollcommand=tree_h_scrollbar.set)
        
        # Grid layout for frame list
        self.frame_tree.grid(row=0, column=0, sticky="nsew")
        tree_v_scrollbar.grid(row=0, column=1, sticky="ns")
        tree_h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Frame editing controls
        edit_frame = ttk.LabelFrame(self.frame_manager_frame, text="Frame Editor")
        edit_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Name
        ttk.Label(edit_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.edit_name_entry = ttk.Entry(edit_frame, width=15)
        self.edit_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # X coordinate
        ttk.Label(edit_frame, text="X:").grid(row=0, column=2, padx=5, pady=5)
        self.edit_x_entry = ttk.Entry(edit_frame, width=8)
        self.edit_x_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Y coordinate
        ttk.Label(edit_frame, text="Y:").grid(row=0, column=4, padx=5, pady=5)
        self.edit_y_entry = ttk.Entry(edit_frame, width=8)
        self.edit_y_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Width
        ttk.Label(edit_frame, text="Width:").grid(row=1, column=0, padx=5, pady=5)
        self.edit_width_entry = ttk.Entry(edit_frame, width=8)
        self.edit_width_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Height
        ttk.Label(edit_frame, text="Height:").grid(row=1, column=2, padx=5, pady=5)
        self.edit_height_entry = ttk.Entry(edit_frame, width=8)
        self.edit_height_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Buttons
        ttk.Button(edit_frame, text="Update", command=self.update_frame).grid(row=1, column=4, padx=5, pady=5)
        ttk.Button(edit_frame, text="Delete", command=self.delete_frame).grid(row=1, column=5, padx=5, pady=5)
        
        # Bind treeview selection
        self.frame_tree.bind('<<TreeviewSelect>>', self.on_frame_select)
        
    def setup_export_tab(self):
        """Set up the export tab."""
        # Export controls
        export_control_frame = ttk.LabelFrame(self.export_frame, text="Export Controls")
        export_control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(export_control_frame, text="Export to JSON", command=self.export_to_json).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(export_control_frame, text="Export to CSV", command=self.export_to_csv).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(export_control_frame, text="Export to XML", command=self.export_to_xml).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(self.export_frame, text="Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Text widget for preview
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, height=20)
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_scrollbar.set)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind export button clicks to update preview
        self.update_export_preview()
        
    def load_sprite_sheet(self):
        """Load a sprite sheet file."""
        file_path = filedialog.askopenfilename(
            title="Load Sprite Sheet",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            if self.processor.load_sprite_sheet(file_path):
                self.update_display()
                self.status_bar.config(text=f"Loaded: {os.path.basename(file_path)}")
                self.update_export_preview()
            else:
                messagebox.showerror("Error", "Failed to load sprite sheet")
    
    def save_sprite_sheet(self):
        """Save the current sprite sheet."""
        if not self.processor.is_loaded():
            messagebox.showwarning("Warning", "No sprite sheet loaded")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Sprite Sheet",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            if self.processor.save_sprite_sheet(file_path):
                self.status_bar.config(text=f"Saved: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("Error", "Failed to save sprite sheet")
    
    def load_frame_data(self):
        """Load frame data from JSON file."""
        file_path = filedialog.askopenfilename(
            title="Load Frame Data",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.processor.load_from_json(file_path):
                self.update_frame_list()
                self.update_display()
                self.status_bar.config(text=f"Loaded frame data: {os.path.basename(file_path)}")
            else:
                messagebox.showerror("Error", "Failed to load frame data")
    
    def create_sample_sheet(self):
        """Create a sample sprite sheet."""
        if self.processor.create_sample_sprite_sheet():
            self.update_display()
            self.update_frame_list()
            self.update_export_preview()
            self.status_bar.config(text="Sample sprite sheet created")
        else:
            messagebox.showerror("Error", "Failed to create sample sprite sheet")
    
    def clear_frames(self):
        """Clear all frames."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all frames?"):
            self.processor.clear_frames()
            self.update_frame_list()
            self.update_display()
            self.update_export_preview()
            self.status_bar.config(text="All frames cleared")
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About", "Sprite Sheet Manager\n\nA tool for managing sprite sheets and frames.\n\nVersion 1.0")
    
    def update_display(self):
        """Update the sprite sheet display."""
        # Clear all canvas items completely before redrawing
        self.canvas.delete("all")

        if self.processor.is_loaded():
            # Scale the image based on zoom level
            pil_image = self.processor.image
            if self.zoom_level != 1.0:
                new_width = int(pil_image.width * self.zoom_level)
                new_height = int(pil_image.height * self.zoom_level)
                scaled_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            else:
                scaled_image = pil_image

            # Convert PIL image to PhotoImage
            self.photo_image = ImageTk.PhotoImage(scaled_image)

            # Display image on canvas with tag
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image, tags="image")
            self.canvas.config(scrollregion=(0, 0, scaled_image.width, scaled_image.height))

            # Draw frame boundaries
            self.draw_frame_boundaries()
            
    def draw_frame_boundaries(self):
        """Draw boundaries for all frames."""
        # Draw detected boxes
        for i, box in enumerate(self.detected_boxes):
            # Scale box coordinates by zoom level
            x = box[0] * self.zoom_level
            y = box[1] * self.zoom_level
            width = box[2] * self.zoom_level
            height = box[3] * self.zoom_level

            outline_color = 'red' if i == self.selected_detected_index else 'green'
            width_line = 3 if i == self.selected_detected_index else 2

            self.canvas.create_rectangle(
                x, y,
                x + width, y + height,
                dash=(5,5), fill='', outline=outline_color, width=width_line, tag=f'detected_frame_{i}'
            )

        # Draw existing frames in red
        for frame in self.processor.frames:
            # Scale frame coordinates by zoom level
            x = frame.x * self.zoom_level
            y = frame.y * self.zoom_level
            width = frame.width * self.zoom_level
            height = frame.height * self.zoom_level

            self.canvas.create_rectangle(
                x, y,
                x + width, y + height,
                outline="red", width=max(1, int(2 * self.zoom_level)),
                tags="frame_boundary"
            )
            # Add frame name label (only if zoom level is high enough to be readable)
            if self.zoom_level > 0.3:
                font_size = max(6, int(8 * self.zoom_level))
                self.canvas.create_text(
                    x + 5, y + 15,
                    text=frame.name, fill="white",
                    anchor=tk.W, font=("Arial", font_size),
                    tags="frame_label"
                )
    
    def update_frame_list(self):
        """Update the frame list display."""
        # Clear existing items
        for item in self.frame_tree.get_children():
            self.frame_tree.delete(item)
        
        # Add frames to treeview
        for frame in self.processor.frames:
            self.frame_tree.insert('', tk.END, values=(
                frame.name, frame.x, frame.y, frame.width, frame.height
            ))
    
    def update_export_preview(self):
        """Update the export preview."""
        self.preview_text.delete(1.0, tk.END)
        
        if not self.processor.frames:
            self.preview_text.insert(tk.END, "No frames to export.")
            return
        
        # Show JSON preview
        self.preview_text.insert(tk.END, "JSON Format Preview:\n\n")
        preview_data = {
            'sprite_sheet': self.processor.original_filename,
            'sheet_width': self.processor.sheet_width,
            'sheet_height': self.processor.sheet_height,
            'total_frames': len(self.processor.frames),
            'frames': [frame.to_dict() for frame in self.processor.frames]
        }
        
        import json
        self.preview_text.insert(tk.END, json.dumps(preview_data, indent=2))
        
        # Show CSV preview
        self.preview_text.insert(tk.END, "\n\nCSV Format Preview:\n\n")
        self.preview_text.insert(tk.END, "Frame Name,X,Y,Width,Height\n")
        for frame in self.processor.frames:
            self.preview_text.insert(tk.END, f"{frame.name},{frame.x},{frame.y},{frame.width},{frame.height}\n")

        # Show XML preview
        self.preview_text.insert(tk.END, "\n\nXML Format Preview (TexturePacker):\n\n")
        import xml.etree.ElementTree as ET
        from xml.dom import minidom

        # Create XML structure in TexturePacker format for preview
        root = ET.Element("TextureAtlas")
        root.set("imagePath", self.processor.original_filename)
        root.set("width", str(self.processor.sheet_width))
        root.set("height", str(self.processor.sheet_height))

        # Add first few sprites for preview
        for frame in self.processor.frames[:3]:  # Show only first 3 frames in preview
            sprite_element = ET.SubElement(root, "sprite")
            sprite_element.set("n", frame.name)
            sprite_element.set("x", str(frame.x))
            sprite_element.set("y", str(frame.y))
            sprite_element.set("w", str(frame.width))
            sprite_element.set("h", str(frame.height))
            sprite_element.set("pX", "0.5")
            sprite_element.set("pY", "0.5")

        # Add ellipsis if there are more frames
        if len(self.processor.frames) > 3:
            comment = ET.Comment("... more sprites ...")
            root.append(comment)

        # Pretty print XML for preview
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        xml_preview = reparsed.toprettyxml(indent="  ")

        # Add XML declaration and comments for preview
        preview_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        preview_xml += '<!-- Created with Texture Packer Tool -->\n'
        preview_xml += '<!-- Format: n=>name, x=>x pos, y=>y pos, w=>width, h=>height, pX=>pivot x, pY=>pivot y -->\n'
        preview_xml += xml_preview

        self.preview_text.insert(tk.END, preview_xml)
    
    def export_to_json(self):
        """Export frame data to JSON file."""
        if not self.processor.frames:
            messagebox.showwarning("Warning", "No frames to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export to JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            if self.processor.export_to_json(file_path):
                self.status_bar.config(text=f"Exported to JSON: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", "Frame data exported successfully!")
            else:
                messagebox.showerror("Error", "Failed to export to JSON")
    
    def export_to_csv(self):
        """Export frame data to CSV file."""
        if not self.processor.frames:
            messagebox.showwarning("Warning", "No frames to export")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            if self.processor.export_to_csv(file_path):
                self.status_bar.config(text=f"Exported to CSV: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", "Frame data exported successfully!")
            else:
                messagebox.showerror("Error", "Failed to export to CSV")

    def export_to_xml(self):
        """Export frame data to XML file."""
        if not self.processor.frames:
            messagebox.showwarning("Warning", "No frames to export")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export to XML",
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )

        if file_path:
            if self.processor.export_to_xml(file_path):
                self.status_bar.config(text=f"Exported to XML: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", "Frame data exported successfully!")
            else:
                messagebox.showerror("Error", "Failed to export to XML")
    
    def add_frame_from_selection(self):
        """Add a frame from the selected rectangle."""
        if self.selected_detected_index is not None:
            box = self.detected_boxes[self.selected_detected_index]
            x, y, w, h = box
            name = self.frame_name_entry.get().strip()
            if name:
                if self.processor.add_frame(name, x, y, w, h):
                    self.update_frame_list()
                    self.update_display()
                    self.update_export_preview()
                    self.frame_name_entry.delete(0, tk.END)
                    del self.detected_boxes[self.selected_detected_index]
                    self.selected_detected_index = None
                    self.status_bar.config(text=f"Frame '{name}' added successfully")
                else:
                    messagebox.showerror("Error", "Failed to add frame. Check if name exists or frame is out of bounds.")
            else:
                messagebox.showwarning("Warning", "Please enter a frame name")
            return

        if not hasattr(self, 'selection_rect') or self.selection_rect is None:
            messagebox.showwarning("Warning", "Please select an area on the sprite sheet first")
            return

        name = self.frame_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a frame name")
            return

        # Get coordinates from the selection (these are in canvas/zoomed space)
        coords = self.canvas.coords(self.selection_rect)
        if len(coords) == 4:
            x1, y1, x2, y2 = coords
            # Convert from canvas coordinates back to image coordinates
            x = int(x1 / self.zoom_level)
            y = int(y1 / self.zoom_level)
            width = int((x2 - x1) / self.zoom_level)
            height = int((y2 - y1) / self.zoom_level)

            if self.processor.add_frame(name, x, y, width, height):
                self.update_frame_list()
                self.update_display()
                self.update_export_preview()
                self.frame_name_entry.delete(0, tk.END)
                # Clear selection rectangle
                self.canvas.delete("selection_rect")
                self.selection_rect = None
                self.status_bar.config(text=f"Frame '{name}' added successfully")
            else:
                messagebox.showerror("Error", "Failed to add frame. Check if name exists or frame is out of bounds.")
        else:
            messagebox.showerror("Error", "Invalid selection rectangle")
    
    def on_canvas_click(self, event):
        """Handle canvas mouse click for frame selection."""
        if not self.processor.is_loaded():
            return

        # Check if clicked on a detected frame
        clicked_items = self.canvas.find_overlapping(event.x-1, event.y-1, event.x+1, event.y+1)
        for item in clicked_items:
            tags = self.canvas.gettags(item)
            for tag in tags:
                if tag.startswith("detected_frame"):
                    # Extract frame index from tag
                    try:
                        # Handle both "detected_frame" and "detected_frame_0" formats
                        if tag == "detected_frame":
                            continue  # Skip the general tag
                        parts = tag.split("_")
                        if len(parts) >= 3:
                            frame_index = int(parts[2])
                            if 0 <= frame_index < len(self.detected_boxes):
                                self.prompt_add_detected_frame(frame_index)
                                return  # Don't start manual selection
                    except (ValueError, IndexError):
                        pass

        # If not clicked on detected frame, start manual selection
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.selecting_frame = True

        # Remove previous selection
        self.canvas.delete("selection_rect")
        self.selection_rect = None

        # Check for selection of detected boxes
        self.selected_detected_index = None
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        for i, box in enumerate(self.detected_boxes):
            x = box[0] * self.zoom_level
            y = box[1] * self.zoom_level
            width = box[2] * self.zoom_level
            height = box[3] * self.zoom_level
            if x <= canvas_x <= x + width and y <= canvas_y <= y + height:
                self.selected_detected_index = i
                self.update_display()
                return
        # No match found, just update display to remove selection
        self.update_display()
    
    def on_canvas_drag(self, event):
        """Handle canvas mouse drag for frame selection."""
        if not self.selecting_frame:
            return
        
        current_x = self.canvas.canvasx(event.x)
        current_y = self.canvas.canvasy(event.y)
        
        # Remove previous rectangle
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        
        # Draw new rectangle
        self.selection_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, current_x, current_y,
            outline="blue", width=2, dash=(5, 5), tags="selection_rect"
        )
    
    def on_canvas_release(self, event):
        """Handle canvas mouse release for frame selection."""
        self.selecting_frame = False

    def on_mouse_wheel(self, event):
        """Handle mouse wheel zoom."""
        if not self.processor.is_loaded():
            return

        # Determine zoom direction
        if event.num == 4 or event.delta > 0:  # Scroll up
            self.zoom_in()
        elif event.num == 5 or event.delta < 0:  # Scroll down
            self.zoom_out()
    
    def on_frame_select(self, event):
        """Handle frame selection in the treeview."""
        selection = self.frame_tree.selection()
        if selection:
            item = selection[0]
            values = self.frame_tree.item(item, 'values')
            if len(values) == 5:
                self.edit_name_entry.delete(0, tk.END)
                self.edit_name_entry.insert(0, values[0])
                self.edit_x_entry.delete(0, tk.END)
                self.edit_x_entry.insert(0, values[1])
                self.edit_y_entry.delete(0, tk.END)
                self.edit_y_entry.insert(0, values[2])
                self.edit_width_entry.delete(0, tk.END)
                self.edit_width_entry.insert(0, values[3])
                self.edit_height_entry.delete(0, tk.END)
                self.edit_height_entry.insert(0, values[4])
                
                self.current_frame_name = values[0]
    
    def update_frame(self):
        """Update the selected frame."""
        if not self.current_frame_name:
            messagebox.showwarning("Warning", "Please select a frame to update")
            return
        
        try:
            name = self.edit_name_entry.get().strip()
            x = int(self.edit_x_entry.get())
            y = int(self.edit_y_entry.get())
            width = int(self.edit_width_entry.get())
            height = int(self.edit_height_entry.get())
            
            if self.processor.update_frame(self.current_frame_name, name, x, y, width, height):
                self.update_frame_list()
                self.update_display()
                self.update_export_preview()
                self.status_bar.config(text=f"Frame '{name}' updated successfully")
            else:
                messagebox.showerror("Error", "Failed to update frame. Check if name conflicts or frame is out of bounds.")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for coordinates and dimensions")
    
    def delete_frame(self):
        """Delete the selected frame."""
        if not self.current_frame_name:
            messagebox.showwarning("Warning", "Please select a frame to delete")
            return
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete frame '{self.current_frame_name}'?"):
            if self.processor.remove_frame(self.current_frame_name):
                self.update_frame_list()
                self.update_display()
                self.update_export_preview()
                self.clear_edit_fields()
                self.status_bar.config(text=f"Frame '{self.current_frame_name}' deleted")
                self.current_frame_name = None
    
    def clear_edit_fields(self):
        """Clear the frame editing fields."""
        self.edit_name_entry.delete(0, tk.END)
        self.edit_x_entry.delete(0, tk.END)
        self.edit_y_entry.delete(0, tk.END)
        self.edit_width_entry.delete(0, tk.END)
        self.edit_height_entry.delete(0, tk.END)

    def zoom_in(self):
        """Zoom in the sprite sheet view."""
        if self.zoom_level < self.max_zoom:
            self.zoom_level = min(self.zoom_level * 1.2, self.max_zoom)
            self.update_display()
            self.update_zoom_label()

    def zoom_out(self):
        """Zoom out the sprite sheet view."""
        if self.zoom_level > self.min_zoom:
            self.zoom_level = max(self.zoom_level / 1.2, self.min_zoom)
            self.update_display()
            self.update_zoom_label()

    def zoom_fit(self):
        """Fit the sprite sheet to the canvas view."""
        if self.processor.is_loaded():
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            if canvas_width > 1 and canvas_height > 1:  # Canvas must be visible
                scale_x = canvas_width / self.processor.sheet_width
                scale_y = canvas_height / self.processor.sheet_height
                self.zoom_level = min(scale_x, scale_y) * 0.9  # 90% to leave some margin
                self.zoom_level = max(self.min_zoom, min(self.zoom_level, self.max_zoom))
                self.update_display()
                self.update_zoom_label()

    def update_zoom_label(self):
        """Update the zoom level display."""
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")

    def auto_detect_frames(self):
        """Automatically detect potential frames in the sprite sheet."""
        if not self.processor.is_loaded():
            messagebox.showwarning("Warning", "No sprite sheet loaded")
            return

        # Clear any existing detected frames first
        self.detected_boxes = []
        self.detected_frames = []
        self.selected_detected_index = None

        # Get performance mode from GUI
        performance_mode = self.performance_mode.get().lower()
        max_frames = None if performance_mode == "thorough" else (20 if performance_mode == "fast" else 50)

        # Update status to show progress
        self.status_bar.config(text=f"Detecting frames in {performance_mode} mode...")
        self.update()

        # Detect frames automatically using the improved comprehensive detection system
        auto_frames = self.processor.detect_frames_automatically(max_frames=max_frames, performance_mode=performance_mode)
        
        # Convert detected frames to boxes for display
        for frame in auto_frames:
            self.detected_boxes.append((frame.x, frame.y, frame.width, frame.height))

        if not self.detected_boxes:
            messagebox.showinfo("Info", "No potential frames detected. Try different frame sizes or check if frames already exist.")
            self.status_bar.config(text="No frames detected")
            return

        # Update display to show detected frames
        self.update_display()
        self.status_bar.config(text=f"Detected {len(self.detected_boxes)} potential frames in {performance_mode} mode. Click on them to add.")

    def clear_detected_frames(self):
        """Clear all detected frames."""
        self.detected_boxes = []
        self.detected_frames = []
        self.selected_detected_index = None
        self.update_display()
        self.status_bar.config(text="Cleared detected frames")

    def prompt_add_detected_frame(self, frame_index):
        """Prompt for name and add a detected frame."""
        if frame_index >= len(self.detected_boxes):
            return

        detected_box = self.detected_boxes[frame_index]
        x, y, width, height = detected_box

        # Create a simple dialog to get frame name
        from tkinter import simpledialog
        frame_name = simpledialog.askstring(
            "Add Frame",
            f"Enter name for frame ({width}x{height}):",
            initialvalue=f"frame_{len(self.processor.frames)}"
        )

        if frame_name and frame_name.strip():
            frame_name = frame_name.strip()
            # Check if name already exists
            for existing_frame in self.processor.frames:
                if existing_frame.name == frame_name:
                    messagebox.showerror("Error", f"Frame name '{frame_name}' already exists!")
                    return

            # Add the frame
            if self.processor.add_frame(frame_name, x, y, width, height):
                # Remove from detected boxes
                self.detected_boxes.pop(frame_index)
                self.selected_detected_index = None

                # Update UI
                self.update_frame_list()
                self.update_display()
                self.update_export_preview()
                self.status_bar.config(text=f"Frame '{frame_name}' added successfully")
            else:
                messagebox.showerror("Error", "Failed to add frame")


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()