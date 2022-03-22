import sys
import getopt
import PySimpleGUI as sg
from repobee_canvas import common
from repobee_canvas.gui import (
    KEY_BASE_URL,
    KEY_ACCESS_TOKEN,
    KEY_COURSE_ID,
    KEY_COURSES,
    KEY_EMAIL,
    KEY_GROUP_CATEGORY,
    KEY_MEMBER_OPTION,
    KEY_CSV_INFO_FILE,
    KEY_XLSX_INFO_FILE,
    KEY_STU_FILE,
    KEY_INC_GROUP,
    KEY_INC_MEMBER,
    KEY_INC_INITIAL,
)
from repobee_canvas.command.create_students_files import CreateStudentsFiles
from repobee_canvas.command.verify_course_id import VerifyCourseByID


KEY_INFO = "info"
KEY_VERIFY = "verify"


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
    action = None
    group_category_name = None
    member_option = None
    stu_csv_info_file = None
    stu_xlsx_info_file = None
    students_yaml_file = None
    include_group = False
    include_member = False
    include_initials = False

    try:
        opts, args = getopt.gnu_getopt(
            sys.argv[1:],
            "ht:g:o:GMI",
            [
                "access_token=",
                "base_url=",
                "bu=",
                "course_id=",
                "group=",
                "option=" "inc_group=",
                "inc_member=",
                "inc_initial=",
                "help",
            ],
        )

        if len(args):
            action = args[0]
            if not action in (KEY_VERIFY, KEY_INFO):
                raise InvalidArgument(
                    "Invalid action. verify or info is available."
                )
        else:
            raise InvalidArgument(
                "Invalid action. verify or info is available."
            )

        for o, a in opts:
            if o in ("-h", "--help"):
                # TODO
                print("help message")
            elif o in ("-t", "--access_token"):
                access_token = a
            elif o in ("--base_url"):
                base_url = a
            elif o in ("--course_id"):
                try:
                    course_id = int(a)
                except Exception:
                    raise InvalidArgument(
                        "Invalid course ID. Course ID should be a number."
                    )
            elif o in ("-g", "--group"):
                group_category_name = a
            elif o in ("-o", "--option"):
                member_option = a
            elif o in ("-G"):
                include_group = True
            elif o in ("--inc_group"):
                include_group = get_boolean_argument(a)
            elif o in ("-M"):
                include_member = True
            elif o in ("--inc_member"):
                include_member = get_boolean_argument(a)
            elif o in ("-I"):
                include_initials = True
            elif o in ("--inc_initial"):
                include_initials = get_boolean_argument(a)

        course = None
        settings = sg.UserSettings("canvas_info.json")
        courses = settings[KEY_COURSES]

        if not course_id:
            course_id = settings[KEY_COURSE_ID]
            if not course_id:
                raise InvalidArgument("Invalid course ID. Please finish the settings")

        if courses:
            for c in courses:
                if c[4:].startswith(course_id):
                    course = settings[course_id]

        if course:
            if not base_url:
                base_url = course[KEY_BASE_URL]

            if not access_token:
                access_token = course[KEY_ACCESS_TOKEN]

        if not base_url:
            raise InvalidArgument("Invalid base url. Please finish the settings")

        if not access_token:
            raise InvalidArgument(
                "Invalid access token. Please finish the settings"
            )

        if action == KEY_VERIFY:
            # course_name, group_set =
            VerifyCourseByID(
                base_url, access_token, int(course_id)
            )
        elif action == KEY_INFO:
            if not group_category_name and course:
                group_category_name = course[KEY_GROUP_CATEGORY]
                if not group_category_name:
                    raise InvalidArgument(
                        "Invalid group category. Please  finish the settings"
                    )

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

                if not member_option:
                    member_option = course[KEY_MEMBER_OPTION]

            if not member_option:
                member_option = KEY_EMAIL

            CreateStudentsFiles(
                base_url,
                access_token,
                int(course_id),
                group_category_name,
                stu_csv_info_file,
                stu_xlsx_info_file,
                students_yaml_file,
                member_option,
                include_group,
                include_member,
                include_initials,
            )
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
