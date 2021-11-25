import PySimpleGUI as sg
import os
import base64

from urllib.parse                        import urlparse
from .command.create_students_yaml_file  import CreateStudentsYAMLFile
from .command.create_students_info_file  import CreateStudentsInfoFile

KEY_SETTINGS = 'settings'
KEY_ACCESS_TOKEN = 'canvas_access_token'
KEY_BASE_URL = 'canvas_base_url'
KEY_COURSE_ID = 'canvas_course_id'
KEY_GROUP_CATEGORY = 'group_category_name'
KEY_STU_FILE = 'students_file'
KEY_INFO_FILE = 'students_info_file'
KEY_INFO_FILE_EXT = 'students_info_file_ext'
KEY_STU_FILE_FOLDER = 'students_file_folder'
KEY_INFO_FILE_FOLDER = 'students_info_file_folder'
KEY_ML = '-ML-'
KEY_PRO_BAR = 'progressbar'
KEY_PRO_TEXT = 'progress'

DEFAULT_INPUT_BG = "#000000" #"#705e52"

token_tip = "To generate a Canvas API key via 'Account', 'Settings', '+ New Access Token'."
course_id_tip = "The course ID is a number."
group_category_tip = "Name of the Canvas Group Set (see Canvas tab People) that contains the student groups."

CSV = "csv"
YAML = "yaml"
XLSX = "xlsx"

TYPE_CSV = ("Text Files", "*.csv")
TYPE_YAML = ("Text Files", "*.yaml")
TYPE_XLSX = ("Excel Workbook", "*.xlsx")

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


def update_browse(file_path: str, save_as: bool, file_types: str, extension: str) -> str:
    (folder, filename) = os.path.split(file_path)
    return sg.popup_get_file("", save_as=save_as, file_types=file_types, no_window=True, default_path=filename, default_extension=extension, initial_folder=folder, history=True)

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

def is_invalid(string: str) -> bool:
    return string is None or string == ""

def add_help_button(key: str, tooltip: str) -> sg.Button:
    return sg.Button(key=key, button_color=(sg.theme_background_color(), sg.theme_background_color()),
               image_filename=help, image_subsample=60, border_width=0, tooltip = tooltip, pad=(2, 0))

def update_progress(pos: int, length: int):
    global progress_bar, progress_text
    percent = int(100 * pos / length)
    progress_bar.UpdateBar(percent)
    progress_text.update("{}%".format(percent))

