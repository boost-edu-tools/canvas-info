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
"""RepoBee command category for Canvas commands."""
import repobee_plug as plug

CANVAS_CATEGORY = plug.cli.category(
        name            = "canvas",
        action_names    = [
            "create_canvas_git_mapping",
            "create_students_file",
            "init_assignment",
            "init_course",
            "prepare_assignment",
            "send_message",
            ],
        help            = "manage Canvas courses and assignments",
        description     = (
            "Manage Canvas courses and assignments."
            )
)