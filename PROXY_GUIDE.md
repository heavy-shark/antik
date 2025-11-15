# 🌐 Proxy Connection Guide

## ✅ Feature Complete!

Each profile now automatically uses its configured proxy when scraping!

---

## 🎯 How It Works

### Automatic Proxy Connection

When you run a scraper:
1. App reads the proxy from profile metadata
2. Validates and formats the proxy
3. Passes it to the browser Driver
4. All traffic goes through the proxy
5. Results show which proxy was used

**No manual configuration needed!** Just import profiles with proxy data and they work automatically.

---

## 📋 Supported Proxy Formats

### Format 1: Simple (IP:Port)
```
123.45.67.89:8080
proxy.example.com:3128
```
→ Automatically adds `http://` prefix

### Format 2: With Protocol
```
http://123.45.67.89:8080
https://proxy.example.com:8080
socks5://123.45.67.89:1080
socks4://123.45.67.89:1080
```
→ Used as-is

### Format 3: Authenticated (Username:Password)
```
username:password@123.45.67.89:8080
http://username:password@proxy.com:8080
socks5://user:pass@123.45.67.89:1080
```
→ Credentials hidden in logs (shown as `***`)

### Format 4: No Proxy
```
[empty field]
```
→ Direct connection (no proxy)

---

## 🚀 Usage Examples

### Example 1: Import Profiles with Proxies

**Excel file:**
```
email               password    proxy                2fa_secret
trader1@mexc.com   pass123     123.45.67.89:8080    JBSWY3DP...
trader2@mexc.com   pass456     45.67.89.12:3128     MFRGGZDF...
```

**After import:**
- Profile `trader1_at_mexc_com` → Uses proxy `123.45.67.89:8080`
- Profile `trader2_at_mexc_com` → Uses proxy `45.67.89.12:3128`

### Example 2: Mixed (Some With, Some Without Proxy)

**Excel file:**
```
email               password    proxy                2fa_secret
user1@test.com     pass123     123.45.67.89:8080
user2@test.com     pass456
```

**After import:**
- Profile `user1_at_test_com` → Uses proxy `123.45.67.89:8080`
- Profile `user2_at_test_com` → Direct connection (no proxy)

### Example 3: Authenticated Proxies

**Excel file:**
```
email               password    proxy                           2fa_secret
vip@mexc.com       pass123     username:password@1.2.3.4:8080  JBSWY3DP...
```

**After import:**
- Profile uses authenticated proxy
- Logs show: `http://***@1.2.3.4:8080` (credentials hidden)

---

## 📊 Logs & Feedback

### What You'll See in Logs

**With Proxy:**
```
🚀 Starting scraper with profile: trader1_at_mexc_com
🌐 Target URL: https://mexc.com
👁️ Mode: Visible
🌐 Using proxy: http://123.45.67.89:8080
🔧 Initializing browser...
✅ Title: MEXC - Bitcoin Exchange
✅ Heading: Trade Crypto
✅ Proxy used: http://123.45.67.89:8080
✅ Scraping completed successfully!
```

**Without Proxy:**
```
🚀 Starting scraper with profile: direct_user
🌐 Target URL: https://example.com
👁️ Mode: Visible
🌐 No proxy configured (direct connection)
🔧 Initializing browser...
✅ Title: Example Domain
✅ Heading: Example
✅ Proxy used: No proxy
✅ Scraping completed successfully!
```

**Authenticated Proxy (credentials hidden):**
```
🌐 Using proxy: http://***@123.45.67.89:8080
```

---

## 📊 Results Table

The Results tab now shows proxy usage:

| URL | Title | Heading | Proxy Used |
|-----|-------|---------|------------|
| https://mexc.com | MEXC Exchange | Trade Crypto | http://123.45.67.89:8080 |
| https://example.com | Example | Example Domain | No proxy |

---

## 🔧 Technical Details

### Proxy Configuration Flow

1. **Storage**
   - Proxy stored in: `%USERPROFILE%\.botasaurus\profiles\profiles_metadata.json`
   - Field: `"proxy": "123.45.67.89:8080"`

2. **Parsing**
   - `parse_proxy()` method validates format
   - Adds protocol if missing
   - Returns formatted proxy string

3. **Usage**
   - Proxy passed to `Driver(proxy=...)`
   - botasaurus_driver handles the connection
   - All browser traffic routed through proxy

