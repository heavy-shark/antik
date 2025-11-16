# How to Start Hysk Mexc Futures

## 🚀 Quick Start (Choose One Method)

### Method 1: Silent Launch (Recommended) ⭐
**No console window appears**

#### Option A: Double-click launcher file
1. Double-click **`launcher.pyw`**
2. App starts instantly without console
3. That's it! ✅

#### Option B: Use VBS launcher
1. Double-click **`Start Hysk Mexc Futures.vbs`**
2. Completely invisible launch
3. App appears without any console

#### Option C: Use silent batch file
1. Double-click **`START_APP_SILENT.bat`**
2. Batch closes immediately
3. App runs without console

### Method 2: With Console Window
**Console window shows for debugging**

1. Double-click **`START_APP.bat`**
2. Console window appears with app
3. Useful for seeing errors/logs

---

## 📋 Comparison

| Method | Console | Speed | Best For |
|--------|---------|-------|----------|
| `launcher.pyw` | ❌ No | ⚡ Fast | Daily use |
| `Start Hysk Mexc Futures.vbs` | ❌ No | ⚡ Fast | Clean desktop |
| `START_APP_SILENT.bat` | ❌ No | ⚡ Fast | Batch scripts |
| `START_APP.bat` | ✅ Yes | ⚡ Fast | Debugging |

---

## 🎯 Recommended for Different Users

### Normal Users
**Use:** `launcher.pyw` (double-click)
- No console clutter
- Clean and simple
- Just works

### Power Users
**Use:** `Start Hysk Mexc Futures.vbs`
- Completely invisible
- Professional feel
- Can add to startup folder

### Developers/Debugging
**Use:** `START_APP.bat`
- See console output
- Debug errors
- Track execution

---

## 📁 File Purposes

### Launch Files
- **`launcher.pyw`** - Python no-console launcher
- **`Start Hysk Mexc Futures.vbs`** - VBScript invisible launcher
- **`START_APP_SILENT.bat`** - Batch silent launcher
- **`START_APP.bat`** - Batch with console (debug)

### App Files
- **`botasaurus_app/app.py`** - Main application entry point
- **`botasaurus_app/main_window.py`** - Main UI window

---

## 🔧 Technical Details

### Why .pyw Files Don't Show Console?
- `.pyw` extension runs with `pythonw.exe` instead of `python.exe`
- `pythonw.exe` = Python without console window
- Perfect for GUI applications

### How VBS Launcher Works?
```vbscript
' Runs Python with hidden window mode
WshShell.Run "pythonw.exe launcher.pyw", 0, False
' 0 = hidden window
' False = don't wait for completion
```

### How Silent BAT Works?
```batch
REM Uses pythonw.exe and exits immediately
start "" pythonw.exe launcher.pyw
exit
```

---

## 💡 Tips

### Create Desktop Shortcut
1. Right-click **`launcher.pyw`**
2. Send to → Desktop (create shortcut)
3. Rename shortcut to "Hysk Mexc Futures"
4. Double-click shortcut to start app

### Add to Windows Startup
1. Press `Win + R`
2. Type `shell:startup` and press Enter
3. Copy **`Start Hysk Mexc Futures.vbs`** to this folder
4. App will auto-start on Windows boot

### Custom Icon for Shortcut
1. Right-click shortcut → Properties
2. Click "Change Icon"
3. Browse to custom .ico file
4. Click OK

---

## 🐛 Troubleshooting

### App Doesn't Start?
1. **Check Python path** in launcher files
2. **Verify** Python 3.12 is installed at:
   ```
   C:\Users\daniel\AppData\Local\Programs\Python\Python312\
   ```
3. **Try START_APP.bat** to see error messages

### Console Still Appears?
- Make sure you're using `.pyw` file or `pythonw.exe`
- Don't use `python.exe` - use `pythonw.exe`
- Check file extension is exactly `.pyw` not `.pyw.txt`

### VBS Launcher Not Working?
- Check Python path in VBS file
- Right-click VBS → Edit to verify paths
- Make sure `launcher.pyw` exists

---

## ⚙️ Advanced Configuration

### Change Python Path
If Python is installed elsewhere, edit these files:

1. **launcher.pyw** - No path needed (uses system Python)
2. **START_APP_SILENT.bat** - Line 8
3. **Start Hysk Mexc Futures.vbs** - Line 11
4. **START_APP.bat** - Line 13

### Example Custom Path
```batch
REM Change this line in batch files:
"C:\Python\python312\pythonw.exe" launcher.pyw

REM Change this line in VBS file:
PythonPath = "C:\Python\python312\pythonw.exe"
```

---

## 📝 Summary

### For Clean Desktop Experience:
```
Double-click: launcher.pyw
         or
Double-click: Start Hysk Mexc Futures.vbs
```

### For Debugging:
```
Double-click: START_APP.bat
```

---

## 🎉 That's It!

Choose your preferred launch method and enjoy Hysk Mexc Futures v0.2!

**Recommended:** Use `launcher.pyw` for daily use - simple, clean, no console! ⭐

---

**Version**: v0.2
**Last Updated**: 2025-11-16
