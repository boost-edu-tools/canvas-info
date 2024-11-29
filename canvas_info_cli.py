import getopt
import sys
from argparse import (
    ArgumentParser,
    BooleanOptionalAction,
    RawDescriptionHelpFormatter,
)
from math import fabs
from tkinter.font import names

import PySimpleGUI as sg

from repobee_canvas import common
from repobee_canvas.command.create_students_files import CreateStudentsFiles
from repobee_canvas.command.verify_course_id import VerifyCourseByID
from repobee_canvas.gui import (
    KEY_ACCESS_TOKEN,
    KEY_BASE_URL,
    KEY_COURSE_ID,
    KEY_COURSES,
    KEY_CSV_INFO_FILE,
    KEY_EMAIL,
    KEY_GIT_ID,
    KEY_INC_GROUP,
    KEY_INC_INITIAL,
    KEY_INC_MEMBER,
    KEY_FULL_GROUPS,
    KEY_MEMBER_OPTION,
    KEY_STU_FILE,
    KEY_XLSX_INFO_FILE,
)
from repobee_canvas.tiphelp import Help

KEY_INFO = "info"
KEY_VERIFY = "verify"

help = Help()


class InvalidArgument(Exception):
    def __init__(self, msg):
        super(InvalidArgument, self).__init__(msg)
        self.msg = msg


def get_boolean_argument(arg):
    if isinstance(arg, bool):
        return arg
    elif arg is None or arg.lower() == "false" or arg.lower() == "f" or arg == "0":
        return False
    elif arg.lower() == "true" or arg.lower() == "t" or arg == "1":
        return True

    raise InvalidArgument("The given option argument is not a valid boolean.")


def main():
    base_url = None
    access_token = None
    course_id = None
    member_option = None
    stu_csv_info_file = None
    stu_xlsx_info_file = None
    students_yaml_file = None
    include_group = False
    include_member = False
    include_initials = False

    try:
        parser = ArgumentParser(
            prog="cavas_info_cli",
            formatter_class=RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "-t",
            "--access_token",
            help=help.access_token,
        )
        parser.add_argument(
            "--base_url",
            help=help.base_url,
        )
        parser.add_argument(
            "--course_id",
            type=int,
            help=help.course_id,
        )
        parser.add_argument(
            "-o",
            "--option",
            action="append",
            choices=[KEY_EMAIL, KEY_GIT_ID],
            help=help.option,
        )
        parser.add_argument(
            "-G",
            "--inc_group",
            action=BooleanOptionalAction,
            default=False,
            help=help.include_group,
        )
        parser.add_argument(
            "-M",
            "--inc_member",
            action=BooleanOptionalAction,
            default=False,
            help=help.include_member,
        )
        parser.add_argument(
            "-I",
            "--inc_initial",
            action=BooleanOptionalAction,
            default=False,
            help=help.include_initial,
        )
        parser.add_argument(
            "-F",
            "--full_groups",
            action=BooleanOptionalAction,
            default=True,
            help=help.full_groups,
        )
        parser.add_argument(
            "--info_file",
            help=help.info_file,
        )
        parser.add_argument(
            "--yaml_file",
            help=help.yaml_file,
        )
        parser.add_argument(
            "action",
            choices=[KEY_INFO, KEY_VERIFY],
            help=help.action,
        )

        namespace = parser.parse_args()

        course = None
        settings = sg.UserSettings("canvas_info.json")
        courses = settings[KEY_COURSES]

        course_id = namespace.course_id
        if not course_id:
            course_id = settings[KEY_COURSE_ID]
            if not course_id:
                raise InvalidArgument("Invalid course ID. Please finish the settings")

        if courses:
            for c in courses:
                if c[4:].startswith(course_id):
                    course = settings[course_id]

        base_url = namespace.base_url
        access_token = namespace.access_token
        if course:
            if not base_url:
                base_url = course[KEY_BASE_URL]

            if not access_token:
                access_token = course[KEY_ACCESS_TOKEN]

        if not base_url:
            raise InvalidArgument("Invalid base url. Please finish the settings")

        if not access_token:
            raise InvalidArgument("Invalid access token. Please finish the settings")

        if namespace.action == KEY_VERIFY:
            # course_name, group_set =
            VerifyCourseByID(base_url, access_token, int(course_id))
        elif namespace.action == KEY_INFO:
            if namespace.info_file:
                stu_csv_info_file = namespace.info_file + ".csv"
                stu_xlsx_info_file = namespace.info_file + ".xlsx"

            if namespace.yaml_file:
                students_yaml_file = namespace.yaml_file + ".yaml"

            include_group = namespace.inc_group
            include_member = namespace.inc_member
            include_initials = namespace.inc_initials
            only_full_groups = namespace.only_full_groups
            member_option = namespace.option

            if course:
                if not stu_csv_info_file:
                    stu_csv_info_file = course[KEY_CSV_INFO_FILE]

                if not stu_xlsx_info_file:
                    stu_xlsx_info_file = course[KEY_XLSX_INFO_FILE]

                if not students_yaml_file:
                    students_yaml_file = course[KEY_STU_FILE]

                if not include_group:
                    include_group = course[KEY_INC_GROUP]

                if not include_member:
                    include_member = course[KEY_INC_MEMBER]

                if not include_initials:
                    include_initials = course[KEY_INC_INITIAL]

                if not only_full_groups:
                    only_full_groups = course[KEY_FULL_GROUPS]

                if not member_option:
                    member_option = course[KEY_MEMBER_OPTION]

            if not member_option:
                member_option = KEY_EMAIL

            CreateStudentsFiles(
                base_url,
                access_token,
                int(course_id),
                stu_csv_info_file,
                stu_xlsx_info_file,
                students_yaml_file,
                member_option,
                include_group,
                include_member,
                include_initials,
            )
            common.inform("Done")
        else:
            common.fault("Invalid action.")
            sys.exit(1)

    except (getopt.error, InvalidArgument) as exception:
        common.fault(sys.argv[0], error=exception)
        common.fault(f"Try `{sys.argv[0]} --help' for more information.")
        sys.exit(1)
    except Exception as e:
        # an unknown, unexpected error occurred which caused the command to abort prematurely.
        common.fault(str(e))
        sys.exit(2)
    else:
        # error code 0: no errors.
        common.inform("Done.")


if __name__ == "__main__":
    main()
