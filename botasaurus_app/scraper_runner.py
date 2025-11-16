"""
Scraper Runner
Integrates Botasaurus browser automation with profile management
"""
from PySide6.QtCore import QThread, Signal
import sys
import traceback
import re

# Only use installed botasaurus_driver package
try:
    from botasaurus_driver import Driver
except ImportError:
    print("Error: botasaurus_driver not found. Please install it:")
    print("pip install botasaurus-driver")
    sys.exit(1)


class ScraperRunner:
    def __init__(self, profile_manager):
        self.profile_manager = profile_manager

    def fix_url(self, url):
        """
        Fix URL by adding https:// if protocol is missing

        Args:
            url: URL string that might be missing protocol

        Returns:
            str: Properly formatted URL with protocol
        """
        url = url.strip()

        # If URL already has protocol, return as is
        if url.startswith('http://') or url.startswith('https://'):
            return url

        # Add https:// by default
        return f'https://{url}'

    def parse_proxy(self, proxy_string):
        """
        Parse proxy string and return properly formatted proxy for Driver

        Supports multiple formats:
        - Simple: "123.45.67.89:8080"
        - With protocol: "http://123.45.67.89:8080"
        - SOCKS5: "socks5://123.45.67.89:1080"
        - Authenticated: "username:password@123.45.67.89:8080"
        - Full: "http://username:password@123.45.67.89:8080"

        Args:
            proxy_string: Proxy configuration string

        Returns:
            str: Formatted proxy string for Driver, or None if invalid
        """
        if not proxy_string or proxy_string.strip() == "":
            return None

        proxy = proxy_string.strip()

        # If proxy already has protocol, return as is
        if proxy.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
            return proxy

        # Add http:// by default for proxies without protocol
        return f'http://{proxy}'

    def get_proxy_for_profile(self, profile_name):
        """
        Get proxy configuration for a profile

        Args:
            profile_name: Name of the profile

        Returns:
            tuple: (proxy_string, proxy_display) - formatted proxy and display text
        """
        profile_info = self.profile_manager.get_profile_info(profile_name)
        if not profile_info:
            return None, "No proxy"

        proxy_raw = profile_info.get('proxy', '')
        if not proxy_raw or proxy_raw.strip() == '':
            return None, "No proxy"

        proxy = self.parse_proxy(proxy_raw)
        if proxy:
            # Create display version (hide credentials if present)
            if '@' in proxy:
                # Has authentication - hide username:password
                parts = proxy.split('@')
                if len(parts) == 2:
                    protocol = parts[0].split('//')[0] if '//' in parts[0] else 'http:'
                    proxy_display = f"{protocol}//***@{parts[1]}"
                else:
                    proxy_display = proxy
            else:
                proxy_display = proxy

            return proxy, proxy_display

        return None, "Invalid proxy format"

    def scrape_page(self, profile_name, url, headless=False):
        """
        Scrape a page using Botasaurus browser with the specified profile

        Args:
            profile_name: Name of the browser profile to use
            url: URL to scrape
            headless: Whether to run in headless mode

        Returns:
            dict: Scraped data containing url, title, and heading
        """
        try:
            # Fix URL by adding https:// if missing
            url = self.fix_url(url)

            # Update last used timestamp
            self.profile_manager.update_last_used(profile_name)

            # Get proxy for profile (if configured)
            proxy, proxy_display = self.get_proxy_for_profile(profile_name)

            # Create driver configuration
            driver_config = {
                'profile': profile_name,
                'headless': headless
            }

            # Add proxy if configured
            if proxy:
                driver_config['proxy'] = proxy

            # Create driver with profile and proxy
            driver = Driver(**driver_config)

            # Navigate to URL
            driver.get(url)

            # Wait for page to load
            driver.sleep(2)

            # Extract data
            title = driver.title

            # Try to get h1 heading
            try:
                heading = driver.get_text("h1")
            except:
                heading = "No h1 found"

            result = {
                "url": url,
                "title": title,
                "heading": heading,
                "proxy_used": proxy_display if proxy else "No proxy"
            }

            # Keep browser open for manual interaction
            # User can close manually when done
            # driver.quit() - removed to keep browser open

            return True, result

        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            return False, error_msg

    def extract_ip_from_proxy(self, proxy_string):
        """
        Extract IP address from proxy string

        Args:
            proxy_string: Proxy string (e.g., "123.45.67.89:8080" or "http://user:pass@123.45.67.89:8080")

        Returns:
            str: IP address only, or None if can't extract
        """
        if not proxy_string:
            return None

        # Remove protocol if present
        proxy = proxy_string.replace('http://', '').replace('https://', '').replace('socks4://', '').replace('socks5://', '')

        # Remove authentication if present (username:password@)
        if '@' in proxy:
            proxy = proxy.split('@')[1]

        # Remove port if present
        if ':' in proxy:
            proxy = proxy.split(':')[0]

        # Validate it looks like an IP
        ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
        if ip_pattern.match(proxy.strip()):
            return proxy.strip()

        return None

    def check_proxy_ip(self, profile_name, headless=False):
        """
        Check if proxy IP matches the actual IP shown on whatismyip.com

        Args:
            profile_name: Name of the profile to check
            headless: Whether to run in headless mode

        Returns:
            tuple: (success, result_dict or error_message)
                result_dict contains: proxy_ip, detected_ip, is_match
        """
        try:
            # Get proxy for profile
            proxy, proxy_display = self.get_proxy_for_profile(profile_name)

            if not proxy:
                return False, "No proxy configured for this profile"

            # Extract expected IP from proxy
            expected_ip = self.extract_ip_from_proxy(proxy)
            if not expected_ip:
                return False, f"Could not extract IP from proxy: {proxy_display}"

            # Create driver configuration
            driver_config = {
                'profile': profile_name,
                'headless': headless
            }

            # Add proxy
            driver_config['proxy'] = proxy

            # Create driver with proxy
            driver = Driver(**driver_config)

            # Navigate to whatismyip.com
            driver.get("https://www.whatismyip.com/")

            # Wait 4 seconds for page to fully load
            driver.sleep(4)

            # Extract IP from page
            try:
                # The IP is displayed in a specific element on whatismyip.com
                # Try multiple selectors to find it
                detected_ip = None

                # Method 1: Try to find by common selectors
                try:
                    detected_ip = driver.get_text("#ipv4 > a")
                except:
                    pass

                if not detected_ip:
                    try:
                        detected_ip = driver.get_text("a[href^='/ip/']")
                    except:
                        pass

                if not detected_ip:
                    # Method 2: Get page text and search for IP pattern
                    page_text = driver.text
                    ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
                    ips_found = ip_pattern.findall(page_text)
                    if ips_found:
                        # Take the first IP found (usually the main one)
                        detected_ip = ips_found[0]

                if not detected_ip:
                    return False, "Could not extract IP from whatismyip.com"

                detected_ip = detected_ip.strip()

                # Compare IPs
                is_match = (expected_ip == detected_ip)

                result = {
                    "proxy_ip": expected_ip,
                    "detected_ip": detected_ip,
                    "is_match": is_match,
                    "proxy_display": proxy_display
                }

                # Keep browser open for 5 more seconds after user sees result
                # (will be handled by the UI thread)

                return True, result

            except Exception as e:
                return False, f"Error extracting IP from page: {str(e)}"

        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            return False, error_msg


