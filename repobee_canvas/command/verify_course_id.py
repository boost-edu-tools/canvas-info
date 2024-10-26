"""Create a students info file from a Canvas course.

"""

from typing import Optional

from canvasapi import Canvas
from canvasapi.course import Course
from canvasapi.paginated_list import PaginatedList

from ..common import fault, inform


def VerifyCourseByID(
    canvas_base_url: str, canvas_access_token: str, canvas_course_id: int
) -> Optional[str]:
    """Command to create a Canvas-Git mapping table and write it to a file."""
    canvas = Canvas(canvas_base_url, canvas_access_token)

    course_name = getCourseName(canvas, canvas_course_id)
    if not course_name:
        return None

    return course_name


def getCourseName(canvas: Canvas, canvas_course_id: int) -> Optional[str]:
    try:
        courses: PaginatedList[Course] = canvas.get_courses()
    except Exception as e:
        if "Not Found" in str(e) or "Failed to establish a new connection" in str(e):
            fault("Verifying Base URL: Failed")
        elif "Unauthorized" in str(e):
            fault("Verifying Access Token: Failed")
        else:
            fault(str(e))
    else:
        inform("Verifying Base URL: Successful")
        inform("Verifying Access Token: Successful")
        for course in courses:
            if course.id == canvas_course_id:
                inform("Verifying Course ID: Successful")
                return course.name
        fault("Verifying Course ID: Failed")
        return None
