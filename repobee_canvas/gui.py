import PySimpleGUI as sg
import os
import base64

from urllib.parse                        import urlparse
from .command.create_students_yaml_file  import CreateStudentsYAMLFile
from .command.create_canvas_git_mapping  import CreateCanvasGitMapping

KEY_SETTINGS = 'settings'
KEY_ACCESS_TOKEN = 'canvas_access_token'
KEY_BASE_URL = 'canvas_base_url'
KEY_COURSE_ID = 'canvas_course_id'
KEY_ASSIGNMENT_ID = 'canvas_assignment_id'
KEY_GIT_MAP = 'canvas_git_map'
KEY_STU_FILE = 'students_file'
KEY_GIT_MAP_FOLDER = 'canvas_git_map_folder'
KEY_STU_FILE_FOLDER = 'students_file_folder'
KEY_ML = '-ML-'
KEY_PRO_BAR = 'progressbar'
KEY_PRO_TEXT = 'progress'

DEFAULT_INPUT_BG = "#000000" #"#705e52"

token_tip = "To generate a Canvas API key via 'Account', 'Settings', '+ New Access Token'."

def resource_path(relative_path = None):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    if relative_path is None:
        return base_path

    return os.path.join(base_path, relative_path)

help = resource_path("help.png")
icon = resource_path("icon.png")
with open(icon, 'rb') as file:
    icon = base64.b64encode(file.read())

progress_bar = None
progress_text = None

def progressBar(bar: sg.ProgressBar, text: sg.Text):
    global progress_bar, progress_text
    progress_bar = bar
    progress_text = text

def update_browser(key: str, path: str, file_type: str, button: sg.B):
    if not path.endswith(file_type):
        path = path + file_type
    sg.user_settings_set_entry(key, path)
    button.InitialFolder = getParent(path)

def getParent(path: str) -> bool:
    return os.path.dirname(os.path.abspath(path))

def popup(message: str):
    sg.popup("Reminder", message, keep_on_top=True)

def is_number(value: str, name: str) -> bool:
    try:
        if value != "":
            int(value)

    except Exception:
        popup(name + " must be a number.")
        return False
    return True

def is_empty(value: str, name: str):
    if value == "":
        popup("Please fill in the " + name)
        return True
    return False

def is_ready(access_token: str, base_url: str) -> bool:
    if access_token is None or access_token == "":
        popup("Please set access token in the settings.")
        return False
    if base_url is None or base_url == "":
        popup("Please set the base url in the settings.")
        return False
    return True


def add_help_button(key: str, tooltip: str) -> sg.Button:
    return sg.Button(key=key, button_color=(sg.theme_background_color(), sg.theme_background_color()),
               image_filename=help, image_subsample=60, border_width=0, tooltip = tooltip, pad=(1, 0))

def update_progress(pos: int, length: int):
    global progress_bar, progress_text
    percent = int(100 * pos / length)
    progress_bar.UpdateBar(percent)
    progress_text.update("{}%".format(percent))

