import PySimpleGUI as sg
import os
import base64
from sys import platform


WINDOW_SIZE_X = 900
WINDOW_SIZE_Y = 600

KEY_ACCESS_TOKEN = 'canvas_access_token'
KEY_BASE_URL = 'canvas_base_url'
KEY_COURSE_ID = 'canvas_course_id'
KEY_GROUP_CATEGORY = 'group_category_name'
KEY_STU_FILE = 'students_file'
KEY_CSV_INFO_FILE = 'stu_csv_info_file'
KEY_XLSX_INFO_FILE = 'stu_xlsx_info_file'
KEY_STU_FILE_FOLDER = 'students_file_folder'
KEY_CSV_INFO_FILE_FOLDER = 'stu_csv_info_file_folder'
KEY_XLSX_INFO_FILE_FOLDER = 'stu_xlsx_info_file_folder'
KEY_ML = '-ML-'
KEY_PRO_BAR = 'progressbar'
KEY_PRO_TEXT = 'progress'

DEFAULT_INPUT_BG = "#000000" #"#705e52"
DISABLED_COLOR = "grey"
DEFAULT_BUTTON_COLOR = ("#000000", "#fdcb52")

token_tip = "Canvas > Account > Settings > New access token > Generate Token"
token_tip_ml = "Generate via: Canvas > Account > Settings > Blue Box '+ New access token' on page > Generate Token"
base_url_tip = "Default value should be correct for Canvas, only change when you know what you are doing."
course_id_tip = "Number at the end of the Canvas URL for your course"
group_category_tip = "Name of the Canvas Group Set (see Canvas tab People) that contains the student groups."
info_file_tip = "Output file with columns: group number, name, Canvas student ID, GitLab student ID, email"
info_file_tip_ml = "Output path for CSV or Excel file, containing for each student the following columns: group number, last name, Canvas student ID, student ID (used for GitLab login), email"
yaml_file_tip = "Student info file for Repobee with for each student group: repo name and student IDs"

CSV = "csv"
YAML = "yaml"
XLSX = "xlsx"

TYPE_CSV = ("Text Files", "*.csv")
TYPE_YAML = ("Text Files", "*.yaml")
TYPE_XLSX = ("Excel Workbook", "*.xlsx")
TYPE_ALL = ("ALL Files", "*.* *")

def set_default_entries():
    if get_entry(KEY_BASE_URL) == None:
        set_entry(KEY_BASE_URL, "https://canvas.tue.nl/api/v1")

    if is_invalid(get_entry(KEY_STU_FILE)) or is_invalid(get_entry(KEY_STU_FILE_FOLDER)):
        set_entry(KEY_STU_FILE, resource_path("students.yaml"))
        set_entry(KEY_STU_FILE_FOLDER, resource_path())

    if is_invalid(get_entry(KEY_XLSX_INFO_FILE)) or is_invalid(get_entry(KEY_CSV_INFO_FILE)):
        set_entry(KEY_CSV_INFO_FILE, resource_path("students_info.csv"))
        set_entry(KEY_XLSX_INFO_FILE, resource_path("students_info.xlsx"))

    if get_entry(KEY_GROUP_CATEGORY) is None:
        set_entry(KEY_GROUP_CATEGORY, "Project Groups")

    if get_entry(KEY_COURSE_ID) is None:
        set_entry(KEY_COURSE_ID, "00000")

    if platform == "darwin": sg.set_options(font = ("Any", 12))

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

def set_entry(key: str, val: str):
    sg.user_settings_set_entry(key, val)

def get_entry(key: str) -> str:
    return sg.user_settings_get_entry(key)

progress_bar = None
progress_text = None

def progressBar(bar: sg.ProgressBar, text: sg.Text):
    global progress_bar, progress_text
    progress_bar = bar
    progress_text = text

def update_browse(file_path: str, save_as: bool, file_types: str) -> str:
    (folder, filename) = os.path.split(file_path)
    return sg.popup_get_file("", save_as=save_as, file_types=file_types, no_window=True, default_path=filename, initial_folder=folder, history=True) #default_extension=extension,

def split_file(path: str) -> list:
    os.path.splitext(path)

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

def is_invalid(string: str) -> bool:
    return string is None or string == ""

def is_path_invalid(path: str, file_type: str):
    parent = os.path.dirname(os.path.abspath(path))
    if os.path.exists(parent):
        return False

    sg.popup("Error", "Invalid "+ file_type + " file path.")
    return True

def add_help_button(key: str, tooltip: str) -> sg.Button:
    return sg.Button(key=key, button_color=(sg.theme_background_color(), sg.theme_background_color()),
               image_filename=help, image_subsample=60, border_width=0, tooltip = tooltip, pad=(2, 0))

def update_progress(pos: int, length: int):
    global progress_bar, progress_text
    percent = int(100 * pos / length)
    progress_bar.UpdateBar(percent)
    progress_text.update("{}%".format(percent))

def update_button(disabled: bool, button: sg.Button):
    if disabled:
        button.update(disabled=disabled, button_color=DISABLED_COLOR)
    else:
        button.update(disabled=disabled, button_color=DEFAULT_BUTTON_COLOR)

