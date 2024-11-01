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
"""Map student IDs from Canvas to Git and vice versa.

To map IDs from Git to Canvas, and the other way around, use the CanvasGitMap
class. The CanvasGitMap class is a table with, for each student in a course,
at least two columns: canvas_id and git_id. Furthermore, for readability, you
can have more columns in the table. For example, an email address or student
name is convenient.

"""
import csv
from pathlib import Path
from typing import List, Dict

import xlsxwriter

from canvasapi.course import Course
from canvasapi.user import User
from canvasapi.group import Group, GroupMembership
from canvasapi.enrollment import Enrollment
from canvasapi.paginated_list import PaginatedList
from .common import inform, warn

CANVAS_ID = "canvas_id"
FIELD_SEP = ","
GIT_ID = "GitID"
FULL_NAME = "FullName"
GROUP = "Group"
ID = "ID"
EMAIL = "Mail"
NAME = "Name"
HEAD = 5


class Table:
    """Table"""

    def __init__(self, data: List):
        self._data = data

    @classmethod
    def load(cls, path: Path):
        """Load Table from a csv file."""
        with path.open() as csv_file:
            return cls(csv.DictReader(csv_file, delimiter=FIELD_SEP))

    def write(self, path: Path):
        # """Write this Canvas-Git map to csv file."""
        with path.open("w", encoding="utf-8-sig", newline="") as csv_file:

            csv_writer = csv.DictWriter(
                csv_file,
                delimiter=FIELD_SEP,
                fieldnames=list(self.columns()),
            )

            csv_writer.writeheader()

            for row in self.rows():
                csv_writer.writerow(row)

    def writeExcel(self, path: str):
        headers = []
        columns = self.columns()
        for col in columns:
            headers.append({"header": col})

        workbook = xlsxwriter.Workbook(path)
        worksheet = workbook.add_worksheet()
        worksheet.set_column("B:B", 15)  # name column 15
        worksheet.set_column("C:C", 25)  # full name column 25
        worksheet.set_column("G:G", 45)  # set email column_width 45

        rows = []
        for row in self.rows():
            rows.append(list(row.values()))

        worksheet.add_table(
            "A1:G" + str(len(rows) + 1),
            {"data": rows, "columns": headers},
        )

        workbook.close()

    def reformatTeammates(self):
        rows = [["Section", "Team", "Name", "Email", "Comments"]]
        for row in self.rows():
            section = ""
            if row[GROUP] != "":
                section = int(int(row[GROUP]) / 100)
            rows.append([section, row[GROUP], row[FULL_NAME], row[EMAIL], row[ID]])
        return rows

    def writeTeammatesExcel(self, path: str):
        rows = self.reformatTeammates()

        workbook = xlsxwriter.Workbook(path)
        worksheet = workbook.add_worksheet()
        worksheet.set_column("C:C", 25)  # full name column 25
        worksheet.set_column("D:D", 40)  # set email column_width 45

        row = 0
        # Iterate over the data and write it out row by row.
        for data in rows:
            for col, d in enumerate(data):
                worksheet.write(row, col, d)
            row += 1

        workbook.close()

    def columns(self):
        """Generator for the column names of this Table."""
        columns = []

        if len(self._data) > 0:
            columns = list(self._data[0].keys())

        return columns

    def rows(self):
        """Generator for each row of this Table."""
        for row in self._data:
            yield row

    def empty(self):
        """Return true if this table is empty, false otherwise."""
        return 0 == len(self._data)

    def get_stu_info(self) -> list:
        student_info = []
        for row in self.rows():
            student_info.append(
                {"group": row[GROUP], "email2git": {row[EMAIL]: str(row[GIT_ID])}}
            )

        return student_info


def canvas_git_map_table_wizard(course: Course) -> Table:
    """Create a Canvas-Git map CSV file."""
    inform("Getting the students' infomation...")
    students: PaginatedList[User] = course.get_users()

    if not students._is_larger_than(0):
        warn((f"No students found for course '{course.name}'."))
        return Table([])

    inform((f"Found students for this course."))

    inform("Getting the information of groups...")
    group_members: Dict[str, str] = {}
    groups: PaginatedList[Group] = course.get_groups()
    for group in groups:
        memberships: PaginatedList[GroupMembership] = group.get_memberships()
        for member in memberships:
            group_members[member.user_id] = group.name

    inform("Getting the infomation of enrollments...")
    user_enrollment: Dict[str, str] = {}
    enrollments: PaginatedList[Enrollment] = course.get_enrollments()
    for enrollment in enrollments:
        user_enrollment[enrollment.user_id] = enrollment.role

    data = []

    for student in students:
        if user_enrollment[student.id] != "StudentEnrollment":
            continue
        row = {}
        if hasattr(student, "id"):
            user_id = student.id
            if user_id in group_members:
                row[GROUP] = group_members[user_id]
            else:
                row[GROUP] = ""
        else:
            row[GROUP] = ""

        email = ""
        if hasattr(student, "email"):
            email = student.email
            row[NAME] = email[:-15].split(".")[-1]
        else:
            row[NAME] = ""

        if hasattr(student, "short_name"):
            row[FULL_NAME] = student.short_name
        else:
            row[FULL_NAME] = ""

        if hasattr(student, "login_id"):
            try:
                row[ID] = int(student.login_id)
            except:
                row[ID] = student.login_id
        else:
            row[ID] = ""

        if hasattr(student, "sis_user_id"):
            try:
                row[GIT_ID] = student.sis_user_id
            except:
                row[GIT_ID] = student.sis_user_id
        else:
            row[GIT_ID] = ""

        row[EMAIL] = email

        data.append(row)

    data = sorted(data, key=lambda d: d[GROUP])

    return Table(data)
