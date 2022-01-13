import PySimpleGUI as sg
import os
import base64
from sys import platform
from pathlib import Path

WINDOW_SIZE_X = 750
WINDOW_SIZE_Y = 770
MAX_COL_HEIGHT = 430
WINDOW_HEIGHT_CORR = 45     # height correction: height of command buttons + title bar
COL_PERCENT = 40
INIT_COL_HEIGHT = int((WINDOW_SIZE_Y - WINDOW_HEIGHT_CORR) * COL_PERCENT / 100)

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
KEY_MEMBER_OPTION = 'member_option'
KEY_GIT_ID = 'git_id'
KEY_EMAIL = 'email'
KEY_CONF_LOCK    = "config_lock"
KEY_CONF_LOCK_STATE = "config_lock_state"
KEY_REPO_NAME_OPTION = "repo_name_options"
KEY_INC_GROUP = "include_group"
KEY_INC_MEMBER = "include_member"
KEY_INC_INITIAL = "include_initials"
KEY_COL_PERCENT = "col_percent"
KEY_HELP = "Help"
KEY_EXECUTE = "Execute"
KEY_EXIT = "Exit"
KEY_CLEAR = "Clear"
KEY_CONFIG_COL = "config_column"
KEY_VERIFY = "Verify"
KEY_DELETE = "Delete Course"
KEY_COURSE_NAME = "course_name"
KEY_COURSES = "courses"
KEY_RENAME_COURSE = "rename_course"
KEY_CLONE_COURSE = "clone_course"

DEFAULT_INPUT_PAD = ((3, 5), 2)
TEXT_CB_SIZE = 8
INPUT_CB_PAD = ((0, 5), 2)

token_tip = "Canvas > Account > Settings > New access token > Generate Token"
token_tip_ml = "Generate via: Canvas > Account > Settings > Blue Box '+ New access token' on page > Generate Token"
base_url_tip = "Default value should be correct for Canvas, only change when you know what you are doing."
course_id_tip = "Number at the end of the Canvas URL for your course"
group_category_tip = "Name of the Canvas Group Set (see Canvas tab People) that contains the student groups."
info_file_tip = "Output file with columns: group number, name, Canvas student ID, GitLab student ID, email"
info_file_tip_ml = "Output path for CSV or Excel file, containing for each student the following columns: group number, last name, Canvas student ID, student ID (used for GitLab login), email"
yaml_file_tip = "Student info file for Repobee with for each student group: repo name and student IDs"
member_options_tip = "Options tip"
yaml_options_tip = "repo option tip"
help_info = "help info"

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

MODE_PARSE = 0
MODE_RENAME = 1
MODE_CLONE = 2
MODE_CREATE = 3

buttons = [KEY_CONF_LOCK, KEY_VERIFY, "token_bt", KEY_RENAME_COURSE, KEY_EXECUTE, KEY_CSV_INFO_FILE_FOLDER, KEY_XLSX_INFO_FILE_FOLDER, KEY_STU_FILE_FOLDER]
TEXT_SETTINGS_KEY = [KEY_BASE_URL, KEY_ACCESS_TOKEN, KEY_GROUP_CATEGORY, KEY_CSV_INFO_FILE, KEY_XLSX_INFO_FILE, KEY_STU_FILE]
BOOL_SETTINGS_KEY = [CSV, XLSX, YAML, KEY_INC_INITIAL, KEY_INC_GROUP, KEY_INC_MEMBER]
COURSE_SETTINGS_KEYS = TEXT_SETTINGS_KEY + BOOL_SETTINGS_KEY
courses_list = []
course_info = None
course_title = "ID: {0} Name: {1}"

if platform == "darwin":
    sg.set_options(font = ("Any", 12))

settings = sg.UserSettings()
course_id = settings[KEY_COURSE_ID]
def set_default_entries():
    col_percent = settings[KEY_COL_PERCENT]
    updated = False
    if col_percent:
        global COL_PERCENT, INIT_COL_HEIGHT
        COL_PERCENT = col_percent
        INIT_COL_HEIGHT = int((WINDOW_SIZE_Y - WINDOW_HEIGHT_CORR) * COL_PERCENT / 100)
        if INIT_COL_HEIGHT > MAX_COL_HEIGHT:
            INIT_COL_HEIGHT = MAX_COL_HEIGHT
    else:
        settings.set(KEY_COL_PERCENT, COL_PERCENT)
        updated = True

    global course_id, course_info
    if not course_id:
        course_id = "00000"
        course_info = Course(course_id, mode=MODE_CREATE)
        settings.set(KEY_COURSE_ID, course_id)
        settings.set(KEY_COURSES, [course_info.get_course_title()])
        updated = True

    if updated:
        settings.load()

