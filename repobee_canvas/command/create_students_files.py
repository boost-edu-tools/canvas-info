"""Create a students info file from a Canvas course.

"""
from pathlib                    import Path

from ..canvas_api.api           import CanvasAPI
from ..canvas_api.course        import Course

from ..canvas_git_map           import canvas_git_map_table_wizard

from ..common                   import inform, warn, fault

GROUP                           = "group"
EMAIL2GIT                       = "email2git"

def CreateStudentsiles(
    canvas_base_url: str,
    canvas_access_token: str,
    canvas_course_id: int,
    group_category_name: str,
    student_info_file : str,
    extensions: list,
    canvas_students_file: str):
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

            group_submissions = {}
            groupless_submissions = []
            for info in canvas_git_mapping_table.get_stu_info():
                group = info[GROUP]
                if group:
                    if group in group_submissions:
                        group_submissions[group][EMAIL2GIT].update(info[EMAIL2GIT])
                    else:
                        group_submissions[group] = info
                else:
                    groupless_submissions.append(info)

            # Students who are not assigned to a group in a group assignment are
            # ignored by default when creating a students file. Most likely these
            # students are not actively participating in the course or have not yet
            # assigned themselves to a group. However, with parameter
            # include_groupless_students, you can override this default behavior.
            if len(group_submissions) == 0:
                warn(
                    ("No group submissions found for this group assignment. "
                    "Please run command 'repobee canvas prepare-assignment' to "
                    "resolve this issue. Or configure this assignment as an "
                    "individual assignment."))

            inform("Create students YAML file...")

            with Path(canvas_students_file).open("w") as outfile:

                for submission in group_submissions.values():
                        team = submission[GROUP]

                        group = []
                        for email, git_id in submission[EMAIL2GIT].items():
                            team += '_' + email[:-15].replace('.', '')
                            group.append(git_id)

                        outfile.write(team +":\n")
                        outfile.write("\tmembers:"+str(group))
                        outfile.write("\n")

            inform(f"Students file written to '{canvas_students_file}'.")

            inform("The following students were not in a group (prefixes from @student.tue.nl):")
            for submission in groupless_submissions:
                email = list(submission[EMAIL2GIT].keys())
                inform(email[0])