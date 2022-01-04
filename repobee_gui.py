import PySimpleGUI as sg
import os
from urllib.parse                                 import urlparse
from repobee_canvas.gui                           import *
from repobee_canvas.command.create_students_files  import CreateStudentsiles

if __name__ == '__main__':
    set_default_entries()
    window = make_window()
    last_screen_height = window.Size[1]

    while True:
        event, values = window.read()

        if event in (KEY_EXIT, sg.WIN_CLOSED): # if user closes window
            break

        elif event == 'token_bt':
            text = sg.popup_get_text('Access Token', default_text=get_entry(KEY_ACCESS_TOKEN), size=(80, 1))
            if text is not None:
                window[KEY_ACCESS_TOKEN].update(value=text)
                set_entry(KEY_ACCESS_TOKEN, text)

        elif event == 'url_bt':
            text = sg.popup_get_text('Base URL', default_text=get_entry(KEY_BASE_URL))
            if text is not None:
                window[KEY_BASE_URL].update(value=text)
                set_entry(KEY_BASE_URL, text)

        elif event == 'course_id_bt':
            text = sg.popup_get_text('Course ID', default_text=get_entry(KEY_COURSE_ID))
            if text is not None:
                if is_number(text, "Course ID"):
                    window[KEY_COURSE_ID].update(value=text)
                    set_entry(KEY_COURSE_ID, text)

        elif event == 'group_set_bt':
            text = sg.popup_get_text('Group Set', default_text=get_entry(KEY_GROUP_CATEGORY))
            if text is not None:
                window[KEY_GROUP_CATEGORY].update(value=text)
                set_entry(KEY_GROUP_CATEGORY, text)

        elif event == KEY_CSV_INFO_FILE_FOLDER:
            file_path = update_browse(values[KEY_CSV_INFO_FILE], True, ((TYPE_CSV),)) #, CSV)
            if file_path != "":
                window[KEY_CSV_INFO_FILE].update(file_path)
                set_entry(KEY_CSV_INFO_FILE, file_path)
                file_path = os.path.splitext(file_path)[0]
                window[KEY_XLSX_INFO_FILE].update(file_path+".xlsx")
                set_entry(KEY_XLSX_INFO_FILE, file_path+".xlsx")

        elif event in (CSV, XLSX, YAML, KEY_BASE_URL, KEY_COURSE_ID, KEY_GROUP_CATEGORY, KEY_STU_FILE):
            set_entry(event, values[event])

        elif event == KEY_XLSX_INFO_FILE_FOLDER:
            file_path = update_browse(values[KEY_XLSX_INFO_FILE], True, ((TYPE_XLSX),)) #, XLSX)
            if file_path != "":
                window[KEY_XLSX_INFO_FILE].update(file_path)
                set_entry(KEY_XLSX_INFO_FILE, file_path)
                file_path = os.path.splitext(file_path)[0]
                window[KEY_CSV_INFO_FILE].update(file_path+".csv")
                set_entry(KEY_CSV_INFO_FILE, file_path+".csv")

        elif event == KEY_STU_FILE_FOLDER:
            file_path = update_browse(values[KEY_STU_FILE], True, (TYPE_YAML,)) #, YAML)
            if file_path != "":
                window[KEY_STU_FILE].update(file_path)
                set_entry(KEY_STU_FILE, file_path)

        elif event in [KEY_GIT_ID, KEY_EMAIL]:
            set_entry(MEMBER_OPTION, event)

        elif event == KEY_CONF_LOCK:
            update_option_state(window, event)

        elif event in (KEY_INC_GROUP, KEY_INC_MEMBER, KEY_INC_INITIAL):
            set_entry(event, values[event])
            if event == KEY_INC_MEMBER:
                window[KEY_INC_INITIAL].update(disabled=not values[KEY_INC_MEMBER])

        elif event == KEY_COL_PERCENT:
            update_col_percent(window, last_screen_height, values[event])

        elif event == "Conf":
            wh = window.Size[1]
            if wh == last_screen_height:
                continue
            update_column_height(window[KEY_CONFIG_COL], wh, last_screen_height)
            last_screen_height = wh

        elif event == KEY_EXECUTE:
            csv = values[CSV]
            xlsx = values[XLSX]
            yaml = values[YAML]
            if not csv and not xlsx and not yaml:
                popup("Please at least select one file to create.")
                continue

            access_token = values[KEY_ACCESS_TOKEN]
            if is_empty(access_token, "Access Token"):
                continue

            base_url = values[KEY_BASE_URL]
            if is_empty(base_url, "Base URL"):
                continue

            course_id = values[KEY_COURSE_ID]
            if is_empty(course_id, "Course ID"):
                continue

            group_category_name = values[KEY_GROUP_CATEGORY]
            if is_empty(group_category_name, "Group Category"):
                continue

            stu_csv_info_file = None
            if csv:
                stu_csv_info_file = values[KEY_CSV_INFO_FILE]
                if is_empty(stu_csv_info_file, "Students Info CSV File") or is_path_invalid(stu_csv_info_file, "Info"):
                    continue

            stu_xlsx_info_file = None
            if xlsx:
                stu_xlsx_info_file = values[KEY_XLSX_INFO_FILE]
                if is_empty(stu_xlsx_info_file, "Students Info Excel File") or is_path_invalid(stu_xlsx_info_file, "Info"):
                    continue

            students_yaml_file = None
            if yaml:
                students_yaml_file = values[KEY_STU_FILE]
                if is_empty(students_yaml_file, "Students YAML File") or is_path_invalid(students_yaml_file, "YAML"):
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

            CreateStudentsiles(urlparse(base_url), access_token, course_id, group_category_name, stu_csv_info_file, stu_xlsx_info_file, students_yaml_file, get_entry(MEMBER_OPTION), include_group, include_member, include_initials)

        elif event == "token_tip":
            window[event].TooltipObject.showtip()
            sg.cprint(token_tip_ml)

        elif event in ("info_file_tip", "info_file_excel_tip"):
            window[event].TooltipObject.showtip()
            sg.cprint(info_file_tip_ml)

        elif event.endswith("_tip"):
            window[event].TooltipObject.showtip()
            sg.cprint(window[event].TooltipObject.text)

        elif event == KEY_CLEAR:
            window[KEY_ML].update('')
            update_progress(0, 100)

    window.close()