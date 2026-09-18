# A-WAY-TO-DOWNLOAD-YOUTUBE-AUDIO-

That is the spirit. You are now entering "Legend" territory. Using yt-dlp is the gold standard because it gives you control that no website ever will.

---

## Getting `HTTP Error 403: Forbidden`? Read this first

If your download dies with:

```
[youtube] XXXXXXXX: Downloading android vr player API JSON
ERROR: unable to download video data: HTTP Error 403: Forbidden
```

your link is fine — your **yt-dlp is too old**. YouTube started rejecting the
`android_vr` player client that old builds use by default, and it was removed
from the defaults in release `2026.08.19`. One command usually ends it:

```bash
python -m pip install -U yt-dlp     # or: yt-dlp -U  for the standalone .exe
```

Everything else that can go wrong — cookies, player clients, ffmpeg, the
JavaScript runtime, rate limits — is written up in
**[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**.

## The easy way: `ytgrab.py`

Instead of memorising flags, run the menu:

```bash
python3 ytgrab.py           # Linux / macOS   (Windows: double-click run.bat)
```

```
================================
  ytgrab  -  keep your media local
================================
  yt-dlp : 2026.08.19
           27 day(s) old (fresh - update if older than 45 days)
  ffmpeg : /usr/bin/ffmpeg
  JS     : deno (~/.deno/bin/deno)

Paste your URL: https://youtu.be/OfS1jFck8YQ

Choose format:
  1) Best video + audio (mp4, works on any phone)
  2) Audio - opus (best quality per MB, small files)
  3) Audio - flac (lossless container, big files)
  4) Audio - m4a (great quality, plays everywhere)
  5) Audio - mp3 (maximum compatibility)
  p) Same thing, but for a whole playlist / album
  c) Retry the last URL with browser cookies (fixes most 403s)
  l) List available formats for a URL
  u) Update yt-dlp
  d) Doctor - check yt-dlp / ffmpeg / deno
  q) Quit
Choice [1-5]: 5
```

What it does that a plain `yt-dlp` call does not:

* **Checks your setup first** — yt-dlp age, ffmpeg, JavaScript runtime — and
  offers to update a stale yt-dlp before it costs you a failed download.
* **Enables node/bun as JS runtimes.** yt-dlp only enables deno on its own, so
  if you have node it still reports `JS runtimes: none` and quietly drops to a
  single player client.
* **Retries on its own.** If YouTube answers 403/429, it walks a ladder —
  defaults → skip `android_vr` + add `web_safari` → TV clients → IPv4 — and
  says what each attempt is doing.
* **Clean files.** Title-only names (safe on Windows too), embedded metadata
  and cover art, saved to `~/Downloads`, and a download archive so re-running a
  playlist never fetches the same track twice.
* **Plain-English errors.** "YouTube refused the stream URL (403). Cause is
  almost always an outdated yt-dlp - update it first, then retry."

Useful one-liners:

```bash
python3 ytgrab.py --doctor                       # is my setup healthy?
python3 ytgrab.py --update                       # update yt-dlp
python3 ytgrab.py "URL" --format 5               # mp3, no menu
python3 ytgrab.py "PLAYLIST" --format 4 --playlist   # whole album as m4a
python3 ytgrab.py --list "URL"                   # what formats exist?
python3 ytgrab.py "URL" --format 5 --cookies chrome  # the 403 last resort
```

Files: `ytgrab.py` (the tool), `run.bat` (Windows double-click),
`run.sh` (Linux/macOS), `TROUBLESHOOTING.md` (every error, explained).

> Keep it personal: your own uploads, Creative-Commons material, offline
> copies you are allowed to keep. Downloading other people's copyright material
> breaks YouTube's terms and, depending on where you live, the law.

---

## Want real software? GrabBox (desktop app + extension + Android)

If menus feel like work, there is a proper app in this repo:

```bash
python3 -m grabbox      # opens a window: paste a link, pick quality, done
```

* **One UI for everything** — video, audio, images, installers, archives,
  playlists, and all 1800+ yt-dlp sites.
* **Browser extension** (`extension/`) — a *faded* icon that lights up when a
  page has something worth grabbing, right-click "Grab with GrabBox", and a
  hover mini-button on any downloadable thing.
* **Android** — Termux one-script install, or a WebView APK built by CI.
* **Windows / macOS / Linux** launchers, and one-file binaries via CI.

Full install + run guide for every platform: **[APP.md](APP.md)**.

## The manual way (how it all works underneath)

Since you are a beginner to this tool, I will give you the "Easiest Possible Method" to get it running on Windows without needing to be a coder.

Step 1: Download the Files
You need two things: the engine (yt-dlp) and the converter (ffmpeg).

Create a Folder:

Go to your Desktop or C: drive and create a new folder named youtube-dl.

Download yt-dlp:

Go to the official yt-dlp GitHub Releases page.

Look under "Assets" and click on yt-dlp.exe to download it.

Move this file into your youtube-dl folder.

Download FFmpeg (Crucial):

yt-dlp needs this to convert the video into a high-quality song file.

Go to gyan.dev/ffmpeg/builds (this is the safe, standard place).

Download the file named ffmpeg-git-essentials.7z (or .zip).

Open that zip file. Go inside the bin folder.

You will see ffmpeg.exe. Drag and drop ffmpeg.exe into your youtube-dl folder (right next to yt-dlp.exe).

Checkpoint: Your folder youtube-dl should now have at least two files: yt-dlp.exe and ffmpeg.exe.

Step 2: Open the "Command Center"
We don't double-click yt-dlp.exe. We talk to it using a text window.

Open your youtube-dl folder where the files are.

Click inside the address bar at the top of the folder window (where it says "This PC > Desktop > youtube-dl").

Erase everything there, type cmd, and hit Enter.

A black window will pop up. This is your command center, and it is already looking at your folder.

Step 3: The Magic Command (Copy & Paste)
To download your favorite video as the highest quality song possible, type this command into the black window:

yt-dlp -x --audio-format m4a "PASTE_YOUR_LINK_HERE"

Breakdown of the command:

yt-dlp: Calls the program.

-x: Tells it "Extract audio only" (delete the video part).

--audio-format m4a: Tells it to keep the audio in M4A.

Legend Tip: YouTube streams in M4A/AAC. Downloading in M4A means you get the exact original quality. Converting to MP3 technically lowers quality slightly, but if you absolutely need MP3, just change m4a to mp3 in the command.

"LINK": Paste your YouTube link inside quotes.

Example: yt-dlp -x --audio-format m4a "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

Hit Enter. You will see lines of text flying by. When it stops, the song file will appear in your folder.

Troubleshooting
"Command not found": You probably didn't open the cmd window inside the folder. Try Step 2 again.


Here is the upgraded command that will:

Remove the ID from the filename.

Add the Cover Art (Thumbnail) to the file so it shows up on your phone.

Add Metadata (Artist/Song info) so your car/phone display reads it correctly.

Copy and paste this command:

DOS :
yt-dlp -x --audio-format m4a --add-metadata --embed-thumbnail -o "%(title)s.%(ext)s" https://youtu.be/WECKJ1VzCVA


What's different in this command?
-o "%(title)s.%(ext)s": This tells the tool: "Name the file just the video title. Don't add the weird ID code at the end."

--embed-thumbnail: This grabs the picture from the YouTube video and "glues" it onto your song file as the album art.

--add-metadata: This writes the song details inside the file, so when you play it on your phone, it doesn't just say "Unknown Artist."

Pro Tip for "Official" Music Videos
Sometimes YouTube titles are messy, like "Linkin Park - Numb (Official Video)". You don't want (Official Video) showing up on your phone.

You can actually rename the file before you download it by typing the name you want inside the quotes.

Example: If you want the file to be named exactly "My Jam.m4a", you type:

DOS:

yt-dlp -x --audio-format m4a -o "My Jam.%(ext)s" https://youtu.be/WECKJ1VzCVA

(Just replace "My Jam" with whatever name you want).

"FFmpeg not found": Make sure ffmpeg.exe is sitting right next to yt-dlp.exe in the same folder.


1. The Playlist Command
You use the same command, but you paste a Playlist Link instead of a video link.

However, for playlists, we usually want the files to stay in the correct order (1, 2, 3...). So we tweak the naming part slightly:

DOS
yt-dlp -x --audio-format m4a --add-metadata --embed-thumbnail -o "%(playlist_index)s - %(title)s.%(ext)s" "PASTE_PLAYLIST_LINK_HERE"
What changed?

%(playlist_index)s: This puts "01", "02", "03" at the start of the filename.

Now your music player will play the album in the exact order you set it on YouTube, rather than shuffling it alphabetically.

2. Important Maintenance (The "Update" Command)
YouTube changes their code constantly to break downloaders. If one day you type a command and get a weird "Error" or "Crash," it means your tool is outdated.

You don't need to re-download anything. Just type this command to update it instantly:

DOS
yt-dlp -U
(Note: Capital U). It will say "Updated to version [date]" and you are good to go again.

If yt-dlp was installed with pip, `-U` cannot update it and you will see the
warning *"You installed yt-dlp with pip... Use that to update."* Then run:

DOS
python -m pip install -U yt-dlp

Check the result with `yt-dlp --version`. It prints a date, like `2026.08.19`;
anything older than about 45 days is worth updating before you blame your link.
`python3 ytgrab.py --update` tries both methods for you.
