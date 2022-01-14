"""Create a students info file from a Canvas course.

"""
from ..canvas_api.api           import CanvasAPI
from ..canvas_api.course        import Course

from ..common                   import inform, warn, fault

def VerifyCourseByID(
    canvas_base_url: str,
    canvas_access_token: str,
    canvas_course_id: int) -> (str, list):
    """Command to create a Canvas-Git mapping table and write it to a file."""
    CanvasAPI().setup(canvas_base_url, canvas_access_token)

    course_name = getCourseName(canvas_course_id)
    group_set = getGroupCategories(canvas_course_id)
    return course_name, group_set

def getCourseName(canvas_course_id: int)->str:
    try:
        course_info = CanvasAPI().course(canvas_course_id)
    except Exception as e:
        if "Unauthorized" in str(e):
            fault("Verifying Base URL and Access Token: failed")
        elif "Not Found" in str(e):
            fault("Verifying Course ID: failed ")
        else:
            fault(e)
    else:
        inform("Verifying Base URL and Access Token: successful")
        inform("Verifying  Course ID: successful")
        return course_info["name"]

def getGroupCategories(canvas_course_id: int)->list:
    try:
        group_info = CanvasAPI().group_categories_per_course(canvas_course_id)
    except Exception as e:
        if "Not Found" in str(e):
            fault("Verifying Group Set: failed")
    else:
        inform("Verifying Group Set: successful")
        group_set = []
        for group in group_info:
            group_set.append(group["name"])
        return group_set
