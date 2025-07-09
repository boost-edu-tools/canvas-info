import json
from pathlib import Path
from typing import Any, Dict, Optional, List
from PySide6.QtCore import QSettings, QStandardPaths

class Settings:
    """Settings management class"""
    
    def __init__(self):
        self.settings = QSettings()
        self.init_default_settings()
    
    def init_default_settings(self):
        """Initialize default settings"""
        if not self.value("initialized"):
            self.set_defaults()
            self.setValue("initialized", True)
    
    def set_defaults(self):
        """Set default values"""
        default_course = self._get_default_course_settings()
        
        self.setValue("courses/00001", default_course)
        self.setValue("course_id", "00001")
        self.setValue("course_list", ["ID: 00001  Name: Unverified"])
        self.setValue("col_percent", 60)
    
    def _get_default_course_settings(self) -> Dict[str, Any]:
        """Get default course settings"""
        home = str(Path.home())
        return {
            "course_id": "00001",
            "course_name": "Unverified",
            "base_url": "https://canvas.tue.nl",
            "access_token": "",
            "info_file_folder": home,
            "csv_info_file": "student-info.csv",
            "xlsx_info_file": "student-info.xlsx",
            "teammates_info_file": "teammates-students.xlsx",
            "member_option": "(email, gitid)",
            "include_group": True,
            "include_member": True,
            "include_initials": False,
            "full_groups": True,
            "csv": False,
            "xlsx": False,
            "yaml": False,
            "teammates": False,
            "url_option": "TUE",
            "url_options": {
                "TUE": "https://canvas.tue.nl",
                "Custom": ""
            }
        }
    
    def value(self, key: str, default: Any = None) -> Any:
        """Get setting value"""
        return self.settings.value(key, default)
    
    def setValue(self, key: str, value: Any):
        """Set setting value"""
        self.settings.setValue(key, value)
    
    def get_course_settings(self, course_id: str) -> Dict[str, Any]:
        """Get course settings"""
        return self.value(f"courses/{course_id}", {})
    
    def set_course_settings(self, course_id: str, settings: Dict[str, Any]):
        """Set course settings"""
        self.setValue(f"courses/{course_id}", settings)
    
    def delete_course(self, course_id: str):
        """Delete course settings"""
        self.settings.remove(f"courses/{course_id}")
    
    def get_course_list(self) -> List[str]:
        """Get list of courses"""
        return self.value("course_list", [])
    
    def set_course_list(self, courses: List[str]):
        """Set course list"""
        self.setValue("course_list", courses)
    
    def get_current_course_id(self) -> str:
        """Get current course ID"""
        return self.value("course_id", "00001")
    
    def set_current_course_id(self, course_id: str):
        """Set current course ID"""
        self.setValue("course_id", course_id)
    
    def sync(self):
        """Synchronize settings to disk"""
        self.settings.sync()