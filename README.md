# Hysk Mexc Futures v0.2

**Professional automation tool for MEXC Futures trading with anti-detection browser technology**

![Version](https://img.shields.io/badge/version-0.2-blue)
![Status](https://img.shields.io/badge/status-stable%20beta-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-Private-red)

---

## 🌟 Features

### ✅ Fully Implemented

#### 🔐 MEXC Login Automation
- **Automatic login** with email, password, and 2FA authentication
- **Live TOTP code generation** with countdown timer
- **Captcha detection** and user interaction handling
- **Sequential profile processing** to avoid conflicts
- **Real-time status updates** with color coding
- **Comprehensive logging** of all operations

#### 🖱️ Manual Browser Mode
- **Simple browser launch** without automation
- **Full manual control** for custom operations
- **Multiple browsers** can be opened simultaneously
- **Perfect for testing** and debugging

#### 📊 Profile Management
- **Excel import** support for bulk profile creation
- **Profile table** with checkboxes for multi-selection
- **Live 2FA codes** displayed with countdown
- **Proxy IP extraction** and display
- **Status tracking** for each profile
- **Delete selected** profiles with confirmation

#### 🎨 Modern UI
- **Dark blue NaVI-inspired theme** (#0a1929)
- **Color-coded statuses** (Blue/Green/Orange/Red)
- **Real-time updates** in profile table
- **Comprehensive logs** section
- **Operation mode selection** via radio buttons

### 🔄 Coming Soon
- 📈 **Short mode** - Automated short position opening
- 📉 **Long mode** - Automated long position opening
- 💰 **Balance mode** - Balance checking automation
- 🔧 **RK mode** - Custom operations
- ⚙️ **Settings dialog** - User preferences

---

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.8 or higher
python --version

# Required packages
pip install PySide6 playwright pyotp qrcode pillow pysocks openpyxl botasaurus-driver
```

### Installation
```bash
# Clone repository
git clone https://github.com/heavy-shark/antik.git
cd antik

# Install dependencies (if needed)
pip install -r requirements.txt  # Create this if needed

# Launch application
python botasaurus_app/app.py
```

### First Time Setup
1. **Launch the app**
2. **Import profiles** from Excel (📥 Import button)
   - Excel format: `email | password | proxy | 2fa_secret`
3. **Select profiles** using checkboxes
4. **Choose operation mode** (Manual or Login)
5. **Click "Open Selected"** and watch it work!

---

## 📖 User Guide

### Operation Modes

#### 🖱️ Manual Mode
**Purpose**: Open browser without automation for manual operations

**How to use**:
1. Select profile(s) with checkboxes
2. Choose "Manual" radio button
3. Click "Open Selected"
4. Browser opens to MEXC homepage
5. Use manually for any operations

**Best for**: Testing, debugging, custom manual workflows

#### 🔐 Login Mode
**Purpose**: Automatic MEXC login with 2FA

**How to use**:
1. Select profile(s) with checkboxes
2. Choose "Login" radio button
3. Click "Open Selected"
4. Watch automatic login process
5. Solve captcha if prompted
6. Browser remains logged in

**Best for**: Quick account access, automated login

#### 📊 Other Modes
- **Short/Long/Balance/RK**: Coming in future versions

### Profile Management

#### Import from Excel
1. Click "📥 Import" button
2. Select Excel file (.xlsx)
3. Excel format:
   ```
   Row 1: email | password | proxy | 2fa_secret
   Row 2+: your data
   ```
4. Profiles automatically created

#### Delete Profiles
1. Select profile(s) with checkboxes
2. "🗑️ Delete Selected" button appears in header
3. Click button and confirm deletion

#### Profile Status Colors
| Color | Meaning | Examples |
|-------|---------|----------|
| 🔵 Blue | In Progress | "Logging in...", "Opening..." |
| 🟢 Green | Success | "Logged in", "Open (Manual)" |
| 🟠 Orange | Warning/Neutral | "Captcha!", "Closed" |
| 🔴 Red | Error | "Login failed", "Error: No password" |

---

## 🔧 Technical Details

### Architecture
- **Frontend**: PySide6 (Qt for Python)
- **Browser**: Botasaurus anti-detection browser
- **Threading**: QThread for non-blocking operations
- **Storage**: JSON metadata in `~/.botasaurus/profiles/`
- **2FA**: pyotp for TOTP generation

### Project Structure
```
antik/
├── botasaurus_app/
│   ├── app.py              # Main entry point
│   ├── main_window.py      # Main UI window
│   ├── scraper_runner.py   # Browser automation
│   ├── profile_manager.py  # Profile management
│   └── profiles/           # Profile storage
├── CHANGELOG.md            # Version history
├── MANUAL_MODE_GUIDE.md    # Manual mode docs
├── MEXC_LOGIN_IMPLEMENTATION.md
├── QTHREAD_FIX.md
└── README.md               # This file
```

### Key Features
- ✅ **Anti-detection browser** (passes bot checks)
- ✅ **Proxy support** (SOCKS5/HTTP)
- ✅ **Profile persistence** (cookies, cache, sessions)
- ✅ **Sequential processing** (prevents 2FA conflicts)
- ✅ **Graceful shutdown** (proper thread cleanup)
- ✅ **Memory safe** (no leaks, proper cleanup)

---

## 🎯 Use Cases

### Trading
- Quick login to multiple accounts
- Check balances across accounts
- Manual trading operations
- Position management

### Testing
- Test proxy configurations
- Verify 2FA settings
- Debug automation issues
- Profile validation

### Automation
- Automated login workflows
- Sequential account operations
- Multi-account management
- Custom scripts (via Manual mode)

---

## ⚙️ Configuration

### Proxy Format
Supported formats:
```
socks5://user:pass@IP:PORT
http://user:pass@IP:PORT
socks5://IP:PORT
http://IP:PORT
```

### 2FA Secret
- Base32 encoded TOTP secret
- Usually provided when setting up 2FA
- Example: `JBSWY3DPEHPK3PXP`

### Excel Import Format
```
Column A: Email address (required)
Column B: Password (optional for Manual mode)
Column C: Proxy (optional)
Column D: 2FA Secret (required for Login mode)
```

---

## 🐛 Troubleshooting

### Common Issues

#### "QThread destroyed while running"
✅ **Fixed in v0.2** - Proper thread cleanup implemented

#### Browser Won't Open
- Check if profile exists
- Verify proxy configuration
- Check logs for detailed error

#### Login Fails
- Verify email/password are correct
- Check 2FA secret is valid
- Ensure proxy is working (test in Manual mode)
- Check if captcha appeared

#### Proxy Not Working
- Use Manual mode to test
- Visit whatismyip.com to verify IP
- Check proxy format is correct
- Try different proxy

---

## 📊 Version History

### v0.2 (Current) - 2025-11-16
- ✅ MEXC Login automation
- ✅ Manual browser mode
- ✅ QThread crash fixes
- ✅ Live TOTP codes
- ✅ Excel import
- ✅ Modern UI theme

### v0.01 - 2025-11-15
- Initial release
- Basic profile management
- Desktop application framework

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

---

## 🔐 Security

### Best Practices
- ✅ Store 2FA secrets securely
- ✅ Use strong passwords
- ✅ Rotate proxies regularly
- ✅ Don't share profile data
- ✅ Close browsers when done

### Privacy
- Profile data stored locally in `~/.botasaurus/profiles/`
- No data sent to external servers (except MEXC during login)
- Proxy configuration keeps your IP private

---

## 🤝 Contributing

This is a private project. Contact the maintainer for access.

---

## 📄 License

Private - All Rights Reserved

---

## 👤 Author

**heavy-shark**
- GitHub: [@heavy-shark](https://github.com/heavy-shark)

---

## 🙏 Acknowledgments

- **Botasaurus** - Anti-detection browser technology
- **PySide6** - Qt for Python framework
- **PyOTP** - TOTP implementation
- **Claude Code** - Development assistance

---

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Contact the maintainer directly

---

**Current Version**: v0.2
**Last Updated**: 2025-11-16
**Status**: ✅ Stable Beta

---

**Made with ❤️ for MEXC Futures traders**