def students_file_window(access_token: str, base_url: str):
    base_url = urlparse(base_url)
    git_map = sg.user_settings_get_entry(KEY_GIT_MAP)
    student_file = sg.user_settings_get_entry(KEY_STU_FILE)
    layout = [
        [
            sg.Text('Course ID', pad=(0, 3)), sg.InputText(k=KEY_COURSE_ID, default_text=sg.user_settings_get_entry(KEY_COURSE_ID), expand_x = True, pad=((34,0), 0))
        ],
        [
            sg.Text('Assignment ID', pad=(0, 3)), sg.InputText(k=KEY_ASSIGNMENT_ID, default_text=sg.user_settings_get_entry(KEY_ASSIGNMENT_ID), expand_x = True, pad=((5, 0), 0))
        ],
        [
            sg.Text('Git Map', pad=(0, 3)), sg.InputText(k=KEY_GIT_MAP, default_text=git_map, enable_events = True, expand_x = True, pad=((42, 0), 0), readonly=True, disabled_readonly_background_color=DEFAULT_INPUT_BG),
            sg.FileBrowse(k=KEY_GIT_MAP_FOLDER, initial_folder=sg.user_settings_get_entry(KEY_GIT_MAP_FOLDER), file_types=(("Text Files", "*.csv"),), pad=((5, 0), 0))
        ],
        [
            sg.Text('Students File', pad=(0, 3)), sg.InputText(k=KEY_STU_FILE, default_text=student_file, enable_events = True, expand_x = True, pad=((10, 0), 0), readonly=True, disabled_readonly_background_color=DEFAULT_INPUT_BG),
            sg.FileSaveAs("Browse", k=KEY_STU_FILE_FOLDER, initial_folder=sg.user_settings_get_entry(KEY_STU_FILE_FOLDER), file_types=(("Text Files", "*.yaml"),), pad=((5, 0), 0))
        ],
        [
            sg.ProgressBar(max_value=100, orientation='h', size=(63, 20), key=KEY_PRO_BAR),
            sg.Text('0%', key=KEY_PRO_TEXT, size=(4, None), justification='right')
        ],
        [
            sg.Multiline(size=(70, 21), key=KEY_ML, reroute_cprint=True, expand_y=True, expand_x=True, auto_refresh=True)
        ],
        [
            sg.B('Execute'), sg.B('Exit'), sg.B('Clear History', pad=((348, 0), 0))
        ]
    ]
    window = sg.Window('CREATE STUDENT FILE', layout, icon=icon, finalize=True, keep_on_top=True)
    sg.cprint_set_output_destination(window, KEY_ML)
    progressBar(window[KEY_PRO_BAR], window[KEY_PRO_TEXT])

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        elif event == KEY_GIT_MAP:
            if git_map == values[event]:
                continue
            update_browser(event, values[event], '.csv', window[KEY_GIT_MAP_FOLDER])
            git_map = values[event]

        elif event == KEY_STU_FILE:
            if student_file == values[event]:
                continue
            update_browser(event, values[event], '.yaml', window[KEY_STU_FILE_FOLDER])
            student_file = values[event]

        elif event == "Execute":
            course_id = values[KEY_COURSE_ID]
            if is_empty(course_id, "Course ID") or not is_number(course_id, "Course ID"):
                continue

            assignment_id = values[KEY_ASSIGNMENT_ID]
            if is_empty(assignment_id, "Assignment ID") or not is_number(assignment_id, "Assignment ID"):
                continue

            git_map = values[KEY_GIT_MAP]
            if is_empty(git_map, "Git Map"):
                continue

            students_file = values[KEY_STU_FILE]
            if is_empty(students_file, "Students File"):
                continue

            sg.user_settings_set_entry(KEY_COURSE_ID, values[KEY_COURSE_ID])
            sg.user_settings_set_entry(KEY_ASSIGNMENT_ID, values[KEY_ASSIGNMENT_ID])

            CreateStudentsYAMLFile(base_url, access_token, course_id, assignment_id, git_map, students_file)

        elif event == 'Clear History':
            window[KEY_ML].update('')
            update_progress(0, 100)

    window.close()

def git_map_window(access_token: str, base_url: str):
    base_url = urlparse(base_url)
    git_map = sg.user_settings_get_entry(KEY_GIT_MAP)
    layout = [
        [
            sg.Text('Course ID', pad=(0, 3)), sg.InputText(k=KEY_COURSE_ID, default_text=sg.user_settings_get_entry(KEY_COURSE_ID), expand_x = True)
        ],
        [
            sg.Text('Git Map', pad=(0, 3)), sg.InputText(k=KEY_GIT_MAP, default_text=git_map, enable_events = True, expand_x = True, pad=((14, 0), 0), readonly=True, disabled_readonly_background_color=DEFAULT_INPUT_BG),
            sg.FileSaveAs("Browse", k=KEY_GIT_MAP_FOLDER, initial_folder=sg.user_settings_get_entry(KEY_GIT_MAP_FOLDER), file_types=(("Text Files", "*.csv"),))
        ],
        [
            sg.ProgressBar(max_value=100, orientation='h', size=(63, 20), key=KEY_PRO_BAR),
            sg.Text('0%', key=KEY_PRO_TEXT, size=(4, None), justification='right')
        ],
        [
            sg.Multiline(size=(70, 21), key=KEY_ML, reroute_cprint=True, expand_y=True, expand_x=True, auto_refresh=True)
        ],
        [
            sg.B('Execute'), sg.B('Exit'), sg.B('Clear History', pad=((348, 0), 0))
        ]
    ]

    window = sg.Window('CREATE GIT MAP', layout, icon=icon, finalize=True, keep_on_top=True)
    sg.cprint_set_output_destination(window, KEY_ML)
    progressBar(window[KEY_PRO_BAR], window[KEY_PRO_TEXT])

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        elif event == KEY_GIT_MAP:
            if git_map == values[event]:
                continue
            update_browser(event, values[event], '.csv', window[KEY_GIT_MAP_FOLDER])
            git_map = values[event]

        elif event == "Execute":
            course_id = values[KEY_COURSE_ID]
            if is_empty(course_id, "Course ID") or not is_number(course_id, "Course ID"):
                continue

            if is_empty(git_map, "Git Map"):
                continue

            sg.user_settings_set_entry(KEY_COURSE_ID, values[KEY_COURSE_ID])
            CreateCanvasGitMapping(base_url, access_token, course_id, git_map)

        elif event == 'Clear History':
            window[KEY_ML].update('')
            update_progress(0, 100)

    window.close()