def students_yaml_file_window(main_window: sg.Window):
    students_info_file = sg.user_settings_get_entry(KEY_INFO_FILE_EXT)
    students_yaml_file = sg.user_settings_get_entry(KEY_STU_FILE)
    layout = [
        [
            sg.Text('Info File', pad=(0, 3)), sg.InputText(k=KEY_INFO_FILE_EXT, default_text=students_info_file, expand_x = True, pad=((42, 0), 0), readonly=True, disabled_readonly_background_color=DEFAULT_INPUT_BG),
            sg.B("Browse", k=KEY_INFO_FILE_FOLDER, pad=((5, 0), 0))
        ],
        [
            sg.Text('Students File', pad=(0, 3)), sg.InputText(k=KEY_STU_FILE, default_text=students_yaml_file, expand_x = True, pad=((10, 0), 0), readonly=True, disabled_readonly_background_color=DEFAULT_INPUT_BG),
            sg.B("Browse", k=KEY_STU_FILE_FOLDER, pad=((5, 0), 0))
        ],
        [
            sg.Multiline(size=(70, 21), key=KEY_ML, reroute_cprint=True, expand_y=True, expand_x=True, auto_refresh=True)
        ],
        [
            sg.B('Execute'), sg.B('Exit'), sg.B('Clear History', pad=((348, 0), 0))
        ]
    ]
    window = sg.Window('CREATE STUDENT YAML FILE', layout, icon=icon, finalize=True)
    sg.cprint_set_output_destination(window, KEY_ML)

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        if event == KEY_INFO_FILE_FOLDER:
            if not students_info_file or students_info_file.endswith(".csv"):
                file_type =  ((TYPE_CSV), (TYPE_XLSX), )
            elif students_info_file.endswith(".xlsx"):
                file_type =  ((TYPE_XLSX), (TYPE_CSV), )
            else:
                file_type = (("ALL Files", "*.* *"),)

            file_path = update_browse(values[KEY_INFO_FILE_EXT], False, file_type, '')
            if file_path != "":
                students_info_file = file_path
                window[KEY_INFO_FILE_EXT].update(file_path)

        elif event == KEY_STU_FILE_FOLDER:
            file_path = update_browse(values[KEY_STU_FILE], True, (TYPE_YAML,), YAML)
            if file_path != "":
                students_yaml_file = file_path
                window[KEY_STU_FILE].update(file_path)

        elif event == "Execute":
            if is_empty(students_info_file, "Students Info File"):
                continue

            if is_empty(students_yaml_file, "Students File"):
                continue

            sg.user_settings_set_entry(KEY_INFO_FILE_EXT, students_info_file)
            sg.user_settings_set_entry(KEY_STU_FILE, students_yaml_file)

            splittext = os.path.splitext(students_info_file)
            if len(splittext) > 1:
                CreateStudentsYAMLFile(students_info_file, students_yaml_file, splittext[1])
            else:
                sg.cprint("Unknown file type. Please select a csv file or a xlsx file")

        elif event.endswith("_tip"):
            window[event].TooltipObject.showtip()
            sg.cprint(window[event].TooltipObject.text)

        elif event == 'Clear History':
            window[KEY_ML].update('')
            update_progress(0, 100)

    window.close()
    sg.cprint_set_output_destination(main_window, KEY_ML)

