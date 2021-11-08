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
"""Create a students file from a Canvas assignment for use with RepoBee.

"""
from pathlib                    import Path

from ..canvas_api.api           import CanvasAPI
from ..canvas_api.assignment    import Assignment
from ..canvas_git_map           import CanvasGitMap

from ..common                   import inform, warn, fault
from ..                         import gui

"""Command to create a students file from a Canvas assignment.

The create_students_yaml_file is a function to create a students file
for a Canvas assignment: All students assigned to this assignment are
listed and written to the students file. If the assignment is a group
assignment, the student groups are written instead.

You have to use this function first to create the students file and then use
the student file to create and manage student repositories.

Because the login ids of students can be different in Canvas and git, a
mapping needs to be made via a database containing both login ids for each
student. This database should be a csv file and have a canvas_id and git_id
column.


Usage:

Assunming the course id, Canvas API URL, and Canvas API key have been
configured, the command

```
repobee -p canvas canvas create-students-yaml-file \
        --canvas-assignment-id 23 \
        --canvas-git-map student_data.csv
```

will create file `students.yaml` with all Git account names of the
students involved in assignment with ID=23.

If you want to use a different output filename, set the filename in the GUI.

"""

# __settings__ = plug.cli.command_settings(
#     action      = CANVAS_CATEGORY.create_students_yaml_file,
#     help        = "create students file in YAML format",
#     description = (
#         "Create the students file in YAML format for a Canvas assignment for use "
#         "with RepoBee."
#         )
#     )

def CreateStudentsYAMLFile(
    canvas_base_url: str,
    canvas_access_token: str,
    canvas_course_id: int,
    canvas_assignment_id: int,
    canvas_git_map: str,
    canvas_students_file: str):

    """Create a students file for a Canvas assignment."""

    CanvasAPI().setup(canvas_base_url, canvas_access_token)
    inform("Loading assignment...")
    try:
        assignment = Assignment.load(canvas_course_id, canvas_assignment_id)
    except Exception as e:
        fault(e)
        if "Unauthorized" in str(e):
            warn("Repobee-canvas was not authorized to access your Canvas information. Please check the tooltip of the access token in the Settings Window.")
    else:
        canvas_git_mapping_table = CanvasGitMap.load(Path(canvas_git_map))

        inform("Loading submissions of this assignment...")
        submissions = assignment.submissions()

        group_submissions = []
        groupless_submissions = []
        for s in submissions:
            if s.is_group_submission():
                group_submissions.append(s)
            else:
                groupless_submissions.append(s)

        group_submissions = sorted(group_submissions, key = lambda s: s.group().name)

        # Students who are not assigned to a group in a group assignment are
        # ignored by default when creating a students file. Most likely these
        # students are not actively participating in the course or have not yet
        # assigned themselves to a group. However, with parameter
        # include_groupless_students, you can override this default behavior.
        if assignment.is_group_assignment():
            if len(group_submissions) == 0:
                warn(
                    ("No group submissions found for this group assignment. "
                    "Please run command 'repobee canvas prepare-assignment' to "
                    "resolve this issue. Or configure this assignment as an "
                    "individual assignment."))

        inform("Create students YAML file...")
        total = len(group_submissions)
        cnt = 1
        with Path(canvas_students_file).open("w") as outfile:

            for submission in group_submissions:
                    team = submission.group().name

                    group = []
                    for u in submission.group().members():
                        team += '_' + canvas_git_mapping_table.canvas2email(u.login_id)[:-15].replace('.', '')
                        group.append(int(canvas_git_mapping_table.canvas2git(u.login_id)))

                    outfile.write(team +":\n")
                    outfile.write("\tmembers:"+str(group))
                    outfile.write("\n")
                    gui.update_progress(cnt, total)
                    cnt += 1

        inform(f"Students file written to '{canvas_students_file}'.")

        inform("The following students were not in a group (prefixes from @student.tue.nl):")
        for submission in groupless_submissions:
            canvas_id   = submission.submitter().login_id
            email       = canvas_git_mapping_table.canvas2email(canvas_id)[:-15]
            inform(email)