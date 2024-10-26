from pathlib import Path

import PySimpleGUI as sg

from repobee_canvas import common, gui
from repobee_canvas.command.create_students_files import CreateStudentsFiles
from repobee_canvas.command.verify_course_id import VerifyCourseByID
from repobee_canvas.gui import (
    CSV,
    DEFAULT_COURSE_ID,
    KEY_ACCESS_TOKEN,
    KEY_BASE_URL,
    KEY_CLEAR,
    KEY_CLONE_COURSE,
    KEY_COL_PERCENT,
    KEY_CONFIG_COL,
    KEY_COURSE_NAME,
    KEY_COURSES,
    KEY_CSV_INFO_FILE,
    KEY_DELETE_COURSE,
    KEY_EDIT_TOKEN,
    KEY_EDIT_URL,
    KEY_EMAIL,
    KEY_END,
    KEY_EXECUTE,
    KEY_EXIT,
    KEY_GIT_ID,
    KEY_HELP,
    KEY_INC_GROUP,
    KEY_INC_INITIAL,
    KEY_INC_MEMBER,
    KEY_INFO_FILE_FOLDER,
    KEY_INFO_FILE_FOLDER_FB,
    KEY_MEM_BOTH,
    KEY_MEMBER_OPTION,
    KEY_ML,
    KEY_NEW_COURSE,
    KEY_STU_FILE,
    KEY_STU_FILE_FOLDER,
    KEY_TEAMMATES_INFO_FILE,
    KEY_URL_OPTION,
    KEY_URL_OPTIONS,
    KEY_VERIFY,
    KEY_XLSX_INFO_FILE,
    MODE_CLONE,
    MODE_CREATE,
    MODE_PARSE,
    TEAMMATES,
    TYPE_YAML,
    XLSX,
    YAML,
    get_entry,
    get_input_course_id,
    is_empty,
    is_path_invalid,
    popup,
    save_as,
    set_course_info,
    set_update_course_info,
    update_browse,
    update_course_settings,
)


