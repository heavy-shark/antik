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
