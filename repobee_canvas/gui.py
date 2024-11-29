import PySimpleGUI as sg
import base64
import sys
from pathlib import Path
from typing import Tuple, Optional, Any

WINDOW_SIZE_X = 750
WINDOW_SIZE_Y = 770
MAX_COL_HEIGHT = 400
WINDOW_HEIGHT_CORR = 45  # height correction: height of command buttons + title bar
COL_PERCENT = 60
INIT_COL_HEIGHT = int((WINDOW_SIZE_Y - WINDOW_HEIGHT_CORR) * COL_PERCENT / 100)

KEY_ACCESS_TOKEN = "canvas_access_token"
KEY_BASE_URL = "canvas_base_url"
KEY_COURSE_ID = "canvas_course_id"
KEY_STU_FILE = "students_file"
KEY_CSV_INFO_FILE = "stu_csv_info_file"
KEY_XLSX_INFO_FILE = "stu_xlsx_info_file"
KEY_TEAMMATES_INFO_FILE = "stu_teammates_info_file"
KEY_INFO_FILE_FOLDER = "info_file_folder"
KEY_INFO_FILE_FOLDER_FB = "info_file_folder_fb"  # folder browse
KEY_STU_FILE_FOLDER = "students_file_folder"
KEY_ML = "-ML-"
KEY_PRO_BAR = "progressbar"
KEY_PRO_TEXT = "progress"
KEY_MEMBER_OPTION = "member_option"
KEY_GIT_ID = "git_id"
KEY_EMAIL = "email"
KEY_MEM_BOTH = "(email, gitid)"
KEY_FULL_GROUPS = "full_groups"
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
KEY_COURSE_NAME = "course_name"
KEY_COURSES = "courses"
KEY_DELETE_COURSE = "delete_course"
KEY_CLONE_COURSE = "clone_course"
KEY_NEW_COURSE = "new_course"
KEY_END = "end"
KEY_TUE = "TUE"
KEY_CUSTOM = "Custom"
KEY_URL_OPTION = "url_option"
KEY_URL_OPTIONS = "url_options"
KEY_EDIT_TOKEN = "token_bt"
KEY_EDIT_URL = "url_bt"

DEFAULT_INPUT_PAD = ((3, 5), 2)
TEXT_CB_SIZE = 11
INPUT_CB_PAD = ((0, 5), 2)

token_tip = "Canvas > Account > Settings > New access token > Generate Token"
token_tip_ml = "Generate via: Canvas > Account > Settings > Blue Box '+ New access token' on page > Generate Token"
base_url_tip = "Default value should be correct for TUe users of Canvas, only change when you know what you are doing."
course_id_tip = "Number at the end of the Canvas URL for your course"
info_file_tip = "Output file with columns: group number, name, Canvas student ID, GitLab student ID, email"
info_file_tip_ml = "Output path for CSV or Excel file, containing for each student the following columns: group number, last name, Canvas student ID, student ID (used for GitLab login), email"
yaml_file_tip = "Student info file for Repobee with for each student group: repo name and student IDs"
full_groups_tip = "Only full groups are included in the generated files"
member_options_tip = "Options tip"
yaml_options_tip = "repo option tip"
help_info = "help info"

CSV = "csv"
YAML = "yaml"
XLSX = "xlsx"
TEAMMATES = "teammates"

TYPE_YAML = ("Text Files", "*.yaml")

DEFAULT_COURSE_ID = "00001"

MODE_PARSE = 0
MODE_CLONE = 2
MODE_CREATE = 3

URL_OPTIONS = [KEY_TUE, KEY_CUSTOM]
TUE_API_URL = "https://canvas.tue.nl"

NABLED_COLOR = ("white", "#082567")
DISABLED_COLOR = ("grey", "#082567")

