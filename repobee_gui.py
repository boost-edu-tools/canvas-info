import PySimpleGUI as sg
from repobee_canvas.gui import *

def make_window():
    sg.theme('DarkAmber')

    layout = [  [sg.Button('Settings', k=KEY_SETTINGS), sg.Button('Create git map', k=KEY_GIT_MAP), sg.Button('Create student file', k=KEY_STU_FILE)] ]

    window = sg.Window('Repobee Canvas', layout, icon=icon, finalize=True)
    return window

if __name__ == '__main__':
    if sg.user_settings_get_entry(KEY_BASE_URL) == None:
        sg.user_settings_set_entry(KEY_BASE_URL, "https://canvas.tue.nl/api/v1")

    if sg.user_settings_get_entry(KEY_GIT_MAP) == None:
        sg.user_settings_set_entry(KEY_GIT_MAP, resource_path("canvas-git-map.csv"))
        sg.user_settings_set_entry(KEY_GIT_MAP_FOLDER, resource_path())

    if sg.user_settings_get_entry(KEY_STU_FILE) == None:
        sg.user_settings_set_entry(KEY_STU_FILE, resource_path("students.yaml"))
        sg.user_settings_set_entry(KEY_STU_FILE_FOLDER, resource_path())

    access_token = sg.user_settings_get_entry(KEY_ACCESS_TOKEN)
    base_url = sg.user_settings_get_entry(KEY_BASE_URL)

    window = make_window()
    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED: # if user closes window
            break

        elif event == KEY_SETTINGS:
            (access_token, base_url) = settings_window(access_token, base_url)

        elif event == KEY_GIT_MAP:
            if is_ready(access_token, base_url):
                git_map_window(access_token, base_url)

        elif event == KEY_STU_FILE:
            if is_ready(access_token, base_url):
                students_file_window(access_token, base_url)

    window.close()