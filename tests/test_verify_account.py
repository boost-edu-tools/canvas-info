from repobee_canvas.command.verify_course_id import VerifyCourseByID
from repobee_canvas.gui import KEY_ACCESS_TOKEN, KEY_BASE_URL, KEY_COURSE_ID
import PySimpleGUI as sg


def test_verify_gitlab():
    sg.user_settings_filename(filename="canvas_info.json")
    course_id = sg.user_settings_get_entry(KEY_COURSE_ID)
    course = sg.user_settings_get_entry(course_id)
    assert course_id is not None
    assert course is not None
    base_url = course[KEY_BASE_URL]
    access_token = course[KEY_ACCESS_TOKEN]
    assert base_url is not None
    assert access_token is not None
    course_name, group_set = VerifyCourseByID(base_url, access_token, int(course_id))
    assert course_name is not None
    assert group_set is not None
