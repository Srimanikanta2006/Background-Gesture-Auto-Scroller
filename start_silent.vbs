' Stealth Background Launcher for Gesture Scroller
' Launches pythonw silently without flashing any command prompt window.

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
strCurDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strCurDir

' Validate that .venv exists before launching
If Not fso.FileExists(strCurDir & "\.venv\Scripts\pythonw.exe") Then
    MsgBox "Virtual environment (.venv) not found!" & vbCrLf & vbCrLf & "Please double-click 'setup.bat' first to install the requirements.", vbExclamation, "Gesture Scroller - Setup Required"
    WScript.Quit 1
End If

WshShell.Run """" & strCurDir & "\.venv\Scripts\pythonw.exe"" """ & strCurDir & "\main.pyw""", 0, False