class Course():
    def __init__(self, course_id:str, course:dict=None, mode:int=MODE_PARSE):
        self.course = {}
        self.course_id = course_id
        self.course[KEY_COURSE_ID] = self.course_id
        if mode == MODE_CREATE:
            self.create_template_course()
            self.save()
        else:
            for key in COURSE_SETTINGS_KEYS:
                self.course[key] = course[key]
            self.course[KEY_MEMBER_OPTION] = course[KEY_MEMBER_OPTION]

            if mode != MODE_PARSE:
                self.course[KEY_COURSE_NAME] = "Unverified"
                self.save()
            else:
                self.course[KEY_COURSE_NAME] = course[KEY_COURSE_NAME]

    def create_template_course(self):
        home = str(Path.home())
        for key in TEXT_SETTINGS_KEY:
            self.course[key] = ""
        for key in BOOL_SETTINGS_KEY:
            self.course[key] = False
        self.course[KEY_MEMBER_OPTION] = KEY_EMAIL
        self.course[KEY_COURSE_NAME] = "Course template for Cloning only, cannot be edited or deleted."
        self.course[KEY_BASE_URL] = "https://canvas.tue.nl/api/v1"
        self.course[KEY_STU_FILE] = home + "/students.yaml"
        self.course[KEY_STU_FILE_FOLDER] = home
        self.course[KEY_CSV_INFO_FILE] = home + "/students_info.csv"
        self.course[KEY_XLSX_INFO_FILE] = home + "/students_info.xlsx"
        self.course[KEY_GROUP_CATEGORY] = "Project Groups"
        self.course[KEY_INC_GROUP] = True
        self.course[KEY_INC_MEMBER] = True

    def get_course_title(self):
        return course_title.format(self.course_id, self.course[KEY_COURSE_NAME])

    def save(self):
        set_entry(self.course_id, self.course)

    def get(self):
        return self.course

    def update(self, key, value):
        self.course[key] = value
        self.save()

def set_course_info(key:str, value:str):
    global course_info
    if course_info:
        course_info.update(key, value)

def valid_course_id(window:sg.Window, course_id:str)->bool:
    if not course_id:
        return False

    for course_title in courses_list:
        if course_id in course_title:
            popup("The course exists")
            return False

    if is_invalid(course_id):
        if course_id:
            popup("Please fill in a valid course ID.")
        return False
    else:
        if not course_id.isnumeric():
            popup("Please fill in a valid course ID.")
            return False
    return True

def update_course_ui(window:sg.Window, course_id:str, course:dict):
    window[KEY_COURSES].update(value=course_info.get_course_title())

    for key in COURSE_SETTINGS_KEYS:
        window[key].update(value=course[key])

    member_option = course[KEY_MEMBER_OPTION]
    window[KEY_EMAIL].update(value=(KEY_EMAIL == member_option))
    window[KEY_GIT_ID].update(value=(KEY_GIT_ID == member_option))

def update_course_settings(window:sg.Window, id:str, course:dict, mode:int):
    global course_info, courses_list, course_id
    if mode == MODE_RENAME:
        courses_list.remove(course_info.get_course_title())
        sg.user_settings_delete_entry(course_id)
    course_id = id
    if mode in (MODE_RENAME, MODE_CLONE):
        course[KEY_COURSE_ID] = course_id
        settings.set(KEY_COURSE_ID, course_id)
        course_info = Course(course_id, course=course, mode=mode)
        window[KEY_COURSES].update(value=course_info.get_course_title())
        #update course_list
        courses_list.append(course_info.get_course_title())
        courses_list.sort(reverse=True)
        update_courses_list(window, courses_list)
    else: #select a course
        course_info = Course(course_id, course)

    settings.set(KEY_COURSE_ID, course_id)
    update_course_ui(window, course_id, course_info.get())

def delete_course_id(window:sg.Window):
    global course_id, course_info
    course_title = course_info.get_course_title()
    ind = courses_list.index(course_title)
    ind -= 1
    if ind < 0:
        ind = 0
    courses_list.remove(course_title)
    sg.user_settings_delete_entry(course_id)
    update_courses_list(window, courses_list)
    course_id = courses_list[ind].split(" ")[1]
    settings.set(KEY_COURSE_ID, course_id)
    course_info = Course(course_id, settings[course_id])
    window[KEY_COURSES].update(set_to_index=ind)
    update_course_ui(window, course_id, course_info.get())
    disable_by_course_id(window, course_id)

def update_courses_list(window:sg.Window, courses_list:list):
    window[KEY_COURSES].update(values=courses_list)
    settings.set(KEY_COURSES, courses_list)

def update_col_percent(window, wh, percent):
    element = window[KEY_CONFIG_COL]
    set_entry(KEY_COL_PERCENT, percent)
    global COL_PERCENT
    if COL_PERCENT != percent:
        COL_PERCENT = percent
        update_column_height(element, wh, wh)

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
    parent = os.path.dirname(path)
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

