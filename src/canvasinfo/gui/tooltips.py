"""Tooltip texts for the application."""

class ToolTips:
    """Container for tooltip texts"""
    
    def __init__(self):
        self.access_token = (
            "Generate via: Canvas > Account > Settings > "
            "Blue Box '+ New access token' on page > Generate Token"
        )
        
        self.base_url = (
            "Default value should be correct for TUe users of Canvas, "
            "only change when you know what you are doing."
        )
        
        self.course_id = (
            "Number at the end of the Canvas URL for your course"
        )
        
        self.info_file = (
            "Output path for CSV or Excel file, containing for each student "
            "the following columns: group number, last name, Canvas student ID, "
            "student ID (used for GitLab login), email"
        )
        
        self.yaml_file = (
            "Student info file for Repobee with for each student group: "
            "repo name and student IDs"
        )
        
        self.full_groups = (
            "Only full groups are included in the generated files"
        )
        
        self.member_options = (
            "Choose how to identify students in the output files"
        )
        
        self.repo_options = (
            "Configure how repository names are generated"
        )
        
        self.help_info = """
Canvas Info Help

This application helps you manage Canvas course information and generate student files.

Output Configuration:
- Select output folder for CSV/Excel files
- Choose which file types to generate
- Configure YAML file for RepoBee integration

Canvas Configuration:
- Set your Canvas base URL and access token
- Verify course settings before execution
- Manage multiple course configurations

Member Options:
- (Email, ID): Include both email and student ID
- Email: Use email addresses only
- Year ID: Use student IDs only

Repo Name Options:
- Include Group Name: Add group name to repository name
- Include Member Names: Add member names to repository name
- Include Initials: Use initials instead of full names

For more information, visit the documentation.
        """