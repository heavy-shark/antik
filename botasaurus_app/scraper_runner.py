"""
Scraper Runner
Integrates Botasaurus browser automation with profile management
"""
from PySide6.QtCore import QThread, Signal
import sys
import traceback
import re
import random
import time
import pyotp

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


class MexcLoginThread(QThread):
    """
    Thread for MEXC login automation using anti-detect browser with human-like behavior
    """
    finished = Signal(bool, object)  # success, result/error
    log_signal = Signal(str)

    # Configuration constants (from try.py)
    MOUSE_MOVE_DURATION_MAIN = 1.2
    MOUSE_MOVE_DURATION_SHORT = 0.8
    MOUSE_MOVE_DURATION_TAB = 1.0
    MOUSE_STEP_INTERVAL_SEC = 0.02
    CURSOR_JITTER_PX = 0.95
    HUMAN_TYPE_TOTAL_TIME_SEC = 2.0

    def __init__(self, scraper_runner, profile_name, email, password, twofa_secret, headless=False):
        super().__init__()
        self.scraper_runner = scraper_runner
        self.profile_name = profile_name
        self.email = email
        self.password = password
        self.twofa_secret = twofa_secret
        self.headless = headless
        self.row = None
        self.driver = None
        self.cursor_pos = (640, 360)

    def run(self):
        """Run the login process using anti-detect browser"""
        import time

        try:
            self.log_signal.emit("🔐 Starting MEXC login with human-like behavior...")

            # Get proxy for profile
            proxy, proxy_display = self.scraper_runner.get_proxy_for_profile(self.profile_name)

            self.log_signal.emit("🔧 Launching anti-detect browser...")

            # Update last used
            self.scraper_runner.profile_manager.update_last_used(self.profile_name)

            # Create driver config (same as ManualBrowserThread)
            driver_config = {
                'profile': self.profile_name,
                'headless': self.headless
            }

            if proxy:
                driver_config['proxy'] = proxy
                self.log_signal.emit(f"🌐 Using proxy: {proxy_display}")

            # Create anti-detect browser
            self.driver = Driver(**driver_config)

            # Step 1: Navigate to login page
            self.log_signal.emit("🌐 Opening MEXC login page...")
            login_url = "https://www.mexc.com/ru-RU/login?previous=%2Fru-RU%2F"
            self.driver.get(login_url)

            # Setup cursor circle after page load
            self.setup_cursor_circle()

            self.log_signal.emit("⏳ Waiting 10 seconds for page to load...")
            time.sleep(10)

            # Step 2: Enter email
            self.step_enter_email()

            # Step 3: Check and click switch if needed
            self.step_check_switch()

            # Step 4: Click "Далее" button
            self.step_click_next()

            # Step 5: Enter password
            self.step_enter_password()

            # Step 6: Click "Войти" button
            self.step_click_login()

            # Step 7: Handle 2FA if exists
            self.step_handle_2fa()

            # Step 8: Click "ОК" button
            self.step_click_ok()

            self.log_signal.emit("🎉 Login completed successfully!")
            self.log_signal.emit("💡 Browser window left open - close manually when done")

            result = {
                "email": self.email,
                "status": "logged_in"
            }
            self.finished.emit(True, result)

            # Keep browser open
            self.exec()

        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            self.log_signal.emit(f"❌ Login error: {str(e)}")
            self.finished.emit(False, error_msg)

    def setup_cursor_circle(self):
        """Setup visual cursor circle indicator"""
        self.log_signal.emit("🎯 Setting up cursor indicator...")

        # Add CSS for cursor
        self.driver.run_js("""
            var style = document.createElement('style');
            style.textContent = `
                #bot-cursor {
                    position: fixed;
                    width: 26px;
                    height: 26px;
                    border-radius: 50%;
                    border: 2px solid red;
                    box-sizing: border-box;
                    pointer-events: none;
                    z-index: 999999;
                    transform: translate(-50%, -50%);
                }
            `;
            document.head.appendChild(style);
        """)

        # Create cursor element and move function
        self.driver.run_js("""
            if (!document.getElementById('bot-cursor')) {
                var d = document.createElement('div');
                d.id = 'bot-cursor';
                d.style.left = '50%';
                d.style.top = '50%';
                document.body.appendChild(d);
            }
            window.botCursorMove = function(x, y) {
                var el = document.getElementById('bot-cursor');
                if (!el) return;
                el.style.left = x + 'px';
                el.style.top = y + 'px';
            };
        """)

        self.cursor_pos = (640, 360)

    def human_mouse_move(self, end, duration_sec=None):
        """Smooth cursor movement with jitter for human-like behavior"""
        import time

        if duration_sec is None:
            duration_sec = self.MOUSE_MOVE_DURATION_MAIN

        steps = max(50, int(duration_sec / self.MOUSE_STEP_INTERVAL_SEC))
        x1, y1 = self.cursor_pos
        x2, y2 = end

        for i in range(steps + 1):
            t = i / steps
            # Ease in-out
            t_eased = 3 * t * t - 2 * t * t * t

            x = x1 + (x2 - x1) * t_eased + random.uniform(-self.CURSOR_JITTER_PX, self.CURSOR_JITTER_PX)
            y = y1 + (y2 - y1) * t_eased + random.uniform(-self.CURSOR_JITTER_PX, self.CURSOR_JITTER_PX)

            # Move cursor visually
            self.driver.run_js(f"window.botCursorMove({x}, {y})")

            time.sleep(random.uniform(
                self.MOUSE_STEP_INTERVAL_SEC * 0.7,
                self.MOUSE_STEP_INTERVAL_SEC * 1.3
            ))

        self.cursor_pos = end

    def human_type(self, selector, text, total_time=None):
        """Type text character by character with random delays - React compatible"""
        if total_time is None:
            total_time = self.HUMAN_TYPE_TOTAL_TIME_SEC
        if not text:
            return

        base_delay = total_time / len(text)
        for ch in text:
            delay = random.uniform(base_delay * 0.5, base_delay * 1.5)
            # Type single character using native setter for React compatibility
            escaped_char = ch.replace("\\", "\\\\").replace("'", "\\'")
            self.driver.run_js(f"""
                var el = document.querySelector('{selector}');
                if (el) {{
                    // Use native setter to properly trigger React state update
                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeInputValueSetter.call(el, el.value + '{escaped_char}');

                    // Dispatch events that React listens to
                    el.dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
                    el.dispatchEvent(new Event('change', {{ bubbles: true, cancelable: true }}));
                }}
            """)
            time.sleep(delay)

    def click_element_by_selector(self, selector, duration=None):
        """Move to element and click with human-like behavior"""
        import time

        if duration is None:
            duration = self.MOUSE_MOVE_DURATION_TAB

        # Get element bounding box
        box = self.driver.run_js(f"""
            var el = document.querySelector('{selector}');
            if (!el) return null;
            var rect = el.getBoundingClientRect();
            return {{
                x: rect.left,
                y: rect.top,
                width: rect.width,
                height: rect.height
            }};
        """)

        if not box:
            raise Exception(f"Element not found: {selector}")

        tx = box["x"] + box["width"] / 2
        ty = box["y"] + box["height"] / 2

        # Move cursor to element
        self.human_mouse_move((tx, ty), duration)

        # Click using JavaScript
        self.driver.run_js(f"""
            var el = document.querySelector('{selector}');
            if (el) {{
                el.click();
            }}
        """)

    def step_enter_email(self):
        """Step 2: Enter email in the input field"""
        import time

        self.log_signal.emit("📧 Finding email input field...")

        selector = "#emailInputwwwmexccom"

        # Wait for element
        self.driver.sleep(2)

        # Check if element exists
        exists = self.driver.run_js(f"return !!document.querySelector('{selector}')")
        if not exists:
            raise Exception("Email input field not found")

        # Click on input
        self.click_element_by_selector(selector)

        # Check if input has value and clear it
        current_value = self.driver.run_js(f"return document.querySelector('{selector}').value")
        if current_value:
            self.log_signal.emit("🔄 Clearing existing email value...")
            self.driver.run_js(f"""
                var el = document.querySelector('{selector}');
                el.select();
            """)
            time.sleep(0.2)
            self.driver.run_js(f"document.querySelector('{selector}').value = ''")
            time.sleep(0.3)

        # Type email with human-like behavior
        self.log_signal.emit(f"⌨️ Typing email: {self.email}")
        self.human_type(selector, self.email)

        self.log_signal.emit("⏳ Waiting 4 seconds...")
        time.sleep(4)

    def step_check_switch(self):
        """Step 3: Check switch state and click if needed"""
        import time

        self.log_signal.emit("🔘 Checking switch state...")

        # Check if switch is already checked
        is_checked = self.driver.run_js("""
            var sw = document.querySelector('button[role="switch"].ant-switch-small');
            return sw ? sw.getAttribute('aria-checked') === 'true' : null;
        """)

        if is_checked is None:
            self.log_signal.emit("⚠️ Switch not found, continuing...")
        elif is_checked:
            self.log_signal.emit("✅ Switch already enabled, skipping...")
        else:
            self.log_signal.emit("🔘 Clicking switch to enable...")
            self.click_element_by_selector('button[role="switch"].ant-switch-small', self.MOUSE_MOVE_DURATION_SHORT)

        self.log_signal.emit("⏳ Waiting 3 seconds...")
        time.sleep(3)

    def step_click_next(self):
        """Step 4: Click 'Далее' button and wait 30 seconds with countdown"""
        import time

        self.log_signal.emit("➡️ Finding 'Далее' button...")

        selector = 'button[type="submit"].ant-btn-v2-primary'

        self.log_signal.emit("🖱️ Clicking 'Далее'...")
        self.click_element_by_selector(selector)

        # Wait 30 seconds with countdown
        self.log_signal.emit("⏳ Waiting 30 seconds (for captcha if needed)...")
        for i in range(6):
            remaining = 30 - (i * 5)
            self.log_signal.emit(f"   ⏳ {remaining} seconds left...")
            time.sleep(5)

    def step_enter_password(self):
        """Step 5: Enter password"""
        import time

        self.log_signal.emit("🔑 Finding password input field...")

        selector = "#passwordInput"

        # Wait for element
        self.driver.sleep(2)

        # Check if element exists
        exists = self.driver.run_js(f"return !!document.querySelector('{selector}')")
        if not exists:
            raise Exception("Password input field not found")

        # Click on input
        self.click_element_by_selector(selector)
        time.sleep(0.3)

        # Type password with human-like behavior
        self.log_signal.emit("⌨️ Typing password...")
        self.human_type(selector, self.password)

        self.log_signal.emit("⏳ Waiting 5 seconds...")
        time.sleep(5)

    def step_click_login(self):
        """Step 6: Click 'Войти' button"""
        import time

        self.log_signal.emit("🔓 Finding 'Войти' button...")

        selector = 'button[type="submit"].ant-btn-v2-primary'

        self.log_signal.emit("🖱️ Clicking 'Войти'...")
        self.click_element_by_selector(selector)

        self.log_signal.emit("⏳ Waiting 10 seconds...")
        time.sleep(10)

    def step_handle_2fa(self):
        """Step 7: Handle 2FA if authenticator code is required"""
        self.log_signal.emit("🔐 Checking for 2FA requirement...")

        # Check if 2FA title exists
        has_2fa = self.driver.run_js("""
            return !!document.querySelector('div._captchaTitle_uq1a0_91');
        """)

        if not has_2fa:
            self.log_signal.emit("ℹ️ No 2FA required, skipping...")
            return

        self.log_signal.emit("🔐 2FA required, generating code...")

        # Generate 2FA code
        totp = pyotp.TOTP(self.twofa_secret)
        code_2fa = totp.now()
        self.log_signal.emit(f"✅ 2FA code generated: {code_2fa}")

        # Find 2FA input field
        selector = 'input[data-id="0"]'

        # Click on input field
        self.click_element_by_selector(selector)
        time.sleep(0.3)

        # Copy 2FA code to clipboard and paste with Ctrl+V
        self.log_signal.emit("📋 Pasting 2FA code (Ctrl+V)...")

        # Copy code to clipboard using JavaScript
        self.driver.run_js(f"""
            navigator.clipboard.writeText('{code_2fa}');
        """)
        time.sleep(0.2)

        # Focus the input and select all (in case there's existing content)
        self.driver.run_js(f"""
            var el = document.querySelector('{selector}');
            if (el) {{
                el.focus();
                el.select();
            }}
        """)
        time.sleep(0.1)

        # Paste using Ctrl+V via JavaScript keyboard event simulation
        self.driver.run_js(f"""
            var el = document.querySelector('{selector}');
            if (el) {{
                // Set value directly and trigger events for React
                var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                nativeInputValueSetter.call(el, '{code_2fa}');
                el.dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true, cancelable: true }}));
            }}
        """)

        self.log_signal.emit(f"✅ 2FA code pasted: {code_2fa}")
        time.sleep(0.5)

        # Click the switch button if exists
        has_switch = self.driver.run_js("""
            return !!document.querySelector('button[role="switch"]._switchBtn_uq1a0_28');
        """)
        if has_switch:
            self.log_signal.emit("🔘 Clicking 2FA switch...")
            self.click_element_by_selector('button[role="switch"]._switchBtn_uq1a0_28', self.MOUSE_MOVE_DURATION_SHORT)

        self.log_signal.emit("⏳ Waiting 10 seconds...")
        time.sleep(10)

    def step_click_ok(self):
        """Step 8: Click 'ОК' button"""
        import time

        self.log_signal.emit("✅ Finding 'ОК' button...")

        selector = 'button[type="button"].ant-btn-v2-primary'

        # Check if button exists
        exists = self.driver.run_js(f"return !!document.querySelector('{selector}')")
        if exists:
            self.log_signal.emit("🖱️ Clicking 'ОК'...")
            self.click_element_by_selector(selector)
        else:
            self.log_signal.emit("ℹ️ 'ОК' button not found, may not be needed...")

        self.log_signal.emit("⏳ Waiting 25 seconds...")
        time.sleep(25)