def disable_by_course_id(window:sg.Window, course_id:str):
    if course_id == "00000":
        disable_all_buttons(window)
    else:
        enable_all_buttons(window)

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

    for key in (KEY_BASE_URL, KEY_GROUP_CATEGORY):
        disable_elements(window[key], state)

def update_column_height(element, wh, last_screen_height):
    ch = element.Widget.canvas.winfo_height()
    if ch < MAX_COL_HEIGHT or (wh - last_screen_height) <= 0:
        ch = (wh - WINDOW_HEIGHT_CORR) * COL_PERCENT / 100
        ch = min(ch, MAX_COL_HEIGHT)
        update_height(element, int(ch))

def Text(text: str, key:str=None, sz: int = 11) -> sg.Text:
    return sg.Text(text, k=key, pad=(0, 2), size=sz)

def InputText(key:str, text:str, password:str='', readOnly:bool=True, pad:tuple=DEFAULT_INPUT_PAD, enable_events:bool=True) -> sg.InputText:
    return sg.InputText(k=key, default_text=text, disabled=readOnly, password_char=password, pad=pad, enable_events=enable_events, expand_x=True)

def Checkbox(key, default, text:str="", disabled:bool=False) -> sg.Checkbox:
    return sg.Checkbox(text, k=key, default=default, enable_events = True, pad=(0, 2), disabled=disabled)

def Button(text, key) -> sg.Button:
    return sg.B(text, k=key, pad=((3, 3), 2))

def Radio(text:str, key:str, default_val: bool) -> sg.Radio:
    return sg.Radio(text, KEY_MEMBER_OPTION, k=key, default=default_val, enable_events=True)

def Folder_Button(key, disable) -> sg.Button:
    return sg.B("Browse", k=key, pad=((3, 0), 2))

def Frame(title:str, layout:list, pad:(int, int)=None) -> sg.Frame:
    return sg.Frame(layout=layout, title=title, relief=sg.RELIEF_SUNKEN, expand_x=True, pad=pad)

def Column(layout:list, key:str=None):
    global INIT_COL_HEIGHT
    return sg.Column(layout, k=key, vertical_scroll_only=True, scrollable=True, expand_x=True, size=(None, INIT_COL_HEIGHT))

def configure_canvas(event, canvas, frame_id):
    canvas.itemconfig(frame_id, width=event.width)

def configure_frame(event, canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))

def update_height(element, height):
    element.Widget.canvas.configure({'height':height})