4. **Display**
   - Credentials masked in UI: `http://***@1.2.3.4:8080`
   - Full proxy used internally
   - Results show proxy used

### Supported Proxy Types

- ✅ HTTP proxies
- ✅ HTTPS proxies
- ✅ SOCKS4 proxies
- ✅ SOCKS5 proxies
- ✅ Authenticated proxies (username:password)
- ✅ Direct connection (no proxy)

---

## 🧪 Testing

### Test 1: Import Profiles with Proxies

1. Update your Excel file:
   ```
   email              password   proxy              2fa_secret
   test1@test.com    pass123    123.45.67.89:8080
   test2@test.com    pass456
   ```

2. Import to app

3. Run scraper with `test1@test.com`
   - Should show: "Using proxy: http://123.45.67.89:8080"

4. Run scraper with `test2@test.com`
   - Should show: "No proxy configured (direct connection)"

### Test 2: View Proxy in Profile Details

1. Select a profile with proxy
2. Profile Details panel shows:
   ```
   Profile: test1_at_test_com
   Email: test1@test.com
   Password: ***
   Proxy: 123.45.67.89:8080
   ```

3. Click "ℹ️ Profile Info" button
   - Full proxy details shown

### Test 3: Check Results Table

1. After scraping
2. Go to Results tab
3. "Proxy Used" column shows:
   - Actual proxy if used
   - "No proxy" if direct connection

---

## 💡 Tips & Best Practices

### Tip 1: Test Proxy Before Importing
Make sure your proxy works before adding to Excel

### Tip 2: Use Different Proxies for Different Accounts
Avoid detection by using unique proxy per profile:
```
trader1@mexc.com → proxy1:8080
trader2@mexc.com → proxy2:8080
```

### Tip 3: Rotate Proxies
Update Excel file with new proxies, re-import (delete old profiles first)

### Tip 4: Monitor Proxy Usage
Check Results table to confirm correct proxy was used

### Tip 5: Authenticated Proxies for Premium Services
Format: `username:password@host:port`
App handles authentication automatically

---

## 🚨 Troubleshooting

### Problem: "Connection timeout"
**Cause:** Proxy not responding
**Solution:**
- Test proxy manually
- Check proxy is online
- Verify proxy format

### Problem: "Proxy authentication failed"
**Cause:** Wrong username/password
**Solution:**
- Check credentials in Excel
- Format: `username:password@host:port`

### Problem: "ERR_PROXY_CONNECTION_FAILED"
**Cause:** Can't connect to proxy
**Solution:**
- Verify proxy IP and port
- Check firewall settings
- Try different proxy

### Problem: Proxy shown but not used
**Cause:** Invalid format
**Solution:**
- Check proxy format in Excel
- Should be: `ip:port` or `protocol://ip:port`

### Problem: "No proxy configured" but I added one
**Cause:** Profile created before proxy was added
**Solution:**
- Delete old profile
- Re-import from updated Excel

---

## 📂 Files Modified

```
✅ botasaurus_app/scraper_runner.py
   - parse_proxy() method
   - get_proxy_for_profile() method
   - Driver initialization with proxy
   - Proxy logging

✅ botasaurus_app/main_window.py
   - Results table: added "Proxy Used" column
   - Export includes proxy data
   - Profile details show proxy

✅ botasaurus_app/profile_manager.py
   - Proxy field in profile metadata
   - Excel import includes proxy
```

---

## 🎉 Ready to Use!

### Quick Test:

1. **Update Excel file** with proxies:
   ```
   email              password   proxy              2fa_secret
   myaccount@mexc.com pass123    123.45.67.89:8080  JBSWY3DP...
   ```

2. **Import to app**
   - Profiles tab → Import Profiles from Excel

3. **Run scraper**
   - Select profile
   - Enter URL
   - Click Run

4. **Check logs**
   - Should show: "🌐 Using proxy: http://123.45.67.89:8080"

5. **Verify results**
   - Results tab shows proxy used

---

## 🔒 Security Notes

- ✅ Proxy credentials stored in metadata (local file)
- ✅ Credentials hidden in UI (shown as `***`)
- ✅ Logs mask credentials for security
- ✅ Results show proxy but hide auth details

---

**Each profile now automatically connects through its configured proxy!** 🚀

Just import profiles with proxy data and everything works automatically!
