import PySimpleGUI as sg
import os
from urllib.parse                                 import urlparse
from repobee_canvas.gui                           import *
from repobee_canvas.command.create_students_files  import CreateStudentsiles

if __name__ == '__main__':
    if get_entry(KEY_BASE_URL) == None:
        set_entry(KEY_BASE_URL, "https://canvas.tue.nl/api/v1")

    if is_invalid(get_entry(KEY_STU_FILE)) or is_invalid(get_entry(KEY_STU_FILE_FOLDER)):
        set_entry(KEY_STU_FILE, resource_path("students.yaml"))
        set_entry(KEY_STU_FILE_FOLDER, resource_path())

    if is_invalid(get_entry(KEY_XLSX_INFO_FILE)) or is_invalid(get_entry(KEY_CSV_INFO_FILE)):
        set_entry(KEY_CSV_INFO_FILE, resource_path("students_info.csv"))
        set_entry(KEY_XLSX_INFO_FILE, resource_path("students_info.xlsx"))
        set_entry(KEY_INFO_FILE_FOLDER, resource_path())

    if get_entry(KEY_GROUP_CATEGORY) is None:
        set_entry(KEY_GROUP_CATEGORY, "Project Groups")

    if get_entry(KEY_COURSE_ID) is None:
        set_entry(KEY_COURSE_ID, "00000")

    window = make_window()

    while True:
        event, values = window.read()

        if event in ('Exit', sg.WIN_CLOSED): # if user closes window
            break

        elif event == 'token_bt':
            text = sg.popup_get_text('Access Token', default_text=get_entry(KEY_ACCESS_TOKEN))
            if text:
                window[KEY_ACCESS_TOKEN].update(value=text)
                set_entry(KEY_ACCESS_TOKEN, text)

        elif event == 'url_bt':
            text = sg.popup_get_text('Base URL', default_text=get_entry(KEY_BASE_URL))
            if text:
                window[KEY_BASE_URL].update(value=text)
                set_entry(KEY_BASE_URL, text)

        elif event == 'course_id_bt':
            text = sg.popup_get_text('Course ID', default_text=get_entry(KEY_COURSE_ID))
            if text:
                window[KEY_COURSE_ID].update(value=text)
                set_entry(KEY_COURSE_ID, text)

        elif event == 'group_set_bt':
            text = sg.popup_get_text('Group Set', default_text=get_entry(KEY_GROUP_CATEGORY))
            if text:
                window[KEY_GROUP_CATEGORY].update(value=text)
                set_entry(KEY_GROUP_CATEGORY, text)

        elif event == KEY_CSV_INFO_FILE_FOLDER:
            file_path = update_browse(values[KEY_CSV_INFO_FILE], True, ((TYPE_CSV),)) #, CSV)
            if file_path != "":
                window[KEY_CSV_INFO_FILE].update(file_path)
                set_entry(KEY_XLSX_INFO_FILE, file_path)
                file_path = os.path.splitext(file_path)[0]
                window[KEY_XLSX_INFO_FILE].update(file_path+".xlsx")
                set_entry(KEY_GROUP_CATEGORY, file_path+".xlsx")

        elif event == CSV:
            updateButton( not values[CSV], window[KEY_CSV_INFO_FILE_FOLDER])

        elif event == KEY_XLSX_INFO_FILE_FOLDER:
            file_path = update_browse(values[KEY_XLSX_INFO_FILE], True, ((TYPE_XLSX),)) #, XLSX)
            if file_path != "":
                window[KEY_XLSX_INFO_FILE].update(file_path)
                set_entry(KEY_XLSX_INFO_FILE, file_path)
                file_path = os.path.splitext(file_path)[0]
                window[KEY_CSV_INFO_FILE].update(file_path+".csv")
                set_entry(KEY_GROUP_CATEGORY, file_path+".csv")

        elif event == XLSX:
            updateButton( not values[XLSX], window[KEY_XLSX_INFO_FILE_FOLDER])

        elif event == KEY_STU_FILE_FOLDER:
            file_path = update_browse(values[KEY_STU_FILE], True, (TYPE_YAML,)) #, YAML)
            if file_path != "":
                window[KEY_STU_FILE].update(file_path)

        elif event == YAML:
            updateButton( not values[YAML], window[KEY_STU_FILE_FOLDER])

        elif event == "Execute":
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
            if is_empty(course_id, "Course ID") or not is_number(course_id, "Course ID"):
                    continue

            group_category_name = values[KEY_GROUP_CATEGORY]
            if is_empty(group_category_name, "Group Category"):
                continue

            stu_csv_info_file = None
            if csv:
                stu_csv_info_file = values[KEY_CSV_INFO_FILE]
                if is_empty(stu_csv_info_file, "Students Info CSV File"):
                    continue

            stu_xlsx_info_file = None
            if xlsx:
                stu_xlsx_info_file = values[KEY_XLSX_INFO_FILE]
                if is_empty(stu_xlsx_info_file, "Students Info Excel File"):
                    continue

            students_yaml_file = None
            if yaml:
                students_yaml_file = values[KEY_STU_FILE]
                if is_empty(students_yaml_file, "Students YAML File"):
                    continue

            CreateStudentsiles(urlparse(base_url), access_token, course_id, group_category_name, stu_csv_info_file, stu_xlsx_info_file, students_yaml_file)

        elif event == "token_tip":
            window[event].TooltipObject.showtip()
            sg.cprint(token_tip_ml)

        elif event == "info_file_tip":
            window[event].TooltipObject.showtip()
            sg.cprint(info_file_tip_ml)

        elif event.endswith("_tip"):
            window[event].TooltipObject.showtip()
            sg.cprint(window[event].TooltipObject.text)

        elif event == 'Clear History':
            window[KEY_ML].update('')

    window.close()