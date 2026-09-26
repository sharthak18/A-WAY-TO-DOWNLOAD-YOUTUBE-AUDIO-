# The Legend's Cheat Sheet for `yt-dlp`

Copy-paste commands for people who like the terminal. You do not need any of
this to use the GrabBox app — see the [front page](../README.md). Organised
into Music (Audio) and Video, plus the command to keep the tool updated.

## 🎵 1. The Music Commands (Audio Only)

**Option A: The "Perfect" Single Song.** Downloads the highest quality audio
(M4A), removes the weird ID from the name, adds the cover art, and fills in the
artist info.

```bat
yt-dlp -x --audio-format m4a --add-metadata --embed-thumbnail -o "%(title)s.%(ext)s" "PASTE_LINK_HERE"
```

**Option B: The "Whole Album/Playlist".** Downloads every song in a playlist,
numbers them (01, 02...) so they play in order, and adds cover art.

```bat
yt-dlp -x --audio-format m4a --add-metadata --embed-thumbnail -o "%(playlist_index)s - %(title)s.%(ext)s" "PASTE_PLAYLIST_LINK_HERE"
```

## 🎬 2. The Video Commands (High Quality Video)

By default, yt-dlp might give you an `.mkv` or `.webm` file, which some phones
can't play. Use these commands to force a high-quality MP4 that works
everywhere.

**Option A: Best Quality Video (MP4).** Downloads the best video and best
audio, then merges them into a clean MP4 file.

```bat
yt-dlp -f "bv+ba/b" --merge-output-format mp4 -o "%(title)s.%(ext)s" "PASTE_LINK_HERE"
```

**Option B: Video with Subtitles.** Same as above, but also burns the
subtitles (lyrics/dialogue) into the video if they exist.

```bat
yt-dlp -f "bv+ba/b" --merge-output-format mp4 --embed-subs -o "%(title)s.%(ext)s" "PASTE_LINK_HERE"
```

## 🛠️ 3. Maintenance

**Update Tool.** Run this once a month or if you get an error.

```bat
yt-dlp -U
```

## ⚡ PRO TIP: The "One-Click" Shortcut (No Typing)

Instead of typing these long codes every time, you can create a mini-program
(a Batch file) on your desktop.

1. Open Notepad.
2. Paste the code below into it.
3. Save the file as `Download_Music.bat` (make sure you select "All Files",
   not "Text Documents").
4. Put this file in your `youtube-dl` folder.

Code for the Batch File:

```bat
@echo off
set /p url="Paste YouTube Link: "
echo Downloading High Quality Audio...
yt-dlp -x --audio-format m4a --add-metadata --embed-thumbnail -o "%%(title)s.%%(ext)s" "%url%"
echo Done! check your folder.
pause
```

**How to use it:** Now, you just double-click `Download_Music.bat`, paste your
link, and hit Enter. It does everything for you.

Here is the code for your `Download_Video.bat` file. Same steps: open Notepad,
paste the code below, save it as `Download_Video.bat` in your `youtube-dl`
folder.

```bat
@echo off
:: Ask for the link
set /p url="Paste YouTube Video Link: "

:: Download Best Video+Audio and merge into MP4
echo Downloading Best Quality Video (MP4)...
yt-dlp -f "bv+ba/b" --merge-output-format mp4 --add-metadata --embed-thumbnail -o "%%(title)s.%%(ext)s" "%url%"

echo.
echo ---------------------------------------------------
echo Done! The video is ready.
echo ---------------------------------------------------
pause
```

Note: `--embed-thumbnail` is in this one too, so your video files on your
computer will show the actual video thumbnail instead of a random frame!

Enjoy your collection!

---

## 2026 UPDATE — read this if you get "403 Forbidden"

The `.bat` files above still work, but if a download dies with

```
ERROR: unable to download video data: HTTP Error 403: Forbidden
```

it is not the link and not ffmpeg: your yt-dlp is too old. Update first:

```bat
python -m pip install -U yt-dlp        (pip install)
yt-dlp -U                              (standalone yt-dlp.exe)
```

Then use `scripts/ytgrab.py` from this repo instead of typing flags — it
checks your setup, enables node/bun as a JavaScript runtime, and automatically
retries with different YouTube player clients when one gets blocked:

```bash
python3 scripts/ytgrab.py            # Windows: double-click scripts\ytgrab.bat
```

Full error-by-error guide: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