class MexcShortThread(QThread):
    """
    Thread for MEXC Short position automation using anti-detect browser with human-like behavior
    Supports both Market and Limit orders
    """
    finished = Signal(bool, object)  # success, result/error
    log_signal = Signal(str)

    # Configuration constants (same as MexcLoginThread)
    MOUSE_MOVE_DURATION_MAIN = 1.2
    MOUSE_MOVE_DURATION_SHORT = 0.8
    MOUSE_MOVE_DURATION_TAB = 1.0
    MOUSE_STEP_INTERVAL_SEC = 0.02
    CURSOR_JITTER_PX = 0.95
    HUMAN_TYPE_TOTAL_TIME_SEC = 2.0

    def __init__(self, scraper_runner, profile_name, email, token_link, position_percent, order_type="Market", limit_price="", headless=False):
        super().__init__()
        self.scraper_runner = scraper_runner
        self.profile_name = profile_name
        self.email = email
        self.token_link = token_link
        self.position_percent = position_percent
        self.order_type = order_type  # "Market" or "Limit"
        self.limit_price = limit_price  # Price for Limit orders
        self.headless = headless
        self.row = None
        self.driver = None
        self.cursor_pos = (640, 360)

    def run(self):
        """Run the short position process using anti-detect browser"""
        try:
            self.log_signal.emit(f"📉 Starting MEXC Short position for: {self.email}")
            self.log_signal.emit(f"🔗 Token link: {self.token_link}")
            self.log_signal.emit(f"📊 Position: {self.position_percent}%")
            self.log_signal.emit(f"📋 Order type: {self.order_type}")
            if self.order_type == "Limit":
                self.log_signal.emit(f"💰 Limit price: {self.limit_price}")

            # Get proxy for profile
            proxy, proxy_display = self.scraper_runner.get_proxy_for_profile(self.profile_name)

            self.log_signal.emit("🔧 Launching anti-detect browser...")

            # Update last used
            self.scraper_runner.profile_manager.update_last_used(self.profile_name)

            # Create driver config
            driver_config = {
                'profile': self.profile_name,
                'headless': self.headless
            }

            if proxy:
                driver_config['proxy'] = proxy
                self.log_signal.emit(f"🌐 Using proxy: {proxy_display}")

            # Create anti-detect browser
            self.driver = Driver(**driver_config)

            # Step 1: Navigate to token page
            self.step_load_token_page()

            # Step 2: Close popups (up to 10 times)
            self.step_close_popups()

            # Step 3: Click Market or Limit tab based on order type
            if self.order_type == "Limit":
                self.step_click_limit_tab()
                # Step 4: Enter limit price
                self.step_enter_limit_price()
            else:
                self.step_click_market_tab()

            # Step 5: Click percentage button
            self.step_click_percentage()

            # Step 6: Click "Открыть Шорт" button
            self.step_click_open_short()

            self.log_signal.emit(f"🎉 SUCCESS - Short {self.order_type} position opened for: {self.email}")
            self.log_signal.emit("💡 Browser window left open - close manually when done")

            result = {
                "email": self.email,
                "status": "short_opened",
                "position": self.position_percent,
                "order_type": self.order_type
            }
            self.finished.emit(True, result)

            # Keep browser open
            self.exec()

        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            self.log_signal.emit(f"❌ Short position error: {str(e)}")
            self.finished.emit(False, error_msg)

    def setup_cursor_circle(self):
        """Setup visual cursor circle indicator"""
        self.log_signal.emit("🎯 Setting up cursor indicator...")

        # Add CSS for cursor
        self.driver.run_js("""
            var style = document.createElement('style');
            style.textContent = `
                #bot-cursor {
                    position: fixed;
                    width: 26px;
                    height: 26px;
                    border-radius: 50%;
                    border: 2px solid red;
                    box-sizing: border-box;
                    pointer-events: none;
                    z-index: 999999;
                    transform: translate(-50%, -50%);
                }
            `;
            document.head.appendChild(style);
        """)

        # Create cursor element and move function
        self.driver.run_js("""
            if (!document.getElementById('bot-cursor')) {
                var d = document.createElement('div');
                d.id = 'bot-cursor';
                d.style.left = '50%';
                d.style.top = '50%';
                document.body.appendChild(d);
            }
            window.botCursorMove = function(x, y) {
                var el = document.getElementById('bot-cursor');
                if (!el) return;
                el.style.left = x + 'px';
                el.style.top = y + 'px';
            };
        """)

        self.cursor_pos = (640, 360)

    def human_mouse_move(self, end, duration_sec=None):
        """Smooth cursor movement with jitter for human-like behavior"""
        if duration_sec is None:
            duration_sec = self.MOUSE_MOVE_DURATION_MAIN

        steps = max(50, int(duration_sec / self.MOUSE_STEP_INTERVAL_SEC))
        x1, y1 = self.cursor_pos
        x2, y2 = end

        for i in range(steps + 1):
            t = i / steps
            # Ease in-out
            t_eased = 3 * t * t - 2 * t * t * t

            x = x1 + (x2 - x1) * t_eased + random.uniform(-self.CURSOR_JITTER_PX, self.CURSOR_JITTER_PX)
            y = y1 + (y2 - y1) * t_eased + random.uniform(-self.CURSOR_JITTER_PX, self.CURSOR_JITTER_PX)

            # Move cursor visually
            self.driver.run_js(f"window.botCursorMove({x}, {y})")

            time.sleep(random.uniform(
                self.MOUSE_STEP_INTERVAL_SEC * 0.7,
                self.MOUSE_STEP_INTERVAL_SEC * 1.3
            ))

        self.cursor_pos = end

    def click_element_by_selector(self, selector, duration=None):
        """Move to element and click with human-like behavior"""
        if duration is None:
            duration = self.MOUSE_MOVE_DURATION_TAB

        # Get element bounding box
        box = self.driver.run_js(f"""
            var el = document.querySelector('{selector}');
            if (!el) return null;
            var rect = el.getBoundingClientRect();
            return {{
                x: rect.left,
                y: rect.top,
                width: rect.width,
                height: rect.height
            }};
        """)

        if not box:
            raise Exception(f"Element not found: {selector}")

        tx = box["x"] + box["width"] / 2
        ty = box["y"] + box["height"] / 2

        # Move cursor to element
        self.human_mouse_move((tx, ty), duration)

        # Click using JavaScript
        self.driver.run_js(f"""
            var el = document.querySelector('{selector}');
            if (el) {{
                el.click();
            }}
        """)

    def click_element_by_js(self, js_selector_code, duration=None):
        """Move to element found by custom JS and click"""
        if duration is None:
            duration = self.MOUSE_MOVE_DURATION_TAB

        # Get element bounding box using custom JS
        box = self.driver.run_js(f"""
            var el = {js_selector_code};
            if (!el) return null;
            var rect = el.getBoundingClientRect();
            return {{
                x: rect.left,
                y: rect.top,
                width: rect.width,
                height: rect.height
            }};
        """)

        if not box:
            return False

        tx = box["x"] + box["width"] / 2
        ty = box["y"] + box["height"] / 2

        # Move cursor to element
        self.human_mouse_move((tx, ty), duration)

        # Click using JavaScript
        self.driver.run_js(f"""
            var el = {js_selector_code};
            if (el) {{
                el.click();
            }}
        """)

        return True

    def step_load_token_page(self):
        """Step 1: Load the token page and wait 20 seconds"""
        self.log_signal.emit(f"🌐 Opening token page: {self.token_link}")
        self.driver.get(self.token_link)

        # Setup cursor circle after page load
        self.setup_cursor_circle()

        self.log_signal.emit("⏳ Waiting 20 seconds for page to load...")
        time.sleep(20)

    def step_close_popups(self):
        """Step 2: Close popups with X button (up to 10 times)"""
        self.log_signal.emit("🔍 Checking for popups...")

        # SVG path for close button
        close_svg_path = "M512 592.440889l414.890667 414.890667 80.440889-80.440889L592.440889 512l414.890667-414.890667L926.890667 16.668444 512 431.559111 97.109333 16.668444 16.668444 97.109333 431.559111 512 16.668444 926.890667l80.440889 80.440889L512 592.440889z"

        for attempt in range(10):
            # Find close button by SVG path
            close_exists = self.driver.run_js(f"""
                var paths = document.querySelectorAll('path');
                for (var i = 0; i < paths.length; i++) {{
                    if (paths[i].getAttribute('d') === '{close_svg_path}') {{
                        return true;
                    }}
                }}
                return false;
            """)

            if not close_exists:
                self.log_signal.emit(f"✅ No more popups found (checked {attempt + 1} times)")
                break

            self.log_signal.emit(f"🔴 Found popup #{attempt + 1}, closing...")

            # Click the close button (find parent clickable element)
            clicked = self.driver.run_js(f"""
                var paths = document.querySelectorAll('path');
                for (var i = 0; i < paths.length; i++) {{
                    if (paths[i].getAttribute('d') === '{close_svg_path}') {{
                        // Find clickable parent (svg or button)
                        var el = paths[i].closest('svg, button, div[role="button"]');
                        if (el) {{
                            var rect = el.getBoundingClientRect();
                            return {{
                                x: rect.left,
                                y: rect.top,
                                width: rect.width,
                                height: rect.height
                            }};
                        }}
                    }}
                }}
                return null;
            """)

            if clicked:
                tx = clicked["x"] + clicked["width"] / 2
                ty = clicked["y"] + clicked["height"] / 2

                # Move and click
                self.human_mouse_move((tx, ty), self.MOUSE_MOVE_DURATION_SHORT)

                self.driver.run_js(f"""
                    var paths = document.querySelectorAll('path');
                    for (var i = 0; i < paths.length; i++) {{
                        if (paths[i].getAttribute('d') === '{close_svg_path}') {{
                            // Try to find clickable parent (button first, then svg)
                            var el = paths[i].closest('button, div[role="button"]');
                            if (el && typeof el.click === 'function') {{
                                el.click();
                                break;
                            }}
                            // If no button found, try clicking the svg or its parent
                            el = paths[i].closest('svg');
                            if (el) {{
                                // SVG doesn't have click(), use dispatchEvent
                                var clickEvent = new MouseEvent('click', {{
                                    bubbles: true,
                                    cancelable: true,
                                    view: window
                                }});
                                el.dispatchEvent(clickEvent);
                                break;
                            }}
                        }}
                    }}
                """)

                self.log_signal.emit("⏳ Waiting 2 seconds after closing popup...")
                time.sleep(2)
            else:
                self.log_signal.emit("⚠️ Could not find clickable close element")
                break

    def step_click_market_tab(self):
        """Step 3: Click 'Маркет' (Market) tab"""
        self.log_signal.emit("📊 Clicking 'Маркет' tab...")

        # Find span with text "Маркет"
        js_selector = "Array.from(document.querySelectorAll('span')).find(el => el.textContent.trim() === 'Маркет')"

        clicked = self.click_element_by_js(js_selector, self.MOUSE_MOVE_DURATION_TAB)

        if not clicked:
            raise Exception("'Маркет' tab not found")

        self.log_signal.emit("⏳ Waiting 2 seconds...")
        time.sleep(2)

    def step_click_limit_tab(self):
        """Step 3: Click 'Лимит' (Limit) tab"""
        self.log_signal.emit("📊 Clicking 'Лимит' tab...")

        # Find span with class EntrustTabs_buttonTextOne__Jx1oT and text "Лимит"
        js_selector = "document.querySelector('span.EntrustTabs_buttonTextOne__Jx1oT') || Array.from(document.querySelectorAll('span')).find(el => el.textContent.trim() === 'Лимит')"

        clicked = self.click_element_by_js(js_selector, self.MOUSE_MOVE_DURATION_TAB)

        if not clicked:
            raise Exception("'Лимит' tab not found")

        self.log_signal.emit("⏳ Waiting 2 seconds...")
        time.sleep(2)

    def step_enter_limit_price(self):
        """Step 4: Enter limit price in the price input field"""
        self.log_signal.emit(f"💰 Entering limit price: {self.limit_price}")

        # Find the price input field
        selector = 'input.ant-input[type="text"]'

        # Click on the input field
        box = self.driver.run_js(f"""
            var el = document.querySelector('{selector}');
            if (!el) return null;
            var rect = el.getBoundingClientRect();
            return {{
                x: rect.left,
                y: rect.top,
                width: rect.width,
                height: rect.height
            }};
        """)

        if not box:
            raise Exception("Price input field not found")

        tx = box["x"] + box["width"] / 2
        ty = box["y"] + box["height"] / 2

        # Move cursor to input
        self.human_mouse_move((tx, ty), self.MOUSE_MOVE_DURATION_TAB)

        # Click on input
        self.driver.run_js(f"""
            var el = document.querySelector('{selector}');
            if (el) el.click();
        """)

        self.log_signal.emit("⏳ Waiting 1 second...")
        time.sleep(1)

        # Select all text (Ctrl+A) and delete (Backspace)
        self.log_signal.emit("🔄 Clearing existing price (Ctrl+A + Backspace)...")
        self.driver.run_js(f"""
            var el = document.querySelector('{selector}');
            if (el) {{
                el.focus();
                el.select();
            }}
        """)
        time.sleep(0.2)

        # Clear the field using native setter
        self.driver.run_js(f"""
            var el = document.querySelector('{selector}');
            if (el) {{
                var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                nativeInputValueSetter.call(el, '');
                el.dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true, cancelable: true }}));
            }}
        """)
        time.sleep(0.3)

        # Type the limit price with human-like behavior
        self.log_signal.emit(f"⌨️ Typing price: {self.limit_price}")
        self.human_type_price(selector, self.limit_price)

        self.log_signal.emit("⏳ Waiting 2 seconds...")
        time.sleep(2)

    def human_type_price(self, selector, text, total_time=None):
        """Type text character by character with random delays - React compatible"""
        if total_time is None:
            total_time = self.HUMAN_TYPE_TOTAL_TIME_SEC
        if not text:
            return

        base_delay = total_time / len(text)
        for ch in text:
            delay = random.uniform(base_delay * 0.5, base_delay * 1.5)
            # Type single character using native setter for React compatibility
            escaped_char = ch.replace("\\", "\\\\").replace("'", "\\'")
            self.driver.run_js(f"""
                var el = document.querySelector('{selector}');
                if (el) {{
                    // Use native setter to properly trigger React state update
                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeInputValueSetter.call(el, el.value + '{escaped_char}');

                    // Dispatch events that React listens to
                    el.dispatchEvent(new Event('input', {{ bubbles: true, cancelable: true }}));
                    el.dispatchEvent(new Event('change', {{ bubbles: true, cancelable: true }}));
                }}
            """)
            time.sleep(delay)

    def step_click_percentage(self):
        """Step 5: Click percentage button (25%, 50%, 75%, or 100%)"""
        percent = self.position_percent

        # Map percentage to left style value
        percent_map = {
            "25": "25%",
            "50": "50%",
            "75": "75%",
            "100": "100%"
        }

        if percent not in percent_map:
            self.log_signal.emit(f"⚠️ Invalid percentage: {percent}%, using 25%")
            percent = "25"

        left_value = percent_map[percent]
        self.log_signal.emit(f"📊 Clicking {percent}% position...")

        # Find the percentage span by its left style and text content
        js_selector = f"""
            Array.from(document.querySelectorAll('span.ant-slider-v2-mark-text')).find(el =>
                el.style.left === '{left_value}' && el.textContent.trim() === '{percent}%'
            )
        """

        clicked = self.click_element_by_js(js_selector, self.MOUSE_MOVE_DURATION_TAB)

        if not clicked:
            # Try alternative: find by text content only
            self.log_signal.emit(f"⚠️ Primary selector failed, trying by text...")
            js_selector_alt = f"""
                Array.from(document.querySelectorAll('span.ant-slider-v2-mark-text')).find(el =>
                    el.textContent.trim() === '{percent}%'
                )
            """
            clicked = self.click_element_by_js(js_selector_alt, self.MOUSE_MOVE_DURATION_TAB)

        if not clicked:
            raise Exception(f"Percentage button '{percent}%' not found")

        self.log_signal.emit("⏳ Waiting 5 seconds...")
        time.sleep(5)

    def step_click_open_short(self):
        """Step 6: Click 'Открыть Шорт' button"""
        self.log_signal.emit("📉 Clicking 'Открыть Шорт' button...")

        # Find div with exact text "Открыть Шорт"
        js_selector = "Array.from(document.querySelectorAll('div')).find(el => el.textContent.trim() === 'Открыть Шорт')"

        clicked = self.click_element_by_js(js_selector, self.MOUSE_MOVE_DURATION_TAB)

        if not clicked:
            raise Exception("'Открыть Шорт' button not found")

        self.log_signal.emit("⏳ Waiting 5 seconds...")
        time.sleep(5)


