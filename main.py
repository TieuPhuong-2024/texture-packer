#!/usr/bin/env python3
"""
Sprite Sheet Manager - Main Entry Point
A desktop application for managing sprite sheets and frames.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from gui.main_application import MainApplication


def main():
    """Main application entry point."""
    try:
        # Create and run the application
        app = MainApplication()
        
        # Set up proper error handling
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            import traceback
            error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            print(f"An unexpected error occurred: {error_msg}")
            
            # Show error dialog
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("Application Error", 
                               f"An unexpected error occurred:\n\n{exc_type.__name__}: {exc_value}")
            root.destroy()
        
        # Set the exception handler
        sys.excepthook = handle_exception
        
        # Start the application
        app.mainloop()
        
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())