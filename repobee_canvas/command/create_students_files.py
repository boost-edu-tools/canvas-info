"""Create a students info file from a Canvas course.

"""

from pathlib import Path

from canvasapi import Canvas
from canvasapi.course import Course
from canvasapi.paginated_list import PaginatedList

from ..canvas_git_map import canvas_git_map_table_wizard, Table
from ..common import fault, inform, warn
from ..gui import KEY_EMAIL, KEY_GIT_ID, KEY_MEM_BOTH

GROUP = "group"
EMAIL2GIT = "email2git"


def CreateStudentsFiles(
        canvas_base_url: str,
        canvas_access_token: str,
        canvas_course_id: int,
        student_csv_info_file: str | None = None,
        student_xlsx_info_file: str | None = None,
        students_yaml_file: str | None = None,
        students_teammates_file: str | None = None,
        student_member_option: str = "email",
        include_group: bool = False,
        include_member: bool = False,
        include_initials: bool = False,
        only_full_groups: bool = True,
):
    if (
            not student_csv_info_file
            and not student_xlsx_info_file
            and not students_yaml_file
            and not students_teammates_file
    ):
        return

    """Command to create a Canvas-Git mapping table and write it to a file."""
    canvas: Canvas = Canvas(canvas_base_url, canvas_access_token)
    inform("Loading course...")

    try:
        courses: PaginatedList[Course] = canvas.get_courses()
    except Exception as e:
        if "Not Found" in str(e) or "Failed to establish a new connection" in str(e):
            fault("Erroneous Base URL")
        elif "Unauthorized" in str(e):
            fault("Erroneous Access Token")
        else:
            fault(str(e))
    else:
        for course in courses:
            if course.id == canvas_course_id:
                course: Course = canvas.get_course(canvas_course_id)
                canvas_git_mapping_table = canvas_git_map_table_wizard(course)

                if canvas_git_mapping_table.empty():
                    warn("No students found.")
                else:
                    if student_csv_info_file:
                        canvas_git_mapping_table.write(Path(student_csv_info_file))
                        inform(
                            f"Created students info CSV file::  {student_csv_info_file}"
                        )

                    if student_xlsx_info_file:
                        canvas_git_mapping_table.writeExcel(student_xlsx_info_file)
                        inform(
                            f"Created students info Excel file:  {student_xlsx_info_file}"
                        )

                    if students_yaml_file:
                        create_yaml_file(canvas_git_mapping_table, students_yaml_file, student_member_option,
                                         include_group, include_member, include_initials, only_full_groups)

                    if students_teammates_file:
                        canvas_git_mapping_table.writeTeammatesExcel(
                            students_teammates_file
                        )
                        inform(
                            f"Created students info Teammates Excel file:  {students_teammates_file}"
                        )

                return
        fault("Non-existing Course ID")


def create_yaml_file(
        canvas_git_mapping_table: Table,
        students_yaml_file: str | None = None,
        student_member_option: str = "email",
        include_group: bool = False,
        include_member: bool = False,
        include_initials: bool = False,
        only_full_groups: bool = True,
):
    group_submissions = {}
    groupless_submissions = []
    smallgroup_submissions = []
    for info in canvas_git_mapping_table.get_stu_info():
        group = info[GROUP]
        if group:
            if group in group_submissions:
                group_submissions[group][EMAIL2GIT].update(
                    info[EMAIL2GIT]
                )
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
            (
                "No group submissions found for this group assignment. "
                "Please run command 'repobee canvas prepare-assignment' to "
                "resolve this issue. Or configure this assignment as an "
                "individual assignment."
            )
        )

    # Filter out the groups that are not full, if requested.
    if only_full_groups:
        for group in list(group_submissions.keys()):
            if group.members_count < group.max_membership:
                # Group is too small, remove it from the list
                for email in list(group_submissions[group][EMAIL2GIT]):
                    smallgroup_submissions.append(email)
                del group_submissions[group]

    inform("Create students YAML file...")

    if student_member_option == KEY_MEM_BOTH:
        write_yaml_file(
            students_yaml_file,
            group_submissions,
            include_group,
            include_member,
            include_initials,
            True,
            True
        )
    elif student_member_option == KEY_EMAIL:
        write_yaml_file(
            students_yaml_file,
            group_submissions,
            include_group,
            include_member,
            include_initials,
            True,
            False
        )

    elif student_member_option == KEY_GIT_ID:
        write_yaml_file(
            students_yaml_file,
            group_submissions,
            include_group,
            include_member,
            include_initials,
            False,
            True
        )

    else:
        fault("Invalid member option.")
        return

    inform(f"Created students YAML file: {students_yaml_file}.")

    n = len(groupless_submissions)
    if n > 0: inform(f"The following {n} students were not in a group:")
    for submission in groupless_submissions:
        email = list(submission[EMAIL2GIT].keys())
        inform(email[0])

    m = len(smallgroup_submissions)
    if m > 0: inform(f"The following {m} students were in too small groups, no repository made for them:")
    for student in smallgroup_submissions:
        inform(student)


def write_yaml_file(
        students_yaml_file: str,
        group_submissions: dict,
        include_group: bool,
        include_member: bool,
        include_initials: bool,
        by_email: bool,
        by_gitid: bool,
):
    sorted_group_submissions = {k: v for k, v in sorted(group_submissions.items(), key=lambda x: x[1][GROUP].name)}
    with Path(students_yaml_file).open("w") as outfile:
        for submission in sorted_group_submissions.values():
            if include_group:
                team = str(submission[GROUP].name)
            else:
                team = ""

            group = []
            for email, git_id in submission[EMAIL2GIT].items():
                if by_email and by_gitid:
                    group.append("(" + email + ", " + git_id + ")")
                elif by_email:
                    group.append(email)
                elif by_gitid:
                    group.append(git_id)
                else:
                    fault("Invalid member option combination.")

                if include_member:
                    email = email[:-15]
                    if include_initials:
                        team += "_" + email.replace(".", "")
                    else:
                        team += "_" + email.split(".")[-1]

            if team[0] == "_":
                team = team[1:]
            outfile.write(team + ":\n")
            outfile.write("\tmembers:[" + ", ".join(group))
            outfile.write("]\n")