buttons = [
    KEY_VERIFY,
    "token_bt",
    KEY_EDIT_URL,
    KEY_DELETE_COURSE,
    KEY_EXECUTE,
    KEY_STU_FILE_FOLDER,
    KEY_INFO_FILE_FOLDER_FB,
    KEY_CLONE_COURSE,
    KEY_NEW_COURSE,
    KEY_HELP,
    KEY_EXIT,
    KEY_CLEAR,
]
TEXT_SETTINGS_KEY = [
    KEY_BASE_URL,
    KEY_ACCESS_TOKEN,
    KEY_INFO_FILE_FOLDER,
    KEY_STU_FILE,
    KEY_URL_OPTION,
]
INFO_FILE_KEY = [KEY_CSV_INFO_FILE, KEY_XLSX_INFO_FILE, KEY_TEAMMATES_INFO_FILE]
BOOL_SETTINGS_KEY = [
    CSV,
    XLSX,
    TEAMMATES,
    YAML,
    KEY_INC_INITIAL,
    KEY_INC_GROUP,
    KEY_INC_MEMBER,
    KEY_FULL_GROUPS,
]
COURSE_SETTINGS_KEYS = TEXT_SETTINGS_KEY + BOOL_SETTINGS_KEY
course_info = None
course_title = "ID: {0}  Name: {1}"

if sys.platform == "darwin":
    sg.set_options(font=("Any", 12))

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

    if not course_id:
        create_template_course()
        updated = True

    if updated:
        settings.load()


def create_template_course():
    global course_id, course_info
    course_id = DEFAULT_COURSE_ID
    course_info = Course(course_id, mode=MODE_CREATE)
    settings.set(KEY_COURSE_ID, course_id)
    settings.set(KEY_COURSES, [course_info.get_course_title()])


class Course:
    def __init__(
        self, course_id: Optional[str], course: dict | None = None, mode: int = MODE_PARSE
    ):
        self.course = {}
        self.course_id = course_id
        self.course[KEY_COURSE_ID] = self.course_id
        if mode == MODE_CREATE:
            self.create_course()
            self.save()
        else:
            assert course is not None
            self.course[KEY_URL_OPTIONS] = course[KEY_URL_OPTIONS]
            for key in COURSE_SETTINGS_KEYS + INFO_FILE_KEY:
                if key in course:
                    self.course[key] = course[key]
                else:
                    self.course[key] = None
            self.course[KEY_MEMBER_OPTION] = course[KEY_MEMBER_OPTION]

            if mode != MODE_PARSE:
                self.course[KEY_COURSE_NAME] = "Unverified"
                self.save()
            else:
                self.course[KEY_COURSE_NAME] = course[KEY_COURSE_NAME]

    def create_course(self):
        home = str(Path.home())
        for key in TEXT_SETTINGS_KEY:
            self.course[key] = ""
        for key in BOOL_SETTINGS_KEY:
            self.course[key] = False
        self.course[KEY_MEMBER_OPTION] = KEY_MEM_BOTH
        self.course[KEY_COURSE_NAME] = "Unverified"
        self.course[KEY_BASE_URL] = TUE_API_URL
        self.course[KEY_STU_FILE] = home + "/students.yaml"
        self.course[KEY_STU_FILE_FOLDER] = home
        self.course[KEY_INFO_FILE_FOLDER] = home
        self.course[KEY_CSV_INFO_FILE] = "student-info.csv"
        self.course[KEY_XLSX_INFO_FILE] = "student-info.xlsx"
        self.course[KEY_TEAMMATES_INFO_FILE] = "teammates-students.xlsx"
        self.course[KEY_INC_GROUP] = True
        self.course[KEY_INC_MEMBER] = True
        self.course[KEY_FULL_GROUPS] = True
        self.course[KEY_URL_OPTIONS] = {KEY_TUE: TUE_API_URL, KEY_CUSTOM: ""}
        self.course[KEY_URL_OPTION] = KEY_TUE

    def get_course_title(self):
        return course_title.format(self.course_id, self.course[KEY_COURSE_NAME])

    def save(self):
        assert self.course_id is not None
        set_entry(self.course_id, self.course)

    def get(self):
        return self.course

    def update(self, key, value):
        self.course[key] = value
        self.save()

    def update_url(self, key, value):
        self.course[KEY_BASE_URL] = value
        self.course[KEY_URL_OPTIONS][key] = value
        self.save()


def set_update_course_info(window: sg.Window, key: str, value: str):
    set_course_info(key, value)
    window[key].update(value=value)


