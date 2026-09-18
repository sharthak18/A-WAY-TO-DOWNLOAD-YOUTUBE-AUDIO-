@echo off
REM  GrabBox for Windows - double-click me.
REM  Needs Python 3 with yt-dlp:  py -m pip install -U yt-dlp
setlocal
where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
%PY% "%~dp0launch.py" %*
pause
endlocal
