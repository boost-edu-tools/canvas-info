from typing import Dict, List, Optional, Any
from pathlib import Path
from .settings import Settings

class CourseManager:
    """Manages course information and settings"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.current_course_id = self.settings.get_current_course_id()
    
    def get_current_course(self) -> Dict[str, Any]:
        """Get current course settings"""
        return self.settings.get_course_settings(self.current_course_id)
    
    def set_current_course(self, course_id: str):
        """Set current course"""
        self.current_course_id = course_id
        self.settings.set_current_course_id(course_id)
    
    def get_course_list(self) -> List[str]:
        """Get list of all courses"""
        return self.settings.get_course_list()
    
    def create_course(self, course_id: str, clone_from: Optional[str] = None) -> Dict[str, Any]:
        """Create a new course"""
        if clone_from:
            # Clone from existing course
            source_course = self.settings.get_course_settings(clone_from)
            new_course = source_course.copy()
        else:
            # Create new course with defaults
            new_course = self._get_default_course_settings()
        
        new_course["course_id"] = course_id
        new_course["course_name"] = "Unverified"
        
        # Save course
        self.settings.set_course_settings(course_id, new_course)
        
        # Update course list
        course_list = self.get_course_list()
        course_title = self.format_course_title(course_id, "Unverified")
        course_list.append(course_title)
        course_list.sort(reverse=True)
        self.settings.set_course_list(course_list)
        
        return new_course
    
    def _get_default_course_settings(self) -> Dict[str, Any]:
        """Get default course settings"""
        home = str(Path.home())
        return {
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
    
    def delete_course(self, course_id: str):
        """Delete a course"""
        # Remove from settings
        self.settings.delete_course(course_id)
        
        # Update course list
        course_list = self.get_course_list()
        course_title = None
        for title in course_list:
            if title.startswith(f"ID: {course_id}"):
                course_title = title
                break
        
        if course_title:
            course_list.remove(course_title)
            self.settings.set_course_list(course_list)
        
        # If this was the current course, switch to first available
        if course_id == self.current_course_id:
            if course_list:
                new_course_id = self.parse_course_id(course_list[0])
                self.set_current_course(new_course_id)
            else:
                # Create default course if none exist
                default_course = self._get_default_course_settings()
                self.settings.set_course_settings("00001", default_course)
                self.settings.set_course_list(["ID: 00001  Name: Unverified"])
                self.set_current_course("00001")
    
    def update_course_setting(self, key: str, value: Any):
        """Update a setting for the current course"""
        course = self.get_current_course()
        course[key] = value
        self.settings.set_course_settings(self.current_course_id, course)
    
    def update_course_name(self, course_name: str):
        """Update course name and refresh course list"""
        self.update_course_setting("course_name", course_name)
        
        # Update course list
        course_list = self.get_course_list()
        old_title = None
        for i, title in enumerate(course_list):
            if title.startswith(f"ID: {self.current_course_id}"):
                old_title = title
                new_title = self.format_course_title(self.current_course_id, course_name)
                course_list[i] = new_title
                break
        
        if old_title:
            course_list.sort(reverse=True)
            self.settings.set_course_list(course_list)
    
    def validate_course_id(self, course_id: str) -> bool:
        """Validate course ID"""
        if not course_id or not course_id.isnumeric():
            return False
        
        if course_id == "00000":
            return False
        
        # Check if course already exists
        course_list = self.get_course_list()
        for title in course_list:
            if title.startswith(f"ID: {course_id}"):
                return False
        
        return True
    
    def format_course_title(self, course_id: str, course_name: str) -> str:
        """Format course title for display"""
        return f"ID: {course_id}  Name: {course_name}"
    
    def parse_course_id(self, course_title: str) -> str:
        """Parse course ID from title"""
        parts = course_title.split(" ")
        if len(parts) >= 2:
            return parts[1]
        return "00001"
    
    def get_url_for_option(self, option: str) -> str:
        """Get URL for the given option"""
        course = self.get_current_course()
        url_options = course.get("url_options", {})
        return url_options.get(option, "")
    
    def update_url_option(self, option: str, url: str):
        """Update URL option"""
        course = self.get_current_course()
        if "url_options" not in course:
            course["url_options"] = {}
        course["url_options"][option] = url
        self.settings.set_course_settings(self.current_course_id, course)