def make_window():
    sg.theme('DarkAmber')

    csv_checked = get_entry(CSV)
    xlsx_checked = get_entry(XLSX)
    yaml_checked = get_entry(YAML)

    layout = [
        [
            [
                sg.Text('Access Token', pad=(0, 2), size=11, background_color="red"),
                sg.InputText(k=KEY_ACCESS_TOKEN, default_text=get_entry(KEY_ACCESS_TOKEN), expand_x = True, readonly=True, disabled_readonly_background_color=DEFAULT_INPUT_BG, password_char='*', pad=((3, 5), 2)),
                sg.B("Update", k='token_bt'),
                add_help_button('token_tip', token_tip)
            ],
            [
                sg.Text('Base URL', pad=(0, 2), size=11, background_color="red"),
                sg.InputText(k=KEY_BASE_URL, default_text=get_entry(KEY_BASE_URL), expand_x = True, readonly=True, disabled_readonly_background_color=DEFAULT_INPUT_BG, pad=((3, 5), 2)),
                sg.B("Update", k='url_bt'),
                add_help_button('base_url_tip', base_url_tip)
            ],
            [
                sg.Text('Course ID', pad=(0, 2), size=11),
                sg.InputText(k=KEY_COURSE_ID, default_text=get_entry(KEY_COURSE_ID), expand_x = True, readonly=True, disabled_readonly_background_color=DEFAULT_INPUT_BG, pad=((3, 5), 2)),
                sg.B("Update", k='course_id_bt'),
                add_help_button('course_id_tip', course_id_tip)
            ],
            [
                sg.Text('Group Set', pad=(0, 2), size=11),
                sg.InputText(k=KEY_GROUP_CATEGORY, default_text=get_entry(KEY_GROUP_CATEGORY), expand_x = True, readonly=True, disabled_readonly_background_color=DEFAULT_INPUT_BG, pad=((3, 5), 2)),
                sg.B("Update", k='group_set_bt'),
                add_help_button('group_category_tip', group_category_tip)
            ],
            [
                sg.Text('Info File', pad=(0, 2), size=8),
                sg.Checkbox("", k=CSV, default=csv_checked, enable_events = True, pad=(0, 2)),
                sg.InputText(k=KEY_CSV_INFO_FILE, default_text=get_entry(KEY_CSV_INFO_FILE), expand_x = True, readonly=True, disabled_readonly_background_color=DEFAULT_INPUT_BG, pad=((0, 5), 2)),
                sg.B("Browse", k=KEY_CSV_INFO_FILE_FOLDER, pad=((5, 3), 0), disabled=not csv_checked, disabled_button_color=DISABLED_COLOR),
                add_help_button('info_file_tip', info_file_tip)
            ],
            [
                sg.Text('', pad=(0, 2), size=8),
                sg.Checkbox("", k=XLSX, default=xlsx_checked, enable_events = True, pad=(0, 2)),
                sg.InputText(k=KEY_XLSX_INFO_FILE, default_text=get_entry(KEY_XLSX_INFO_FILE), expand_x = True, readonly=True, disabled_readonly_background_color=DEFAULT_INPUT_BG, pad=((0, 5), 2)),
                sg.B("Browse", k=KEY_XLSX_INFO_FILE_FOLDER, pad=((5, 27), 0), disabled=not xlsx_checked, disabled_button_color=DISABLED_COLOR),
            ],
            [
                sg.Text('YAML File', pad=(0, 2), size=8),
                sg.Checkbox("", k=YAML, default=yaml_checked, enable_events = True, pad=(0, 2)),
                sg.InputText(k=KEY_STU_FILE, default_text=get_entry(KEY_STU_FILE), expand_x = True, readonly=True, disabled_readonly_background_color=DEFAULT_INPUT_BG, pad=((0, 5), 2)),
                sg.B("Browse", k=KEY_STU_FILE_FOLDER, pad=((5, 3), 0), disabled=not xlsx_checked, disabled_button_color=DISABLED_COLOR),
                add_help_button('yaml_file_tip', yaml_file_tip)
            ],
            [
                sg.ProgressBar(max_value=100, orientation='h', size=(0, 20), expand_x=True, key=KEY_PRO_BAR), #expand_x will overwrite the width
                sg.Text('0%', key=KEY_PRO_TEXT, size=(4, None), justification='right')
            ],
            [
                sg.Multiline(size=(70, 20), key=KEY_ML, reroute_cprint=True, expand_y=True, expand_x=True, auto_refresh=True)
            ],
            [
                sg.B('Execute'), sg.B('Exit'), sg.B('Clear History')
            ]
        ],
    ]

    window = sg.Window('Repobee Canvas', layout, size=(WINDOW_SIZE_X, WINDOW_SIZE_Y), icon=icon, finalize=True)
    progressBar(window[KEY_PRO_BAR], window[KEY_PRO_TEXT])
    update_button(not csv_checked, window[KEY_CSV_INFO_FILE_FOLDER])
    update_button(not xlsx_checked, window[KEY_XLSX_INFO_FILE_FOLDER])
    update_button(not yaml_checked, window[KEY_STU_FILE_FOLDER])
    return window
