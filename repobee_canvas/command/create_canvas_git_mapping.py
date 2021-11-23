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
"""Create a Canvas-Git mapping table."""
from pathlib import Path

from ..canvas_api.api           import CanvasAPI
from ..canvas_api.course        import Course

from ..canvas_git_map           import canvas_git_map_table_wizard

from ..common                   import inform, warn, fault

# class CreateCanvasGitMapping(plug.Plugin, plug.cli.Command):
#     """Create a Canvas-Git mapping table and write to file.
#     """
#     __settings__ = plug.cli.command_settings(
#             action = CANVAS_CATEGORY.create_canvas_git_mapping,
#             help = ("create a Canvas-Git mapping table"),
#             description = (
#                 "Create a Canvas-Git mapping table for a Canvas course "
#                 "via a wizard and write the table to file."
#                 ),
#             )

#     canvas_access_token                 = CANVAS_ACCESS_TOKEN_OPTION
#     canvas_base_url                     = CANVAS_API_BASE_URL_OPTION
#     canvas_course_id                    = CANVAS_COURSE_ID_OPTION
#     canvas_git_map                      = CANVAS_GIT_MAP_OPTION

def CreateCanvasGitMapping(
    canvas_base_url: str,
    canvas_access_token: str,
    canvas_course_id: int,
    canvas_git_map : str,
    group_category_name: str):
    """Command to create a Canvas-Git mapping table and write it to a file."""
    CanvasAPI().setup(canvas_base_url, canvas_access_token)
    inform("Loading course...")
    print (canvas_git_map)
    try:
        course = Course.load(canvas_course_id)
    except Exception as e:
        fault(e)
        if "Unauthorized" in str(e):
            warn("Repobee-canvas was not authorized to access your Canvas information. Please check the tooltip of the access token in the Settings Window.")
    else:
        canvas_git_mapping_table = canvas_git_map_table_wizard(course, group_category_name)

        if canvas_git_mapping_table.empty():
            warn("Canvas-Git mapping table CSV is not created.")
        else:
            path = Path(canvas_git_map)
            canvas_git_mapping_table.write(path)
            inform(f"Created file:  {str(path)}     ⇝  the Canvas-Git mapping table CSV file")
