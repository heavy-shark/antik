"""
Custom Playwright Inspector with Anti-Detection
Launches browser with stealth settings for recording actions
"""
import sys
import asyncio
from playwright.sync_api import sync_playwright


def launch_inspector(url):
    """
    Launch Playwright browser with anti-detection for element inspection

    Args:
        url: URL to navigate to
    """
    print(f"🎬 Launching Playwright Inspector with anti-detection...")
    print(f"🌐 URL: {url}")
    print(f"🛡️ Anti-detection enabled")
    print()

    with sync_playwright() as p:
        # Launch Chrome with anti-detection arguments
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",  # Use real Chrome browser
            args=[
                '--disable-blink-features=AutomationControlled',  # Remove navigator.webdriver
                '--disable-dev-shm-usage',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-infobars',
                '--window-size=1280,720',
            ]
        )

        # Create context with realistic settings
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
        )

        # Additional stealth: Remove webdriver property
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # Create page
        page = context.new_page()

        print("✅ Browser launched successfully!")
        print()
        print("💡 How to inspect elements and record actions:")
        print("   1. Press F12 to open Chrome DevTools")
        print("   2. Click the 'Select element' icon (Ctrl+Shift+C)")
        print("   3. Click on elements to inspect them")
        print("   4. Right-click element → Copy → Copy selector")
        print("   5. Or use the Elements tab to find CSS selectors")
        print()
        print("🎬 Alternative - Record with Playwright:")
        print("   In DevTools Console, you can test selectors:")
        print("   document.querySelector('your-selector-here')")
        print()
        print("🛡️ Anti-detection features active:")
        print("   • Using real Chrome browser")
        print("   • navigator.webdriver = undefined")
        print("   • Automation flags disabled")
        print()
        print("💡 Browser will stay open - close window when done")
        print()

        # Navigate to URL
        try:
            page.goto(url, wait_until='networkidle', timeout=30000)
            print(f"✅ Navigated to: {url}")
            print(f"✅ Page title: {page.title()}")
        except Exception as e:
            print(f"⚠️ Navigation warning: {e}")
            print(f"⚠️ Page may still be loading...")

        print()
        print("=" * 60)
        print("Browser is ready! Press Ctrl+C in this window to close.")
        print("=" * 60)

        # Keep browser open until user closes it
        try:
            # Wait indefinitely
            while True:
                page.wait_for_timeout(1000)
        except KeyboardInterrupt:
            print("\n👋 Closing browser...")
        except Exception as e:
            print(f"\n⚠️ Browser closed: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python playwright_inspector.py <url>")
        sys.exit(1)

    url = sys.argv[1]
    launch_inspector(url)
