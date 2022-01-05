"""Create a students info file from a Canvas course.

"""
from ..canvas_api.api           import CanvasAPI
from ..canvas_api.course        import Course

from ..common                   import inform, warn, fault

def VerifyCourseID(
    canvas_base_url: str,
    canvas_access_token: str,
    canvas_course_id: int) -> str:
    """Command to create a Canvas-Git mapping table and write it to a file."""
    CanvasAPI().setup(canvas_base_url, canvas_access_token)

    try:
        course_info = CanvasAPI().course(canvas_course_id)
    except Exception as e:
        fault(e)
        if "Unauthorized" in str(e):
            warn("Repobee-canvas was not authorized to access your Canvas information. Please check the tooltip of the access token in the Settings Window.")
    else:
        return course_info["name"]