class ScraperThread(QThread):
    """Thread for running scraper without blocking UI"""
    finished = Signal(bool, object)  # success, result/error
    log_signal = Signal(str)

    def __init__(self, scraper_runner, profile_name, url, headless=False):
        super().__init__()
        self.scraper_runner = scraper_runner
        self.profile_name = profile_name
        self.url = url
        self.headless = headless

    def run(self):
        """Run the scraper in background thread"""
        try:
            # Fix URL and log it
            fixed_url = self.scraper_runner.fix_url(self.url)
            if fixed_url != self.url:
                self.log_signal.emit(f"🔧 Auto-fixed URL: {self.url} → {fixed_url}")

            # Get proxy info for this profile
            proxy, proxy_display = self.scraper_runner.get_proxy_for_profile(self.profile_name)
            if proxy:
                self.log_signal.emit(f"🌐 Using proxy: {proxy_display}")
            else:
                self.log_signal.emit(f"🌐 No proxy configured (direct connection)")

            self.log_signal.emit("🔧 Initializing browser...")
            success, result = self.scraper_runner.scrape_page(
                self.profile_name,
                self.url,
                self.headless
            )

            if success:
                self.log_signal.emit(f"✅ Title: {result['title']}")
                self.log_signal.emit(f"✅ Heading: {result['heading']}")
                self.log_signal.emit(f"✅ Proxy used: {result.get('proxy_used', 'N/A')}")
                self.log_signal.emit(f"💡 Browser window left open - close manually when done")

            self.finished.emit(success, result)

        except Exception as e:
            error_msg = f"Thread error: {str(e)}\n{traceback.format_exc()}"
            self.log_signal.emit(f"❌ Error: {str(e)}")
            self.finished.emit(False, error_msg)


class CheckProxyThread(QThread):
    """Thread for checking proxy IP without blocking UI"""
    finished = Signal(bool, object)  # success, result/error
    log_signal = Signal(str)

    def __init__(self, scraper_runner, profile_name, headless=False):
        super().__init__()
        self.scraper_runner = scraper_runner
        self.profile_name = profile_name
        self.headless = headless

    def run(self):
        """Run the proxy check in background thread"""
        try:
            self.log_signal.emit("🔍 Starting proxy verification...")

            # Get proxy info for logging
            proxy, proxy_display = self.scraper_runner.get_proxy_for_profile(self.profile_name)
            if proxy:
                self.log_signal.emit(f"🌐 Proxy configured: {proxy_display}")
            else:
                self.log_signal.emit("❌ No proxy configured for this profile")
                self.finished.emit(False, "No proxy configured")
                return

            self.log_signal.emit("🌍 Navigating to whatismyip.com...")
            self.log_signal.emit("⏳ Waiting 4 seconds for page to load...")

            # Run the check
            success, result = self.scraper_runner.check_proxy_ip(
                self.profile_name,
                self.headless
            )

            if success:
                self.log_signal.emit(f"✅ Expected IP (from proxy): {result['proxy_ip']}")
                self.log_signal.emit(f"🌐 Detected IP (from site): {result['detected_ip']}")

                if result['is_match']:
                    self.log_signal.emit("✅ IPs match! Proxy is working correctly!")
                else:
                    self.log_signal.emit("⚠️ IPs don't match! Proxy might not be working!")

            self.finished.emit(success, result)

        except Exception as e:
            error_msg = f"Thread error: {str(e)}\n{traceback.format_exc()}"
            self.log_signal.emit(f"❌ Error: {str(e)}")
            self.finished.emit(False, error_msg)


