#!/usr/bin/env python3
"""Command-line interface for Canvas Info."""

import sys
import argparse
from pathlib import Path
from typing import Optional

from .core.settings import Settings
from .core.course_manager import CourseManager
from .canvas.create_students_files import CreateStudentsFiles
from .canvas.verify_course_id import VerifyCourseByID


class InvalidArgument(Exception):
    """Exception for invalid command-line arguments."""
    
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg


def get_boolean_argument(arg) -> bool:
    """Convert string argument to boolean."""
    if isinstance(arg, bool):
        return arg
    elif arg is None or arg.lower() == "false" or arg.lower() == "f" or arg == "0":
        return False
    elif arg.lower() == "true" or arg.lower() == "t" or arg == "1":
        return True
    
    raise InvalidArgument("The given option argument is not a valid boolean.")


def print_message(message: str):
    """Print message to stdout."""
    print(message)


def main():
    """Main CLI entry point."""
    try:
        parser = argparse.ArgumentParser(
            prog="canvasinfo-cli",
            description="Canvas Info CLI - Manage Canvas course information",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        
        parser.add_argument(
            "-t", "--access_token",
            help="Canvas access token"
        )
        
        parser.add_argument(
            "--base_url",
            help="Canvas base URL"
        )
        
        parser.add_argument(
            "--course_id",
            type=int,
            help="Canvas course ID"
        )
        
        parser.add_argument(
            "-o", "--option",
            action="append",
            choices=["email", "git_id"],
            help="Member identification option"
        )
        
        parser.add_argument(
            "-G", "--inc_group",
            action="store_true",
            default=False,
            help="Include group name in repository name"
        )
        
        parser.add_argument(
            "-M", "--inc_member",
            action="store_true",
            default=False,
            help="Include member names in repository name"
        )
        
        parser.add_argument(
            "-I", "--inc_initial",
            action="store_true",
            default=False,
            help="Include initials instead of full names"
        )
        
        parser.add_argument(
            "-F", "--full_groups",
            action="store_true",
            default=True,
            help="Only include full groups"
        )
        
        parser.add_argument(
            "--info_file",
            help="Base name for info files (without extension)"
        )
        
        parser.add_argument(
            "--yaml_file",
            help="YAML file path (without extension)"
        )
        
        parser.add_argument(
            "action",
            choices=["info", "verify"],
            help="Action to perform"
        )
        
        args = parser.parse_args()
        
        # Initialize settings and course manager
        settings = Settings()
        course_manager = CourseManager(settings)
        
        # Get course settings
        course_id = args.course_id
        if not course_id:
            course_id = course_manager.current_course_id
            if not course_id or course_id == "00001":
                # Check if default course exists
                course = course_manager.get_current_course()
                if not course:
                    raise InvalidArgument("No course configured. Please set up a course first.")
        
        course = course_manager.get_course_settings(str(course_id))
        if not course:
            raise InvalidArgument(f"Course {course_id} not found in settings.")
        
        # Get base URL and access token
        base_url = args.base_url or course.get("base_url")
        access_token = args.access_token or course.get("access_token")
        
        if not base_url:
            raise InvalidArgument("Invalid base URL. Please provide a base URL.")
        
        if not access_token:
            raise InvalidArgument("Invalid access token. Please provide an access token.")
        
        # Execute action
        if args.action == "verify":
            course_name = VerifyCourseByID(
                base_url, 
                access_token, 
                int(course_id),
                print_message
            )
            if course_name:
                print_message(f"Course verified: {course_name}")
            else:
                print_message("Course verification failed")
                sys.exit(1)
                
        elif args.action == "info":
            # Prepare file paths
            csv_file = None
            xlsx_file = None
            yaml_file = None
            
            if args.info_file:
                csv_file = args.info_file + ".csv"
                xlsx_file = args.info_file + ".xlsx"
            
            if args.yaml_file:
                yaml_file = args.yaml_file + ".yaml"
            
            # Use course defaults if not specified
            if not csv_file and course.get("csv", False):
                csv_file = course.get("csv_info_file")
            if not xlsx_file and course.get("xlsx", False):
                xlsx_file = course.get("xlsx_info_file")
            if not yaml_file and course.get("yaml", False):
                yaml_file = course.get("students_file")
            
            # Get options
            member_option = args.option[0] if args.option else course.get("member_option", "email")
            include_group = args.inc_group or course.get("include_group", False)
            include_member = args.inc_member or course.get("include_member", False)
            include_initials = args.inc_initial or course.get("include_initials", False)
            full_groups = args.full_groups if args.full_groups else course.get("full_groups", True)
            
            # Create files
            CreateStudentsFiles(
                base_url,
                access_token,
                int(course_id),
                csv_file,
                xlsx_file,
                yaml_file,
                None,  # teammates file
                member_option,
                include_group,
                include_member,
                include_initials,
                full_groups,
                message_callback=print_message
            )
            
        else:
            raise InvalidArgument("Invalid action.")
            
    except (InvalidArgument, Exception) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        if isinstance(e, InvalidArgument):
            print(f"Try '{sys.argv[0]} --help' for more information.", file=sys.stderr)
            sys.exit(1)
        else:
            sys.exit(2)
    
    print_message("Done.")


if __name__ == "__main__":
    main()