def students_info_file_window(access_token: str, base_url: str, main_window: sg.Window):
    base_url = urlparse(base_url)
    group_category_name = sg.user_settings_get_entry(KEY_GROUP_CATEGORY)
    students_info_file = sg.user_settings_get_entry(KEY_INFO_FILE)
    if group_category_name is None:
        group_category_name = "Project Groups"
        sg.user_settings_set_entry(KEY_GROUP_CATEGORY, group_category_name)

    layout = [
        [
            sg.Text('Course ID', pad=(0, 3)), sg.InputText(k=KEY_COURSE_ID, default_text=sg.user_settings_get_entry(KEY_COURSE_ID), expand_x = True),
            add_help_button('course_id_tip', course_id_tip)
        ],
        [
            sg.Text('Group Set', pad=(0, 3)), sg.InputText(k=KEY_GROUP_CATEGORY, default_text=group_category_name, expand_x = True, pad=((1, 0), 0)),
            add_help_button('group_category_tip', group_category_tip)
        ],
        [
            sg.Text('Info File', pad=(0, 3)), sg.InputText(k=KEY_INFO_FILE, default_text=students_info_file, expand_x = True, pad=((15, 0), 0), readonly=True, disabled_readonly_background_color=DEFAULT_INPUT_BG),
            sg.B("Browse", k=KEY_INFO_FILE_FOLDER, pad=((5, 0), 0))
        ],
        [
            sg.Text('File Type', pad=(0, 3)), sg.Checkbox(CSV, k=CSV, default=sg.user_settings_get_entry(CSV)), sg.Checkbox(XLSX, k=XLSX, default=sg.user_settings_get_entry(XLSX))
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

    window = sg.Window('CREATE STUDENTS INFO FILE', layout, icon=icon, finalize=True)
    sg.cprint_set_output_destination(window, KEY_ML)
    progressBar(window[KEY_PRO_BAR], window[KEY_PRO_TEXT])

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Exit"):
            break

        elif event == KEY_INFO_FILE_FOLDER:
            file_type = ()
            if values[CSV]:
                file_type = file_type + (TYPE_CSV,)

            if values[XLSX]:
                file_type = file_type + (TYPE_XLSX,)

            file_path = update_browse(values[KEY_INFO_FILE], True, file_type, '')
            if file_path != "":
                file_path = os.path.splitext(file_path)[0]
                students_info_file = file_path
                window[KEY_INFO_FILE].update(file_path)

        elif event == "Execute":
            course_id = values[KEY_COURSE_ID]

            if is_empty(course_id, "Course ID") or not is_number(course_id, "Course ID"):
                continue

            group_category_name = values[KEY_GROUP_CATEGORY]
            if is_empty(group_category_name, "Group Category"):
                continue

            file_csv = values[CSV]
            file_xlsx = values[XLSX]
            if not file_csv and not file_xlsx:
                popup("Please select at least one file type")
                continue

            extensions = []
            if file_csv:
                extensions.append(CSV)

            if file_xlsx:
                extensions.append(XLSX)

            del(values[KEY_ML])
            for key, val in values.items():
                sg.user_settings_set_entry(key, val)

            CreateStudentsInfoFile(base_url, access_token, course_id, group_category_name, students_info_file, extensions)

        elif event.endswith("_tip"):
            window[event].TooltipObject.showtip()
            sg.cprint(window[event].TooltipObject.text)

        elif event == 'Clear History':
            window[KEY_ML].update('')
            update_progress(0, 100)

    window.close()
    sg.cprint_set_output_destination(main_window, KEY_ML)

def settings_window(access_token: str, base_url: str, main_window: sg.Window) -> (str, str):
    students_info_file = sg.user_settings_get_entry(KEY_INFO_FILE)
    student_file = sg.user_settings_get_entry(KEY_STU_FILE)
    layout = [
            [
                sg.Text('Access Token', pad=(0, 3)), sg.InputText(k=KEY_ACCESS_TOKEN, default_text=access_token, expand_x = True, pad=(2, 0)),
                add_help_button('token_tip', token_tip)
            ],
            [
                sg.Text('Base URL', pad=(0, 3)), sg.InputText(k=KEY_BASE_URL, default_text=base_url, expand_x = True, pad=((26, 25), 0))
            ],
            [
                sg.Text('Course ID', pad=(0, 3)), sg.InputText(k=KEY_COURSE_ID, default_text=sg.user_settings_get_entry(KEY_COURSE_ID), expand_x = True, pad=((28, 0), 0)),
                add_help_button('course_id_tip', course_id_tip)
            ],
            [
                sg.Multiline(size=(70, 20), key=KEY_ML, reroute_cprint=True, expand_y=True, expand_x=True, auto_refresh=True)
            ],
            [
                sg.B('Save'), sg.B('Cancel'), sg.B('Clear History', pad=((348, 0), 0))
            ]
        ]
    window = sg.Window('SETTINGS', layout, icon=icon, finalize=True)

    while True:
        event, values = window.read()

        if event in ('Cancel', sg.WIN_CLOSED):
            break


        elif event.endswith("_tip"):
            window[event].TooltipObject.showtip()
            sg.cprint(window[event].TooltipObject.text)

        elif event == 'Save':
            if is_empty(values[KEY_ACCESS_TOKEN], "Access Token"):
                continue
            if is_empty(values[KEY_BASE_URL], "Base URL"):
                continue
            if not is_number(values[KEY_COURSE_ID], "Course ID"):
                continue

            access_token = values[KEY_ACCESS_TOKEN]
            base_url = values[KEY_BASE_URL]

            del(values[KEY_ML])
            for key, val in values.items():
                sg.user_settings_set_entry(key, val)
            break

        elif event.endswith("_tip"):
            window[event].TooltipObject.showtip()
            sg.cprint(window[event].TooltipObject.text)

        elif event == 'Clear History':
            window[KEY_ML].update('')

    window.close()
    sg.cprint_set_output_destination(main_window, KEY_ML)
    return (access_token, base_url)