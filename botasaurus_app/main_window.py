"""
Main Window for Botasaurus Desktop App
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QLineEdit,
    QTextEdit, QListWidget, QMessageBox, QInputDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QGroupBox, QComboBox, QFileDialog
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QColor
from profile_manager import ProfileManager
from scraper_runner import ScraperRunner, ScraperThread, CheckProxyThread, MexcAuthThread
import json
import time


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.profile_manager = ProfileManager()
        self.scraper_runner = ScraperRunner(self.profile_manager)
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Botasaurus - Browser Automation & Profiles")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Header
        header = QLabel("🤖 Botasaurus Desktop App")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Create tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_profiles_tab(), "📁 Profiles")
        self.tabs.addTab(self.create_scraper_tab(), "🚀 Run Scraper")
        self.tabs.addTab(self.create_results_tab(), "📊 Results")

        layout.addWidget(self.tabs)

        # Status bar
        self.statusBar().showMessage("Ready")

    def create_profiles_tab(self):
        """Create the profiles management tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = QLabel("Manage Browser Profiles")
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)

        # Profile list
        list_label = QLabel("Available Profiles:")
        layout.addWidget(list_label)

        self.profile_list = QListWidget()
        self.refresh_profile_list()
        layout.addWidget(self.profile_list)

        # Buttons - Row 1
        btn_layout1 = QHBoxLayout()

        create_btn = QPushButton("➕ Create New Profile")
        create_btn.clicked.connect(self.create_new_profile)
        btn_layout1.addWidget(create_btn)

        delete_btn = QPushButton("🗑️ Delete Selected Profile")
        delete_btn.clicked.connect(self.delete_selected_profile)
        btn_layout1.addWidget(delete_btn)

        info_btn = QPushButton("ℹ️ Profile Info")
        info_btn.clicked.connect(self.show_profile_info)
        btn_layout1.addWidget(info_btn)

        layout.addLayout(btn_layout1)

        # Buttons - Row 2 (Import)
        btn_layout2 = QHBoxLayout()

        import_btn = QPushButton("📥 Import Profiles from Excel")
        import_btn.clicked.connect(self.import_profiles_from_excel)
        import_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 8px;")
        btn_layout2.addWidget(import_btn)

        layout.addLayout(btn_layout2)

        # Buttons - Row 3 (Check Proxy & Record Actions)
        btn_layout3 = QHBoxLayout()

        check_proxy_btn = QPushButton("🔍 Check Proxy (whatismyip.com)")
        check_proxy_btn.clicked.connect(self.check_selected_profile_proxy)
        check_proxy_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")
        btn_layout3.addWidget(check_proxy_btn)

        record_actions_btn = QPushButton("🎬 Record Actions (Playwright)")
        record_actions_btn.clicked.connect(self.record_actions_for_profile)
        record_actions_btn.setStyleSheet("background-color: #FF5722; color: white; font-weight: bold; padding: 8px;")
        btn_layout3.addWidget(record_actions_btn)

        layout.addLayout(btn_layout3)

        # Row 4: MEXC Auth button
        btn_layout4 = QHBoxLayout()

        mexc_auth_btn = QPushButton("🔐 MEXC Auth (Login)")
        mexc_auth_btn.clicked.connect(self.mexc_auth_for_profile)
        mexc_auth_btn.setStyleSheet("background-color: #9C27B0; color: white; font-weight: bold; padding: 8px;")
        btn_layout4.addWidget(mexc_auth_btn)

        layout.addLayout(btn_layout4)

        # Profile details
        self.profile_details = QTextEdit()
        self.profile_details.setReadOnly(True)
        self.profile_details.setMaximumHeight(150)
        self.profile_details.setPlaceholderText("Select a profile to view details...")
        layout.addWidget(QLabel("Profile Details:"))
        layout.addWidget(self.profile_details)

        # Connect selection change
        self.profile_list.currentItemChanged.connect(self.on_profile_selected)

        return widget

    def create_scraper_tab(self):
        """Create the scraper runner tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = QLabel("Run Web Scraper with Profile")
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)

        # Profile selection
        profile_group = QGroupBox("Select Profile")
        profile_layout = QVBoxLayout()

        self.profile_combo = QComboBox()
        self.refresh_profile_combo()
        profile_layout.addWidget(self.profile_combo)

        profile_group.setLayout(profile_layout)
        layout.addWidget(profile_group)

        # URL input
        url_group = QGroupBox("Target URL")
        url_layout = QVBoxLayout()

        url_hint = QLabel("💡 Tip: You can enter 'example.com' or 'https://example.com'")
        url_hint.setStyleSheet("color: #888; font-size: 10px;")
        url_layout.addWidget(url_hint)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("example.com or https://example.com")
        self.url_input.setText("mexc.com")
        url_layout.addWidget(self.url_input)

        url_group.setLayout(url_layout)
        layout.addWidget(url_group)

        # Scraper options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()

        self.headless_combo = QComboBox()
        self.headless_combo.addItems(["Visible Browser", "Headless Mode"])
        options_layout.addWidget(QLabel("Browser Mode:"))
        options_layout.addWidget(self.headless_combo)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Run button
        self.run_btn = QPushButton("▶️ Run Scraper")
        self.run_btn.setMinimumHeight(50)
        self.run_btn.clicked.connect(self.run_scraper)
        layout.addWidget(self.run_btn)

        # Log output
        layout.addWidget(QLabel("Log Output:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(200)
        layout.addWidget(self.log_output)

        layout.addStretch()

        return widget

    def create_results_tab(self):
        """Create the results viewer tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = QLabel("Scraping Results")
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["URL", "Title", "Heading", "Proxy Used"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.results_table)

        # Buttons
        btn_layout = QHBoxLayout()

        clear_btn = QPushButton("🗑️ Clear Results")
        clear_btn.clicked.connect(self.clear_results)
        btn_layout.addWidget(clear_btn)

        export_btn = QPushButton("💾 Export to JSON")
        export_btn.clicked.connect(self.export_results)
        btn_layout.addWidget(export_btn)

        layout.addLayout(btn_layout)

        return widget

    def refresh_profile_list(self):
        """Refresh the profile list widget"""
        self.profile_list.clear()
        profiles = self.profile_manager.get_all_profiles()
        self.profile_list.addItems(profiles)

    def refresh_profile_combo(self):
        """Refresh the profile combo box"""
        self.profile_combo.clear()
        profiles = self.profile_manager.get_all_profiles()
        if profiles:
            self.profile_combo.addItems(profiles)
        else:
            self.profile_combo.addItem("No profiles available")

    def create_new_profile(self):
        """Create a new browser profile"""
        name, ok = QInputDialog.getText(
            self,
            "Create Profile",
            "Enter profile name:"
        )

        if ok and name:
            description, ok2 = QInputDialog.getText(
                self,
                "Create Profile",
                "Enter profile description (optional):"
            )

            success, message = self.profile_manager.create_profile(
                name,
                description if ok2 else ""
            )

            if success:
                QMessageBox.information(self, "Success", message)
                self.refresh_profile_list()
                self.refresh_profile_combo()
                self.log(f"✅ Created profile: {name}")
            else:
                QMessageBox.warning(self, "Error", message)

    def delete_selected_profile(self):
        """Delete the selected profile"""
        current_item = self.profile_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a profile to delete")
            return

        profile_name = current_item.text()

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete profile '{profile_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success, message = self.profile_manager.delete_profile(profile_name)
            if success:
                QMessageBox.information(self, "Success", message)
                self.refresh_profile_list()
                self.refresh_profile_combo()
                self.profile_details.clear()
                self.log(f"🗑️ Deleted profile: {profile_name}")
            else:
                QMessageBox.warning(self, "Error", message)

    def show_profile_info(self):
        """Show detailed info about selected profile"""
        current_item = self.profile_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a profile")
            return

        profile_name = current_item.text()
        info = self.profile_manager.get_profile_info(profile_name)

        if info:
            info_text = f"""
Profile Name: {info['name']}
Description: {info.get('description', 'N/A')}
Email: {info.get('email', 'N/A')}
Password: {'***' if info.get('password') else 'N/A'}
Proxy: {info.get('proxy', 'N/A')}
2FA Secret: {'***' if info.get('twofa_secret') else 'N/A'}
Created: {info['created_at']}
Last Used: {info.get('last_used', 'Never')}
Path: {info['path']}
            """
            QMessageBox.information(self, "Profile Info", info_text)

    def import_profiles_from_excel(self):
        """Import profiles from Excel file"""
        # Open file dialog to select Excel file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Excel File",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*)"
        )

        if not file_path:
            return  # User cancelled

        # Confirm import
        reply = QMessageBox.question(
            self,
            "Confirm Import",
            f"Import profiles from:\n{file_path}\n\nExpected format:\nRow 1: email | password | proxy | 2fa_secret\nRow 2+: data\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Show progress message
        self.statusBar().showMessage("Importing profiles from Excel...")
        self.log("📥 Starting Excel import...")

        try:
            # Import profiles
            success_count, skipped_count, errors = self.profile_manager.import_from_excel(file_path)

            # Refresh profile list
            self.refresh_profile_list()
            self.refresh_profile_combo()

            # Build result message
            result_msg = f"""
Import Complete!

✅ Successfully imported: {success_count} profiles
⚠️ Skipped: {skipped_count} profiles

"""

            if errors:
                result_msg += "Errors/Warnings:\n"
                # Show only first 10 errors
                for error in errors[:10]:
                    result_msg += f"• {error}\n"
                if len(errors) > 10:
                    result_msg += f"\n... and {len(errors) - 10} more"

            # Show result
            if success_count > 0:
                QMessageBox.information(self, "Import Complete", result_msg)
                self.log(f"✅ Imported {success_count} profiles successfully!")
            else:
                QMessageBox.warning(self, "Import Failed", result_msg)
                self.log("❌ No profiles were imported")

            self.statusBar().showMessage(f"Import complete: {success_count} imported, {skipped_count} skipped")

        except Exception as e:
            error_msg = f"Failed to import profiles:\n{str(e)}"
            QMessageBox.critical(self, "Import Error", error_msg)
            self.log(f"❌ Import error: {str(e)}")
            self.statusBar().showMessage("Import failed")

    def on_profile_selected(self, current, previous):
        """Handle profile selection change"""
        if current:
            profile_name = current.text()
            info = self.profile_manager.get_profile_info(profile_name)

            if info:
                # Show password/2FA as masked if present
                password_display = '***' if info.get('password') else 'N/A'
                twofa_display = '***' if info.get('twofa_secret') else 'N/A'

                details = f"""
<b>Profile:</b> {info['name']}<br>
<b>Description:</b> {info.get('description', 'N/A')}<br>
<b>Email:</b> {info.get('email', 'N/A')}<br>
<b>Password:</b> {password_display}<br>
<b>Proxy:</b> {info.get('proxy', 'N/A')}<br>
<b>2FA Secret:</b> {twofa_display}<br>
<b>Created:</b> {info['created_at']}<br>
<b>Last Used:</b> {info.get('last_used', 'Never')}<br>
<b>Path:</b> {info['path']}
                """
                self.profile_details.setHtml(details)

    def run_scraper(self):
        """Run the scraper with selected profile"""
        profile_name = self.profile_combo.currentText()
        url = self.url_input.text().strip()

        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL")
            return

        if profile_name == "No profiles available":
            QMessageBox.warning(self, "Warning", "Please create a profile first")
            return

        headless = self.headless_combo.currentIndex() == 1

        self.log(f"🚀 Starting scraper with profile: {profile_name}")
        self.log(f"🌐 Target URL: {url}")
        self.log(f"👁️ Mode: {'Headless' if headless else 'Visible'}")

        self.run_btn.setEnabled(False)
        self.statusBar().showMessage("Scraping in progress...")

        # Run scraper in thread
        self.scraper_thread = ScraperThread(
            self.scraper_runner,
            profile_name,
            url,
            headless
        )
        self.scraper_thread.finished.connect(self.on_scraper_finished)
        self.scraper_thread.log_signal.connect(self.log)
        self.scraper_thread.start()

    def on_scraper_finished(self, success, result):
        """Handle scraper completion"""
        self.run_btn.setEnabled(True)

        if success:
            self.log("✅ Scraping completed successfully!")
            self.statusBar().showMessage("Scraping completed")
            self.add_result_to_table(result)
            self.tabs.setCurrentIndex(2)  # Switch to results tab
        else:
            self.log(f"❌ Scraping failed: {result}")
            self.statusBar().showMessage("Scraping failed")
            QMessageBox.warning(self, "Error", f"Scraping failed: {result}")

    def add_result_to_table(self, result):
        """Add scraping result to results table"""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)

        self.results_table.setItem(row, 0, QTableWidgetItem(result.get("url", "")))
        self.results_table.setItem(row, 1, QTableWidgetItem(result.get("title", "")))
        self.results_table.setItem(row, 2, QTableWidgetItem(result.get("heading", "")))
        self.results_table.setItem(row, 3, QTableWidgetItem(result.get("proxy_used", "No proxy")))

    def clear_results(self):
        """Clear all results from table"""
        self.results_table.setRowCount(0)
        self.log("🗑️ Results cleared")

    def export_results(self):
        """Export results to JSON file"""
        if self.results_table.rowCount() == 0:
            QMessageBox.warning(self, "Warning", "No results to export")
            return

        results = []
        for row in range(self.results_table.rowCount()):
            results.append({
                "url": self.results_table.item(row, 0).text(),
                "title": self.results_table.item(row, 1).text(),
                "heading": self.results_table.item(row, 2).text(),
                "proxy_used": self.results_table.item(row, 3).text() if self.results_table.item(row, 3) else "No proxy"
            })

        import datetime
        filename = f"results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = Path.home() / "Desktop" / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        QMessageBox.information(self, "Success", f"Results exported to:\n{filepath}")
        self.log(f"💾 Exported results to: {filepath}")

    def check_selected_profile_proxy(self):
        """Check proxy IP for selected profile"""
        current_item = self.profile_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a profile to check")
            return

        profile_name = current_item.text()

        # Check if profile has proxy
        profile_info = self.profile_manager.get_profile_info(profile_name)
        if not profile_info or not profile_info.get('proxy'):
            QMessageBox.warning(
                self,
                "No Proxy",
                f"Profile '{profile_name}' does not have a proxy configured.\n\nAdd a proxy to the profile first."
            )
            return

        # Show confirmation
        reply = QMessageBox.question(
            self,
            "Check Proxy",
            f"Check proxy for profile: {profile_name}\n\nThis will:\n1. Open browser with proxy\n2. Navigate to whatismyip.com\n3. Wait 4 seconds\n4. Compare proxy IP with detected IP\n\nContinue?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Clear log
        self.log_output.clear()
        self.log(f"🔍 Checking proxy for profile: {profile_name}")

        # Start proxy check in thread
        self.check_thread = CheckProxyThread(
            self.scraper_runner,
            profile_name,
            headless=False  # Always visible for manual verification
        )
        self.check_thread.finished.connect(self.on_proxy_check_finished)
        self.check_thread.log_signal.connect(self.log)
        self.check_thread.start()

        self.statusBar().showMessage("Checking proxy...")

    def on_proxy_check_finished(self, success, result):
        """Handle proxy check completion"""
        if success:
            # Show result popup
            if result['is_match']:
                message = f"✅ Proxy is similar!\n\n"
                message += f"Proxy IP: {result['proxy_ip']}\n"
                message += f"Detected IP: {result['detected_ip']}\n\n"
                message += f"The proxy is working correctly!"
                title = "✅ Proxy Verified"
                icon = QMessageBox.Information
            else:
                message = f"⚠️ Proxy IP mismatch!\n\n"
                message += f"Expected IP (from proxy): {result['proxy_ip']}\n"
                message += f"Detected IP (from site): {result['detected_ip']}\n\n"
                message += f"The proxy might not be working correctly."
                title = "⚠️ Proxy Mismatch"
                icon = QMessageBox.Warning

            # Create message box
            msg_box = QMessageBox(self)
            msg_box.setIcon(icon)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.Ok)

            # Show the dialog and wait for OK
            msg_box.exec()

            # After user clicks OK, wait 5 seconds then log
            self.log("💡 User clicked OK")
            self.log("⏳ Waiting 5 seconds before finishing...")

            # Use QTimer to wait 5 seconds
            QTimer.singleShot(5000, lambda: self.after_proxy_check_delay())

            self.statusBar().showMessage("Proxy check completed")
        else:
            QMessageBox.critical(
                self,
                "Proxy Check Error",
                f"Failed to check proxy:\n\n{result}"
            )
            self.statusBar().showMessage("Proxy check failed")

    def after_proxy_check_delay(self):
        """Called after 5 second delay following proxy check"""
        self.log("✅ Proxy check complete!")
        self.log("💡 Browser window left open - close manually when done")

    def record_actions_for_profile(self):
        """Launch YOUR real Chrome browser with YOUR Chrome profile for element inspection"""
        current_item = self.profile_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a profile to inspect elements")
            return

        profile_name = current_item.text()

        # Ask for URL to navigate to
        url, ok = QInputDialog.getText(
            self,
            "Inspect Elements",
            f"Enter URL to navigate and inspect elements:\n(Botasaurus Profile: {profile_name})",
            text="https://www.whatismyip.com/"
        )

        if not ok or not url.strip():
            return

        # Ask for Chrome profile name (optional)
        chrome_profile, ok = QInputDialog.getText(
            self,
            "Chrome Profile",
            "Enter Chrome profile directory name:\n\n"
            "Common profiles:\n"
            "• 'Default' - first/main profile\n"
            "• 'Profile 1' - second profile\n"
            "• 'Profile 2' - third profile\n\n"
            "To find your profile: open Chrome → chrome://version/\n"
            "Look at 'Profile Path' line",
            text="Profile 1"
        )

        if not ok:
            return

        # Show confirmation
        message = f"Launch YOUR real Chrome browser\n\n"
        message += f"URL: {url}\n"
        if chrome_profile.strip():
            message += f"Chrome Profile: {chrome_profile}\n"
        else:
            message += f"Chrome Profile: Default\n"
        message += "\n"
        message += "This will:\n"
        message += "1. Open YOUR real Chrome browser\n"
        message += "2. Load YOUR Chrome profile (cookies, logins, history)\n"
        message += "3. Navigate to the URL\n"
        message += "4. Enable Remote Debugging\n"
        message += "5. You use F12 DevTools to inspect elements\n\n"
        message += "✅ Real Chrome + Your profile = NO DETECTION!\n"
        message += "✅ Captchas WILL work!\n"
        message += "✅ Your cookies already loaded!\n\n"
        message += "Continue?"

        reply = QMessageBox.question(
            self,
            "Launch Chrome",
            message,
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Clear log
        self.log_output.clear()
        self.log(f"🎬 Launching YOUR real Chrome browser")
        self.log(f"🌐 URL: {url}")
        if chrome_profile.strip():
            self.log(f"👤 Chrome Profile: {chrome_profile}")
        else:
            self.log(f"👤 Chrome Profile: Default")

        # Launch real Chrome browser with user's profile
        try:
            import subprocess
            import sys
            import os

            # Find Chrome executable
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            ]

            chrome_exe = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_exe = path
                    break

            if not chrome_exe:
                raise FileNotFoundError("Chrome browser not found! Please install Google Chrome.")

            self.log(f"✅ Found Chrome: {chrome_exe}")

            # Build Chrome command
            cmd_parts = [chrome_exe]

            # Add profile directory
            if chrome_profile.strip():
                cmd_parts.append(f'--profile-directory={chrome_profile.strip()}')
                self.log(f"✅ Using profile: {chrome_profile.strip()}")
            else:
                self.log(f"✅ Using Default profile")

            # Add remote debugging for DevTools access
            cmd_parts.append("--remote-debugging-port=9222")

            # Add new window flag
            cmd_parts.append("--new-window")

            # Add URL
            cmd_parts.append(url)

            self.log("🚀 Launching YOUR real Chrome browser...")
            self.log(f"📝 Command: {' '.join(cmd_parts)}")

            # Launch Chrome directly
            subprocess.Popen(cmd_parts)

            self.log("✅ Chrome browser launched successfully!")
            self.log("")
            self.log("💡 How to inspect elements:")
            self.log("   1. Chrome opened with YOUR profile (cookies loaded!)")
            self.log("   2. Press F12 to open Chrome DevTools")
            self.log("   3. Click 'Elements' tab")
            self.log("   4. Click the 'Select element' icon (Ctrl+Shift+C)")
            self.log("   5. Click on any element on the page")
            self.log("   6. Right-click in HTML → Copy → Copy selector")
            self.log("")
            self.log("🎯 Alternative methods to get selectors:")
            self.log("   • Copy CSS selector")
            self.log("   • Copy XPath")
            self.log("   • Copy JS path")
            self.log("")
            self.log("🛡️ Using YOUR real Chrome profile:")
            self.log("   ✅ Your cookies are loaded")
            self.log("   ✅ Your logins are available")
            self.log("   ✅ Captchas WILL work!")
            self.log("   ✅ No automation detection!")
            self.log("")
            self.log("💡 Remote debugging enabled on port 9222")
            self.log("💡 Close the browser window when done")

            self.statusBar().showMessage("Chrome browser launched with your profile")

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()

            QMessageBox.critical(
                self,
                "Launch Error",
                f"Failed to launch Chrome browser:\n\n{str(e)}\n\n"
                f"Make sure:\n"
                f"1. Google Chrome is installed\n"
                f"2. Chrome profile name is correct\n"
                f"   (Check chrome://version/ in Chrome to see profile path)"
            )
            self.log(f"❌ Error: {str(e)}")
            self.log(f"📋 Details: {error_details}")
            self.statusBar().showMessage("Failed to launch Chrome")

    def mexc_auth_for_profile(self):
        """Perform MEXC login automation with Botasaurus"""
        current_item = self.profile_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a profile for MEXC login")
            return

        profile_name = current_item.text()

        # Get profile info to get credentials from Excel
        profile_info = self.profile_manager.get_profile_info(profile_name)

        if not profile_info:
            QMessageBox.warning(self, "Warning", f"Profile {profile_name} not found!")
            return

        # Get credentials from profile
        email = profile_info.get('email', '').strip()
        password = profile_info.get('password', '').strip()
        secret = profile_info.get('twofa_secret', '').strip()  # Saved as 'twofa_secret' in profile dict

        # Check if all required fields are present
        if not email:
            QMessageBox.warning(
                self,
                "Missing Email",
                f"Profile {profile_name} doesn't have Email configured!\n\n"
                "Please add Email in Excel file."
            )
            return

        if not password:
            QMessageBox.warning(
                self,
                "Missing Password",
                f"Profile {profile_name} doesn't have Password configured!\n\n"
                "Please add Password in Excel file."
            )
            return

        if not secret:
            QMessageBox.warning(
                self,
                "Missing 2FA Secret",
                f"Profile {profile_name} doesn't have 2FA Secret configured!\n\n"
                "Please add 2FA Secret in Excel file (column: 2fa_secret)."
            )
            return

        # Show confirmation
        message = f"Start MEXC login for profile: {profile_name}\n\n"
        message += f"📧 Email: {email}\n"
        message += f"🔑 Password: {'*' * len(password)}\n"
        message += f"🔐 2FA Secret: {'*' * len(secret)}\n"
        message += f"(Loaded from Excel)\n\n"
        message += "This will:\n"
        message += "1. Navigate to MEXC login page\n"
        message += "2. Enter email and password\n"
        message += "3. Handle captcha (you will be prompted)\n"
        message += "4. Generate and enter 2FA code automatically\n"
        message += "5. Complete login\n\n"
        message += "✅ Using Botasaurus anti-detection browser\n"
        message += "✅ Using profile's proxy (if configured)\n\n"
        message += "Continue?"

        reply = QMessageBox.question(
            self,
            "MEXC Login",
            message,
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Clear log
        self.log_output.clear()
        self.log(f"🔐 Starting MEXC login for profile: {profile_name}")
        self.log(f"📧 Email: {email}")
        self.log(f"🔑 Password: {'*' * len(password)}")
        self.log(f"🔐 2FA Secret: {'*' * len(secret)}")
        self.log(f"✅ Credentials loaded from Excel profile")

        # Launch MEXC auth in thread
        self.mexc_thread = MexcAuthThread(
            self.scraper_runner,
            profile_name,
            email,
            password,
            secret,
            headless=False
        )

        self.mexc_thread.log_signal.connect(self.log)
        self.mexc_thread.captcha_signal.connect(self.on_mexc_captcha)
        self.mexc_thread.finished.connect(self.on_mexc_finished)
        self.mexc_thread.start()

        self.statusBar().showMessage(f"MEXC login started for {profile_name}...")

    def on_mexc_captcha(self):
        """Handle captcha detection - pause and wait for user"""
        QMessageBox.warning(
            self,
            "Captcha Detected",
            "⚠️ Пройдите капчу в браузере!\n\n"
            "Нажмите OK после того как пройдете капчу.\n"
            "Скрипт подождет 10 секунд и продолжит работу."
        )

    def on_mexc_finished(self, success, result):
        """Handle MEXC auth completion"""
        if success:
            self.statusBar().showMessage("MEXC login completed successfully")
            self.log("✅ MEXC login completed!")
        else:
            self.statusBar().showMessage("MEXC login failed")
            self.log(f"❌ Error: {result}")

    def log(self, message):
        """Add message to log output"""
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )
