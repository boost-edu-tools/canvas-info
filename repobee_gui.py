import PySimpleGUI as sg
from repobee_canvas.gui import *

settings_tip = "Please complete the settings before clicking the other buttons."
stu_yaml_tip = "This is used to generate the students file in Yaml format used by RepoBee. RepoBee uses the students file to create a GitHub team or GitLab subgroup for groups of students or an individual student participating in an assignment, and then create a repository for this team or subgroup."
stu_info_tip = "This is used to generate an Excel info file that is converted from the Canvas-Git mapping table."

def make_window():
    sg.theme('DarkAmber')

    layout = [
        [
            sg.Button('Settings', k=KEY_SETTINGS), add_help_button('settings_tip', settings_tip),
            sg.Button('Create student info file', k=KEY_CSV_INFO_FILE), add_help_button('stu_info_tip', stu_info_tip),
            sg.Button('Create student yaml file', k=KEY_STU_FILE), add_help_button('stu_yaml_tip', stu_yaml_tip)
        ],
        [
            sg.Multiline(size=(70, 20), key=KEY_ML, reroute_cprint=True, expand_y=True, expand_x=True, auto_refresh=True)
        ],
        [
            sg.B('Exit'), sg.B('Clear History')
        ]
    ]

    window = sg.Window('Repobee Canvas', layout, icon=icon, finalize=True)
    return window

if __name__ == '__main__':
    if sg.user_settings_get_entry(KEY_BASE_URL) == None:
        sg.user_settings_set_entry(KEY_BASE_URL, "https://canvas.tue.nl/api/v1")

    if is_invalid(sg.user_settings_get_entry(KEY_STU_FILE)) or is_invalid(sg.user_settings_get_entry(KEY_STU_FILE_FOLDER)):
        sg.user_settings_set_entry(KEY_STU_FILE, resource_path("students.yaml"))
        sg.user_settings_set_entry(KEY_STU_FILE_FOLDER, resource_path())

    if is_invalid(sg.user_settings_get_entry(KEY_XLSX_INFO_FILE)) or is_invalid(sg.user_settings_get_entry(KEY_INFO_FILE_FOLDER)):
        sg.user_settings_set_entry(KEY_CSV_INFO_FILE, resource_path("students_info.csv"))
        sg.user_settings_set_entry(KEY_XLSX_INFO_FILE, resource_path("students_info.xlsx"))
        sg.user_settings_set_entry(KEY_INFO_FILE_FOLDER, resource_path())

    if not sg.user_settings_get_entry(CSV) and not sg.user_settings_get_entry(XLSX):
        sg.user_settings_set_entry(CSV, True)

    access_token = sg.user_settings_get_entry(KEY_ACCESS_TOKEN)
    base_url = sg.user_settings_get_entry(KEY_BASE_URL)

    window = make_window()
    while True:
        event, values = window.read()

        if event in ('Exit', sg.WIN_CLOSED): # if user closes window
            break

        elif event == KEY_SETTINGS:
            (access_token, base_url) = settings_window(access_token, base_url, window)

        elif event == KEY_STU_FILE:
            if is_ready(access_token, base_url):
                students_yaml_file_window(window)

        elif event == KEY_CSV_INFO_FILE:
            if is_ready(access_token, base_url):
                students_info_file_window(access_token, base_url, window)

        elif event.endswith("_tip"):
            window[event].TooltipObject.showtip()
            sg.cprint(window[event].TooltipObject.text)

        elif event == 'Clear History':
            window[KEY_ML].update('')

    window.close()