from dataclasses import dataclass

@dataclass
class Help:
    help: str = """Help message"""
    access_token: str = "Help message for access token"
    base_url: str = "Help message for base url"
    course_id: str = "Help message for course id"
    group_category_name: str = "Help message for group"
    option: str = "Help message for option"
    include_group: str = "Help message for include group"
    include_member: str = "Help message for include member"
    include_initial: str = "Help message for include initial"
    info_file: str = "Help message for info file"
    yaml_file: str = "Help message for yaml file"
    action: str = "Help message for yaml action"