class InspectElementsThread(QThread):
    """Thread for launching browser with DevTools for element inspection"""
    finished = Signal(bool, object)  # success, result/error
    log_signal = Signal(str)

    def __init__(self, scraper_runner, profile_name, url, headless=False):
        super().__init__()
        self.scraper_runner = scraper_runner
        self.profile_name = profile_name
        self.url = url
        self.headless = headless

    def run(self):
        """Launch browser for element inspection"""
        try:
            # Fix URL and log it
            fixed_url = self.scraper_runner.fix_url(self.url)
            if fixed_url != self.url:
                self.log_signal.emit(f"🔧 Auto-fixed URL: {self.url} → {fixed_url}")

            # Get proxy info for this profile
            proxy, proxy_display = self.scraper_runner.get_proxy_for_profile(self.profile_name)
            if proxy:
                self.log_signal.emit(f"🌐 Using proxy: {proxy_display}")
            else:
                self.log_signal.emit(f"🌐 No proxy configured (direct connection)")

            self.log_signal.emit("🔧 Initializing anti-detection browser...")

            # Update last used timestamp
            self.scraper_runner.profile_manager.update_last_used(self.profile_name)

            # Create driver configuration
            driver_config = {
                'profile': self.profile_name,
                'headless': self.headless
            }

            # Add proxy if configured
            if proxy:
                driver_config['proxy'] = proxy

            # Create driver with profile and proxy
            driver = Driver(**driver_config)

            # Navigate to URL
            self.log_signal.emit(f"🌐 Navigating to {fixed_url}...")
            driver.get(fixed_url)

            # Wait for page to load
            driver.sleep(2)

            self.log_signal.emit("✅ Browser launched successfully!")
            self.log_signal.emit("")
            self.log_signal.emit("💡 How to inspect elements:")
            self.log_signal.emit("   1. Press F12 to open Chrome DevTools")
            self.log_signal.emit("   2. Click the 'Select element' icon (top-left of DevTools)")
            self.log_signal.emit("   3. Hover over elements to see their selectors")
            self.log_signal.emit("   4. Click on an element to inspect it")
            self.log_signal.emit("   5. Copy selectors from the Elements tab")
            self.log_signal.emit("")
            self.log_signal.emit("🛡️ Anti-detection enabled - captchas will work!")
            self.log_signal.emit("💡 Browser window left open - close manually when done")

            result = {
                "url": fixed_url,
                "proxy_used": proxy_display if proxy else "No proxy"
            }

            self.finished.emit(True, result)

            # Keep browser open - user will close manually
            # driver.quit() - NOT called

        except Exception as e:
            error_msg = f"Thread error: {str(e)}\n{traceback.format_exc()}"
            self.log_signal.emit(f"❌ Error: {str(e)}")
            self.finished.emit(False, error_msg)


class MexcAuthThread(QThread):
    """Thread for MEXC login automation"""
    finished = Signal(bool, object)  # success, result/error
    log_signal = Signal(str)
    captcha_signal = Signal()  # Signal when captcha detected

    def __init__(self, scraper_runner, profile_name, email, password, secret, headless=False):
        super().__init__()
        self.scraper_runner = scraper_runner
        self.profile_name = profile_name
        self.email = email
        self.password = password
        self.secret = secret
        self.headless = headless

    def run(self):
        """Run MEXC login automation"""
        try:
            self.log_signal.emit("🔐 Starting MEXC login automation...")

            # Get proxy info for this profile
            proxy, proxy_display = self.scraper_runner.get_proxy_for_profile(self.profile_name)
            if proxy:
                self.log_signal.emit(f"🌐 Using proxy: {proxy_display}")
            else:
                self.log_signal.emit(f"🌐 No proxy configured (direct connection)")

            self.log_signal.emit("🔧 Initializing anti-detection browser...")

            # Update last used timestamp
            self.scraper_runner.profile_manager.update_last_used(self.profile_name)

            # Create driver configuration
            driver_config = {
                'profile': self.profile_name,
                'headless': self.headless
            }

            # Add proxy if configured
            if proxy:
                driver_config['proxy'] = proxy

            # Create driver with profile and proxy
            driver = Driver(**driver_config)

            # Navigate to MEXC login page
            login_url = "https://www.mexc.com/ru-RU/login?previous=%2Fru-RU%2F"
            self.log_signal.emit(f"🌐 Navigating to MEXC login page...")
            driver.get(login_url)

            # Wait for page to load
            driver.sleep(3)

            # Step 1: Enter email
            self.log_signal.emit("📧 Entering email...")
            try:
                email_field = driver.select("#emailInputwwwmexccom", wait=5)
                email_field.click()
                driver.sleep(0.5)
                email_field.type(self.email)
                self.log_signal.emit(f"✅ Email entered: {self.email}")
            except Exception as e:
                raise Exception(f"Email field not found: {e}")

            driver.sleep(1)

            # Step 2: Click switcher
            self.log_signal.emit("🔘 Clicking switcher...")
            try:
                switcher = driver.select(".ant-switch-handle", wait=3)
                switcher.click()
                self.log_signal.emit("✅ Switcher clicked")
            except:
                self.log_signal.emit("⚠️ Switcher not found, skipping...")

            driver.sleep(1)

            # Step 3: Click "Next" button
            self.log_signal.emit("➡️ Clicking 'Next' button...")
            try:
                # Find submit button (should be "Далее" button)
                next_button = driver.select("button[type='submit'].ant-btn-v2-primary", wait=3)
                next_button.click()
                self.log_signal.emit("✅ 'Next' clicked")
            except Exception as e:
                self.log_signal.emit(f"⚠️ Error finding Next button: {e}")
                raise Exception("'Next' button not found")

            driver.sleep(3)

            # Step 4: Check for captcha
            self.log_signal.emit("🔍 Checking for captcha...")
            try:
                captcha_element = driver.select(".geetest_text_tips", wait=2)
                if captcha_element:
                    self.log_signal.emit("⚠️ Captcha detected!")
                    self.log_signal.emit("⏸️ Waiting for user to solve captcha...")

                    # Emit signal to show dialog to user
                    self.captcha_signal.emit()

                    # Wait 10 seconds after user clicks OK
                    self.log_signal.emit("⏳ Waiting 10 seconds...")
                    driver.sleep(10)
                    self.log_signal.emit("✅ Continuing after captcha...")
            except:
                self.log_signal.emit("✅ No captcha detected")

            # Step 5: Enter password
            self.log_signal.emit("🔑 Entering password...")
            try:
                password_field = driver.select("#passwordInput", wait=5)
                password_field.click()
                driver.sleep(0.5)
                password_field.type(self.password)
                self.log_signal.emit("✅ Password entered")
            except Exception as e:
                raise Exception(f"Password field not found: {e}")

            driver.sleep(3)

            # Step 6: Click "Login" button
            self.log_signal.emit("🔓 Clicking 'Login' button...")
            try:
                # Find submit button (should be "Войти" button)
                login_button = driver.select("button[type='submit'].ant-btn-v2-primary", wait=3)
                login_button.click()
                self.log_signal.emit("✅ 'Login' clicked")
            except Exception as e:
                self.log_signal.emit(f"⚠️ Error finding Login button: {e}")
                raise Exception("'Login' button not found")

            driver.sleep(5)

            # Step 7: Click switcher again
            self.log_signal.emit("🔘 Clicking switcher (2nd time)...")
            try:
                switcher2 = driver.select(".ant-switch-handle", wait=3)
                switcher2.click()
                self.log_signal.emit("✅ Switcher clicked")
            except:
                self.log_signal.emit("⚠️ Switcher not found, skipping...")

            driver.sleep(1)

            # Step 8: Generate and enter 2FA code
            self.log_signal.emit("🔐 Generating 2FA code...")
            import pyotp
            totp = pyotp.TOTP(self.secret)
            code_2fa = totp.now()
            self.log_signal.emit(f"✅ 2FA code generated: {code_2fa}")

            self.log_signal.emit("🔢 Entering 2FA code...")
            try:
                code_field = driver.select('input[data-id="0"]', wait=5)
                code_field.click()
                driver.sleep(0.5)
                code_field.type(code_2fa)
                self.log_signal.emit("✅ 2FA code entered")
            except Exception as e:
                raise Exception(f"2FA code field not found: {e}")

            driver.sleep(5)

            # Step 9: Click "OK" button
            self.log_signal.emit("✅ Clicking 'OK' button...")
            try:
                # Find button type="button" (should be "ОК" button)
                ok_button = driver.select("button[type='button'].ant-btn-v2-primary", wait=3)
                ok_button.click()
                self.log_signal.emit("✅ 'OK' clicked")
            except Exception as e:
                self.log_signal.emit(f"⚠️ Error finding OK button: {e}")
                raise Exception("'OK' button not found")

            driver.sleep(15)

            self.log_signal.emit("🎉 MEXC login completed successfully!")
            self.log_signal.emit("💡 Browser window left open - close manually when done")

            result = {
                "email": self.email,
                "status": "logged_in"
            }

            self.finished.emit(True, result)

            # Keep browser open - user will close manually
            # driver.quit() - NOT called

        except Exception as e:
            error_msg = f"MEXC Auth error: {str(e)}\n{traceback.format_exc()}"
            self.log_signal.emit(f"❌ Error: {str(e)}")
            self.finished.emit(False, error_msg)
        finally:
            # Ensure thread completes cleanly
            # Sleep briefly to allow signals to be processed
            import time
            time.sleep(0.1)


