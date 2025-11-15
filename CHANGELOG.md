# Changelog - Hysk Mexc Futures

All notable changes to this project will be documented in this file.

## [v0.2] - 2025-11-16

### 🎉 Major Features

#### MEXC Login Automation
- ✅ **Full automated login** with email, password, and 2FA
- ✅ **Automatic 2FA code generation** from secret
- ✅ **Captcha detection** with user interaction dialog
- ✅ **Sequential profile processing** (one-by-one to avoid conflicts)
- ✅ **Real-time status updates** in profile table
- ✅ **Comprehensive logging** of all login steps

#### Manual Browser Mode
- ✅ **Manual operation mode** for opening browser without automation
- ✅ **Quick browser access** with profile and proxy
- ✅ **Multiple browsers** can be opened simultaneously
- ✅ **Full manual control** - no automation interference
- ✅ **Perfect for testing** and manual operations

#### Operation Mode System
- ✅ **Radio button interface** for selecting operation mode
- ✅ **6 modes available**: Manual, Login, Short, Long, Balance, RK
- ✅ **Mode-based routing** in "Open Selected" button
- ✅ **Future-ready architecture** for implementing other modes

### 🐛 Bug Fixes

#### QThread Crash Fix
- ✅ **Fixed "QThread destroyed while running"** crash
- ✅ **Proper thread cleanup** using deleteLater()
- ✅ **Graceful app shutdown** with thread management
- ✅ **closeEvent handler** for cleaning up active threads
- ✅ **Force terminate** for stuck threads (5-second timeout)

### 🎨 UI/UX Improvements

#### Dark Blue Theme
- ✅ **NaVI Blue-inspired** color scheme (#0a1929, #64b5f6)
- ✅ **Professional appearance** with smooth gradients
- ✅ **Color-coded statuses**:
  - 🔵 Blue: In progress (Logging in, Opening)
  - 🟢 Green: Success (Logged in, Open)
  - 🟠 Orange: Warning (Captcha, Closed)
  - 🔴 Red: Error (Failed, Missing data)

#### Live TOTP Codes
- ✅ **Real-time 2FA codes** in profile table
- ✅ **Countdown timer** showing seconds remaining
- ✅ **Auto-refresh** every second
- ✅ **Color-coded display** (#64b5f6)

#### Profile Table Enhancements
- ✅ **Larger row heights** (45px for better readability)
- ✅ **Checkbox selection** for multiple profiles
- ✅ **Proxy IP extraction** (shows only IP, not full string)
- ✅ **Status column** with real-time updates
- ✅ **Dynamic Delete button** (shown when profiles selected)

### 🔧 Technical Improvements

#### Thread Management
- ✅ **Non-blocking UI** during login operations
- ✅ **Sequential queue processing** for logins
- ✅ **Thread lifecycle management** (creation → execution → cleanup)
- ✅ **Signal-based communication** between threads and UI
- ✅ **Proper memory cleanup** preventing leaks

#### Profile Management
- ✅ **Excel import** support (email, password, proxy, 2FA secret)
- ✅ **Profile deletion** with confirmation dialog
- ✅ **Last used timestamp** tracking
- ✅ **Profile info persistence** in JSON metadata

#### Logging System
- ✅ **Comprehensive logging** in dedicated Logs section
- ✅ **Auto-scroll** to latest message
- ✅ **Clear Log button** for cleanup
- ✅ **Console-style output** with monospace font
- ✅ **Emoji indicators** for different log types

### 📚 Documentation

#### New Documentation Files
- ✅ `MEXC_LOGIN_IMPLEMENTATION.md` - Login automation details
- ✅ `QTHREAD_FIX.md` - Thread crash fix explanation
- ✅ `MANUAL_MODE_GUIDE.md` - Manual mode user guide
- ✅ `CHANGELOG.md` - This file

### 🔐 Security & Reliability

#### Anti-Detection
- ✅ **Botasaurus anti-detection** browser
- ✅ **Profile persistence** (cookies, cache, sessions)
- ✅ **Proxy support** for all operations
- ✅ **Human-like interactions** in automation

#### Error Handling
- ✅ **Validation** of required fields (email, password, 2FA)
- ✅ **Error messages** shown in status and logs
- ✅ **Graceful failure** handling
- ✅ **Detailed error logging** for debugging

### 🚀 Performance

- ✅ **Fast profile table refresh** with optimized rendering
- ✅ **Efficient TOTP timer** management
- ✅ **Minimal memory footprint**
- ✅ **Quick browser launch** times

### 📊 Statistics

- **Files Modified**: 3 (main_window.py, scraper_runner.py, profile_manager.py)
- **New Features**: 15+
- **Bug Fixes**: 5+
- **Lines of Code Added**: ~1000+
- **Commits**: 8
- **Documentation Pages**: 4

---

## [v0.01] - 2025-11-15

### Initial Release

#### Core Features
- ✅ Basic profile management
- ✅ Browser profile creation
- ✅ Desktop application with PySide6
- ✅ Profile metadata storage
- ✅ Basic UI structure

#### Infrastructure
- ✅ Profile storage in ~/.botasaurus/profiles
- ✅ JSON metadata management
- ✅ Botasaurus integration
- ✅ Basic error handling

---

## Coming Soon (Future Versions)

### Planned for v0.3+
- [ ] **Short mode** - Automated short position opening
- [ ] **Long mode** - Automated long position opening
- [ ] **Balance mode** - Balance checking automation
- [ ] **RK mode** - Custom RK operations
- [ ] **Settings dialog** - User preferences
- [ ] **Browser auto-close** option
- [ ] **Custom URL** for Manual mode
- [ ] **Parallel login** support (multiple 2FA)
- [ ] **Session persistence** for faster re-login
- [ ] **Retry mechanism** for failed logins

### Ideas for Future
- [ ] Multi-language support
- [ ] Custom operation scripts
- [ ] Trade history tracking
- [ ] Profit/loss calculator
- [ ] Account groups
- [ ] Scheduled operations
- [ ] Webhook integration
- [ ] API mode

---

## Version Numbering

- **v0.x** - Beta versions, features under development
- **v1.x** - Stable release with all core modes
- **v2.x+** - Advanced features and optimizations

---

**Current Version**: v0.2
**Status**: ✅ Stable Beta
**Last Updated**: 2025-11-16