def main():
    common.CLI = False
    gui.set_default_entries()
    window = gui.make_window()
    last_screen_height = window.Size[1]

    while True:
        event, values = window.read()

        if event in (KEY_EXIT, sg.WIN_CLOSED):  # if user closes window
            break

        elif event == KEY_EDIT_TOKEN:
            text = sg.popup_get_text(
                "Access Token",
                default_text=window[KEY_ACCESS_TOKEN].DefaultText,
                size=(80, 1),
            )
            if text is not None:
                set_update_course_info(window, KEY_ACCESS_TOKEN, text)

        elif event == KEY_EDIT_URL:
            text = sg.popup_get_text(
                "Base URL", default_text=window[KEY_BASE_URL].DefaultText
            )
            if text is not None:
                window[KEY_BASE_URL].update(value=text)
                gui.set_course_url(values[KEY_URL_OPTION], text)

        elif event == KEY_INFO_FILE_FOLDER_FB:
            file_path = update_browse(values[KEY_INFO_FILE_FOLDER])
            if file_path != "":
                set_course_info(KEY_INFO_FILE_FOLDER, file_path)
                window[KEY_INFO_FILE_FOLDER].update(value=file_path)

        elif event in (CSV, XLSX, YAML, TEAMMATES, KEY_STU_FILE):
            set_course_info(event, values[event])

        elif event == KEY_STU_FILE_FOLDER:
            file_path = save_as(values[KEY_STU_FILE], (TYPE_YAML,))  # , YAML)
            if file_path != "":
                set_update_course_info(window, KEY_STU_FILE, file_path)

        elif event in [KEY_GIT_ID, KEY_EMAIL, KEY_MEM_BOTH]:
            set_course_info(KEY_MEMBER_OPTION, event)

        elif event in (KEY_INC_GROUP, KEY_INC_MEMBER, KEY_INC_INITIAL):
            set_course_info(event, values[event])
            if event == KEY_INC_MEMBER:
                window[KEY_INC_INITIAL].update(disabled=not values[KEY_INC_MEMBER])

        elif event == KEY_COL_PERCENT:
            gui.update_col_percent(window, last_screen_height, values[event])

        elif event == KEY_CLONE_COURSE:
            course_id = get_input_course_id(
                window[KEY_COURSES].Values, DEFAULT_COURSE_ID
            )
            if course_id:
                update_course_settings(
                    window, course_id, get_entry(gui.course_id), MODE_CLONE
                )

        elif event == KEY_NEW_COURSE:
            course_id = course_id = get_input_course_id(
                window[KEY_COURSES].Values, DEFAULT_COURSE_ID
            )
            if course_id:
                update_course_settings(window, course_id, None, MODE_CREATE)

        elif event == KEY_COURSES:
            course_id = values[event].split(" ")[1]
            update_course_settings(
                window, course_id, gui.settings[course_id], MODE_PARSE
            )

        elif event == "Conf":
            wh = window.Size[1]
            if wh == last_screen_height:
                continue
            gui.update_column_height(window[KEY_CONFIG_COL], wh, last_screen_height)
            last_screen_height = wh

        elif event == KEY_DELETE_COURSE:
            res = sg.popup_ok_cancel(
                "Are you sure: this will remove the course "
                + window[KEY_COURSES].DefaultValue
                + " from the Canvas Info app?",
                keep_on_top=True,
            )
            if res == "OK":
                gui.delete_course_id(window)

        elif event == KEY_URL_OPTION:
            set_course_info(KEY_URL_OPTION, values[event])
            set_update_course_info(
                window,
                KEY_BASE_URL,
                gui.course_info.course[KEY_URL_OPTIONS][values[event]],
            )
            gui.check_url_lock(window[KEY_EDIT_URL], values[KEY_URL_OPTION])

        elif event in (KEY_EXECUTE, KEY_VERIFY):
            access_token = values[KEY_ACCESS_TOKEN]
            if is_empty(access_token, "Access Token"):
                continue

            base_url = values[KEY_BASE_URL]
            if is_empty(base_url, "Base URL"):
                continue

            if event == KEY_VERIFY:
                course_title = window[KEY_COURSES].DefaultValue
                courses_list = window[KEY_COURSES].Values
                ind = courses_list.index(course_title)
                common.inform("Verifying...")
                course_name, group_set = VerifyCourseByID(
                    base_url, access_token, int(gui.course_id)
                )
                if (
                    course_name
                    and gui.course_info.course[KEY_COURSE_NAME] != course_name
                ):
                    set_course_info(KEY_COURSE_NAME, course_name)
                    course_title = gui.course_info.get_course_title()
                    courses_list[ind] = course_title
                    gui.update_courses_list(window, courses_list)
                    window[KEY_COURSES].update(value=course_title)

                if course_name and group_set:
                    common.inform("All settings successfully verified")
                continue

            csv = values[CSV]
            xlsx = values[XLSX]
            yaml = values[YAML]
            teammates = values[TEAMMATES]
            if not csv and not xlsx and not yaml and not teammates:
                popup("Please at least select one file to create.")
                continue

            current_course = gui.course_info.get()
            stu_csv_info_file = None
            stu_xlsx_info_file = None
            stu_teammates_file = None
            if csv or xlsx or teammates:
                homepath = values[KEY_INFO_FILE_FOLDER]
                if is_path_invalid(homepath, "Info"):
                    continue

                if csv:
                    stu_csv_info_file = str(
                        Path(homepath, current_course[KEY_CSV_INFO_FILE])
                    )

                if xlsx:
                    stu_xlsx_info_file = str(
                        Path(homepath, current_course[KEY_XLSX_INFO_FILE])
                    )

                if teammates:
                    stu_teammates_file = str(
                        Path(homepath, current_course[KEY_TEAMMATES_INFO_FILE])
                    )

            students_yaml_file = None
            if yaml:
                students_yaml_file = values[KEY_STU_FILE]
                if is_empty(
                    students_yaml_file, "Students YAML File"
                ) or is_path_invalid(students_yaml_file, "YAML"):
                    continue

            include_group = values[KEY_INC_GROUP]
            include_member = values[KEY_INC_MEMBER]
            if include_member:
                include_initials = values[KEY_INC_INITIAL]
            else:
                include_initials = False

            if not include_group and not include_member and not include_initials:
                popup("Please select at least 1 option.")
                continue

            common.inform("Executing the Execute command...")
            gui.disable_all_buttons(window)
            window.perform_long_operation(
                lambda: CreateStudentsFiles(
                    base_url,
                    access_token,
                    int(gui.course_id),
                    stu_csv_info_file,
                    stu_xlsx_info_file,
                    students_yaml_file,
                    stu_teammates_file,
                    gui.course_info.course[KEY_MEMBER_OPTION],
                    include_group,
                    include_member,
                    include_initials,
                ),
                KEY_END,
            )

        elif event == KEY_END:
            common.inform("Done")
            gui.enable_all_buttons(window)

        elif event == KEY_HELP:
            common.inform(gui.help_info)

        elif event == "token_tip":
            tooltip = window[event].TooltipObject
            assert tooltip is not None
            tooltip.showtip()
            common.inform(gui.token_tip_ml)

        elif event in ("info_file_tip", "info_file_excel_tip"):
            tooltip = window[event].TooltipObject
            assert tooltip is not None
            tooltip.showtip()
            common.inform(gui.info_file_tip_ml)

        elif event.endswith("_tip"):
            tooltip = window[event].TooltipObject
            assert tooltip is not None
            tooltip.showtip()
            common.inform(tooltip.text)

        elif event == KEY_CLEAR:
            window[KEY_ML].update(value="")
            gui.update_progress(0, 100)

    window.close()
