"""
Scraper Runner
Integrates Botasaurus browser automation with profile management
"""
from PySide6.QtCore import QThread, Signal
import sys
import traceback
import re
import asyncio
import random
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
    Thread for MEXC login automation using Playwright with human-like behavior
    """
    finished = Signal(bool, object)  # success, result/error
    log_signal = Signal(str)
    driver_ready = Signal(object, dict)  # For keeping browser open

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
        self.page = None
        self.browser = None
        self.cursor_pos = (640, 360)

    def run(self):
        """Run the async login process"""
        try:
            # Run async code in event loop
            asyncio.run(self.async_login())
        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            self.log_signal.emit(f"❌ Login error: {str(e)}")
            self.finished.emit(False, error_msg)

    async def async_login(self):
        """Main async login process"""
        from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

        self.log_signal.emit("🔐 Starting MEXC login with human-like behavior...")

        async with async_playwright() as p:
            # Get proxy for profile
            proxy, proxy_display = self.scraper_runner.get_proxy_for_profile(self.profile_name)

            # Get profile path for persistent context
            profile_path = self.scraper_runner.profile_manager.get_profile_path(self.profile_name)

            self.log_signal.emit("🔧 Launching browser...")

            # Browser launch options
            launch_args = ["--start-maximized"]

            # Launch browser with persistent context (like manual mode)
            context = await p.chromium.launch_persistent_context(
                profile_path,
                headless=self.headless,
                args=launch_args,
                proxy={"server": proxy} if proxy else None,
                viewport={"width": 1280, "height": 720}
            )

            context.set_default_timeout(15000)
            self.page = await context.new_page()

            if proxy:
                self.log_signal.emit(f"🌐 Using proxy: {proxy_display}")

            try:
                # Step 0: Setup cursor circle
                self.cursor_pos = await self.setup_cursor_circle()

                # Step 1: Navigate to login page
                self.log_signal.emit("🌐 Opening MEXC login page...")
                login_url = "https://www.mexc.com/ru-RU/login?previous=%2Fru-RU%2F"
                try:
                    await self.page.goto(login_url, wait_until="domcontentloaded", timeout=60000)
                except PlaywrightTimeoutError:
                    self.log_signal.emit("⚠️ Page load timeout, continuing...")

                self.log_signal.emit("⏳ Waiting 10 seconds for page to load...")
                await self.page.wait_for_timeout(10000)

                # Step 2: Enter email
                await self.step_enter_email()

                # Step 3: Check and click switch if needed
                await self.step_check_switch()

                # Step 4: Click "Далее" button
                await self.step_click_next()

                # Step 5: Enter password
                await self.step_enter_password()

                # Step 6: Click "Войти" button
                await self.step_click_login()

                # Step 7: Handle 2FA if exists
                await self.step_handle_2fa()

                # Step 8: Click "ОК" button
                await self.step_click_ok()

                self.log_signal.emit("🎉 Login completed successfully!")
                self.log_signal.emit("💡 Browser window left open - close manually when done")

                result = {
                    "email": self.email,
                    "status": "logged_in"
                }
                self.finished.emit(True, result)

                # Keep browser open
                await asyncio.sleep(3600)  # Keep alive for 1 hour

            except Exception as e:
                raise e
            finally:
                pass  # Don't close browser

    async def setup_cursor_circle(self):
        """Setup visual cursor circle indicator"""
        self.log_signal.emit("🎯 Setting up cursor indicator...")

        await self.page.add_style_tag(content="""
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
        """)

        await self.page.evaluate("""
            if (!document.getElementById('bot-cursor')) {
                const d = document.createElement('div');
                d.id = 'bot-cursor';
                d.style.left = '50%';
                d.style.top = '50%';
                document.body.appendChild(d);
            }
            window.botCursorMove = (x, y) => {
                const el = document.getElementById('bot-cursor');
                if (!el) return;
                el.style.left = x + 'px';
                el.style.top = y + 'px';
            };
        """)

        cx, cy = 640, 360
        await self.page.evaluate("(pos) => window.botCursorMove(pos.x, pos.y)", {"x": cx, "y": cy})
        await self.page.mouse.move(cx, cy)
        return (cx, cy)

    async def human_mouse_move(self, end, duration_sec=None):
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

            await self.page.mouse.move(x, y)
            await self.page.evaluate(
                "(pos) => window.botCursorMove(pos.x, pos.y)",
                {"x": x, "y": y}
            )
            await asyncio.sleep(random.uniform(
                self.MOUSE_STEP_INTERVAL_SEC * 0.7,
                self.MOUSE_STEP_INTERVAL_SEC * 1.3
            ))

        self.cursor_pos = end

    async def human_type(self, locator, text, total_time=None):
        """Type text character by character with random delays"""
        if total_time is None:
            total_time = self.HUMAN_TYPE_TOTAL_TIME_SEC
        if not text:
            return

        base_delay = total_time / len(text)
        for ch in text:
            delay = random.uniform(base_delay * 0.5, base_delay * 1.5)
            await locator.type(ch)
            await asyncio.sleep(delay)

    async def click_element(self, locator, duration=None):
        """Move to element and click with human-like behavior"""
        if duration is None:
            duration = self.MOUSE_MOVE_DURATION_TAB

        box = await locator.bounding_box()
        if not box:
            raise Exception("Element bounding box not found")

        tx = box["x"] + box["width"] / 2
        ty = box["y"] + box["height"] / 2

        await self.human_mouse_move((tx, ty), duration)
        await self.page.mouse.click(tx, ty)

    async def step_enter_email(self):
        """Step 2: Enter email in the input field"""
        self.log_signal.emit("📧 Finding email input field...")

        email_input = self.page.locator("#emailInputwwwmexccom")

        try:
            await email_input.wait_for(timeout=10000)
        except:
            raise Exception("Email input field not found")

        # Click on input
        await self.click_element(email_input)

        # Check if input has value and clear it
        current_value = await email_input.input_value()
        if current_value:
            self.log_signal.emit("🔄 Clearing existing email value...")
            await self.page.keyboard.press("Control+A")
            await self.page.keyboard.press("Backspace")
            await asyncio.sleep(0.3)

        # Type email with human-like behavior
        self.log_signal.emit(f"⌨️ Typing email: {self.email}")
        await self.human_type(email_input, self.email)

        self.log_signal.emit("⏳ Waiting 4 seconds...")
        await self.page.wait_for_timeout(4000)

    async def step_check_switch(self):
        """Step 3: Check switch state and click if needed"""
        self.log_signal.emit("🔘 Checking switch state...")

        # Check if switch is already checked (aria-checked="true")
        switch_checked = self.page.locator('button[role="switch"][aria-checked="true"].ant-switch-small')
        switch_unchecked = self.page.locator('button[role="switch"][aria-checked="false"].ant-switch-small')

        try:
            checked_count = await switch_checked.count()
            if checked_count > 0:
                self.log_signal.emit("✅ Switch already enabled, skipping...")
            else:
                unchecked_count = await switch_unchecked.count()
                if unchecked_count > 0:
                    self.log_signal.emit("🔘 Clicking switch to enable...")
                    await self.click_element(switch_unchecked.first, self.MOUSE_MOVE_DURATION_SHORT)
                else:
                    self.log_signal.emit("⚠️ Switch not found, continuing...")
        except:
            self.log_signal.emit("⚠️ Error checking switch, continuing...")

        self.log_signal.emit("⏳ Waiting 3 seconds...")
        await self.page.wait_for_timeout(3000)

    async def step_click_next(self):
        """Step 4: Click 'Далее' button and wait 30 seconds with countdown"""
        self.log_signal.emit("➡️ Finding 'Далее' button...")

        next_button = self.page.locator('button[type="submit"].ant-btn-v2-primary span:has-text("Далее")').first

        try:
            await next_button.wait_for(timeout=10000)
        except:
            # Try alternative selector
            next_button = self.page.locator('button[type="submit"].ant-btn-v2-primary').first
            await next_button.wait_for(timeout=5000)

        self.log_signal.emit("🖱️ Clicking 'Далее'...")
        # Click the parent button
        parent_button = self.page.locator('button[type="submit"].ant-btn-v2-primary').first
        await self.click_element(parent_button)

        # Wait 30 seconds with countdown
        self.log_signal.emit("⏳ Waiting 30 seconds (for captcha if needed)...")
        for i in range(6):
            remaining = 30 - (i * 5)
            self.log_signal.emit(f"   ⏳ {remaining} seconds left...")
            await self.page.wait_for_timeout(5000)

    async def step_enter_password(self):
        """Step 5: Enter password"""
        self.log_signal.emit("🔑 Finding password input field...")

        password_input = self.page.locator("#passwordInput")

        try:
            await password_input.wait_for(timeout=10000)
        except:
            raise Exception("Password input field not found")

        # Click on input
        await self.click_element(password_input)
        await asyncio.sleep(0.3)

        # Type password with human-like behavior
        self.log_signal.emit("⌨️ Typing password...")
        await self.human_type(password_input, self.password)

        self.log_signal.emit("⏳ Waiting 5 seconds...")
        await self.page.wait_for_timeout(5000)

    async def step_click_login(self):
        """Step 6: Click 'Войти' button"""
        self.log_signal.emit("🔓 Finding 'Войти' button...")

        login_button = self.page.locator('button[type="submit"].ant-btn-v2-primary span:has-text("Войти")').first

        try:
            await login_button.wait_for(timeout=10000)
        except:
            # Try alternative selector
            login_button = self.page.locator('button[type="submit"].ant-btn-v2-primary').first
            await login_button.wait_for(timeout=5000)

        self.log_signal.emit("🖱️ Clicking 'Войти'...")
        parent_button = self.page.locator('button[type="submit"].ant-btn-v2-primary').first
        await self.click_element(parent_button)

        self.log_signal.emit("⏳ Waiting 10 seconds...")
        await self.page.wait_for_timeout(10000)

    async def step_handle_2fa(self):
        """Step 7: Handle 2FA if authenticator code is required"""
        self.log_signal.emit("🔐 Checking for 2FA requirement...")

        # Check if 2FA title exists
        twofa_title = self.page.locator('div._captchaTitle_uq1a0_91:has-text("Код аутентификатора")')

        try:
            title_count = await twofa_title.count()
            if title_count == 0:
                self.log_signal.emit("ℹ️ No 2FA required, skipping...")
                return
        except:
            self.log_signal.emit("ℹ️ No 2FA required, skipping...")
            return

        self.log_signal.emit("🔐 2FA required, generating code...")

        # Generate 2FA code
        totp = pyotp.TOTP(self.twofa_secret)
        code_2fa = totp.now()
        self.log_signal.emit(f"✅ 2FA code generated: {code_2fa}")

        # Find 2FA input field (input with data-id="0")
        twofa_input = self.page.locator('input[data-id="0"][type="tel"]').first

        try:
            await twofa_input.wait_for(timeout=5000)
        except:
            raise Exception("2FA input field not found")

        # Click and type 2FA code
        await self.click_element(twofa_input)
        await asyncio.sleep(0.3)

        self.log_signal.emit("⌨️ Typing 2FA code...")
        await self.human_type(twofa_input, code_2fa, total_time=1.5)

        # Click the switch button if exists
        twofa_switch = self.page.locator('button[role="switch"].ant-switch._switchBtn_uq1a0_28')
        try:
            switch_count = await twofa_switch.count()
            if switch_count > 0:
                self.log_signal.emit("🔘 Clicking 2FA switch...")
                await self.click_element(twofa_switch.first, self.MOUSE_MOVE_DURATION_SHORT)
        except:
            self.log_signal.emit("⚠️ 2FA switch not found, continuing...")

        self.log_signal.emit("⏳ Waiting 10 seconds...")
        await self.page.wait_for_timeout(10000)

    async def step_click_ok(self):
        """Step 8: Click 'ОК' button"""
        self.log_signal.emit("✅ Finding 'ОК' button...")

        ok_button = self.page.locator('button[type="button"].ant-btn-v2-primary span:has-text("ОК")').first

        try:
            await ok_button.wait_for(timeout=10000)
            self.log_signal.emit("🖱️ Clicking 'ОК'...")
            parent_button = self.page.locator('button[type="button"].ant-btn-v2-primary').first
            await self.click_element(parent_button)
        except:
            self.log_signal.emit("ℹ️ 'ОК' button not found, may not be needed...")

        self.log_signal.emit("⏳ Waiting 25 seconds...")
        await self.page.wait_for_timeout(25000)
