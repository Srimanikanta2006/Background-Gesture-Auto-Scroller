@echo off
echo Stopping Background Gesture Scroller...
powershell -NoProfile -Command "$procs = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*main.pyw*' }; if ($procs) { $procs | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host '[+] Stopped Gesture Scroller PID:' $_.ProcessId } } else { Write-Host '[*] No running Gesture Scroller found.' }"
timeout /t 2 >nul