def set_course_info(key: str, value: Any):
    global course_info
    if course_info:
        course_info.update(key, value)


def set_course_url(key: str, value: str):
    global course_info
    if course_info:
        course_info.update_url(key, value)


def get_input_course_id(course_list: list, default_course: str) -> Optional[str]:
    course_id = sg.popup_get_text(
        "New Course ID", default_text=default_course, keep_on_top=True
    )
    while course_id:
        if valid_course_id(course_list, course_id):
            return course_id
        course_id = sg.popup_get_text(
            "New Course ID", default_text=course_id, keep_on_top=True
        )
    return None


def valid_course_id(course_list: list, course_id: str) -> bool:
    for course_title in course_list:
        info = course_title.split(" ")
        if len(info) > 1:
            if course_id == info[1]:
                popup("The course exists")
                return False

    if course_id == "00000":
        popup("Course ID 00000 cannot be added.")
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


def update_course_ui(window: sg.Window, course: dict):
    assert course_info is not None
    window[KEY_COURSES].update(value=course_info.get_course_title())

    for key in COURSE_SETTINGS_KEYS:
        window[key].update(value=course[key])

    member_option = course[KEY_MEMBER_OPTION]
    window[KEY_EMAIL].update(value=(KEY_EMAIL == member_option))
    window[KEY_GIT_ID].update(value=(KEY_GIT_ID == member_option))
    window[KEY_MEM_BOTH].update(value=(KEY_MEM_BOTH == member_option))
    check_url_lock(window[KEY_EDIT_URL], course[KEY_URL_OPTION])


def update_course_settings(
    window: sg.Window, id: str, course: Optional[dict], mode: int
):
    global course_info, course_id
    courses_list = window[KEY_COURSES].Values
    course_id = id
    course_info = Course(course_id, course=course, mode=mode)
    if mode in (MODE_CLONE, MODE_CREATE):
        course = course_info.get()
        window[KEY_COURSES].update(value=course_info.get_course_title())
        # update course_list
        courses_list.append(course_info.get_course_title())
        courses_list.sort(reverse=True)
        update_courses_list(window, courses_list)

    settings.set(KEY_COURSE_ID, course_id)
    update_course_ui(window, course_info.get())


def delete_course_id(window: sg.Window):
    global course_id, course_info
    course_title = window[KEY_COURSES].DefaultValue
    courses_list = window[KEY_COURSES].Values
    ind = courses_list.index(course_title)
    ind -= 1
    if ind < 0:
        ind = 0
    courses_list.remove(course_title)
    sg.user_settings_delete_entry(course_id)
    if len(courses_list) == 0:
        create_template_course()
        courses_list = settings[KEY_COURSES]
    assert courses_list is not None
    update_courses_list(window, courses_list)
    course_id = courses_list[ind].split(" ")[1]
    settings.set(KEY_COURSE_ID, course_id)
    course_info = Course(course_id, settings[course_id])
    window[KEY_COURSES].update(set_to_index=ind)
    update_course_ui(window, course_info.get())


def check_url_lock(button: sg.Button, url_option: str):
    if url_option == KEY_TUE:
        button.update(disabled=True)
    else:
        button.update(disabled=False)


def update_courses_list(window: sg.Window, courses_list: list):
    window[KEY_COURSES].update(values=courses_list)
    settings.set(KEY_COURSES, courses_list)


def update_col_percent(window, wh, percent):
    element = window[KEY_CONFIG_COL]
    set_entry(KEY_COL_PERCENT, percent)
    global COL_PERCENT
    if COL_PERCENT != percent:
        COL_PERCENT = percent
        update_column_height(element, wh, wh)


def resource_path(relative_path=None):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = Path(".").resolve()

    if relative_path is None:
        return base_path

    return Path(base_path) / relative_path


icon = resource_path("icon.png")
with open(icon, "rb") as file:
    icon = base64.b64encode(file.read())


def set_entry(key: str, val: Any):
    sg.user_settings_set_entry(key, val)


def get_entry(key: str) -> Any:
    return sg.user_settings_get_entry(key)


progress_bar = None
progress_text = None


