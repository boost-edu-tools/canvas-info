from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QRadioButton, QComboBox, QTextEdit, 
    QProgressBar, QFileDialog, QMessageBox, QInputDialog,
    QScrollArea, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

from ..core.course_manager import CourseManager
from ..core.settings import Settings
from ..workers.canvas_worker import CanvasWorker
from .tooltips import ToolTips

class MainWindow(QWidget):
    def __init__(self, course_manager: CourseManager, settings: Settings):
        super().__init__()
        self.course_manager = course_manager
        self.settings = settings
        self.tooltips = ToolTips()
        self.worker_thread = None
        self.worker = None
        
        self.init_ui()
        self.load_current_course()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        
        # Top button bar
        self.create_top_buttons(layout)
        
        # Progress bar
        self.create_progress_bar(layout)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Vertical)
        
        # Main content area with scroll
        self.create_main_content(splitter)
        
        # Output text area
        self.create_output_area(splitter)
        
        # Set splitter proportions (70% for main content, 30% for output)
        splitter.setSizes([500, 200])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def create_top_buttons(self, layout: QVBoxLayout):
        """Create top button bar"""
        button_layout = QHBoxLayout()
        
        # Main action buttons
        self.execute_btn = QPushButton("Execute")
        self.execute_btn.clicked.connect(self.execute_command)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_output)
        
        self.help_btn = QPushButton("Help")
        self.help_btn.clicked.connect(self.show_help)
        
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self.close_application)
        
        button_layout.addWidget(self.execute_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.help_btn)
        button_layout.addWidget(self.exit_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def create_progress_bar(self, layout: QVBoxLayout):
        """Create progress bar"""
        progress_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        self.progress_label = QLabel("0%")
        self.progress_label.setMinimumWidth(40)
        self.progress_label.setVisible(False)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        
        layout.addLayout(progress_layout)
    
    def create_main_content(self, splitter: QSplitter):
        """Create main content area"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        
        # Step 1: Canvas Authentication
        self.create_canvas_auth(content_layout)
        
        # Step 2: Course Selection
        self.create_course_selection(content_layout)
        
        # Step 3: Output Configuration
        self.create_output_config(content_layout)
        
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)
        
        splitter.addWidget(scroll_area)
    
    def create_canvas_auth(self, layout: QVBoxLayout):
        """Create Canvas authentication section"""
        group = QGroupBox("Step 1: Canvas Authentication")
        group_layout = QVBoxLayout()
        
        # Base URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Base URL:"))
        
        self.url_combo = QComboBox()
        self.url_combo.addItems(["TUE", "Custom"])
        self.url_combo.currentTextChanged.connect(self.url_option_changed)
        
        self.base_url_edit = QLineEdit()
        
        self.edit_url_btn = QPushButton("Edit")
        self.edit_url_btn.clicked.connect(self.edit_url)
        
        url_layout.addWidget(self.url_combo)
        url_layout.addWidget(self.base_url_edit)
        url_layout.addWidget(self.edit_url_btn)
        
        group_layout.addLayout(url_layout)
        
        # Access token
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel("Access Token:"))
        
        self.access_token_edit = QLineEdit()
        self.access_token_edit.setEchoMode(QLineEdit.Password)
        
        self.edit_token_btn = QPushButton("Edit")
        self.edit_token_btn.clicked.connect(self.edit_token)
        
        token_layout.addWidget(self.access_token_edit)
        token_layout.addWidget(self.edit_token_btn)
        
        group_layout.addLayout(token_layout)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def create_course_selection(self, layout: QVBoxLayout):
        """Create course selection section"""
        group = QGroupBox("Step 2: Course Selection")
        group_layout = QVBoxLayout()
        
        # Course selection
        course_select_layout = QHBoxLayout()
        course_select_layout.addWidget(QLabel("Course:"))
        
        self.course_combo = QComboBox()
        self.course_combo.currentTextChanged.connect(self.course_changed)
        
        course_select_layout.addWidget(self.course_combo)
        group_layout.addLayout(course_select_layout)
        
        # Course management buttons
        course_btn_layout = QHBoxLayout()
        
        self.new_course_btn = QPushButton("New Course")
        self.new_course_btn.clicked.connect(self.new_course)
        
        self.delete_course_btn = QPushButton("Delete Course")
        self.delete_course_btn.clicked.connect(self.delete_course)
        
        course_btn_layout.addWidget(self.new_course_btn)
        course_btn_layout.addWidget(self.delete_course_btn)
        course_btn_layout.addStretch()
        
        group_layout.addLayout(course_btn_layout)
        
        # Verify button (after course selection and management)
        verify_layout = QHBoxLayout()
        self.verify_btn = QPushButton("Verify Course")
        self.verify_btn.clicked.connect(self.verify_course)
        verify_layout.addWidget(self.verify_btn)
        verify_layout.addStretch()
        group_layout.addLayout(verify_layout)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def create_output_config(self, layout: QVBoxLayout):
        """Create output configuration section"""
        group = QGroupBox("Step 3: File Generation")
        group_layout = QVBoxLayout()
        
        # Output folder (single folder for all files)
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Output Folder:"))
        
        self.output_folder_edit = QLineEdit()
        self.output_folder_browse = QPushButton("Browse")
        self.output_folder_browse.clicked.connect(self.browse_output_folder)
        
        folder_layout.addWidget(self.output_folder_edit)
        folder_layout.addWidget(self.output_folder_browse)
        
        group_layout.addLayout(folder_layout)
        
        # Output files section
        files_group = QGroupBox("Output Files")
        files_layout = QVBoxLayout()
        
        # Standard files row
        standard_files_layout = QHBoxLayout()
        self.csv_check = QCheckBox("CSV File (student-info.csv)")
        self.xlsx_check = QCheckBox("Excel File (student-info.xlsx)")
        self.teammates_check = QCheckBox("Teammates File (teammates-students.xlsx)")
        
        standard_files_layout.addWidget(self.csv_check)
        standard_files_layout.addWidget(self.xlsx_check)
        standard_files_layout.addWidget(self.teammates_check)
        
        files_layout.addLayout(standard_files_layout)
        
        # YAML file row
        yaml_layout = QHBoxLayout()
        self.yaml_check = QCheckBox("YAML File:")
        self.yaml_filename_edit = QLineEdit("students.yaml")
        self.yaml_filename_edit.setMaximumWidth(200)
        
        yaml_layout.addWidget(self.yaml_check)
        yaml_layout.addWidget(self.yaml_filename_edit)
        yaml_layout.addStretch()
        
        files_layout.addLayout(yaml_layout)
        
        files_group.setLayout(files_layout)
        group_layout.addWidget(files_group)
        
        # Options section
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        # Member identification
        member_group = QGroupBox("Member Identification")
        member_layout = QHBoxLayout()
        
        self.member_both_radio = QRadioButton("(Email, ID)")
        self.member_email_radio = QRadioButton("Email")
        self.member_git_radio = QRadioButton("Year ID")
        
        member_layout.addWidget(self.member_both_radio)
        member_layout.addWidget(self.member_email_radio)
        member_layout.addWidget(self.member_git_radio)
        
        member_group.setLayout(member_layout)
        options_layout.addWidget(member_group)
        
        # Repository naming
        repo_group = QGroupBox("Repository Naming")
        repo_layout = QHBoxLayout()
        
        self.include_group_check = QCheckBox("Include Group Name")
        self.include_member_check = QCheckBox("Include Member Names")
        self.include_initials_check = QCheckBox("Include Initials")
        
        self.include_member_check.toggled.connect(self.update_initials_state)
        
        repo_layout.addWidget(self.include_group_check)
        repo_layout.addWidget(self.include_member_check)
        repo_layout.addWidget(self.include_initials_check)
        
        repo_group.setLayout(repo_layout)
        options_layout.addWidget(repo_group)
        
        # Filters
        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout()
        
        self.full_groups_check = QCheckBox("Only full groups")
        filter_layout.addWidget(self.full_groups_check)
        
        filter_group.setLayout(filter_layout)
        options_layout.addWidget(filter_group)
        
        options_group.setLayout(options_layout)
        group_layout.addWidget(options_group)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
    
    def create_output_area(self, splitter: QSplitter):
        """Create output text area"""
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout()
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMinimumHeight(150)
        
        output_layout.addWidget(self.output_text)
        output_group.setLayout(output_layout)
        
        splitter.addWidget(output_group)
    
    def load_current_course(self):
        """Load current course settings"""
        # Load course list
        course_list = self.course_manager.get_course_list()
        self.course_combo.clear()
        self.course_combo.addItems(course_list)
        
        # Set current course
        current_course_id = self.course_manager.current_course_id
        for i, course_title in enumerate(course_list):
            if course_title.startswith(f"ID: {current_course_id}"):
                self.course_combo.setCurrentIndex(i)
                break
        
        # Load course settings
        self.update_ui_from_course()
    
    def update_ui_from_course(self):
        """Update UI from current course settings"""
        course = self.course_manager.get_current_course()
        
        # Canvas authentication
        self.base_url_edit.setText(course.get("base_url", ""))
        self.access_token_edit.setText(course.get("access_token", ""))
        
        # URL option
        url_option = course.get("url_option", "TUE")
        self.url_combo.setCurrentText(url_option)
        self.update_url_edit_state()
        
        # Output configuration
        self.output_folder_edit.setText(course.get("info_file_folder", ""))
        self.csv_check.setChecked(course.get("csv", False))
        self.xlsx_check.setChecked(course.get("xlsx", False))
        self.teammates_check.setChecked(course.get("teammates", False))
        self.yaml_check.setChecked(course.get("yaml", False))
        
        # YAML filename - extract filename from full path if it exists
        yaml_file = course.get("students_file", "students.yaml")
        if yaml_file:
            yaml_filename = Path(yaml_file).name if yaml_file else "students.yaml"
            self.yaml_filename_edit.setText(yaml_filename)
        
        # Member options
        member_option = course.get("member_option", "(email, gitid)")
        if member_option == "(email, gitid)":
            self.member_both_radio.setChecked(True)
        elif member_option == "email":
            self.member_email_radio.setChecked(True)
        elif member_option == "git_id":
            self.member_git_radio.setChecked(True)
        else:
            # Default fallback
            self.member_both_radio.setChecked(True)
        
        # Repo name options
        self.include_group_check.setChecked(course.get("include_group", True))
        self.include_member_check.setChecked(course.get("include_member", True))
        self.include_initials_check.setChecked(course.get("include_initials", False))
        
        # Filters
        self.full_groups_check.setChecked(course.get("full_groups", True))
        
        # Update initials state
        self.update_initials_state()
    
    def update_initials_state(self):
        """Update initials checkbox state"""
        enabled = self.include_member_check.isChecked()
        self.include_initials_check.setEnabled(enabled)
        if not enabled:
            self.include_initials_check.setChecked(False)
    
    def update_url_edit_state(self):
        """Update URL edit button state"""
        is_custom = self.url_combo.currentText() == "Custom"
        self.edit_url_btn.setEnabled(is_custom)
    
    def browse_output_folder(self):
        """Browse for output folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            self.output_folder_edit.text()
        )
        if folder:
            self.output_folder_edit.setText(folder)
            self.course_manager.update_course_setting("info_file_folder", folder)
    
    def course_changed(self, course_title: str):
        """Handle course selection change"""
        if course_title:
            course_id = self.course_manager.parse_course_id(course_title)
            self.course_manager.set_current_course(course_id)
            self.update_ui_from_course()
    
    def new_course(self):
        """Create new course"""
        course_id, ok = QInputDialog.getText(
            self,
            "New Course",
            "Enter Course ID:",
            text="00001"
        )
        
        if ok and course_id:
            if self.course_manager.validate_course_id(course_id):
                self.course_manager.create_course(course_id)
                self.course_manager.set_current_course(course_id)
                self.load_current_course()
                self.log_message(f"Created new course: {course_id}")
            else:
                QMessageBox.warning(
                    self,
                    "Invalid Course ID",
                    "Please enter a valid numeric course ID that doesn't already exist."
                )
    
    def delete_course(self):
        """Delete current course"""
        current_course = self.course_combo.currentText()
        
        reply = QMessageBox.question(
            self,
            "Delete Course",
            f"Are you sure you want to delete {current_course}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.course_manager.delete_course(self.course_manager.current_course_id)
            self.load_current_course()
            self.log_message(f"Deleted course: {current_course}")
    
    def url_option_changed(self, option: str):
        """Handle URL option change"""
        self.course_manager.update_course_setting("url_option", option)
        
        # Update base URL
        url = self.course_manager.get_url_for_option(option)
        self.base_url_edit.setText(url)
        self.course_manager.update_course_setting("base_url", url)
        
        self.update_url_edit_state()
    
    def edit_url(self):
        """Edit base URL"""
        url, ok = QInputDialog.getText(
            self,
            "Edit Base URL",
            "Enter Base URL:",
            text=self.base_url_edit.text()
        )
        
        if ok and url:
            self.base_url_edit.setText(url)
            self.course_manager.update_course_setting("base_url", url)
            
            # Update URL option
            option = self.url_combo.currentText()
            self.course_manager.update_url_option(option, url)
    
    def edit_token(self):
        """Edit access token"""
        token, ok = QInputDialog.getText(
            self,
            "Edit Access Token",
            "Enter Access Token:",
            text=self.access_token_edit.text()
        )
        
        if ok and token:
            self.access_token_edit.setText(token)
            self.course_manager.update_course_setting("access_token", token)
    
    def verify_course(self):
        """Verify course settings"""
        course = self.course_manager.get_current_course()
        
        if not course.get("access_token"):
            QMessageBox.warning(self, "Missing Token", "Please set an access token first.")
            return
        
        if not course.get("base_url"):
            QMessageBox.warning(self, "Missing URL", "Please set a base URL first.")
            return
        
        self.log_message("Verifying course...")
        self.start_worker("verify")
    
    def execute_command(self):
        """Execute the main command"""
        course = self.course_manager.get_current_course()
        
        # Validate required fields
        if not course.get("access_token"):
            QMessageBox.warning(self, "Missing Token", "Please set an access token first.")
            return
        
        if not course.get("base_url"):
            QMessageBox.warning(self, "Missing URL", "Please set a base URL first.")
            return
        
        # Check if at least one output file is selected
        if not (self.csv_check.isChecked() or self.xlsx_check.isChecked() or 
                self.yaml_check.isChecked() or self.teammates_check.isChecked()):
            QMessageBox.warning(self, "No Output", "Please select at least one output file.")
            return
        
        # Validate output folder
        output_folder = self.output_folder_edit.text()
        if not output_folder or not Path(output_folder).exists():
            QMessageBox.warning(self, "Invalid Folder", "Please select a valid output folder.")
            return
        
        # Check if at least one option is selected
        if not (self.include_group_check.isChecked() or self.include_member_check.isChecked() or 
                self.include_initials_check.isChecked()):
            QMessageBox.warning(self, "No Options", "Please select at least one repo name option.")
            return
        
        # Update course settings from UI
        self.save_ui_to_course()
        
        self.log_message("Executing command...")
        self.start_worker("execute")
    
    def save_ui_to_course(self):
        """Save UI state to course settings"""
        output_folder = self.output_folder_edit.text()
        yaml_filename = self.yaml_filename_edit.text()
        
        settings = {
            "info_file_folder": output_folder,
            "csv": self.csv_check.isChecked(),
            "xlsx": self.xlsx_check.isChecked(),
            "teammates": self.teammates_check.isChecked(),
            "yaml": self.yaml_check.isChecked(),
            "students_file": str(Path(output_folder) / yaml_filename) if yaml_filename else "",
            "include_group": self.include_group_check.isChecked(),
            "include_member": self.include_member_check.isChecked(),
            "include_initials": self.include_initials_check.isChecked(),
            "full_groups": self.full_groups_check.isChecked(),
            "base_url": self.base_url_edit.text(),
            "access_token": self.access_token_edit.text(),
            "url_option": self.url_combo.currentText(),
        }
        
        # Member option
        if self.member_both_radio.isChecked():
            settings["member_option"] = "(email, gitid)"
        elif self.member_email_radio.isChecked():
            settings["member_option"] = "email"
        elif self.member_git_radio.isChecked():
            settings["member_option"] = "git_id"
        else:
            settings["member_option"] = "(email, gitid)"  # Default fallback
        
        # Update course settings
        for key, value in settings.items():
            self.course_manager.update_course_setting(key, value)
    
    def start_worker(self, operation: str):
        """Start background worker thread"""
        # Clean up any existing thread first
        if self.worker_thread is not None:
            try:
                if self.worker_thread.isRunning():
                    self.worker_thread.quit()
                    self.worker_thread.wait()
            except RuntimeError:
                # Thread already deleted, ignore
                pass
            finally:
                self.worker_thread = None
                self.worker = None
        
        # Create new thread and worker
        self.worker_thread = QThread()
        self.worker = CanvasWorker(self.course_manager, operation)
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        # Connect to our slots
        self.worker.message.connect(self.log_message)
        self.worker.progress.connect(self.update_progress)
        self.worker.course_verified.connect(self.on_course_verified)
        self.worker.finished.connect(self.on_worker_finished)
        
        # Clean up references when thread finishes
        self.worker_thread.finished.connect(self.cleanup_thread)
        
        # Disable UI during operation
        self.set_ui_enabled(False)
        self.show_progress(True)
        
        self.worker_thread.start()
    
    def cleanup_thread(self):
        """Clean up thread references"""
        self.worker_thread = None
        self.worker = None
    
    def on_course_verified(self, course_name: str):
        """Handle course verification result"""
        if course_name:
            self.course_manager.update_course_name(course_name)
            self.load_current_course()
            self.log_message("Course verified successfully")
        else:
            self.log_message("Course verification failed")
    
    def on_worker_finished(self):
        """Handle worker finished"""
        self.set_ui_enabled(True)
        self.show_progress(False)
        self.log_message("Operation completed")
    
    def set_ui_enabled(self, enabled: bool):
        """Enable/disable UI elements"""
        self.execute_btn.setEnabled(enabled)
        self.verify_btn.setEnabled(enabled)
        self.new_course_btn.setEnabled(enabled)
        self.delete_course_btn.setEnabled(enabled)
        self.edit_url_btn.setEnabled(enabled and self.url_combo.currentText() == "Custom")
        self.edit_token_btn.setEnabled(enabled)
        self.output_folder_browse.setEnabled(enabled)
    
    def show_progress(self, show: bool):
        """Show/hide progress bar"""
        self.progress_bar.setVisible(show)
        self.progress_label.setVisible(show)
        if not show:
            self.progress_bar.setValue(0)
            self.progress_label.setText("0%")
    
    def update_progress(self, value: int, maximum: int):
        """Update progress bar"""
        if maximum > 0:
            percent = int(100 * value / maximum)
            self.progress_bar.setValue(percent)
            self.progress_label.setText(f"{percent}%")
    
    def log_message(self, message: str):
        """Log message to output area"""
        self.output_text.append(message)
        self.output_text.ensureCursorVisible()
    
    def clear_output(self):
        """Clear output text"""
        self.output_text.clear()
    
    def show_help(self):
        """Show help information"""
        help_text = """
Canvas Info Help

Step 1: Canvas Authentication
- Set your Canvas base URL (usually https://canvas.tue.nl for TUE)
- Enter your Canvas access token
- Generate token: Canvas > Account > Settings > New Access Token

Step 2: Course Selection
- Click "Verify Course" to test your credentials
- Select a course from the dropdown
- Create new courses or delete existing ones

Step 3: File Generation
- Choose output folder for all generated files
- Select which file types to generate
- Configure member identification and repository naming options

For more information, visit the documentation.
        """
        QMessageBox.information(self, "Help", help_text)
    
    def close_application(self):
        """Close the application"""
        self.window().close()
    
    def cleanup(self):
        """Cleanup resources"""
        if self.worker_thread is not None:
            try:
                if self.worker_thread.isRunning():
                    self.worker_thread.quit()
                    self.worker_thread.wait(5000)  # Wait up to 5 seconds
                    if self.worker_thread.isRunning():
                        self.worker_thread.terminate()
                        self.worker_thread.wait()
            except RuntimeError:
                # Thread already deleted, ignore
                pass
            finally:
                self.worker_thread = None
                self.worker = None
        
        self.settings.sync()