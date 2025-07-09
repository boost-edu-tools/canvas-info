#!/usr/bin/env python3

import sys
import os
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import QSettings, QStandardPaths
from PySide6.QtGui import QIcon

from .gui.main_window import MainWindow
from .core.settings import Settings
from .core.course_manager import CourseManager

class CanvasInfoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Canvas Info")
        self.setWindowIcon(self.get_icon())
        
        # Initialize settings
        self.settings = Settings()
        
        # Initialize course manager
        self.course_manager = CourseManager(self.settings)
        
        # Create main window
        self.main_window = MainWindow(self.course_manager, self.settings)
        self.setCentralWidget(self.main_window)
        
        # Set initial size
        self.resize(750, 770)
        
        # Load window geometry from settings
        self.load_geometry()
        
    def get_icon(self) -> QIcon:
        """Get application icon"""
        # Try to find icon in resources
        icon_paths = [
            Path(__file__).parent / "resources" / "icon.png",
            Path(__file__).parent / "resources" / "icon.ico",
            Path(__file__).parent / "icon.png",
            Path(__file__).parent / "icon.ico",
        ]
        
        for icon_path in icon_paths:
            if icon_path.exists():
                return QIcon(str(icon_path))
        
        # Use default icon if none found
        return QIcon()
    
    def load_geometry(self):
        """Load window geometry from settings"""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.settings.value("window_state")
        if state:
            self.restoreState(state)
    
    def save_geometry(self):
        """Save window geometry to settings"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("window_state", self.saveState())
    
    def closeEvent(self, event):
        """Handle application close event"""
        self.save_geometry()
        self.main_window.cleanup()
        event.accept()


def main():
    """Main entry point for the application"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Canvas Info")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Canvas Info")
    app.setOrganizationDomain("canvasinfo.example.com")
    
    # Create and show main window
    window = CanvasInfoApp()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()