class MexcLongThread(QThread):
    """
    Thread for MEXC Long position automation using anti-detect browser with human-like behavior
    """
    finished = Signal(bool, object)  # success, result/error
    log_signal = Signal(str)

    # Configuration constants (same as MexcShortThread)
    MOUSE_MOVE_DURATION_MAIN = 1.2
    MOUSE_MOVE_DURATION_SHORT = 0.8
    MOUSE_MOVE_DURATION_TAB = 1.0
    MOUSE_STEP_INTERVAL_SEC = 0.02
    CURSOR_JITTER_PX = 0.95

    def __init__(self, scraper_runner, profile_name, email, token_link, position_percent, headless=False):
        super().__init__()
        self.scraper_runner = scraper_runner
        self.profile_name = profile_name
        self.email = email
        self.token_link = token_link
        self.position_percent = position_percent
        self.headless = headless
        self.row = None
        self.driver = None
        self.cursor_pos = (640, 360)

    def run(self):
        """Run the long position process using anti-detect browser"""
        try:
            self.log_signal.emit(f"📈 Starting MEXC Long position for: {self.email}")
            self.log_signal.emit(f"🔗 Token link: {self.token_link}")
            self.log_signal.emit(f"📊 Position: {self.position_percent}%")

            # Get proxy for profile
            proxy, proxy_display = self.scraper_runner.get_proxy_for_profile(self.profile_name)

            self.log_signal.emit("🔧 Launching anti-detect browser...")

            # Update last used
            self.scraper_runner.profile_manager.update_last_used(self.profile_name)

            # Create driver config
            driver_config = {
                'profile': self.profile_name,
                'headless': self.headless
            }

            if proxy:
                driver_config['proxy'] = proxy
                self.log_signal.emit(f"🌐 Using proxy: {proxy_display}")

            # Create anti-detect browser
            self.driver = Driver(**driver_config)

            # Step 1: Navigate to token page
            self.step_load_token_page()

            # Step 2: Close popups (up to 10 times)
            self.step_close_popups()

            # Step 3: Click Market tab
            self.step_click_market_tab()

            # Step 4: Click percentage button
            self.step_click_percentage()

            # Step 5: Click "Открыть Лонг" button
            self.step_click_open_long()

            self.log_signal.emit(f"🎉 SUCCESS - Long position opened for: {self.email}")
            self.log_signal.emit("💡 Browser window left open - close manually when done")

            result = {
                "email": self.email,
                "status": "long_opened",
                "position": self.position_percent
            }
            self.finished.emit(True, result)

            # Keep browser open
            self.exec()

        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            self.log_signal.emit(f"❌ Long position error: {str(e)}")
            self.finished.emit(False, error_msg)

    def setup_cursor_circle(self):
        """Setup visual cursor circle indicator"""
        self.log_signal.emit("🎯 Setting up cursor indicator...")

        # Add CSS for cursor
        self.driver.run_js("""
            var style = document.createElement('style');
            style.textContent = `
                #bot-cursor {
                    position: fixed;
                    width: 26px;
                    height: 26px;
                    border-radius: 50%;
                    border: 2px solid red;
                    box-sizing: border-box;
                    pointer-events: none;
                    z-index: 999999;
                    transform: translate(-50%, -50%);
                }
            `;
            document.head.appendChild(style);
        """)

        # Create cursor element and move function
        self.driver.run_js("""
            if (!document.getElementById('bot-cursor')) {
                var d = document.createElement('div');
                d.id = 'bot-cursor';
                d.style.left = '50%';
                d.style.top = '50%';
                document.body.appendChild(d);
            }
            window.botCursorMove = function(x, y) {
                var el = document.getElementById('bot-cursor');
                if (!el) return;
                el.style.left = x + 'px';
                el.style.top = y + 'px';
            };
        """)

        self.cursor_pos = (640, 360)

    def human_mouse_move(self, end, duration_sec=None):
        """Smooth cursor movement with jitter for human-like behavior"""
        if duration_sec is None:
            duration_sec = self.MOUSE_MOVE_DURATION_MAIN

        steps = max(50, int(duration_sec / self.MOUSE_STEP_INTERVAL_SEC))
        x1, y1 = self.cursor_pos
        x2, y2 = end

        for i in range(steps + 1):
            t = i / steps
            # Ease in-out
            t_eased = 3 * t * t - 2 * t * t * t

            x = x1 + (x2 - x1) * t_eased + random.uniform(-self.CURSOR_JITTER_PX, self.CURSOR_JITTER_PX)
            y = y1 + (y2 - y1) * t_eased + random.uniform(-self.CURSOR_JITTER_PX, self.CURSOR_JITTER_PX)

            # Move cursor visually
            self.driver.run_js(f"window.botCursorMove({x}, {y})")

            time.sleep(random.uniform(
                self.MOUSE_STEP_INTERVAL_SEC * 0.7,
                self.MOUSE_STEP_INTERVAL_SEC * 1.3
            ))

        self.cursor_pos = end

    def click_element_by_js(self, js_selector_code, duration=None):
        """Move to element found by custom JS and click"""
        if duration is None:
            duration = self.MOUSE_MOVE_DURATION_TAB

        # Get element bounding box using custom JS
        box = self.driver.run_js(f"""
            var el = {js_selector_code};
            if (!el) return null;
            var rect = el.getBoundingClientRect();
            return {{
                x: rect.left,
                y: rect.top,
                width: rect.width,
                height: rect.height
            }};
        """)

        if not box:
            return False

        tx = box["x"] + box["width"] / 2
        ty = box["y"] + box["height"] / 2

        # Move cursor to element
        self.human_mouse_move((tx, ty), duration)

        # Click using JavaScript
        self.driver.run_js(f"""
            var el = {js_selector_code};
            if (el) {{
                el.click();
            }}
        """)

        return True

    def step_load_token_page(self):
        """Step 1: Load the token page and wait 20 seconds"""
        self.log_signal.emit(f"🌐 Opening token page: {self.token_link}")
        self.driver.get(self.token_link)

        # Setup cursor circle after page load
        self.setup_cursor_circle()

        self.log_signal.emit("⏳ Waiting 20 seconds for page to load...")
        time.sleep(20)

    def step_close_popups(self):
        """Step 2: Close popups with X button (up to 10 times)"""
        self.log_signal.emit("🔍 Checking for popups...")

        # SVG path for close button
        close_svg_path = "M512 592.440889l414.890667 414.890667 80.440889-80.440889L592.440889 512l414.890667-414.890667L926.890667 16.668444 512 431.559111 97.109333 16.668444 16.668444 97.109333 431.559111 512 16.668444 926.890667l80.440889 80.440889L512 592.440889z"

        for attempt in range(10):
            # Find close button by SVG path
            close_exists = self.driver.run_js(f"""
                var paths = document.querySelectorAll('path');
                for (var i = 0; i < paths.length; i++) {{
                    if (paths[i].getAttribute('d') === '{close_svg_path}') {{
                        return true;
                    }}
                }}
                return false;
            """)

            if not close_exists:
                self.log_signal.emit(f"✅ No more popups found (checked {attempt + 1} times)")
                break

            self.log_signal.emit(f"🔴 Found popup #{attempt + 1}, closing...")

            # Click the close button (find parent clickable element)
            clicked = self.driver.run_js(f"""
                var paths = document.querySelectorAll('path');
                for (var i = 0; i < paths.length; i++) {{
                    if (paths[i].getAttribute('d') === '{close_svg_path}') {{
                        // Find clickable parent (svg or button)
                        var el = paths[i].closest('svg, button, div[role="button"]');
                        if (el) {{
                            var rect = el.getBoundingClientRect();
                            return {{
                                x: rect.left,
                                y: rect.top,
                                width: rect.width,
                                height: rect.height
                            }};
                        }}
                    }}
                }}
                return null;
            """)

            if clicked:
                tx = clicked["x"] + clicked["width"] / 2
                ty = clicked["y"] + clicked["height"] / 2

                # Move and click
                self.human_mouse_move((tx, ty), self.MOUSE_MOVE_DURATION_SHORT)

                self.driver.run_js(f"""
                    var paths = document.querySelectorAll('path');
                    for (var i = 0; i < paths.length; i++) {{
                        if (paths[i].getAttribute('d') === '{close_svg_path}') {{
                            // Try to find clickable parent (button first, then svg)
                            var el = paths[i].closest('button, div[role="button"]');
                            if (el && typeof el.click === 'function') {{
                                el.click();
                                break;
                            }}
                            // If no button found, try clicking the svg or its parent
                            el = paths[i].closest('svg');
                            if (el) {{
                                // SVG doesn't have click(), use dispatchEvent
                                var clickEvent = new MouseEvent('click', {{
                                    bubbles: true,
                                    cancelable: true,
                                    view: window
                                }});
                                el.dispatchEvent(clickEvent);
                                break;
                            }}
                        }}
                    }}
                """)

                self.log_signal.emit("⏳ Waiting 2 seconds after closing popup...")
                time.sleep(2)
            else:
                self.log_signal.emit("⚠️ Could not find clickable close element")
                break

    def step_click_market_tab(self):
        """Step 3: Click 'Маркет' (Market) tab"""
        self.log_signal.emit("📊 Clicking 'Маркет' tab...")

        # Find span with text "Маркет"
        js_selector = "Array.from(document.querySelectorAll('span')).find(el => el.textContent.trim() === 'Маркет')"

        clicked = self.click_element_by_js(js_selector, self.MOUSE_MOVE_DURATION_TAB)

        if not clicked:
            raise Exception("'Маркет' tab not found")

        self.log_signal.emit("⏳ Waiting 2 seconds...")
        time.sleep(2)

    def step_click_percentage(self):
        """Step 4: Click percentage button (25%, 50%, 75%, or 100%)"""
        percent = self.position_percent

        # Map percentage to left style value
        percent_map = {
            "25": "25%",
            "50": "50%",
            "75": "75%",
            "100": "100%"
        }

        if percent not in percent_map:
            self.log_signal.emit(f"⚠️ Invalid percentage: {percent}%, using 25%")
            percent = "25"

        left_value = percent_map[percent]
        self.log_signal.emit(f"📊 Clicking {percent}% position...")

        # Find the percentage span by its left style and text content
        js_selector = f"""
            Array.from(document.querySelectorAll('span.ant-slider-v2-mark-text')).find(el =>
                el.style.left === '{left_value}' && el.textContent.trim() === '{percent}%'
            )
        """

        clicked = self.click_element_by_js(js_selector, self.MOUSE_MOVE_DURATION_TAB)

        if not clicked:
            # Try alternative: find by text content only
            self.log_signal.emit(f"⚠️ Primary selector failed, trying by text...")
            js_selector_alt = f"""
                Array.from(document.querySelectorAll('span.ant-slider-v2-mark-text')).find(el =>
                    el.textContent.trim() === '{percent}%'
                )
            """
            clicked = self.click_element_by_js(js_selector_alt, self.MOUSE_MOVE_DURATION_TAB)

        if not clicked:
            raise Exception(f"Percentage button '{percent}%' not found")

        self.log_signal.emit("⏳ Waiting 5 seconds...")
        time.sleep(5)

    def step_click_open_long(self):
        """Step 5: Click 'Открыть Лонг' button"""
        self.log_signal.emit("📈 Clicking 'Открыть Лонг' button...")

        # Find div with exact text "Открыть Лонг"
        js_selector = "Array.from(document.querySelectorAll('div')).find(el => el.textContent.trim() === 'Открыть Лонг')"

        clicked = self.click_element_by_js(js_selector, self.MOUSE_MOVE_DURATION_TAB)

        if not clicked:
            raise Exception("'Открыть Лонг' button not found")

        self.log_signal.emit("⏳ Waiting 5 seconds...")
        time.sleep(5)
