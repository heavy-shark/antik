' ========================================
' Hysk Mexc Futures - Silent Launcher
' VBScript launcher - completely invisible
' ========================================

Set WshShell = CreateObject("WScript.Shell")

' Get the directory where this script is located
ScriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Python path
PythonPath = "C:\Users\daniel\AppData\Local\Programs\Python\Python312\pythonw.exe"

' Launcher file
LauncherFile = ScriptDir & "\launcher.pyw"

' Run without showing any window (0 = hidden, False = don't wait)
WshShell.Run """" & PythonPath & """ """ & LauncherFile & """", 0, False

Set WshShell = Nothing
