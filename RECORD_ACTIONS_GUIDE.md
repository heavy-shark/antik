# 🎬 Record Actions Feature - Complete Guide

## ✅ NEW FEATURE: Record Actions with Playwright Inspector

You can now launch Playwright Inspector directly from the app to record your actions and get exact selectors for any element on a webpage!

---

## 🎯 What It Does

The **Record Actions** feature:

1. ✅ Launches Playwright Inspector with your profile's proxy
2. ✅ Opens browser at your specified URL
3. ✅ Records all your actions (clicks, typing, navigation)
4. ✅ Generates Python code with exact selectors
5. ✅ Shows element selectors in real-time
6. ✅ Provides "Pick Locator" tool to find any element

---

## 🚀 How to Use

### Step-by-Step:

1. **Launch the app**
   ```
   START_APP.bat
   ```

2. **Go to Profiles tab**

3. **Select a profile** (with or without proxy)

4. **Click the orange button:**
   ```
   🎬 Record Actions (Playwright)
   ```

5. **Enter URL**
   - Dialog appears asking for URL
   - Default: https://www.whatismyip.com/
   - Enter any URL you want to record actions on

6. **Confirm launch**
   - Shows profile, URL, and proxy (if configured)
   - Click "Yes" to continue

7. **Two windows open:**
   - **Browser window** - The actual webpage
   - **Inspector panel** - Recording tool on the side

8. **Record actions:**
   - Click on elements
   - Type in fields
   - Navigate pages
   - All actions recorded automatically

9. **Get selectors:**
   - Inspector shows generated code
   - Copy selectors from the code
   - Use "Pick Locator" (target icon) to find specific elements

10. **Close when done**
    - Close Inspector window
    - Browser window also closes

---

## 📊 What You'll See in Logs

```
🎬 Launching Playwright Inspector for profile: nesterov_88blp_at_rambler_ru
🌐 URL: https://www.whatismyip.com/
🔒 Proxy: socks5://***@5.22.204.238:50101
✅ Using proxy: socks5://user:pass@5.22.204.238:50101
🚀 Launching Playwright Inspector...
✅ Playwright Inspector launched successfully!
💡 Instructions:
   1. Browser window will open with Inspector panel
   2. Click on elements to record actions
   3. Inspector shows generated Python code
   4. Copy the selectors from the Inspector
   5. Use 'Pick Locator' (target icon) to find element selectors
💡 Close the Inspector window when done
```

---

## 🔍 Finding Cookie Button Selector

### Example: Finding "Accept all" button on whatismyip.com

1. **Launch Record Actions** for a profile
2. **Enter URL:** https://www.whatismyip.com/
3. **Wait for page to load** with cookie dialog
4. **Method 1: Click the button**
   - Click "Accept all" button
   - Inspector records the click
   - Copy the selector from Inspector code:
     ```python
     page.get_by_role("button", name="Accept all").click()
     # OR
     page.locator("button").filter(has_text="Accept all").click()
     # OR
     page.click("text=Accept all")
     ```

5. **Method 2: Use Pick Locator**
   - Click the target icon 🎯 in Inspector
   - Hover over "Accept all" button
   - Selector shows in Inspector
   - Click to select
   - Copy the exact selector

---

## 💡 Use Cases

### Use Case 1: Find Cookie Button Selector

**Scenario:** Need exact selector for cookie consent button

**Steps:**
1. Select profile with proxy
2. Click "Record Actions"
3. Enter website URL
4. Use "Pick Locator" tool
5. Click on cookie button
6. Copy selector from Inspector
7. Use selector in your code

### Use Case 2: Record Login Flow

**Scenario:** Need to record complete login sequence

**Steps:**
1. Click "Record Actions"
2. Enter login page URL
3. Fill username field (recorded)
4. Fill password field (recorded)
5. Click login button (recorded)
6. Copy all generated code
7. Adapt code for your script

### Use Case 3: Find Dynamic Element

**Scenario:** Element has changing classes or complex structure

**Steps:**
1. Launch Inspector
2. Navigate to page
3. Use "Pick Locator" tool
4. Click the element
5. Inspector shows robust selector
6. Selector works even if classes change

---

## 🔧 Technical Details

### How It Works:

1. **Command Built:**
   ```bash
   python -m playwright codegen --proxy-server=socks5://5.22.207.9:50101 https://www.whatismyip.com/
   ```

