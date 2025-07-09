"""Verify Canvas course ID and credentials.

"""

from typing import Optional, Callable

from canvasapi import Canvas
from canvasapi.course import Course
from canvasapi.paginated_list import PaginatedList


def VerifyCourseByID(
    canvas_base_url: str, 
    canvas_access_token: str, 
    canvas_course_id: int,
    message_callback: Optional[Callable[[str], None]] = None
) -> Optional[str]:
    """Command to verify Canvas course ID and credentials."""
    canvas = Canvas(canvas_base_url, canvas_access_token)
    return getCourseName(canvas, canvas_course_id, message_callback)


def getCourseName(
    canvas: Canvas, 
    canvas_course_id: int,
    message_callback: Optional[Callable[[str], None]] = None
) -> Optional[str]:
    """Get course name by ID."""
    
    def inform(msg: str):
        if message_callback:
            message_callback(msg)
    
    def fault(msg: str):
        if message_callback:
            message_callback(f"ERROR: {msg}")
    
    try:
        courses: PaginatedList[Course] = canvas.get_courses()
    except Exception as e:
        if "Not Found" in str(e) or "Failed to establish a new connection" in str(e):
            fault("Verifying Base URL: Failed")
        elif "Unauthorized" in str(e):
            fault("Verifying Access Token: Failed")
        else:
            fault(str(e))
        return None
    else:
        inform("Verifying Base URL: Successful")
        inform("Verifying Access Token: Successful")
        
        for course in courses:
            if course.id == canvas_course_id:
                inform("Verifying Course ID: Successful")
                return course.name
        
        fault("Verifying Course ID: Failed")
        return None