class ManualBrowserThread(QThread):
    """
    Thread for opening browser in manual mode
    Uses exec() to keep thread alive and prevent Driver garbage collection
    """
    driver_ready = Signal(object, dict)  # (Driver instance, profile_info)
    log_signal = Signal(str)
    error_signal = Signal(str, str)  # (email, error_message)

    def __init__(self, scraper_runner, profile_name, email, headless=False):
        super().__init__()
        self.scraper_runner = scraper_runner
        self.profile_name = profile_name
        self.email = email
        self.headless = headless
        self.row = None  # Will be set by caller

    def run(self):
        """Create browser and keep thread alive"""
        driver = None
        try:
            self.log_signal.emit(f"🔧 Initializing browser for {self.email}...")

            # Get proxy info
            proxy, proxy_display = self.scraper_runner.get_proxy_for_profile(self.profile_name)
            if proxy:
                self.log_signal.emit(f"🌐 Using proxy: {proxy_display}")

            # Update last used
            self.scraper_runner.profile_manager.update_last_used(self.profile_name)

            # Create driver config
            driver_config = {
                'profile': self.profile_name,
                'headless': self.headless
            }

            if proxy:
                driver_config['proxy'] = proxy

            # Create driver (blocking, but in background thread!)
            self.log_signal.emit(f"⏳ Creating browser instance...")
            driver = Driver(**driver_config)

            # Navigate to MEXC
            self.log_signal.emit(f"🌐 Opening MEXC...")
            driver.get("https://www.mexc.com/")

            self.log_signal.emit(f"✅ Browser ready for: {self.email}")

            # Transfer Driver to main thread via signal
            profile_info = {
                'profile_name': self.profile_name,
                'email': self.email,
                'row': self.row
            }
            self.driver_ready.emit(driver, profile_info)

            # CRITICAL: Keep thread alive to maintain Driver context
            # This prevents garbage collection and keeps browser open
            self.exec()  # Enter event loop - thread stays alive!

        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            self.log_signal.emit(f"❌ Failed to open browser: {str(e)}")
            self.error_signal.emit(self.email, error_msg)

            # Clean up driver if created
            if driver:
                try:
                    driver.close()
                except:
                    pass

    def stop(self):
        """Stop the thread's event loop"""
        self.quit()  # Exit exec() loop


