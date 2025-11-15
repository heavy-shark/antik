"""
Hysk Mexc Futures - Main Window
Dark blue theme UI inspired by NaVI Blue design
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QCheckBox, QRadioButton,
    QButtonGroup, QMessageBox, QFileDialog, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QColor
from profile_manager import ProfileManager
from scraper_runner import ScraperRunner, ScraperThread, CheckProxyThread, MexcAuthThread
import json
import pyotp
import time


class MainWindow(QMainWindow):
    """Main application window with dark blue theme"""

    def __init__(self):
        super().__init__()
        self.profile_manager = ProfileManager()
        self.scraper_runner = ScraperRunner(self.profile_manager)
        self.version = "v0.01"
        self.totp_timers = {}  # Store TOTP update timers for each row
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface with dark blue theme"""
        self.setWindowTitle(f"Hysk Mexc Futures {self.version}")
        self.setGeometry(100, 100, 1400, 900)

        # Apply dark blue theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a1929;
            }
            QWidget {
                background-color: #0a1929;
                color: #ffffff;
                font-family: 'Segoe UI', Arial;
                font-size: 12px;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QPushButton#settingsBtn {
                background-color: #1e3a5f;
                padding: 8px 16px;
            }
            QPushButton#settingsBtn:hover {
                background-color: #2d4a6f;
            }
            QPushButton#importBtn {
                background-color: #1976d2;
            }
            QPushButton#openSelectedBtn {
                background-color: #1976d2;
            }
            QPushButton#closeSelectedBtn {
                background-color: #455a64;
            }
            QPushButton#closeSelectedBtn:hover {
                background-color: #546e7a;
            }
            QPushButton#clearLogBtn {
                background-color: #1e3a5f;
                padding: 6px 12px;
                font-size: 11px;
            }
            QTableWidget {
                background-color: #0d1b2a;
                border: 1px solid #1e3a5f;
                gridline-color: #1e3a5f;
                color: #ffffff;
            }
            QTableWidget QWidget {
                background-color: #0d1b2a;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #1e3a5f;
                height: 40px;
            }
            QTableWidget::item:selected {
                background-color: #1e3a5f;
            }
            QHeaderView::section {
                background-color: #0d1b2a;
                color: #64b5f6;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #1e3a5f;
                border-right: 1px solid #1e3a5f;
                font-weight: bold;
            }
            QTextEdit {
                background-color: #0d1b2a;
                border: 1px solid #1e3a5f;
                color: #4caf50;
                font-family: 'Consolas', 'Courier New', monospace;
                padding: 8px;
            }
            QRadioButton {
                color: #ffffff;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #1976d2;
                border-radius: 10px;
                background-color: #0d1b2a;
            }
            QRadioButton::indicator:checked {
                background-color: #1976d2;
                border: 2px solid #64b5f6;
            }
            QRadioButton::indicator:hover {
                border: 2px solid #64b5f6;
            }
            QCheckBox {
                spacing: 5px;
                background: none;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #1976d2;
                border-radius: 8px;
                background-color: rgba(0, 0, 0, 0);
            }
            QCheckBox::indicator:unchecked {
                background-color: rgba(0, 0, 0, 0);
                background: none;
            }
            QCheckBox::indicator:checked {
                background-color: #1976d2;
                border: 2px solid #1976d2;
            }
            QCheckBox::indicator:unchecked:hover {
                background-color: rgba(0, 0, 0, 0);
                border: 2px solid #64b5f6;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #1976d2;
                border: 2px solid #64b5f6;
            }
            QFrame#separator {
                background-color: #1e3a5f;
            }
        """)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === HEADER ===
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)

        # Content area with padding
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        # === PROFILES SECTION ===
        profiles_section = self.create_profiles_section()
        content_layout.addWidget(profiles_section)

        # === OPERATION MODE SECTION ===
        operation_section = self.create_operation_mode_section()
        content_layout.addWidget(operation_section)

        # === LOGS SECTION ===
        logs_section = self.create_logs_section()
        content_layout.addWidget(logs_section)

        main_layout.addWidget(content_widget)

        # Load profiles into table
        self.refresh_profiles_table()

    def create_header(self):
        """Create header with title and settings button"""
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet("background-color: #0d1b2a; border-bottom: 2px solid #1e3a5f;")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)

        # Title
        title = QLabel(f"Hysk Mexc Futures {self.version}")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #64b5f6;")

        layout.addWidget(title)
        layout.addStretch()

        # Delete Selected button (hidden by default)
        self.delete_selected_btn = QPushButton("🗑️ Delete Selected")
        self.delete_selected_btn.setObjectName("deleteSelectedBtn")
        self.delete_selected_btn.setStyleSheet("background-color: #d32f2f; padding: 8px 16px;")
        self.delete_selected_btn.clicked.connect(self.delete_selected_profiles)
        self.delete_selected_btn.setFixedWidth(150)
        self.delete_selected_btn.hide()  # Hidden by default

        layout.addWidget(self.delete_selected_btn)

        # Settings button
        settings_btn = QPushButton("⚙ Settings")
        settings_btn.setObjectName("settingsBtn")
        settings_btn.clicked.connect(self.open_settings)
        settings_btn.setFixedWidth(120)

        layout.addWidget(settings_btn)

        return header

    def create_profiles_section(self):
        """Create profiles table section"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setSpacing(15)

        # Section title
        title = QLabel("Profiles")
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #64b5f6;")
        layout.addWidget(title)

        # Profiles table
        self.profiles_table = QTableWidget()
        self.profiles_table.setColumnCount(5)
        self.profiles_table.setHorizontalHeaderLabels([
            "", "Email", "Proxy", "2FA Code", "Status"
        ])

        # Set column widths
        header = self.profiles_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # Select
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Email
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Proxy
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # 2FA Code
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # Status

        self.profiles_table.setColumnWidth(0, 50)  # Select (smaller)
        self.profiles_table.setColumnWidth(3, 150)  # 2FA Code
        self.profiles_table.setColumnWidth(4, 100)  # Status

        self.profiles_table.setMinimumHeight(250)
        self.profiles_table.setMaximumHeight(350)

        layout.addWidget(self.profiles_table)

        # Buttons row
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # Import button
        import_btn = QPushButton("📥 Import")
        import_btn.setObjectName("importBtn")
        import_btn.clicked.connect(self.import_profiles)
        import_btn.setFixedWidth(150)
        buttons_layout.addWidget(import_btn)

        buttons_layout.addStretch()

        # Open Selected button
        open_selected_btn = QPushButton("Open Selected")
        open_selected_btn.setObjectName("openSelectedBtn")
        open_selected_btn.clicked.connect(self.open_selected_profiles)
        open_selected_btn.setFixedWidth(150)
        buttons_layout.addWidget(open_selected_btn)

        # Close Selected button
        close_selected_btn = QPushButton("Close Selected")
        close_selected_btn.setObjectName("closeSelectedBtn")
        close_selected_btn.clicked.connect(self.close_selected_profiles)
        close_selected_btn.setFixedWidth(150)
        buttons_layout.addWidget(close_selected_btn)

        layout.addLayout(buttons_layout)

        return section

    def create_operation_mode_section(self):
        """Create operation mode section with radio buttons"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setSpacing(12)

        # Section title
        title = QLabel("Operation Mode")
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #64b5f6;")
        layout.addWidget(title)

        # Radio buttons layout
        radio_layout = QHBoxLayout()
        radio_layout.setSpacing(30)

        # Create button group
        self.operation_group = QButtonGroup()

        # Create radio buttons
        modes = [
            ("Login", "login"),
            ("Short", "short"),
            ("Long", "long"),
            ("Balance", "balance"),
            ("RK", "rk")
        ]

        for i, (label, value) in enumerate(modes):
            radio = QRadioButton(label)
            radio.setProperty("mode", value)
            self.operation_group.addButton(radio, i)
            radio_layout.addWidget(radio)

            # Select first option by default
            if i == 0:
                radio.setChecked(True)

        radio_layout.addStretch()
        layout.addLayout(radio_layout)

        return section

    def create_logs_section(self):
        """Create logs section"""
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setSpacing(10)

        # Header with title and clear button
        header_layout = QHBoxLayout()

        title = QLabel("Logs")
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #64b5f6;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        clear_btn = QPushButton("Clear Log")
        clear_btn.setObjectName("clearLogBtn")
        clear_btn.clicked.connect(self.clear_log)
        clear_btn.setFixedWidth(100)
        header_layout.addWidget(clear_btn)

        layout.addLayout(header_layout)

        # Log text area
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(150)
        self.log_output.setMaximumHeight(250)

        layout.addWidget(self.log_output)

        # Initial log message
        self.log("✓ Hysk Mexc Futures ready - You can now manage profiles")

        return section

    def refresh_profiles_table(self):
        """Refresh profiles table with data from profile manager"""
        # Stop all existing TOTP timers
        for timer in self.totp_timers.values():
            timer.stop()
        self.totp_timers.clear()

        # Clear table
        self.profiles_table.setRowCount(0)

        # Get all profiles
        profiles = self.profile_manager.get_all_profiles()

        for profile_name in profiles:
            profile_info = self.profile_manager.get_profile_info(profile_name)
            if not profile_info:
                continue

            row = self.profiles_table.rowCount()
            self.profiles_table.insertRow(row)

            # Set row height (30% bigger than default ~30px = ~40px)
            self.profiles_table.setRowHeight(row, 45)

            # Column 0: Select checkbox
            checkbox = QCheckBox()
            checkbox.setText("")
            checkbox.setStyleSheet("""
                QCheckBox {
                    background: none;
                    border: none;
                    padding: 0px;
                    margin: 0px;
                    margin-left: 7px;
                }
                QCheckBox::indicator {
                    width: 12px;
                    height: 12px;
                    border: 2px solid #1976d2;
                    border-radius: 6px;
                    background: none;
                }
                QCheckBox::indicator:unchecked {
                    background: none;
                }
                QCheckBox::indicator:checked {
                    background-color: #1976d2;
                }
                QCheckBox::indicator:hover {
                    border-color: #64b5f6;
                }
            """)

            self.profiles_table.setCellWidget(row, 0, checkbox)

            # Column 1: Email
            email = profile_info.get('email', 'N/A')
            email_item = QTableWidgetItem(email)
            email_item.setFlags(email_item.flags() & ~Qt.ItemIsEditable)
            self.profiles_table.setItem(row, 1, email_item)

            # Column 2: Proxy (extract IP only)
            proxy = profile_info.get('proxy', '')
            proxy_ip = self.extract_proxy_ip(proxy)
            proxy_item = QTableWidgetItem(proxy_ip)
            proxy_item.setFlags(proxy_item.flags() & ~Qt.ItemIsEditable)
            self.profiles_table.setItem(row, 2, proxy_item)

            # Column 3: 2FA Code (with countdown)
            twofa_secret = profile_info.get('twofa_secret', '')
            if twofa_secret:
                # Generate initial TOTP code
                totp_text = self.generate_totp_with_timer(twofa_secret)
                totp_item = QTableWidgetItem(totp_text)
                totp_item.setForeground(QColor("#64b5f6"))
                totp_item.setFlags(totp_item.flags() & ~Qt.ItemIsEditable)
                self.profiles_table.setItem(row, 3, totp_item)

                # Start timer to update TOTP every second
                timer = QTimer()
                timer.timeout.connect(lambda r=row, s=twofa_secret: self.update_totp_cell(r, s))
                timer.start(1000)  # Update every second
                self.totp_timers[row] = timer
            else:
                totp_item = QTableWidgetItem("—")
                totp_item.setFlags(totp_item.flags() & ~Qt.ItemIsEditable)
                self.profiles_table.setItem(row, 3, totp_item)

            # Column 4: Status
            status_item = QTableWidgetItem("Closed")
            status_item.setForeground(QColor("#ff9800"))
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            self.profiles_table.setItem(row, 4, status_item)

            # Connect checkbox to update delete button visibility
            checkbox.stateChanged.connect(self.update_delete_button_visibility)

    def extract_proxy_ip(self, proxy_string):
        """Extract IP address from proxy string"""
        if not proxy_string:
            return "—"

        # Format: socks5://user:pass@IP:PORT
        # Extract just the IP part
        try:
            if '@' in proxy_string:
                # Format: protocol://user:pass@IP:port
                ip_port = proxy_string.split('@')[1]
                ip = ip_port.split(':')[0]
                return ip
            else:
                return "Invalid proxy format"
        except:
            return proxy_string

    def generate_totp_with_timer(self, secret):
        """Generate TOTP code with remaining time"""
        try:
            totp = pyotp.TOTP(secret)
            code = totp.now()

            # Calculate remaining time
            import time
            current_time = int(time.time())
            time_remaining = 30 - (current_time % 30)

            return f"{code} ({time_remaining}s)"
        except:
            return "Invalid secret"

    def update_totp_cell(self, row, secret):
        """Update TOTP code in table cell"""
        try:
            totp_text = self.generate_totp_with_timer(secret)
            item = self.profiles_table.item(row, 3)
            if item:
                item.setText(totp_text)
        except:
            pass

    def get_selected_profile_rows(self):
        """Get list of selected profile rows"""
        selected_rows = []
        for row in range(self.profiles_table.rowCount()):
            checkbox = self.profiles_table.cellWidget(row, 0)
            if checkbox and isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                selected_rows.append(row)
        return selected_rows

    def update_delete_button_visibility(self):
        """Show/hide delete button based on selection"""
        selected_rows = self.get_selected_profile_rows()
        if selected_rows:
            self.delete_selected_btn.show()
        else:
            self.delete_selected_btn.hide()

    def delete_selected_profiles(self):
        """Delete all selected profiles"""
        selected_rows = self.get_selected_profile_rows()

        if not selected_rows:
            return

        # Get profile names for selected rows
        profiles_to_delete = []
        for row in selected_rows:
            email_item = self.profiles_table.item(row, 1)
            if email_item:
                email = email_item.text()

                # Find profile name by email
                profiles = self.profile_manager.get_all_profiles()
                for name in profiles:
                    info = self.profile_manager.get_profile_info(name)
                    if info and info.get('email') == email:
                        profiles_to_delete.append((name, email))
                        break

        if not profiles_to_delete:
            return

        # Confirm deletion
        profile_list = "\n".join([f"• {email}" for name, email in profiles_to_delete])
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete {len(profiles_to_delete)} selected profile(s)?\n\n{profile_list}\n\nThis cannot be undone!",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Delete all profiles
            deleted_count = 0
            for profile_name, email in profiles_to_delete:
                success, message = self.profile_manager.delete_profile(profile_name)
                if success:
                    self.log(f"🗑️ Deleted profile: {email}")
                    deleted_count += 1
                else:
                    self.log(f"❌ Failed to delete {email}: {message}")

            # Refresh table
            self.refresh_profiles_table()
            self.log(f"✅ Deleted {deleted_count} of {len(profiles_to_delete)} profile(s)")

            # Hide delete button
            self.delete_selected_btn.hide()

    # === BUTTON HANDLERS ===

    def open_settings(self):
        """Open settings dialog"""
        self.log("⚙ Settings clicked (functionality to be implemented)")
        QMessageBox.information(
            self,
            "Settings",
            "Settings functionality will be implemented in future version"
        )

    def import_profiles(self):
        """Import profiles from Excel"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel File",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )

        if not file_path:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Import",
            f"Import profiles from:\n{file_path}\n\nExpected format:\nRow 1: email | password | proxy | 2fa_secret\nRow 2+: data\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        self.log("📥 Starting Excel import...")

        try:
            success_count, skipped_count, errors = self.profile_manager.import_from_excel(file_path)

            self.refresh_profiles_table()

            result_msg = f"Import Complete!\n\n✅ Successfully imported: {success_count} profiles\n⚠️ Skipped: {skipped_count} profiles"

            if errors:
                result_msg += "\n\nErrors/Warnings:\n"
                for error in errors[:5]:
                    result_msg += f"• {error}\n"
                if len(errors) > 5:
                    result_msg += f"\n... and {len(errors) - 5} more"

            if success_count > 0:
                QMessageBox.information(self, "Import Complete", result_msg)
                self.log(f"✅ Imported {success_count} profiles successfully")
            else:
                QMessageBox.warning(self, "Import Failed", result_msg)
                self.log("❌ No profiles were imported")

        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import profiles:\n{str(e)}")
            self.log(f"❌ Import error: {str(e)}")

    def open_selected_profiles(self):
        """Open selected profiles"""
        selected_rows = self.get_selected_profile_rows()

        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select at least one profile")
            return

        self.log(f"🚀 Opening {len(selected_rows)} selected profile(s)...")

        # Placeholder - functionality to be implemented
        for row in selected_rows:
            email_item = self.profiles_table.item(row, 1)
            if email_item:
                self.log(f"  • Opening profile: {email_item.text()}")

        self.log("💡 Open functionality will be implemented in next version")

    def close_selected_profiles(self):
        """Close selected profiles"""
        selected_rows = self.get_selected_profile_rows()

        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select at least one profile")
            return

        self.log(f"🛑 Closing {len(selected_rows)} selected profile(s)...")

        # Placeholder - functionality to be implemented
        for row in selected_rows:
            email_item = self.profiles_table.item(row, 1)
            if email_item:
                self.log(f"  • Closing profile: {email_item.text()}")

        self.log("💡 Close functionality will be implemented in next version")

    def clear_log(self):
        """Clear log output"""
        self.log_output.clear()
        self.log("✓ Log cleared")

    def log(self, message):
        """Add message to log output"""
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )
