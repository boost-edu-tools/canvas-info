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
    student_csv_info_file: str,
    student_xlsx_info_file: str,
    students_yaml_file: str,
    student_member_option: str):
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
            warn("No students found.")
        else:
            if student_csv_info_file:
                canvas_git_mapping_table.write(Path(student_csv_info_file))
                inform(f"Created students info CSV file::  {student_csv_info_file}")

            if student_xlsx_info_file:
                canvas_git_mapping_table.writeExcel(student_xlsx_info_file)
                inform(f"Created students info Excel file:  {student_xlsx_info_file}")

            if students_yaml_file:
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

                if student_member_option == "email":
                    member_as_email(students_yaml_file, group_submissions)

                elif student_member_option == "git_id":
                    member_as_gitid(students_yaml_file, group_submissions)

                inform(f"Created students YAML file: {students_yaml_file}.")

                inform("The following students were not in a group (prefixes from @student.tue.nl):")
                for submission in groupless_submissions:
                    email = list(submission[EMAIL2GIT].keys())
                    inform(email[0])

def member_as_email(students_yaml_file: str, group_submissions: dict):
    with Path(students_yaml_file).open("w") as outfile:
        for submission in group_submissions.values():
            team = submission[GROUP]

            group = []
            for email in submission[EMAIL2GIT].keys():
                team += '_' + email[:-15].replace('.', '')
                group.append(email)

            outfile.write(team +":\n")
            outfile.write("\tmembers:["+ ', '.join(group))
            outfile.write("]\n")

def member_as_gitid(students_yaml_file: str, group_submissions: dict):
    with Path(students_yaml_file).open("w") as outfile:
        for submission in group_submissions.values():
            team = submission[GROUP]

            group = []
            for email, git_id in submission[EMAIL2GIT].items():
                team += '_' + email[:-15].replace('.', '')
                group.append(git_id)

            outfile.write(team +":\n")
            outfile.write("\tmembers:["+ ', '.join(group))
            outfile.write("]\n")