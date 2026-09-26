@echo off
REM  GrabBox from source, for Windows - double-click me.
REM  Needs Python 3 with yt-dlp:  py -m pip install -U yt-dlp
REM  (Prefer the installer? https://github.com/sharthak18/A-WAY-TO-DOWNLOAD-YOUTUBE-AUDIO-/releases/latest)
setlocal
cd /d "%~dp0.."
where py >nul 2>nul
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
%PY% -m grabbox %*
pause
endlocal
