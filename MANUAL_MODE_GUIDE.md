# Manual Mode - Quick Guide

## Overview
Manual mode allows you to open browser(s) with your profile and proxy configuration **without any automation**. Perfect for manual operations, testing, or custom workflows.

## How to Use

### Step 1: Select Profiles
- ✅ Check the boxes next to the profiles you want to open
- You can select multiple profiles to open multiple browsers

### Step 2: Choose Manual Mode
- 🔘 Click the **"Manual"** radio button in Operation Mode section
- This is the first option (leftmost)

### Step 3: Open Browser(s)
- 🚀 Click **"Open Selected"** button
- Browser(s) will open automatically

### Step 4: Use Manually
- 💡 Browser is now open with your profile and proxy
- Use it for any manual operations you need
- Browser stays open until you close it manually

## What Happens?

1. **Browser Opens**: Anti-detection browser with your profile
2. **Proxy Applied**: If configured, proxy is automatically used
3. **MEXC Homepage**: Opens to https://www.mexc.com/ by default
4. **Status Update**: Profile status shows "Open (Manual)" in green
5. **Logs**: All operations logged in the Logs section

## Features

✅ **Profile Configuration**: Your saved profile data is used
✅ **Proxy Support**: Proxy automatically applied if configured
✅ **Multiple Browsers**: Open several profiles at once
✅ **No Automation**: Full manual control - no scripts running
✅ **Anti-Detection**: Same browser as Login mode (anti-bot protection)

## Use Cases

### 🔍 Testing
- Test if proxy is working
- Verify profile settings
- Check browser anti-detection

### 🛠️ Manual Operations
- Perform custom actions
- Navigate to any website
- Manual account management

### 🐛 Debugging
- Debug login issues
- Test new workflows
- Troubleshoot automation problems

### 📊 Account Work
- Check balances manually
- Place manual trades
- Verify account information

## Status Colors

| Status | Color | Meaning |
|--------|-------|---------|
| Opening... | 🔵 Blue | Browser is launching |
| Open (Manual) | 🟢 Green | Browser successfully opened |
| Failed to open | 🔴 Red | Error launching browser |

## Tips

💡 **Multiple Browsers**: You can open multiple profiles simultaneously. Each gets its own browser window.

💡 **Browser Stays Open**: The browser window remains open even after you close the app. Close manually when done.

💡 **Proxy Check**: Use this mode to verify your proxy is working correctly by visiting whatismyip.com

💡 **Fresh Start**: Each time you open, you get the saved profile state. Cookies and login sessions persist.

## Comparison with Other Modes

| Mode | What It Does |
|------|-------------|
| **Manual** | Opens browser - you do everything manually |
| **Login** | Automatic MEXC login with 2FA |
| **Short/Long/Balance/RK** | Future automation modes (not yet implemented) |

## Example Workflow

### Quick Account Check
1. Select your profile
2. Choose "Manual" mode
3. Click "Open Selected"
4. Browser opens to MEXC
5. Manually login or navigate to your account
6. Check balances, positions, etc.
7. Close browser when done

### Proxy Testing
1. Select profile with proxy
2. Choose "Manual" mode
3. Click "Open Selected"
4. In browser, go to whatismyip.com
5. Verify IP matches your proxy IP
6. Close browser

## Troubleshooting

### ❌ "Failed to open" Error
- **Check**: Profile exists and is valid
- **Check**: Proxy configuration (if using proxy)
- **Check**: Logs section for detailed error message

### 🌐 Proxy Not Working
- Use Manual mode to test proxy
- Visit whatismyip.com to see actual IP
- Compare with proxy IP in table
- Check proxy format in profile settings

### 🔒 Browser Won't Open
- Check if another browser is already open for this profile
- Close existing browser windows
- Try again

## Advanced

### Opening Specific URL
Currently opens MEXC homepage. Future versions may allow custom URLs.

### Profile Persistence
All cookies, cache, and browser data are saved in the profile. Next time you open the same profile, everything persists.

### Closing Browsers
- Close browser window manually (X button)
- OR use "Close Selected" button in app (marks as closed)
- Browser must be closed manually from the window

---

**Mode**: Manual
**Status**: ✅ Fully Implemented
**Perfect For**: Manual operations, testing, debugging
**No Automation**: You have full control