class ShortLongTradeThread(QThread):
    """
    Thread for executing Short/Long trades on MEXC Futures
    """
    finished = Signal(bool, object)  # success, result/error
    log_signal = Signal(str)
    driver_ready = Signal(object, dict)  # driver, info dict

    def __init__(self, scraper_runner, profile_name, email, mode, settings, headless=False):
        super().__init__()
        self.scraper_runner = scraper_runner
        self.profile_name = profile_name
        self.email = email
        self.mode = mode  # "short" or "long"
        self.settings = settings  # Trading settings dict
        self.headless = headless

    def add_cursor_circle(self, driver):
        """
        Add red circle around cursor for visual feedback
        """
        cursor_js = """
        // Remove old cursor circle if exists
        var oldCircle = document.getElementById('playwright-cursor-circle');
        if (oldCircle) {
            oldCircle.remove();
        }

        // Create cursor circle element
        var cursorCircle = document.createElement('div');
        cursorCircle.id = 'playwright-cursor-circle';
        cursorCircle.style.cssText = `
            position: fixed;
            border: 3px solid red;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            pointer-events: none;
            z-index: 999999;
            transform: translate(-50%, -50%);
            transition: all 0.1s ease;
            box-shadow: 0 0 10px rgba(255, 0, 0, 0.5);
        `;
        document.body.appendChild(cursorCircle);

        // Track mouse movement
        document.addEventListener('mousemove', function(e) {
            var circle = document.getElementById('playwright-cursor-circle');
            if (circle) {
                circle.style.left = e.clientX + 'px';
                circle.style.top = e.clientY + 'px';
            }
        });

        // Pulse effect on click
        document.addEventListener('click', function() {
            var circle = document.getElementById('playwright-cursor-circle');
            if (circle) {
                circle.style.transform = 'translate(-50%, -50%) scale(1.5)';
                circle.style.borderColor = '#ff0000';
                circle.style.borderWidth = '5px';
                setTimeout(function() {
                    circle.style.transform = 'translate(-50%, -50%) scale(1)';
                    circle.style.borderWidth = '3px';
                }, 200);
            }
        });
        """

        try:
            driver.run_js(cursor_js)
            self.log_signal.emit("🔴 Red cursor circle enabled")
        except Exception as e:
            self.log_signal.emit(f"⚠️ Could not add cursor circle: {str(e)[:50]}")

    def click_position_slider(self, driver, position_percent):
        """
        Click position slider dot using JavaScript to find it

        Args:
            driver: Botasaurus Driver instance
            position_percent: Position percentage (25, 50, 75, 100)

        Returns:
            bool: True if clicked successfully, False otherwise
        """
        try:
            self.log_signal.emit(f"🔍 Searching for {position_percent}% slider position...")

            # STEP 1: Find slider dot using JavaScript
            find_slider_js = f"""
            // Remove old markers
            var oldMarked = document.querySelectorAll('[data-slider-target]');
            for (var j = 0; j < oldMarked.length; j++) {{
                oldMarked[j].removeAttribute('data-slider-target');
            }}

            // Find all slider dots
            var dots = document.querySelectorAll('.ant-slider-v2-dot, .ant-slider-dot, [class*="slider"] [class*="dot"]');
            var found = false;

            for (var i = 0; i < dots.length; i++) {{
                // Check style attribute for position
                var style = dots[i].getAttribute('style') || '';
                if (style.includes('left: {position_percent}%') || style.includes('left:{position_percent}%')) {{
                    // Mark this dot
                    dots[i].setAttribute('data-slider-target', 'true');
                    // Scroll into view
                    dots[i].scrollIntoView({{block: 'center', behavior: 'instant'}});
                    found = true;
                    break;
                }}
            }}

            // If not found by exact match, try to find by proximity
            if (!found) {{
                var targetPercent = {position_percent};
                for (var i = 0; i < dots.length; i++) {{
                    var style = dots[i].getAttribute('style') || '';
                    var match = style.match(/left:\\s*(\\d+)%/);
                    if (match) {{
                        var dotPercent = parseInt(match[1]);
                        if (Math.abs(dotPercent - targetPercent) < 3) {{  // Within 3% tolerance
                            dots[i].setAttribute('data-slider-target', 'true');
                            dots[i].scrollIntoView({{block: 'center', behavior: 'instant'}});
                            found = true;
                            break;
                        }}
                    }}
                }}
            }}

            return found;
            """

            result = driver.run_js(find_slider_js)
            if not result:
                self.log_signal.emit(f"⚠️ Could not find {position_percent}% slider dot with JavaScript")
                return False

            driver.sleep(0.5)

            # STEP 2: Select marked element
            slider_dot = driver.select('[data-slider-target="true"]', wait=2)
            if not slider_dot:
                self.log_signal.emit(f"⚠️ Could not select marked slider dot")
                return False

            # STEP 3: Click the dot
            slider_dot.click()

            # Clean up marker
            cleanup_js = """
            var marked = document.querySelector('[data-slider-target="true"]');
            if (marked) {
                marked.removeAttribute('data-slider-target');
            }
            """
            driver.run_js(cleanup_js)

            self.log_signal.emit(f"✓ Clicked {position_percent}% slider position")
            return True

        except Exception as e:
            self.log_signal.emit(f"⚠️ Position slider click failed: {str(e)[:100]}")
            return False

    def find_and_click_by_text(self, driver, text, element_type='*'):
        """
        Find element by text using JavaScript, then click using Driver.select()

        This is the CORRECT way for botasaurus_driver!

        Args:
            driver: Botasaurus Driver instance
            text: Text to search for
            element_type: HTML element type (button, div, span, *)

        Returns:
            bool: True if clicked successfully, False otherwise
        """
        try:
            # STEP 1: Find element using JavaScript and mark it
            find_js = f"""
            // Remove old markers
            var oldMarked = document.querySelectorAll('[data-botasaurus-click-target]');
            for (var j = 0; j < oldMarked.length; j++) {{
                oldMarked[j].removeAttribute('data-botasaurus-click-target');
            }}

            // Find element containing text
            var elements = document.querySelectorAll('{element_type}');
            var found = false;
            for (var i = 0; i < elements.length; i++) {{
                var textContent = elements[i].textContent || elements[i].innerText || '';
                if (textContent.includes('{text}')) {{
                    // Check if visible
                    var rect = elements[i].getBoundingClientRect();
                    var isVisible = rect.width > 0 && rect.height > 0 &&
                                   window.getComputedStyle(elements[i]).visibility !== 'hidden' &&
                                   window.getComputedStyle(elements[i]).display !== 'none';

                    if (isVisible) {{
                        // Mark element
                        elements[i].setAttribute('data-botasaurus-click-target', 'true');
                        // Scroll into view
                        elements[i].scrollIntoView({{block: 'center', behavior: 'instant'}});
                        found = true;
                        break;
                    }}
                }}
            }}
            return found;
            """

            result = driver.run_js(find_js)
            if not result:
                return False

            # Small wait for scroll
            driver.sleep(0.5)

            # STEP 2: Select marked element using Driver.select() (CSS selector)
            element = driver.select('[data-botasaurus-click-target="true"]', wait=2)
            if not element:
                return False

            # STEP 3: Click using botasaurus element.click()
            element.click()

            # Clean up marker
            cleanup_js = """
            var marked = document.querySelector('[data-botasaurus-click-target="true"]');
            if (marked) {
                marked.removeAttribute('data-botasaurus-click-target');
            }
            """
            driver.run_js(cleanup_js)

            self.log_signal.emit(f"✓ Clicked element with text: {text}")
            return True

        except Exception as e:
            self.log_signal.emit(f"⚠️ Click failed: {str(e)[:100]}")
            return False

    def find_element_by_text(self, driver, text, element_type='*'):
        """
        Find element by text content using JavaScript

        Args:
            driver: Botasaurus Driver instance
            text: Text to search for
            element_type: HTML element type (button, div, span, etc.) or * for any

        Returns:
            Element or None
        """
        # JavaScript to find element containing exact text
        js_code = f"""
        // Clear any previous markers
        var oldMarked = document.querySelectorAll('[data-found-by-text]');
        for (var j = 0; j < oldMarked.length; j++) {{
            oldMarked[j].removeAttribute('data-found-by-text');
        }}

        // Search for new element
        var elements = document.querySelectorAll('{element_type}');
        for (var i = 0; i < elements.length; i++) {{
            if (elements[i].textContent.trim() === '{text}' ||
                elements[i].innerText.trim() === '{text}') {{
                elements[i].setAttribute('data-found-by-text', 'true');
                elements[i].scrollIntoView({{block: 'center', behavior: 'smooth'}});
                return true;
            }}
        }}
        return false;
        """

        try:
            # Execute JavaScript to mark the element
            result = driver.run_js(js_code)
            if result:
                # Small wait for scroll to complete
                driver.sleep(0.5)
                # Now select the marked element using CSS
                return driver.select('[data-found-by-text="true"]', wait=1)
        except Exception as e:
            self.log_signal.emit(f"⚠️ JS error finding element: {str(e)[:50]}")
            pass

        return None

    def find_element_containing_text(self, driver, text, element_type='*'):
        """
        Find element containing text (partial match) using JavaScript

        Args:
            driver: Botasaurus Driver instance
            text: Text to search for (partial match)
            element_type: HTML element type or * for any

        Returns:
            Element or None
        """
        # JavaScript to find element containing text
        js_code = f"""
        // Clear any previous markers
        var oldMarked = document.querySelectorAll('[data-found-by-text]');
        for (var j = 0; j < oldMarked.length; j++) {{
            oldMarked[j].removeAttribute('data-found-by-text');
        }}

        // Search for new element
        var elements = document.querySelectorAll('{element_type}');
        for (var i = 0; i < elements.length; i++) {{
            var textContent = elements[i].textContent || elements[i].innerText || '';
            if (textContent.includes('{text}')) {{
                elements[i].setAttribute('data-found-by-text', 'true');
                elements[i].scrollIntoView({{block: 'center', behavior: 'smooth'}});
                return true;
            }}
        }}
        return false;
        """

        try:
            # Execute JavaScript to mark the element
            result = driver.run_js(js_code)
            if result:
                # Small wait for scroll to complete
                driver.sleep(0.5)
                # Now select the marked element using CSS
                return driver.select('[data-found-by-text="true"]', wait=1)
        except Exception as e:
            self.log_signal.emit(f"⚠️ JS error finding element: {str(e)[:50]}")
            pass

        return None

    def click_element_with_text(self, driver, text, element_type='*'):
        """
        Find and click element containing text using JavaScript click

        Args:
            driver: Botasaurus Driver instance
            text: Text to search for
            element_type: HTML element type or * for any

        Returns:
            bool: True if clicked successfully, False otherwise
        """
        # First, find and scroll to the element
        scroll_js = f"""
        var elements = document.querySelectorAll('{element_type}');
        for (var i = 0; i < elements.length; i++) {{
            var textContent = elements[i].textContent || elements[i].innerText || '';
            if (textContent.includes('{text}')) {{
                // Check if element is visible
                var rect = elements[i].getBoundingClientRect();
                var isVisible = rect.width > 0 && rect.height > 0 &&
                               window.getComputedStyle(elements[i]).visibility !== 'hidden' &&
                               window.getComputedStyle(elements[i]).display !== 'none';

                if (isVisible) {{
                    // Scroll into view
                    elements[i].scrollIntoView({{block: 'center', behavior: 'instant'}});
                    // Mark element for clicking
                    elements[i].setAttribute('data-click-target', 'true');
                    return true;
                }}
            }}
        }}
        return false;
        """

        try:
            # First scroll to element
            result = driver.run_js(scroll_js)
            if not result:
                return False

            # Small wait for scroll
            driver.sleep(0.5)

            # Now click the marked element
            click_js = """
            var element = document.querySelector('[data-click-target="true"]');
            if (element) {
                // Try multiple click methods for maximum compatibility
                element.click();  // Standard click

                // Also dispatch a mouse click event
                var clickEvent = new MouseEvent('click', {
                    view: window,
                    bubbles: true,
                    cancelable: true
                });
                element.dispatchEvent(clickEvent);

                // Clean up marker
                element.removeAttribute('data-click-target');
                return true;
            }
            return false;
            """

            click_result = driver.run_js(click_js)
            if click_result:
                driver.sleep(1)  # Wait for click to process
                return True

        except Exception as e:
            self.log_signal.emit(f"⚠️ JS click error: {str(e)[:50]}")

        return False

    def parse_token_url(self, token_link):
        """
        Parse token link and generate MEXC Futures URL

        Supports:
        - Full URL: https://www.mexc.com/ru-RU/futures/BTC_USDT?...
        - Ticker only: BTC_USDT
        - Contract address: (will search for it)
        """
        # If already a full MEXC URL
        if "mexc.com" in token_link and "futures" in token_link:
            return token_link

        # If looks like a ticker (BTC_USDT format)
        if "_" in token_link and len(token_link) < 20:
            ticker = token_link.upper()
            return f"https://www.mexc.com/ru-RU/futures/{ticker}?type=linear_swap&lang=ru-RU"

        # Otherwise, assume it's a contract address or search term
        # For now, default to BTC_USDT (you can improve this later)
        self.log_signal.emit(f"⚠️ Could not parse token link, using BTC_USDT as fallback")
        return "https://www.mexc.com/ru-RU/futures/BTC_USDT?type=linear_swap&lang=ru-RU"

    def run(self):
        """Execute the trade"""
        driver = None
        try:
            self.log_signal.emit(f"🔧 Initializing browser for trade: {self.email}")

            # Get proxy info
            proxy, proxy_display = self.scraper_runner.get_proxy_for_profile(self.profile_name)
            if proxy:
                self.log_signal.emit(f"🌐 Using proxy: {proxy_display}")

            # Update last used
            self.scraper_runner.profile_manager.update_last_used(self.profile_name)

            # Create driver config
            driver_config = {
                'profile': self.profile_name,
                'headless': self.headless
            }

            if proxy:
                driver_config['proxy'] = proxy

            # Create driver
            self.log_signal.emit(f"⏳ Creating browser instance...")
            driver = Driver(**driver_config)

            # Parse and navigate to token URL
            token_url = self.parse_token_url(self.settings['token_link'])
            self.log_signal.emit(f"🌐 Opening: {token_url}")
            driver.get(token_url)
            self.log_signal.emit("⏳ Waiting 7 seconds for page to load...")
            driver.sleep(7)  # Wait for page load

            # Add red cursor circle for visual feedback
            self.add_cursor_circle(driver)

            # === STEP 1: Select Order Type (Limit/Market) ===
            self.log_signal.emit(f"📊 Selecting order type: {self.settings['zaliv_type']}")
            driver.sleep(7)  # 7 second delay BEFORE searching for tab

            if self.settings['zaliv_type'] == "Limit":
                # Click "Лимит" / "Limit" tab
                try:
                    self.log_signal.emit("🔍 Searching for Limit tab...")

                    # Try to click Limit tab (try BOTH Russian and English)
                    clicked = False

                    # Try Russian "Лимит" first
                    self.log_signal.emit("🔍 Trying Russian 'Лимит'...")
                    clicked = self.find_and_click_by_text(driver, 'Лимит', 'div')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Лимит', 'button')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Лимит', 'span')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Лимит', '*')

                    # Try English "Limit" if Russian didn't work
                    if not clicked:
                        self.log_signal.emit("🔍 Trying English 'Limit'...")
                        clicked = self.find_and_click_by_text(driver, 'Limit', 'div')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Limit', 'button')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Limit', 'span')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Limit', '*')

                    if clicked:
                        self.log_signal.emit("✓ Limit tab clicked!")
                        driver.sleep(7)  # 7 second delay after clicking Limit tab
                        self.log_signal.emit("✓ Selected Limit order type")
                    else:
                        self.log_signal.emit("⚠️ Could not find or click Limit tab (tried both Russian and English)")
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Could not find Limit tab: {e}")

                # Enter limit price
                self.log_signal.emit(f"💰 Entering limit price: {self.settings['limit_price']}")
                driver.sleep(7)  # 7 second delay BEFORE searching for input
                # Find price input - it's the first ant-input after selecting Limit
                try:
                    price_input = driver.select('.ant-input[type="text"]', wait=10)
                    # Clear existing value
                    price_input.clear()
                    driver.sleep(1)
                    # Type new price
                    price_input.type(self.settings['limit_price'])
                    self.log_signal.emit(f"✓ Limit price entered: {self.settings['limit_price']}")
                    driver.sleep(7)  # 7 second delay after entering limit price
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Could not find price input field: {e}")

            else:  # Market order
                # Click "Маркет" / "Market" tab
                try:
                    self.log_signal.emit("🔍 Searching for Market tab...")

                    # Try to click Market tab (try BOTH Russian and English)
                    clicked = False

                    # Try Russian "Маркет" first
                    self.log_signal.emit("🔍 Trying Russian 'Маркет'...")
                    clicked = self.find_and_click_by_text(driver, 'Маркет', 'div')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Маркет', 'button')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Маркет', 'span')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Маркет', '*')

                    # Try English "Market" if Russian didn't work
                    if not clicked:
                        self.log_signal.emit("🔍 Trying English 'Market'...")
                        clicked = self.find_and_click_by_text(driver, 'Market', 'div')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Market', 'button')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Market', 'span')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Market', '*')

                    if clicked:
                        self.log_signal.emit("✓ Market tab clicked!")
                        driver.sleep(7)  # 7 second delay after clicking Market tab
                        self.log_signal.emit("✓ Selected Market order type")
                    else:
                        self.log_signal.emit("⚠️ Could not find or click Market tab (tried both Russian and English)")
                except Exception as e:
                    self.log_signal.emit(f"⚠️ Could not find Market tab: {e}")

            # === STEP 2: Select Position Percentage ===
            position = self.settings['position_percent']
            self.log_signal.emit(f"📈 Selecting position: {position}%")
            driver.sleep(7)  # 7 second delay BEFORE searching for slider

            # Click on slider dot based on percentage
            position_clicked = False

            if position in ["25", "50", "75", "100"]:
                # Try new JavaScript method first
                position_clicked = self.click_position_slider(driver, position)

                # Fallback to CSS selector if JavaScript method failed
                if not position_clicked:
                    self.log_signal.emit(f"🔍 Trying CSS selector fallback...")
                    dot_selector = f'.ant-slider-v2-dot[style*="left: {position}%"]'
                    try:
                        position_dot = driver.select(dot_selector, wait=10)
                        position_dot.click()
                        self.log_signal.emit(f"✓ Selected {position}% position (CSS)")
                        position_clicked = True
                    except Exception as e:
                        self.log_signal.emit(f"⚠️ CSS selector also failed: {str(e)[:100]}")
            else:
                # Custom percentage - try 100% as fallback
                self.log_signal.emit(f"⚠️ Custom percentage not yet implemented, trying 100%")
                position_clicked = self.click_position_slider(driver, "100")

                if not position_clicked:
                    try:
                        position_dot = driver.select('.ant-slider-v2-dot[style*="left: 100%"]', wait=10)
                        position_dot.click()
                        self.log_signal.emit("✓ Selected 100% position (CSS)")
                        position_clicked = True
                    except Exception as e:
                        self.log_signal.emit(f"⚠️ Could not find 100% slider dot: {str(e)[:100]}")

            if position_clicked:
                driver.sleep(7)  # 7 second delay after clicking position slider
            else:
                self.log_signal.emit(f"⚠️ WARNING: Could not select position slider!")

            # === STEP 3: Execute Trade (Long/Short) ===
            driver.sleep(7)  # 7 second delay BEFORE searching for execute button
            try:
                clicked = False

                if self.mode == "long":
                    self.log_signal.emit("🚀 Executing LONG trade...")
                    self.log_signal.emit("🔍 Searching for LONG execute button...")

                    # Try Russian variants first
                    clicked = self.find_and_click_by_text(driver, 'Открыть Лонг', 'button')

                    if not clicked:
                        self.log_signal.emit("🔍 Trying shorter text 'Лонг'...")
                        clicked = self.find_and_click_by_text(driver, 'Лонг', 'button')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Открыть Лонг', 'div')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Лонг', '*')

                    # Try English variants if Russian didn't work
                    if not clicked:
                        self.log_signal.emit("🔍 Trying English 'Open Long'...")
                        clicked = self.find_and_click_by_text(driver, 'Open Long', 'button')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Long', 'button')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Open Long', 'div')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Long', '*')

                else:  # short
                    self.log_signal.emit("🚀 Executing SHORT trade...")
                    self.log_signal.emit("🔍 Searching for SHORT execute button...")

                    # Try Russian variants first
                    clicked = self.find_and_click_by_text(driver, 'Открыть Шорт', 'button')

                    if not clicked:
                        self.log_signal.emit("🔍 Trying shorter text 'Шорт'...")
                        clicked = self.find_and_click_by_text(driver, 'Шорт', 'button')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Открыть Шорт', 'div')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Шорт', '*')

                    # Try English variants if Russian didn't work
                    if not clicked:
                        self.log_signal.emit("🔍 Trying English 'Open Short'...")
                        clicked = self.find_and_click_by_text(driver, 'Open Short', 'button')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Short', 'button')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Open Short', 'div')

                    if not clicked:
                        clicked = self.find_and_click_by_text(driver, 'Short', '*')

                if clicked:
                    self.log_signal.emit("✓ Execute button clicked!")
                    driver.sleep(7)  # 7 second delay after clicking execute button

                    # Check for confirmation dialog
                    driver.sleep(7)  # 7 second delay BEFORE searching for confirm button
                    try:
                        self.log_signal.emit("🔍 Looking for confirmation button...")

                        # Try Russian "Подтвердить" first
                        confirm_clicked = self.find_and_click_by_text(driver, 'Подтвердить', 'button')

                        if not confirm_clicked:
                            confirm_clicked = self.find_and_click_by_text(driver, 'Подтвердить', '*')

                        # Try English "Confirm" if Russian didn't work
                        if not confirm_clicked:
                            self.log_signal.emit("🔍 Trying English 'Confirm'...")
                            confirm_clicked = self.find_and_click_by_text(driver, 'Confirm', 'button')

                        if not confirm_clicked:
                            confirm_clicked = self.find_and_click_by_text(driver, 'Confirm', '*')

                        # Try common alternatives
                        if not confirm_clicked:
                            confirm_clicked = self.find_and_click_by_text(driver, 'OK', 'button')

                        if not confirm_clicked:
                            confirm_clicked = self.find_and_click_by_text(driver, 'Yes', 'button')

                        if confirm_clicked:
                            self.log_signal.emit("✓ Confirmation button clicked!")
                            driver.sleep(7)  # 7 second delay after clicking confirm button
                        else:
                            self.log_signal.emit("ℹ️ No confirmation dialog found (might not be needed)")
                    except Exception as e:
                        # No confirmation dialog - that's ok
                        self.log_signal.emit(f"ℹ️ No confirmation dialog: {str(e)[:50]}")
                else:
                    raise Exception(f"Could not find or click execute button for {self.mode}")

                # Wait a bit to see if trade executed
                driver.sleep(7)

                result = {
                    'email': self.email,
                    'mode': self.mode,
                    'status': 'executed',
                    'token': self.settings['token_link'],
                    'position': f"{position}%",
                    'type': self.settings['zaliv_type']
                }

                self.log_signal.emit(f"✅ {self.mode.upper()} trade executed for: {self.email}")
                self.finished.emit(True, result)

            except Exception as e:
                error_msg = f"Could not find execute button for {self.mode}: {e}"
                self.log_signal.emit(f"❌ {error_msg}")
                self.finished.emit(False, error_msg)

            # Transfer driver to main window (regardless of success/failure)
            # This prevents driver from being garbage collected
            info = {
                'profile_name': self.profile_name,
                'email': self.email,
                'thread': self,
                'mode': self.mode
            }

            self.log_signal.emit(f"🌐 Browser ready for {self.email} - use 'Close All Browsers' to close")
            self.driver_ready.emit(driver, info)

            # Keep thread alive to prevent driver GC
            self.exec()

        except Exception as e:
            error_msg = f"Trade execution error: {str(e)}\n{traceback.format_exc()}"
            self.log_signal.emit(f"❌ Trade failed for {self.email}: {str(e)}")
            self.finished.emit(False, error_msg)

            # Still transfer driver even on error (for debugging)
            if driver:
                info = {
                    'profile_name': self.profile_name,
                    'email': self.email,
                    'thread': self,
                    'mode': self.mode
                }
                self.driver_ready.emit(driver, info)
                self.exec()

    def stop(self):
        """Stop the thread's event loop"""
        self.quit()  # Exit exec() loop
