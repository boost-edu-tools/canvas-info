import PySimpleGUI as sg
import os
from urllib.parse import urlparse
from repobee_canvas.gui import *
from repobee_canvas import gui
from repobee_canvas.command.create_students_files import CreateStudentsFiles
from repobee_canvas.command.verify_course_id import VerifyCourseByID

if __name__ == "__main__":
    set_default_entries()
    window = make_window()
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
                set_course_url(values[KEY_URL_OPTION], text)

        elif event == KEY_CSV_INFO_FILE_FOLDER:
            file_path = update_browse(
                values[KEY_CSV_INFO_FILE], True, ((TYPE_CSV),)
            )  # , CSV)
            if file_path != "":
                set_update_course_info(window, KEY_CSV_INFO_FILE, file_path)
                file_path = os.path.splitext(file_path)[0]
                set_update_course_info(window, KEY_XLSX_INFO_FILE, file_path + ".xlsx")

        elif event in (CSV, XLSX, YAML, KEY_GROUP_CATEGORY, KEY_STU_FILE):
            set_course_info(event, values[event])

        elif event == KEY_XLSX_INFO_FILE_FOLDER:
            file_path = update_browse(
                values[KEY_XLSX_INFO_FILE], True, ((TYPE_XLSX),)
            )  # , XLSX)
            if file_path != "":
                set_update_course_info(window, KEY_XLSX_INFO_FILE, file_path)
                file_path = os.path.splitext(file_path)[0]
                set_update_course_info(window, KEY_CSV_INFO_FILE, file_path + ".csv")

        elif event == KEY_STU_FILE_FOLDER:
            file_path = update_browse(
                values[KEY_STU_FILE], True, (TYPE_YAML,)
            )  # , YAML)
            if file_path != "":
                set_update_course_info(window, KEY_STU_FILE, file_path)

        elif event in [KEY_GIT_ID, KEY_EMAIL]:
            set_course_info(KEY_MEMBER_OPTION, event)

        elif event in (KEY_INC_GROUP, KEY_INC_MEMBER, KEY_INC_INITIAL):
            set_course_info(event, values[event])
            if event == KEY_INC_MEMBER:
                window[KEY_INC_INITIAL].update(disabled=not values[KEY_INC_MEMBER])

        elif event == KEY_COL_PERCENT:
            update_col_percent(window, last_screen_height, values[event])

        elif event == KEY_CLONE_COURSE:
            course_id = get_input_course_id(
                window[KEY_COURSES].Values, DEFAULT_COURSE_ID
            )
            if course_id:
                update_course_settings(
                    window, course_id, get_entry(gui.course_id), MODE_CLONE
                )

        elif event == KEY_RENAME_COURSE:
            course_id = get_input_course_id(window[KEY_COURSES].Values, gui.course_id)
            if course_id:
                update_course_settings(
                    window, course_id, get_entry(gui.course_id), MODE_RENAME
                )

        elif event == KEY_NEW_COURSE:
            course_id = course_id = get_input_course_id(
                window[KEY_COURSES].Values, DEFAULT_COURSE_ID
            )
            if course_id:
                update_course_settings(window, course_id, None, MODE_CREATE)

        elif event == KEY_COURSES:
            course_id = values[event].split(" ")[1]
            update_course_settings(window, course_id, settings[course_id], MODE_PARSE)

        elif event == KEY_GROUP_CATEGORIES:
            set_update_course_info(window, KEY_GROUP_CATEGORY, values[event])

        elif event == "Conf":
            wh = window.Size[1]
            if wh == last_screen_height:
                continue
            update_column_height(window[KEY_CONFIG_COL], wh, last_screen_height)
            last_screen_height = wh

        elif event == KEY_DELETE:
            res = sg.popup_ok_cancel(
                "Are you sure: this will remove the course "
                + window[KEY_COURSES].DefaultValue
                + " from the Canvas Info app?",
                keep_on_top=True,
            )
            if res == "OK":
                delete_course_id(window)

        elif event == KEY_URL_OPTION:
            set_course_info(KEY_URL_OPTION, values[event])
            set_update_course_info(
                window,
                KEY_BASE_URL,
                gui.course_info.course[KEY_URL_OPTIONS][values[event]],
            )
            check_url_lock(window[KEY_EDIT_URL], values[KEY_URL_OPTION])

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
                sg.cprint("Verifying...")
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
                    update_courses_list(window, courses_list)
                    window[KEY_COURSES].update(value=course_title)
                if group_set and group_set != window[KEY_GROUP_CATEGORY].Values:
                    set_course_info(KEY_GROUP_CATEGORIES, group_set)
                    window[KEY_GROUP_CATEGORY].update(values=group_set)
                    set_update_course_info(window, KEY_GROUP_CATEGORY, group_set[0])

                if course_name and group_set:
                    sg.cprint("All settings successfully verified")
                continue

            csv = values[CSV]
            xlsx = values[XLSX]
            yaml = values[YAML]
            if not csv and not xlsx and not yaml:
                popup("Please at least select one file to create.")
                continue

            group_category_name = values[KEY_GROUP_CATEGORY]
            if is_invalid(group_category_name):
                popup("Please verify first, and select the group category")
                continue

            stu_csv_info_file = None
            if csv:
                stu_csv_info_file = values[KEY_CSV_INFO_FILE]
                if is_empty(
                    stu_csv_info_file, "Students Info CSV File"
                ) or is_path_invalid(stu_csv_info_file, "Info"):
                    continue

            stu_xlsx_info_file = None
            if xlsx:
                stu_xlsx_info_file = values[KEY_XLSX_INFO_FILE]
                if is_empty(
                    stu_xlsx_info_file, "Students Info Excel File"
                ) or is_path_invalid(stu_xlsx_info_file, "Info"):
                    continue

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

            sg.cprint("Executing the Execute command...")
            disable_all_buttons(window)
            window.perform_long_operation(
                lambda: CreateStudentsFiles(
                    base_url,
                    access_token,
                    gui.course_id,
                    group_category_name,
                    str(stu_csv_info_file),
                    str(stu_xlsx_info_file),
                    str(students_yaml_file),
                    gui.course_info.course[KEY_MEMBER_OPTION],
                    include_group,
                    include_member,
                    include_initials,
                ),
                KEY_END,
            )

        elif event == KEY_END:
            enable_all_buttons(window)

        elif event == KEY_HELP:
            sg.cprint(help_info)

        elif event == "token_tip":
            tooltip = window[event].TooltipObject
            assert tooltip is not None
            tooltip.showtip()
            sg.cprint(token_tip_ml)

        elif event in ("info_file_tip", "info_file_excel_tip"):
            tooltip = window[event].TooltipObject
            assert tooltip is not None
            tooltip.showtip()
            sg.cprint(info_file_tip_ml)

        elif event.endswith("_tip"):
            tooltip = window[event].TooltipObject
            assert tooltip is not None
            tooltip.showtip()
            sg.cprint(tooltip.text)

        elif event == KEY_CLEAR:
            window[KEY_ML].update("")
            update_progress(0, 100)

    window.close()
