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
from typing import List

from .canvas_api.course import Course
from .common import warn, inform
import xlsxwriter

CANVAS_ID = "canvas_id"
FIELD_SEP = ","
GIT_ID = "GitID"
SHORT_NAME = "short_name"
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
        worksheet.set_column("F:F", 45)  # set email column_width 45

        rows = []
        for row in self.rows():
            rows.append(list(row.values()))

        worksheet.add_table(
            "A1:F" + str(len(rows) + 1),
            {"data": rows, "columns": headers},
        )

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
                {"group": row[GROUP], "email2git": {row[EMAIL]: row[GIT_ID]}}
            )

        return student_info


def canvas_git_map_table_wizard(course: Course, group_category: str = None) -> Table:
    """Create a Canvas-Git map CSV file."""
    inform("Getting the students' infomation...")
    students = course.students()

    if len(students) <= 0:
        warn((f"No students found for course '{course.name}'."))
        return Table([])

    inform((f"Found {len(students)} students for this course. "))

    inform("Getting the information of groups...")
    group_members = course.group_members(group_category)

    git_id_key = "sis_user_id"
    email_key = "email"
    student_id = "id"
    canvas_id_key = "login_id"

    data = []

    for student in students:
        row = {}
        fields = student.fields()

        if student_id in fields:
            user_id = fields[student_id]
            if user_id in group_members:
                row[GROUP] = group_members[user_id]
            else:
                row[GROUP] = ""
        else:
            row[GROUP] = ""

        email = ""
        if email_key in fields:
            email = fields[email_key]
            row[NAME] = email[:-15].split(".")[-1]
        else:
            row[NAME] = ""

        if SHORT_NAME in fields:
            row[FULL_NAME] = fields[SHORT_NAME]
        else:
            row[FULL_NAME] = ""

        if canvas_id_key in fields:
            row[ID] = fields[canvas_id_key]
        else:
            row[ID] = ""

        if git_id_key in fields:
            row[GIT_ID] = fields[git_id_key]
        else:
            row[GIT_ID] = ""

        row[EMAIL] = email

        data.append(row)

    data = sorted(data, key=lambda d: d[GROUP])

    return Table(data)
