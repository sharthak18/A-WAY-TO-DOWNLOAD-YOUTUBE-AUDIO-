@echo off
REM  ytgrab launcher for Windows - double-click me.
REM  Needs Python 3 (https://www.python.org/downloads/, tick "Add to PATH")
REM  and yt-dlp:  python -m pip install -U yt-dlp
setlocal
where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")

%PY% "%~dp0ytgrab.py" %*

echo.
pause
endlocal
