"""Create a students info file from a Canvas assignment.

"""
from pathlib                    import Path

from ..canvas_git_map           import CanvasGitMap

from ..common                   import inform, warn, fault
from ..                         import gui

import xlsxwriter

"""Command to create a students info file from a Canvas assignment.

The create_students_info_file is a function to create a students info excel file
for a Canvas assignment: All students assigned to this assignment are
listed and written to the students file. If the assignment is a group
assignment, the student groups are written instead.

Because the login ids of students can be different in Canvas and git, a
mapping needs to be made via a database containing both login ids for each
student. This database should be a csv file and have a canvas_id and git_id
column.


Usage:

```
repobee -p canvas canvas create-students-yaml-file \
        --canvas-assignment-id 23 \
        --canvas-git-map student_data.csv
```

will create file `students.yaml` with all Git account names of the
students involved in assignment with ID=23.

If you want to use a different output filename, set the filename in the GUI.

"""

def CreateStudentsInfoFile(
    canvas_git_map: str,
    canvas_students_info_file: str):

    """Create a students info file for a Canvas assignment."""
    canvas_git_mapping_table = CanvasGitMap.load(Path(canvas_git_map))

    # inform(canvas_git_mapping_table.rows())
    # for row in canvas_git_mapping_table.rows():
        # inform (row)

    infos = canvas_git_mapping_table._student_info
    # inform (canvas_git_mapping_table._student_info)
    # for info in canvas_git_mapping_table._student_info:
    #     inform("info  : ")
    #     inform(info)
    workbook = xlsxwriter.Workbook(canvas_students_info_file)
    worksheet = workbook.add_worksheet()
    worksheet.set_column('A:D', 12) #set columns_width 12
    worksheet.set_column('E:E', 45) #set email column_width 45
    worksheet.add_table('A1:E'+str(len(infos)+1),
        {
            'data': infos,
            'columns': [
                {'header': 'Group'},
                {'header': 'Name'},
                {'header': 'canvas_id'},
                {'header': 'git_id'},
                {'header': 'email'},
            ]
        }
    )

    workbook.close()
    inform(f"Created file:  {str(canvas_students_info_file)}     ⇝  the student info xlsx file")