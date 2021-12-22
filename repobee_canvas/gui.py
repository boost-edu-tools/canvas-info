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
MEMBER_OPTION = 'member_option'
KEY_GIT_ID = 'git_id'
KEY_EMAIL = 'email'
KEY_CONF_LOCK    = "config_lock"
KEY_CONF_LOCK_STATE = "config_lock_state"

DISABLED_BT_COLOR = "grey"

DEFAULT_INPUT_SIZE = 99
DEFAULT_INPUT_PAD = ((3, 5), 2)
TEXT_CB_SIZE = 8
INPUT_CB_PAD = ((0, 5), 2)
ALIGN_RIGHT = ((690, 0), 5)

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

LOCK = "Lock"
UNLOCK = "Unlock"
LOCKED = "Locked"
UNLOCKED = "UnLocked"

if platform == "darwin":
    sg.set_options(font = ("Any", 12))
    ALIGN_RIGHT = ((685, 0), 0)

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

    if get_entry(MEMBER_OPTION) is None:
        set_entry(MEMBER_OPTION, KEY_EMAIL)

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

def help_button(key: str, tooltip: str) -> sg.Button:
    return sg.Button("?", key=key, tooltip = tooltip, pad=(3, 0))

def update_progress(pos: int, length: int):
    global progress_bar, progress_text
    percent = int(100 * pos / length)
    progress_bar.UpdateBar(percent)
    progress_text.update("{}%".format(percent))

def disable_elements(ele: sg.Element, disable: bool):
    ele.update(disabled=disable)

def disable_all_buttons(window: sg.Window):
    for bt in buttons:
        disable_elements(window[bt], True)

def enable_all_buttons(window: sg.Window):
    for bt in buttons:
        disable_elements(window[bt], False)

def update_option_state(window: sg.Window, key: str):
    state = (window[key].ButtonText == LOCK)
    if state:
        window[key].update(text=UNLOCK)
        window[key+"_state"].update(value=LOCKED)
    else:
        window[key].update(text=LOCK)
        window[key+"_state"].update(value=UNLOCKED)

    for key in (KEY_BASE_URL, KEY_COURSE_ID, KEY_GROUP_CATEGORY):
        disable_elements(window[key], state)

def Text(text: str, key:str=None, sz: int = 11) -> sg.Text:
    return sg.Text(text, k=key, pad=(0, 2), size=sz)

def InputText(key:str, text:str, password:str='', readOnly:bool=True, pad:tuple=DEFAULT_INPUT_PAD, enable_events:bool=True) -> sg.InputText:
    return sg.InputText(k=key, default_text=text, disabled=readOnly, password_char=password, pad=pad, enable_events=enable_events, expand_x=True)

def Checkbox(key, default) -> sg.Checkbox:
    return sg.Checkbox("", k=key, default=default, enable_events = True, pad=(0, 2))

def Button(text, key) -> sg.Button:
    return sg.B(text, k=key, pad=((3, 0), 2))

def Radio(text:str, key:str, default_val: bool, size:(int, int)=(10,1)) -> sg.Radio:
    return sg.Radio(text, MEMBER_OPTION, k=key, default=default_val, s=size, enable_events=True)

def Folder_Button(key, disable) -> sg.Button:
    return sg.B("Browse", k=key, pad=((3, 0), 2))

def Frame(title:str, layout:list) -> sg.Frame:
    return sg.Frame(layout=layout, title=title, relief=sg.RELIEF_SUNKEN, expand_x=True)

def make_window():
    sg.theme("SystemDefault")

    csv_checked = get_entry(CSV)
    xlsx_checked = get_entry(XLSX)
    yaml_checked = get_entry(YAML)
    member_option = get_entry(MEMBER_OPTION)

    layout = [
        [
            Text(LOCKED, KEY_CONF_LOCK_STATE),
            Button(UNLOCK, KEY_CONF_LOCK)
        ],
        [
            Frame('Canvas configuration',
                layout = [
                    [
                        Text('Access Token'),
                        InputText(KEY_ACCESS_TOKEN, get_entry(KEY_ACCESS_TOKEN), password='*', enable_events=False),
                        Button("Edit", 'token_bt'),
                        help_button('token_tip', token_tip)
                    ],
                    [
                        Text('Base URL'),
                        InputText(KEY_BASE_URL, get_entry(KEY_BASE_URL)),
                        help_button('base_url_tip', base_url_tip)
                    ],
                    [
                        Text('Course ID'),
                        InputText(KEY_COURSE_ID, get_entry(KEY_COURSE_ID)),
                        help_button('course_id_tip', course_id_tip)
                    ],
                    [
                        Text('Group Set'),
                        InputText(KEY_GROUP_CATEGORY, get_entry(KEY_GROUP_CATEGORY)),
                        help_button('group_category_tip', group_category_tip)
                    ]
                ]
            )
        ],
        [
            Frame('Local computer configuration',
                layout = [
                    [
                        Text('Info File', sz=TEXT_CB_SIZE),
                        Checkbox(CSV, csv_checked),
                        InputText(KEY_CSV_INFO_FILE, get_entry(KEY_CSV_INFO_FILE), pad=INPUT_CB_PAD, enable_events=False),
                        Folder_Button(KEY_CSV_INFO_FILE_FOLDER, not csv_checked),
                        help_button('info_file_tip', info_file_tip)
                    ],
                    [
                        Text('', sz=TEXT_CB_SIZE),
                        Checkbox(XLSX, xlsx_checked),
                        InputText(KEY_XLSX_INFO_FILE, get_entry(KEY_XLSX_INFO_FILE), pad=INPUT_CB_PAD, enable_events=False),
                        Folder_Button(KEY_XLSX_INFO_FILE_FOLDER, not xlsx_checked),
                        help_button('info_file_excel_tip', info_file_tip)
                    ],
                    [
                        Text('YAML File', sz=TEXT_CB_SIZE),
                        Checkbox(YAML, yaml_checked),
                        InputText(KEY_STU_FILE, get_entry(KEY_STU_FILE), pad=INPUT_CB_PAD, readOnly=False),
                        Folder_Button(KEY_STU_FILE_FOLDER, not xlsx_checked),
                        help_button('yaml_file_tip', yaml_file_tip)
                    ],
                    [
                        sg.Text('Member Option', size=22, justification='right'),
                        Radio('Email', KEY_EMAIL, KEY_EMAIL == member_option),
                        Radio('Year ID', KEY_GIT_ID, KEY_GIT_ID == member_option)
                    ]
                ]
            )
        ],
        [
            sg.ProgressBar(max_value=100, orientation='h', size=(0, 20), expand_x=True, key=KEY_PRO_BAR), #expand_x will overwrite the width
            sg.Text('0%', key=KEY_PRO_TEXT, size=(4, None), justification='right')
        ],
        [
            sg.Multiline(size=(70, 10), key=KEY_ML, reroute_cprint=True, expand_y=True, expand_x=True, auto_refresh=True)
        ],
        [
            sg.B('Execute'), sg.B('Clear History', pad=ALIGN_RIGHT), sg.B('Exit')
        ]
    ]

    window = sg.Window('Repobee Canvas', layout, size=(WINDOW_SIZE_X, WINDOW_SIZE_Y), icon=icon, finalize=True)
    progressBar(window[KEY_PRO_BAR], window[KEY_PRO_TEXT])
    return window