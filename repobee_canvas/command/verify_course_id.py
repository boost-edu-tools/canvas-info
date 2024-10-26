"""Create a students info file from a Canvas course.

"""

from canvasapi import Canvas

from ..common import inform, fault
from typing import Tuple, Optional


def VerifyCourseByID(
    canvas_base_url: str, canvas_access_token: str, canvas_course_id: int
) -> Tuple[Optional[str], Optional[list]]:
    """Command to create a Canvas-Git mapping table and write it to a file."""
    canvas = Canvas(canvas_base_url, canvas_access_token)

    course_name = getCourseName(canvas, canvas_course_id)
    if not course_name:
        return None, None
    group_set = getGroupCategories(canvas, canvas_course_id)
    return course_name, group_set


def getCourseName(canvas: Canvas, canvas_course_id: int) -> Optional[str]:
    try:
        courses = canvas.get_courses()
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


def getGroupCategories(canvas: Canvas, canvas_course_id: int) -> Optional[list]:
    try:
        course = canvas.get_course(canvas_course_id)
        group_info = course.get_group_categories()
    except Exception as e:
        if "Not Found" in str(e):
            fault("Verifying Group Set: Failed")
            return None
    else:
        inform("Verifying Group Set: Successful")
        group_set = []
        for group in group_info:
            group_set.append(group.name)
        return group_set
