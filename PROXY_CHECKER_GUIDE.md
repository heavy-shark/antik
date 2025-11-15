# 🔍 Proxy Checker Feature - Complete Guide

## ✅ NEW FEATURE: Verify Proxy IP with whatismyip.com

You can now verify that your proxy is working correctly by checking the IP address!

---

## 🎯 What It Does

The **Check Proxy** feature:

1. ✅ Opens browser with your profile's proxy
2. ✅ Navigates to https://www.whatismyip.com/
3. ✅ Waits 4 seconds for page to load
4. ✅ Extracts the IP shown on the page
5. ✅ Compares it with your proxy IP
6. ✅ Shows popup: "Proxy is similar" or "Proxy mismatch"
7. ✅ Waits 5 seconds after you click OK
8. ✅ Keeps browser open for manual verification

---

## 🚀 How to Use

### Step-by-Step:

1. **Launch the app**
   ```
   START_APP.bat
   ```

2. **Go to Profiles tab**

3. **Select a profile** (that has a proxy configured)

4. **Click the blue button:**
   ```
   🔍 Check Proxy (whatismyip.com)
   ```

5. **Confirm the check**
   - Popup asks: "Continue?"
   - Click "Yes"

6. **Wait for browser to open**
   - Browser opens with proxy
   - Navigates to whatismyip.com
   - Waits 4 seconds

7. **View result popup**
   - ✅ "Proxy is similar!" - IPs match, proxy working!
   - ⚠️ "Proxy IP mismatch!" - IPs don't match

8. **Click OK**
   - App waits 5 seconds
   - Browser stays open
   - You can verify manually

9. **Close browser when done**

---

## 📊 What You'll See

### Logs During Check:

```
🔍 Checking proxy for profile: nesterov_88blp_at_rambler_ru
🔍 Starting proxy verification...
🌐 Proxy configured: socks5://***@5.22.204.238:50101
🌍 Navigating to whatismyip.com...
⏳ Waiting 4 seconds for page to load...
✅ Expected IP (from proxy): 5.22.204.238
🌐 Detected IP (from site): 5.22.204.238
✅ IPs match! Proxy is working correctly!
💡 User clicked OK
⏳ Waiting 5 seconds before finishing...
✅ Proxy check complete!
💡 Browser window left open - close manually when done
```

### Popup If IPs Match (✅ Success):

```
┌─────────────────────────────────────┐
│  ✅ Proxy Verified                  │
├─────────────────────────────────────┤
│                                     │
│  ✅ Proxy is similar!               │
│                                     │
│  Proxy IP: 5.22.204.238             │
│  Detected IP: 5.22.204.238          │
│                                     │
│  The proxy is working correctly!    │
│                                     │
│            [    OK    ]             │
└─────────────────────────────────────┘
```

### Popup If IPs Don't Match (⚠️ Warning):

```
┌─────────────────────────────────────┐
│  ⚠️ Proxy Mismatch                  │
├─────────────────────────────────────┤
│                                     │
│  ⚠️ Proxy IP mismatch!              │
│                                     │
│  Expected IP: 5.22.204.238          │
│  Detected IP: 1.2.3.4               │
│                                     │
│  Proxy might not be working!        │
│                                     │
│            [    OK    ]             │
└─────────────────────────────────────┘
```

---

## 🔧 Technical Details

### How It Works:

1. **Extract Proxy IP**
   - From: `socks5://user:pass@5.22.204.238:50101`
   - Extracted: `5.22.204.238`

2. **Open Browser**
   - Uses botasaurus_driver
   - Profile + Proxy configured
   - Always visible mode (not headless)

3. **Navigate & Extract**
   - Goes to whatismyip.com
   - Waits 4 seconds
   - Extracts IP from page using multiple methods:
     - CSS selector: `#ipv4 > a`
     - Fallback: `a[href^='/ip/']`
     - Regex: `\b(?:\d{1,3}\.){3}\d{1,3}\b`

4. **Compare**
   - Exact string match
   - `5.22.204.238 == 5.22.204.238` → ✅ Match
   - `5.22.204.238 != 1.2.3.4` → ⚠️ Mismatch

5. **Show Result**
   - QMessageBox with result
   - User clicks OK
   - Waits 5 seconds
   - Logs completion

---

## 💡 Use Cases

### Use Case 1: Verify New Proxy

**Scenario:** Just added a new proxy to profile

**Steps:**
1. Import profile with proxy
2. Select profile
3. Click "Check Proxy"
4. Verify IPs match
5. Proxy confirmed working!

