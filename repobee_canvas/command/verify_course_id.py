"""Create a students info file from a Canvas course.

"""
from ..canvas_api.api import CanvasAPI

from ..common import inform, fault
from typing import Tuple, Optional


def VerifyCourseByID(
    canvas_base_url: str, canvas_access_token: str, canvas_course_id: int
) -> Tuple[Optional[str], Optional[list]]:
    """Command to create a Canvas-Git mapping table and write it to a file."""
    CanvasAPI().setup(canvas_base_url, canvas_access_token)

    course_name = getCourseName(canvas_course_id)
    if not course_name:
        return None, None
    group_set = getGroupCategories(canvas_course_id)
    return course_name, group_set


def getCourseName(canvas_course_id: int) -> Optional[str]:
    try:
        courses = CanvasAPI().courses()
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
            if course["id"] == canvas_course_id:
                inform("Verifying Course ID: Successful")
                return course["name"]
        fault("Verifying Course ID: Failed")
        return None


def getGroupCategories(canvas_course_id: int) -> Optional[list]:
    try:
        group_info = CanvasAPI().group_categories_per_course(canvas_course_id)
    except Exception as e:
        if "Not Found" in str(e):
            fault("Verifying Group Set: Failed")
            return None
    else:
        inform("Verifying Group Set: Successful")
        group_set = []
        for group in group_info:
            group_set.append(group["name"])
        return group_set
