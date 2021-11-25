# Copyright 2021 Huub de Beer <h.t.d.beer@tue.nl>
#
# Licensed under the EUPL, Version 1.2 or later. You may not use this work
# except in compliance with the EUPL. You may obtain a copy of the EUPL at:
#
# https://joinup.ec.europa.eu/software/page/eupl
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the EUPL is distributed on an "AS IS" basis, WITHOUT
# WARRANTY OR CONDITIONS OF ANY KIND, either express or implied. See the EUPL
# for the specific language governing permissions and limitations under the
# licence.
"""Create a students yaml file from a students info csv/excel file for use with RepoBee.

"""
from pathlib                    import Path

from ..canvas_api.api           import CanvasAPI
from ..canvas_api.assignment    import Assignment
from ..canvas_git_map           import CanvasGitMap

from ..common                   import inform, warn, fault
from ..                         import gui

GROUP                           = "group"
EMAIL2GIT                       = "email2git"

def CreateStudentsYAMLFile(
    student_info_file: str,
    canvas_students_file: str,
    extension: str):

    """Create a students yaml file for a Canvas assignment."""

    canvas_git_mapping_table = None
    if extension == ".csv":
        canvas_git_mapping_table = CanvasGitMap.load(Path(student_info_file))

    elif extension == ".xlsx":
        canvas_git_mapping_table = CanvasGitMap.loadExcel(student_info_file)

    if canvas_git_mapping_table:
        group_submissions = {}
        groupless_submissions = []
        for info in canvas_git_mapping_table._student_info:
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
    else:
        inform("Unknown file type. Please select a csv file or a xlsx file")