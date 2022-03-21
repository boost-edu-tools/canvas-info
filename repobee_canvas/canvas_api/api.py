# Copyright 2021 Huub de Beer <h.t.d.beer@tue.nl>
#
# Licensed under the EUPL, Version 1.2 or later. You may not use this work
# except in compliance with the EUPL. You may obtain a copy of the EUPL at:
#
# https://joinup.ec.europa.eu/software/page/eupl
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the EUPL is distributed on an "AS IS" basis, WITHOUT
# WARRANTY OR CONDITIONS OF ANY KIND, either express or implied. See the EUPL
# for the specific language governing permissions and limitations under the
# licence.
"""Access to the Canvas API"""
import os
import requests

# HTTP header constants
AUTHORIZATION = "Authorization"
LOCATION = "Location"
BEARER = "Bearer {key}"

# Canvas API component names
ASSIGNMENTS = "assignments"
BODY = "body"
COMMENT = "comment"
COMMENTS = "comments"
COURSE = "course"
COURSE_ID = "course_id"
COURSES = "courses"
EMPTY = ""
ENROLLMENT_TYPE = "enrollment_type[]"
ERRORS = "errors"
FILE = "file"
FILE_IDS = "file_ids"
FILES = "files"
GROUP = "group"
GROUP_COMMENT = "group_comment"
GROUPS = "groups"
GROUPED = "grouped"
GROUP_CATEGORIES = "group_categories"
ID = "id"
INCLUDE = "include[]"
MEMBERSHIPS = "memberships"
NAME = "name"
NEXT = "next"
ONLINE_TEXT_ENTRY = "online_text_entry"
ONLINE_UPLOAD = "online_upload"
ONLINE_URL = "online_url"
OVERRIDES = "overrides"
PEER_REVIEWS = "peer_reviews"
PER_PAGE = "per_page"
PROFILE = "profile"
SECTIONS = "sections"
SIZE = "size"
STUDENT = "student"
STUDENTS = "students"
SUBMISSION = "submission"
SUBMISSION_COMMENTS = "submission_comments"
SUBMISSION_TYPE = "submission_type"
SUBMISSIONS = "submissions"
SUBMITTED_AT = "submitted_at"
TEXT_COMMENT = "text_comment"
TOTAL_STUDENTS = "total_students"
UPLOAD_PARAMS = "upload_params"
UPLOAD_URL = "upload_url"
URL = "url"
USER_ID = "user_id"
USERS = "users"

# Canvas API parameters
GROUPED_SUBMISSION = {INCLUDE: [GROUP, COURSE, SUBMISSION_COMMENTS], GROUPED: True}
ASSIGNMENT_OVERRIDES = {INCLUDE: [OVERRIDES]}
ALL_SECTIONS = {INCLUDE: [SECTIONS, TOTAL_STUDENTS]}
ALL_STUDENTS = {INCLUDE: [STUDENTS, TOTAL_STUDENTS]}
WITH_COURSE = {INCLUDE: [COURSE, SUBMISSION_COMMENTS]}
COURSE_STUDENTS = {ENROLLMENT_TYPE: [STUDENT]}

# Canvas data parameters
COMMENT_TEXT_COMMENT = COMMENT + "[" + TEXT_COMMENT + "]"
COMMENT_GROUP_COMMENT = COMMENT + "[" + GROUP_COMMENT + "]"
COMMENT_FILE_IDS = COMMENT + "[" + FILE_IDS + "][]"

SUB_SUBMISSION_TYPE = SUBMISSION + "[" + SUBMISSION_TYPE + "]"
SUB_FILE_IDS = SUBMISSION + "[" + FILE_IDS + "][]"
SUB_BODY = SUBMISSION + "[" + BODY + "]"
SUB_URL = SUBMISSION + "[" + URL + "]"
SUB_SUBMITTED_AT = SUBMISSION + "[" + SUBMITTED_AT + "]"
SUB_USER_ID = SUBMISSION + "[" + USER_ID + "]"
SUB_COMMENT = SUBMISSION + "[" + COMMENT + "]"

# Canvas API constants
PAGE_SIZE = 100
REDIRECT_STATUS_CODES = [300, 301, 303, 304, 305, 306, 307, 308]
UPLOAD_OKAY_STATUS_CODE = 201

# Error messages
REQUEST_FAILED = "Request failed: response code {code}, {reason}"
API_SETUP_PROBLEM = "CanvasAPI is not setup properly. See CanvasAPI#setup for details."
INCORRECT_UPLOAD_STATUS = "Incorrect status code for upload: {c} - {r}"
FILE_READ_ERROR = "Cannot read file at path '{p}'"
UPLOAD_ERRORS = "Upload failed:  {errors}"


class CanvasAPI:
    """Canvas API"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = object.__new__(cls, *args, **kwargs)

        return cls._instance

    def setup(self, api_url: str = None, access_token: str = None) -> None:
        """Setup this CanvasAPI with an url and access token."""
        self._session = requests.Session()

        if api_url:
            self._api_url = api_url

        if access_token:
            self._session.headers.update(
                {AUTHORIZATION: BEARER.format(key=access_token)}
            )

    def courses(self):
        """Get courses"""
        return self.__get({COURSES: EMPTY})

    def course(self, course_id):
        """Get course"""
        return self.__get({COURSES: course_id}, params=ALL_SECTIONS)

    def students_per_course(self, course_id):
        """Get students enrolled in a course."""
        return self.__get({COURSES: course_id, USERS: EMPTY}, params=COURSE_STUDENTS)

    def group(self, group_id):
        """Get group"""
        return self.__get({GROUPS: group_id})

    def group_memberships(self, group_id):
        """Get group memberships"""
        return self.__get({GROUPS: group_id, MEMBERSHIPS: EMPTY})

    def groups_per_course(self, course_id):
        """List the groups available in in a course."""
        return self.__get({COURSES: course_id, GROUPS: EMPTY})

    def group_categories_per_course(self, course_id):
        """List the group categories available in in a course."""
        return self.__get({COURSES: course_id, GROUP_CATEGORIES: EMPTY})

    def user(self, user_id):
        """Get user"""
        return self.__get({USERS: user_id, PROFILE: EMPTY})

    # Private utility methods
    def __get(self, components, params={}):
        url = self._create_url(components)
        params[PER_PAGE] = PAGE_SIZE
        response = self._session.get(url, params=params)

        self._check_response(response)

        # Handle multiple pages
        data = response.json()

        while NEXT in response.links:
            url = response.links[NEXT][URL]
            response = self._session.get(url, params=params)
            self._check_response(response)
            data.extend(response.json())

        return data

    def _create_url(self, components):
        if self._api_url is None:
            raise ValueError(API_SETUP_PROBLEM)

        url = self._api_url

        for object, id in components.items():
            if id:
                url += f"/{object}/{id}"
            else:
                url += f"/{object}"

        return url

    def _check_response(self, response, expected=requests.codes.ok):
        if response.status_code != expected:
            raise ValueError(
                REQUEST_FAILED.format(code=response.status_code, reason=response.reason)
            )
