@echo off
echo ========================================
echo  Excel Profile Import - Quick Setup
echo ========================================
echo.
echo This will:
echo  1. Create sample Excel file on Desktop
echo  2. Launch the app
echo.
echo Press any key to continue...
pause > nul
echo.
echo Creating sample Excel file...
echo.

cd /d "%~dp0"
"C:\Users\daniel\AppData\Local\Programs\Python\Python312\python.exe" create_sample_excel.py

echo.
echo ========================================
echo Sample file created on Desktop!
echo ========================================
echo.
echo Next steps:
echo  1. App will launch in 3 seconds...
echo  2. Go to Profiles tab
echo  3. Click "Import Profiles from Excel"
echo  4. Select the file from your Desktop
echo.
timeout /t 3 /nobreak > nul

echo Launching app...
"C:\Users\daniel\AppData\Local\Programs\Python\Python312\python.exe" LAUNCHER.py