### Use Case 2: Debug Proxy Issues

**Scenario:** Scraping fails, suspect proxy problem

**Steps:**
1. Select problematic profile
2. Click "Check Proxy"
3. If IPs don't match → Proxy not working
4. Fix proxy or use different one

### Use Case 3: Test Proxy Provider

**Scenario:** Testing if proxy service is reliable

**Steps:**
1. Add proxy to profile
2. Check proxy
3. If match → Service working
4. If no match → Service has issues

### Use Case 4: Verify Location

**Scenario:** Need to confirm proxy is in specific country

**Steps:**
1. Check proxy
2. Browser stays open on whatismyip.com
3. Page shows location info
4. Verify country/city matches

---

## ⚙️ Configuration

### Button Location:
- **Tab:** Profiles
- **Row:** 3 (below Import button)
- **Color:** Blue
- **Icon:** 🔍

### Requirements:
- ✅ Profile must be selected
- ✅ Profile must have proxy configured
- ✅ If no proxy → Warning shown

### Browser Mode:
- **Always visible** (not headless)
- Allows manual verification
- Stays open after check

### Timing:
- **4 seconds:** Wait for page load
- **5 seconds:** Wait after OK clicked
- **Browser:** Stays open until manually closed

---

## 🧪 Testing

### Test 1: Profile With Working Proxy

1. Select profile: `nesterov_88blp_at_rambler_ru`
2. Click "Check Proxy"
3. Expected:
   ```
   ✅ Proxy IP: 5.22.204.238
   ✅ Detected IP: 5.22.204.238
   ✅ Proxy is similar!
   ```

### Test 2: Profile Without Proxy

1. Select profile without proxy
2. Click "Check Proxy"
3. Expected:
   ```
   ⚠️ Warning: No proxy configured
   ```

### Test 3: No Profile Selected

1. Don't select any profile
2. Click "Check Proxy"
3. Expected:
   ```
   ⚠️ Warning: Please select a profile
   ```

---

## 🚨 Troubleshooting

### Problem: "Could not extract IP from whatismyip.com"

**Cause:** Page structure changed or blocking

**Solution:**
- Check browser window manually
- See if IP is visible on page
- May need to update selectors

### Problem: IPs don't match but proxy is working

**Cause:** Proxy might use different exit IP

**Solution:**
- Some proxies rotate IPs
- Check with proxy provider
- Verify on the open browser window

### Problem: Page doesn't load

**Cause:** Proxy connection failed

**Solution:**
- Check proxy is online
- Verify proxy credentials
- Try different proxy

### Problem: Browser closes immediately

**Cause:** Not applicable - browser stays open!

**Solution:**
- Browser is designed to stay open
- Close manually when done

---

## 📂 Files Modified

```
✅ botasaurus_app/scraper_runner.py
   - extract_ip_from_proxy() method
   - check_proxy_ip() method
   - CheckProxyThread class

✅ botasaurus_app/main_window.py
   - Added "Check Proxy" button
   - check_selected_profile_proxy() method
   - on_proxy_check_finished() method
   - after_proxy_check_delay() method
   - Import CheckProxyThread
```

---

## 🎯 Workflow Diagram

```
[Select Profile] → [Click Check Proxy]
        ↓
   [Confirm?] → No → [Cancel]
        ↓ Yes
   [Open Browser]
        ↓
   [Navigate to whatismyip.com]
        ↓
   [Wait 4 seconds]
        ↓
   [Extract IP from page]
        ↓
   [Compare with proxy IP]
        ↓
   [Show Popup: Match or Mismatch]
        ↓
   [User clicks OK]
        ↓
   [Wait 5 seconds]
        ↓
   [Log completion]
        ↓
   [Browser stays open]
```

---

## ✅ Summary

### What You Get:

✅ **One-click proxy verification**
✅ **Visual IP comparison**
✅ **Automatic detection**
✅ **Clear success/fail indication**
✅ **Browser stays open for manual check**
✅ **Detailed logs**

### Perfect For:

✅ Verifying new proxies
✅ Debugging connection issues
✅ Testing proxy services
✅ Confirming geo-location
✅ Quality assurance

---

## 🎉 Ready to Use!

**To test your proxy right now:**

1. `START_APP.bat`
2. Profiles tab
3. Select: `nesterov_88blp_at_rambler_ru`
4. Click: `🔍 Check Proxy (whatismyip.com)`
5. Watch it work!

**Simple, fast, reliable proxy verification!** 🚀
