from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal

from canvasapi import Canvas
from canvasapi.course import Course
from canvasapi.exceptions import CanvasException

from ..core.course_manager import CourseManager
from ..canvas.create_students_files import CreateStudentsFiles
from ..canvas.verify_course_id import VerifyCourseByID

class CanvasWorker(QObject):
    """Worker thread for Canvas operations"""
    
    finished = Signal()
    message = Signal(str)
    progress = Signal(int, int)
    course_verified = Signal(str)
    
    def __init__(self, course_manager: CourseManager, operation: str):
        super().__init__()
        self.course_manager = course_manager
        self.operation = operation
    
    def run(self):
        """Run the worker operation"""
        try:
            if self.operation == "verify":
                self.verify_course()
            elif self.operation == "execute":
                self.execute_command()
        except Exception as e:
            self.message.emit(f"ERROR: {str(e)}")
        finally:
            self.finished.emit()
    
    def verify_course(self):
        """Verify course settings"""
        course = self.course_manager.get_current_course()
        
        try:
            course_name = VerifyCourseByID(
                course["base_url"],
                course["access_token"],
                int(self.course_manager.current_course_id),
                self.message.emit
            )
            
            self.course_verified.emit(course_name or "")
            
        except Exception as e:
            self.message.emit(f"Verification failed: {str(e)}")
            self.course_verified.emit("")
    
    def execute_command(self):
        """Execute the main command"""
        course = self.course_manager.get_current_course()
        
        try:
            # Prepare file paths
            stu_csv_info_file = None
            stu_xlsx_info_file = None
            stu_teammates_file = None
            students_yaml_file = None
            
            if course.get("csv"):
                stu_csv_info_file = str(Path(course["info_file_folder"]) / course["csv_info_file"])
            
            if course.get("xlsx"):
                stu_xlsx_info_file = str(Path(course["info_file_folder"]) / course["xlsx_info_file"])
            
            if course.get("teammates"):
                stu_teammates_file = str(Path(course["info_file_folder"]) / course["teammates_info_file"])
            
            if course.get("yaml"):
                students_yaml_file = course["students_file"]
            
            # Create students files
            CreateStudentsFiles(
                course["base_url"],
                course["access_token"],
                int(self.course_manager.current_course_id),
                stu_csv_info_file,
                stu_xlsx_info_file,
                students_yaml_file,
                stu_teammates_file,
                course["member_option"],
                course["include_group"],
                course["include_member"],
                course["include_initials"],
                course["full_groups"],
                progress_callback=self.progress.emit,
                message_callback=self.message.emit
            )
            
        except Exception as e:
            self.message.emit(f"Execution failed: {str(e)}")