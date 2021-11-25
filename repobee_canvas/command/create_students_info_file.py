"""Create a students info file from a Canvas course.

"""
from pathlib                    import Path

from ..canvas_api.api           import CanvasAPI
from ..canvas_api.course        import Course

from ..canvas_git_map           import canvas_git_map_table_wizard

from ..common                   import inform, warn, fault

def CreateStudentsInfoFile(
    canvas_base_url: str,
    canvas_access_token: str,
    canvas_course_id: int,
    group_category_name: str,
    student_info_file : str,
    extensions: list):
    """Command to create a Canvas-Git mapping table and write it to a file."""
    CanvasAPI().setup(canvas_base_url, canvas_access_token)
    inform("Loading course...")

    try:
        course = Course.load(canvas_course_id)
    except Exception as e:
        fault(e)
        if "Unauthorized" in str(e):
            warn("Repobee-canvas was not authorized to access your Canvas information. Please check the tooltip of the access token in the Settings Window.")
    else:
        canvas_git_mapping_table = canvas_git_map_table_wizard(course, group_category_name)

        if canvas_git_mapping_table.empty():
            warn("Student info file is not created.")
        else:
            if "csv" in extensions:
                path = Path(student_info_file + ".csv")
                canvas_git_mapping_table.write(path)
                inform(f"Created file:  {str(path)}     ⇝  the student info CSV file")

            if "xlsx" in extensions:
                path = Path(student_info_file + ".xlsx")
                canvas_git_mapping_table.writeExcel(path)
                inform(f"Created file:  {str(path)}     ⇝  the student info xlsx file")