def progressBar(bar: sg.ProgressBar, text: sg.Text):
    global progress_bar, progress_text
    progress_bar = bar
    progress_text = text


def update_browse(file_path: str) -> str:
    return sg.popup_get_folder(
        "",
        no_window=True,
        initial_folder=str(Path(file_path).parent),
        history=True,
    )  # default_extension=extension,


def save_as(file_path: str, file_types: Tuple[Tuple[str, str]]) -> str:
    file = Path(file_path)
    return sg.popup_get_file(
        "",
        save_as=True,
        file_types=file_types,
        no_window=True,
        default_path=file.name,
        initial_folder=str(file.parent),
        history=True,
    )  # default_extension=extension,


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
    if Path(path).parent.exists():
        return False

    sg.popup("Error", "Invalid " + file_type + " file path.")
    return True


def help_button(key: str, tooltip: str) -> sg.Button:
    buttons.append(key)
    return sg.Button("?", key=key, tooltip=tooltip, pad=(3, 0))


def update_progress(pos: int, length: int):
    global progress_bar, progress_text
    if not progress_bar and not progress_text:
        return
    percent = int(100 * pos / length)
    assert progress_bar is not None
    assert progress_text is not None
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


def update_column_height(element, wh, last_screen_height):
    ch = element.Widget.canvas.winfo_height()
    if ch < MAX_COL_HEIGHT or (wh - last_screen_height) <= 0:
        ch = (wh - WINDOW_HEIGHT_CORR) * COL_PERCENT / 100
        ch = min(ch, MAX_COL_HEIGHT)
        update_height(element, int(ch))


def Text(text: str, key: str = None, sz: int = 11) -> sg.Text:
    return sg.Text(text, k=key, pad=(0, 2), size=sz)


def InputText(
    key: str,
    text: str,
    password: str = "",
    readOnly: bool = True,
    pad: tuple = DEFAULT_INPUT_PAD,
    enable_events: bool = True,
) -> sg.InputText:
    return sg.InputText(
        k=key,
        default_text=text,
        disabled=readOnly,
        password_char=password,
        pad=pad,
        enable_events=enable_events,
        expand_x=True,
    )


def Checkbox(
    key, default, text: str = "", disabled: bool = False, size=(None, None)
) -> sg.Checkbox:
    return sg.Checkbox(
        text,
        k=key,
        default=default,
        enable_events=True,
        pad=(0, 2),
        disabled=disabled,
        s=size,
    )


def Button(text, key) -> sg.Button:
    return sg.B(text, k=key, pad=(3, 2))


def Radio(text: str, key: str, default_val: bool) -> sg.Radio:
    return sg.Radio(
        text, KEY_MEMBER_OPTION, k=key, default=default_val, enable_events=True
    )


def Folder_Button(key, disable) -> sg.Button:
    return sg.B(
        "Browse",
        k=key,
        pad=((3, 0), 2),
        disabled=disable,
        disabled_button_color=DISABLED_COLOR,
    )


def Combo(
    values: Optional[list], key: str, default: str, expand_x: bool = True
) -> sg.Combo:
    return sg.Combo(
        values,
        k=key,
        default_value=default,
        pad=DEFAULT_INPUT_PAD,
        enable_events=True,
        readonly=True,
        expand_x=expand_x,
    )


def Frame(title: str, layout: list, pad: Tuple[int, int] = None) -> sg.Frame:
    return sg.Frame(
        layout=layout, title=title, relief=sg.RELIEF_SUNKEN, expand_x=True, pad=pad
    )


def Column(layout: list, key: str = None):
    global INIT_COL_HEIGHT
    return sg.Column(
        layout,
        k=key,
        vertical_scroll_only=True,
        scrollable=True,
        expand_x=True,
        size=(None, INIT_COL_HEIGHT),
    )


def configure_canvas(event, canvas, frame_id):
    canvas.itemconfig(frame_id, width=event.width)


def configure_frame(event, canvas):
    canvas.configure(scrollregion=canvas.bbox("all"))


def update_height(element, height):
    element.Widget.canvas.configure({"height": height})