2. **Proxy Integration:**
   - Automatically uses profile's proxy
   - Supports HTTP, HTTPS, SOCKS4, SOCKS5
   - Authenticated proxies supported

3. **Browser Launch:**
   - Opens in new console window (Windows)
   - Opens in new terminal (Mac/Linux)
   - Runs independently from app

4. **Recording:**
   - All actions logged to Inspector
   - Code generated in real-time
   - Multiple selector strategies shown

---

## 📝 Inspector Features

### Main Tools:

1. **Record** 🔴
   - Toggle recording on/off
   - Auto-enabled on launch

2. **Pick Locator** 🎯
   - Click to enter pick mode
   - Click any element to get its selector
   - Most useful for finding specific elements

3. **Assert** ✓
   - Add assertions to verify element state
   - Check visibility, text content, etc.

4. **Copy** 📋
   - Copy all generated code
   - Paste into your script

5. **Clear** 🗑️
   - Clear all recorded actions
   - Start fresh

### Generated Code Examples:

```python
# Click button by text
page.click("text=Accept all")

# Click by role and name
page.get_by_role("button", name="Accept all").click()

# Click by CSS selector
page.click("button.cookie-accept")

# Click by XPath
page.click("xpath=//button[contains(text(), 'Accept')]")

# Type in field
page.fill("#email", "user@example.com")

# Navigate
page.goto("https://example.com")
```

---

## ⚠️ Important Notes

1. **Playwright Must Be Installed:**
   ```bash
   pip install playwright
   python -m playwright install
   ```

2. **Browser Launch:**
   - Inspector opens in separate window
   - Doesn't block the main app
   - Can launch multiple Inspectors

3. **Proxy Format:**
   - App automatically formats proxy correctly
   - Supports authenticated proxies
   - Credentials included if configured

4. **Code Adaptation:**
   - Generated code uses Playwright syntax
   - May need to adapt for Botasaurus Driver
   - Selectors work across both

---

## 🎯 Quick Reference

### Button Location:
- **Tab:** Profiles
- **Row:** 3 (same as Check Proxy)
- **Color:** Orange
- **Icon:** 🎬

### Keyboard Shortcuts in Inspector:
- `Ctrl+C` - Copy code
- `Esc` - Exit pick locator mode
- `F12` - Open browser DevTools

### Common Selectors:
```python
# By text (most flexible)
"text=Accept all"

# By role
"role=button[name='Accept all']"

# By CSS class
".cookie-consent-button"

# By ID
"#accept-cookies"

# By data attribute
"[data-testid='cookie-accept']"
```

---

## 🚨 Troubleshooting

### Problem: "Playwright not installed"

**Solution:**
```bash
pip install playwright
python -m playwright install chrome
```

### Problem: Inspector doesn't open

**Cause:** Playwright not in PATH

**Solution:**
- Restart app after installing Playwright
- Check `python -m playwright --version`

### Problem: Proxy not working

**Cause:** Proxy format incorrect

**Solution:**
- Check profile proxy configuration
- Format: `protocol://ip:port` or `protocol://user:pass@ip:port`

### Problem: Can't find selector

**Cause:** Element in iframe or shadow DOM

**Solution:**
- Use "Pick Locator" tool
- Inspector handles iframes automatically
- May need manual XPath for shadow DOM

---

## ✅ Summary

### What You Get:

✅ **One-click Inspector launch**
✅ **Automatic proxy integration**
✅ **Real-time action recording**
✅ **Multiple selector strategies**
✅ **Pick any element tool**
✅ **Generated Python code**
✅ **Works with any website**

### Perfect For:

✅ Finding cookie button selectors
✅ Recording login flows
✅ Discovering element selectors
✅ Testing proxy connections
✅ Debugging scraping issues
✅ Learning Playwright syntax

---

## 🎉 Ready to Use!

**To record actions right now:**

1. `START_APP.bat`
2. Profiles tab
3. Select any profile
4. Click: `🎬 Record Actions (Playwright)`
5. Enter URL
6. Start recording!

**Simple, powerful, integrated selector discovery!** 🚀

---

## 📚 Learn More

- [Playwright Documentation](https://playwright.dev/)
- [Playwright Selectors Guide](https://playwright.dev/docs/selectors)
- [Botasaurus Documentation](https://github.com/omkarcloud/botasaurus)

---

**Feature added and ready to use!**

The Record Actions button is now available in the Profiles tab, making it easy to discover selectors and record interactions on any website! 🎬