def make_window():
    sg.theme("SystemDefault")

    global course_info, courses_list
    courses_list = settings[KEY_COURSES]
    course_info = Course(course_id, course=settings[course_id])
    course = course_info.get()
    csv_checked = course[CSV]
    xlsx_checked = course[XLSX]
    yaml_checked = course[YAML]
    member_option = course[KEY_MEMBER_OPTION]

    menu = [['Course', KEY_DELETE]]
    local_config_frame = Frame('Local computer configuration',
        layout = [
            [
                Frame('',
                    layout= [
                        [
                            Text('Info File', sz=TEXT_CB_SIZE),
                            Checkbox(CSV, csv_checked),
                            InputText(KEY_CSV_INFO_FILE, course[KEY_CSV_INFO_FILE], pad=INPUT_CB_PAD, enable_events=False),
                            Folder_Button(KEY_CSV_INFO_FILE_FOLDER, not csv_checked),
                            help_button('info_file_tip', info_file_tip)
                        ],
                        [
                            Text('', sz=TEXT_CB_SIZE),
                            Checkbox(XLSX, xlsx_checked),
                            InputText(KEY_XLSX_INFO_FILE, course[KEY_XLSX_INFO_FILE], pad=INPUT_CB_PAD, enable_events=False),
                            Folder_Button(KEY_XLSX_INFO_FILE_FOLDER, not xlsx_checked),
                            help_button('info_file_excel_tip', info_file_tip)
                        ]
                    ]
                )
            ],
            [
                Frame('',
                    layout = [
                        [
                            Text('YAML File', sz=TEXT_CB_SIZE),
                            Checkbox(YAML, yaml_checked),
                            InputText(KEY_STU_FILE, course[KEY_STU_FILE], pad=INPUT_CB_PAD, readOnly=False),
                            Folder_Button(KEY_STU_FILE_FOLDER, not xlsx_checked),
                            help_button('yaml_file_tip', yaml_file_tip)
                        ],
                        [
                            Frame('Members',
                                layout=[
                                    [
                                        Radio('Email', KEY_EMAIL, KEY_EMAIL == member_option),
                                        Radio('Year ID', KEY_GIT_ID, KEY_GIT_ID == member_option),
                                        help_button('member_options_tip', member_options_tip)
                                    ]
                            ]),
                            Frame('Repo Name',
                                layout=[
                                    [
                                        Checkbox(KEY_INC_GROUP, course[KEY_INC_GROUP], "Include Group Name"),
                                        Checkbox(KEY_INC_MEMBER, course[KEY_INC_MEMBER], "Include Member Names"),
                                        Checkbox(KEY_INC_INITIAL, course[KEY_INC_INITIAL], "Include Initials", disabled=not course[KEY_INC_MEMBER]),
                                        help_button('yamloptions_tip', yaml_options_tip)
                                    ]
                                ]
                            )
                        ]
                    ]
                )
            ]
        ], pad=(0,0)
    )

    canvas_config_frame = Frame('Canvas configuration',
        layout = [
            [
                Text(LOCKED, KEY_CONF_LOCK_STATE),
                Button(UNLOCK, KEY_CONF_LOCK),
                sg.Column(
                    [
                        [
                            Button(KEY_VERIFY, KEY_VERIFY),
                        ]
                    ], element_justification="right", expand_x=True, pad=(0,(4,0))
                )
            ],
            [
                Text('Group Set'),
                InputText(KEY_GROUP_CATEGORY, course[KEY_GROUP_CATEGORY]),
                help_button('group_category_tip', group_category_tip)
            ],
            [
                Frame('Course IDs',
                    layout = [
                        [
                            sg.Text('Course ID', pad=(0, 2), size=10),
                            sg.Combo(courses_list, k=KEY_COURSES, default_value=course_info.get_course_title(), pad=DEFAULT_INPUT_PAD, enable_events=True, readonly=True, expand_x=True),
                            help_button('course_id_tip', course_id_tip)
                        ],
                        [
                            Button("Rename Course ID", KEY_RENAME_COURSE),
                            Button("Clone Course", KEY_CLONE_COURSE),
                        ]
                    ]
                )
            ],
            [
                Text('Base URL'),
                InputText(KEY_BASE_URL, course[KEY_BASE_URL]),
                help_button('base_url_tip', base_url_tip)
            ],
            [
                Text('Access Token'),
                InputText(KEY_ACCESS_TOKEN, course[KEY_ACCESS_TOKEN], password='*', enable_events=False),
                Button("Edit", 'token_bt'),
                help_button('token_tip', token_tip)
            ]
        ]
    )

    layout = [
        [
            sg.Menu(menu)
        ],
        [
            sg.Column(
                [
                    [
                        Button(KEY_EXECUTE, KEY_EXECUTE)
                    ]
                ], pad=(0,(4,0))
            ),
            sg.Column(
                [
                    [
                        Button(KEY_HELP, KEY_HELP),
                        Button(KEY_CLEAR, KEY_CLEAR),
                        Button(KEY_EXIT, KEY_EXIT),
                        sg.Spin([i for i in range(20,90,10)], initial_value=COL_PERCENT, k=KEY_COL_PERCENT, enable_events=True, pad=((5,0),None), readonly=True),
                        sg.Text("%", pad=((0,5), None))
                    ]
                ], element_justification="right", expand_x=True, pad=(0,(4,0))
            )
        ],
        [
            Column(
                [
                    [
                        sg.ProgressBar(max_value=100, orientation='h', size=(0, 20), expand_x=True, key=KEY_PRO_BAR, pad=(0,0)), #expand_x will overwrite the width
                        sg.Text('0%', key=KEY_PRO_TEXT, size=(4, None), justification='right')
                    ],
                    [
                        local_config_frame
                    ],
                    [
                        canvas_config_frame
                    ]
                ], KEY_CONFIG_COL
            )
        ],
        [
            sg.Multiline(size=(70, 10), key=KEY_ML, reroute_cprint=True, expand_y=True, expand_x=True, auto_refresh=True)
        ]
    ]

    window = sg.Window('Canvas group info', layout, size=(WINDOW_SIZE_X, WINDOW_SIZE_Y), icon=icon, margins=(0, 0), resizable=True, finalize=True)
    progressBar(window[KEY_PRO_BAR], window[KEY_PRO_TEXT])
    col = window[KEY_CONFIG_COL]
    frame_id = col.Widget.frame_id
    frame = col.Widget.TKFrame
    canvas = col.Widget.canvas
    canvas.bind("<Configure>", lambda event, canvas=canvas, frame_id=frame_id:configure_canvas(event, canvas, frame_id))
    frame.bind("<Configure>", lambda event, canvas=canvas:configure_frame(event, canvas))
    window.bind('<Configure>', "Conf")
    sg.cprint_set_output_destination(window, KEY_ML)
    canvas.itemconfig(frame_id, width=canvas.winfo_width())
    window.refresh()
    return window