def make_window():
    sg.theme("SystemDefault")

    global course_info
    course_info = Course(course_id, course=settings[course_id])
    course = course_info.get()
    xlsx_checked = course[XLSX]
    member_option = course[KEY_MEMBER_OPTION]

    menu = [["Course"]]
    local_config_frame = Frame(
        "Output configuration",
        layout=[
            [
                Frame(
                    "",
                    layout=[
                        [
                            Text("Output Folder", sz=TEXT_CB_SIZE),
                            InputText(
                                KEY_INFO_FILE_FOLDER,
                                course[KEY_INFO_FILE_FOLDER],
                                pad=INPUT_CB_PAD,
                                enable_events=False,
                            ),
                            Folder_Button(KEY_INFO_FILE_FOLDER_FB, False),
                            help_button("info_folder_tip", info_file_tip),
                        ],
                        [
                            Text("Output Files", sz=TEXT_CB_SIZE),
                            Checkbox(
                                CSV,
                                course[CSV],
                                course[KEY_CSV_INFO_FILE],
                                size=(20, 0),
                            ),
                            Checkbox(
                                XLSX,
                                xlsx_checked,
                                course[KEY_XLSX_INFO_FILE],
                                size=(20, 0),
                            ),
                            Checkbox(
                                TEAMMATES,
                                course[TEAMMATES],
                                course[KEY_TEAMMATES_INFO_FILE],
                                size=(20, 0),
                            ),
                            sg.Text("", expand_x=True),
                            help_button("info_file_teammates_tip", info_file_tip),
                        ],
                    ],
                )
            ],
            [
                Frame(
                    "",
                    layout=[
                        [
                            Text("YAML File", sz=TEXT_CB_SIZE),
                            Checkbox(YAML, course[YAML]),
                            InputText(
                                KEY_STU_FILE,
                                course[KEY_STU_FILE],
                                pad=INPUT_CB_PAD,
                                readOnly=False,
                            ),
                            Folder_Button(KEY_STU_FILE_FOLDER, not xlsx_checked),
                            help_button("yaml_file_tip", yaml_file_tip),
                        ],
                        [
                            Frame(
                                "Members",
                                layout=[
                                    [
                                        Radio(
                                            "(Email, ID)",
                                            KEY_MEM_BOTH,
                                            KEY_MEM_BOTH == member_option,
                                        ),
                                        Radio(
                                            "Email",
                                            KEY_EMAIL,
                                            KEY_EMAIL == member_option,
                                        ),
                                        Radio(
                                            "Year ID",
                                            KEY_GIT_ID,
                                            KEY_GIT_ID == member_option,
                                        ),
                                        help_button(
                                            "member_options_tip", member_options_tip
                                        ),
                                    ]
                                ],
                            ),
                            Frame(
                                "Repo Name",
                                layout=[
                                    [
                                        Checkbox(
                                            KEY_INC_GROUP,
                                            course[KEY_INC_GROUP],
                                            "Include Group Name",
                                        ),
                                        Checkbox(
                                            KEY_INC_MEMBER,
                                            course[KEY_INC_MEMBER],
                                            "Include Member Names",
                                        ),
                                        Checkbox(
                                            KEY_INC_INITIAL,
                                            course[KEY_INC_INITIAL],
                                            "Include Initials",
                                            disabled=not course[KEY_INC_MEMBER],
                                        ),
                                        help_button(
                                            "yamloptions_tip", yaml_options_tip
                                        ),
                                    ]
                                ],
                            ),
                        ],
                        [
                            Frame(
                                "Filters",
                                layout=[
                                    [
                                        Checkbox(
                                            KEY_FULL_GROUPS,
                                            course[KEY_FULL_GROUPS],
                                            "Only full groups",
                                        ),
                                        help_button(
                                            "full_groups_tip", full_groups_tip
                                        ),
                                    ]
                                ],
                            ),
                        ],
                    ],
                )
            ],
        ],
        pad=(0, 0),
    )

    canvas_config_frame = Frame(
        "Canvas configuration",
        layout=[
            [Button(KEY_VERIFY, KEY_VERIFY)],
            [
                Frame(
                    "Course IDs",
                    layout=[
                        [
                            sg.Text("Course ID", pad=(0, 2), size=10),
                            Combo(
                                settings[KEY_COURSES],
                                KEY_COURSES,
                                default=course_info.get_course_title(),
                            ),
                            help_button("course_id_tip", course_id_tip),
                        ],
                        [
                            Button("New Course", KEY_NEW_COURSE),
                            Button("Copy Course", KEY_CLONE_COURSE),
                            Button("Delete Course", KEY_DELETE_COURSE),
                        ],
                    ],
                )
            ],
            [
                Text("Base URL"),
                Combo(
                    URL_OPTIONS,
                    KEY_URL_OPTION,
                    default=course[KEY_URL_OPTION],
                    expand_x=False,
                ),
                InputText(KEY_BASE_URL, course[KEY_BASE_URL]),
                sg.Button(
                    "Edit",
                    k=KEY_EDIT_URL,
                    pad=(3, 2),
                    disabled=course[KEY_URL_OPTION] == KEY_TUE,
                    disabled_button_color=("grey", "#082567"),
                ),
                help_button("base_url_tip", base_url_tip),
            ],
            [
                Text("Access Token"),
                InputText(
                    KEY_ACCESS_TOKEN,
                    course[KEY_ACCESS_TOKEN],
                    password="*",
                    enable_events=False,
                ),
                Button("Edit", KEY_EDIT_TOKEN),
                help_button("token_tip", token_tip),
            ],
        ],
    )

    layout = [
        [sg.Menu(menu)],
        [
            sg.Column(
                [
                    [
                        Button(KEY_EXECUTE, KEY_EXECUTE),
                        Button(KEY_CLEAR, KEY_CLEAR),
                        Button(KEY_HELP, KEY_HELP),
                        Button(KEY_EXIT, KEY_EXIT),
                    ]
                ],
                pad=(0, (4, 0)),
            ),
            sg.Column(
                [
                    [
                        sg.Spin(
                            [i for i in range(20, 90, 10)],
                            initial_value=COL_PERCENT,
                            k=KEY_COL_PERCENT,
                            enable_events=True,
                            pad=((5, 0), None),
                            readonly=True,
                        ),
                        sg.Text("%", pad=((0, 5), None)),
                    ]
                ],
                element_justification="right",
                expand_x=True,
                pad=(0, (4, 0)),
            ),
        ],
        [
            Column(
                [
                    [
                        sg.ProgressBar(
                            max_value=100,
                            orientation="h",
                            size=(0, 20),
                            expand_x=True,
                            key=KEY_PRO_BAR,
                            pad=(0, 0),
                        ),  # expand_x will overwrite the width
                        sg.Text(
                            "0%",
                            key=KEY_PRO_TEXT,
                            size=(4, None),
                            justification="right",
                        ),
                    ],
                    [local_config_frame],
                    [canvas_config_frame],
                ],
                KEY_CONFIG_COL,
            )
        ],
        [
            sg.Multiline(
                size=(70, 10),
                key=KEY_ML,
                reroute_cprint=True,
                expand_y=True,
                expand_x=True,
                auto_refresh=True,
            )
        ],
    ]

    window = sg.Window(
        "Canvas group info",
        layout,
        size=(WINDOW_SIZE_X, WINDOW_SIZE_Y),
        icon=icon,
        margins=(0, 0),
        resizable=True,
        finalize=True,
    )
    progressBar(window[KEY_PRO_BAR], window[KEY_PRO_TEXT])
    col = window[KEY_CONFIG_COL]
    widget = col.Widget
    assert widget is not None
    frame_id = widget.frame_id
    frame = widget.TKFrame
    canvas = widget.canvas
    canvas.bind(
        "<Configure>",
        lambda event, canvas=canvas, frame_id=frame_id: configure_canvas(
            event, canvas, frame_id
        ),
    )
    frame.bind(
        "<Configure>", lambda event, canvas=canvas: configure_frame(event, canvas)
    )
    window.bind("<Configure>", "Conf")
    sg.cprint_set_output_destination(window, KEY_ML)
    canvas.itemconfig(frame_id, width=canvas.winfo_width())
    window.refresh()
    return window
