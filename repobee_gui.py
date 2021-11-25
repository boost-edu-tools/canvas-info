import PySimpleGUI as sg
import os
from urllib.parse                                 import urlparse
from repobee_canvas.gui                           import *
from repobee_canvas.command.create_students_files  import CreateStudentsiles

if __name__ == '__main__':
    if sg.user_settings_get_entry(KEY_BASE_URL) == None:
        sg.user_settings_set_entry(KEY_BASE_URL, "https://canvas.tue.nl/api/v1")

    if is_invalid(sg.user_settings_get_entry(KEY_STU_FILE)) or is_invalid(sg.user_settings_get_entry(KEY_STU_FILE_FOLDER)):
        sg.user_settings_set_entry(KEY_STU_FILE, resource_path("students.yaml"))
        sg.user_settings_set_entry(KEY_STU_FILE_FOLDER, resource_path())

    if is_invalid(sg.user_settings_get_entry(KEY_XLSX_INFO_FILE)) or is_invalid(sg.user_settings_get_entry(KEY_CSV_INFO_FILE)):
        sg.user_settings_set_entry(KEY_CSV_INFO_FILE, resource_path("students_info.csv"))
        sg.user_settings_set_entry(KEY_XLSX_INFO_FILE, resource_path("students_info.xlsx"))
        sg.user_settings_set_entry(KEY_INFO_FILE_FOLDER, resource_path())

    if sg.user_settings_get_entry(KEY_GROUP_CATEGORY) is None:
        sg.user_settings_set_entry(KEY_GROUP_CATEGORY, "Project Groups")

    window = make_window()

    while True:
        event, values = window.read()

        if event in ('Exit', sg.WIN_CLOSED): # if user closes window
            break

        elif event == KEY_CSV_INFO_FILE_FOLDER:
            file_path = update_browse(values[KEY_CSV_INFO_FILE], True, ((TYPE_CSV),)) #, CSV)
            if file_path != "":
                window[KEY_CSV_INFO_FILE].update(file_path)
                file_path = os.path.splitext(file_path)[0]
                window[KEY_XLSX_INFO_FILE].update(file_path+".xlsx")

        elif event == CSV:
            updateButton( not values[CSV], window[KEY_CSV_INFO_FILE_FOLDER])

        elif event == KEY_XLSX_INFO_FILE_FOLDER:
            file_path = update_browse(values[KEY_XLSX_INFO_FILE], True, ((TYPE_XLSX),)) #, XLSX)
            if file_path != "":
                window[KEY_XLSX_INFO_FILE].update(file_path)
                file_path = os.path.splitext(file_path)[0]
                window[KEY_CSV_INFO_FILE].update(file_path+".csv")

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

            del(values[KEY_ML])
            for key, val in values.items():
                sg.user_settings_set_entry(key, val)

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