def settings_window(access_token: str, base_url: str) -> (str, str):
    git_map = sg.user_settings_get_entry(KEY_GIT_MAP)
    student_file = sg.user_settings_get_entry(KEY_STU_FILE)
    layout = [
            [
                sg.Text('Access Token', pad=(0, 3)), sg.InputText(k=KEY_ACCESS_TOKEN, default_text=access_token, expand_x = True, pad=(2, 0), tooltip=token_tip),
                add_help_button('token_tip', token_tip)
            ],
            [
                sg.Text('Base URL', pad=(0, 3)), sg.InputText(k=KEY_BASE_URL, default_text=base_url, expand_x = True, pad=((26, 25), 0))
            ],
            [
                sg.Text('Course ID', pad=(0, 3)), sg.InputText(k=KEY_COURSE_ID, default_text=sg.user_settings_get_entry(KEY_COURSE_ID), expand_x = True, pad=((28, 25), 0))
            ],
            [
                sg.Text('Assignment ID', pad=(0, 3)), sg.InputText(k=KEY_ASSIGNMENT_ID, default_text=sg.user_settings_get_entry(KEY_ASSIGNMENT_ID), expand_x = True, pad=((0, 25), 0))
            ],
            [
                sg.Text('Git Map', pad=(0, 3)), sg.InputText(k=KEY_GIT_MAP, default_text=git_map, enable_events = True, expand_x = True, pad=((38, 0), 0), readonly=True, disabled_readonly_background_color=DEFAULT_INPUT_BG),
                sg.FileSaveAs("Browse", k=KEY_GIT_MAP_FOLDER, initial_folder=sg.user_settings_get_entry(KEY_GIT_MAP_FOLDER), file_types=(("Text Files", "*.csv"),))
            ],
            [
                sg.Text('Students File', pad=(0, 3)), sg.InputText(k=KEY_STU_FILE, default_text=student_file, enable_events = True, expand_x = True, pad=((6, 1), 0), readonly=True, disabled_readonly_background_color=DEFAULT_INPUT_BG),
                sg.FileSaveAs("Browse", k=KEY_STU_FILE_FOLDER, initial_folder=sg.user_settings_get_entry(KEY_STU_FILE_FOLDER), file_types=(("Text Files", "*.yaml"),))
            ],
            [
                sg.B('Save'), sg.B('Cancel')
            ]
        ]
    window = sg.Window('SETTINGS', layout, icon=icon, finalize=True, keep_on_top=True)

    while True:
        event, values = window.read()

        if event in ('Cancel', sg.WIN_CLOSED):
            break

        elif event == KEY_GIT_MAP:
            if git_map == values[event]:
                continue
            update_browser(event, values[event], '.csv', window[KEY_GIT_MAP_FOLDER])
            git_map = values[event]

        elif event == KEY_STU_FILE:
            if student_file == values[event]:
                continue
            update_browser(event, values[event], '.yaml', window[KEY_STU_FILE_FOLDER])
            student_file = values[event]

        elif event.endswith("_tip"):
            window[event].TooltipObject.showtip()

        elif event == 'Save':
            if is_empty(values[KEY_ACCESS_TOKEN], "Access Token"):
                continue
            if is_empty(values[KEY_BASE_URL], "Base URL"):
                continue
            if not is_number(values[KEY_COURSE_ID], "Course ID"):
                continue
            if not is_number(values[KEY_ASSIGNMENT_ID], "Assignment ID"):
                continue
            access_token = values[KEY_ACCESS_TOKEN]
            base_url = values[KEY_BASE_URL]
            for key, val in values.items():
                sg.user_settings_set_entry(key, val)
            break
    window.close()
    return (access_token, base_url)
