# A-WAY-TO-DOWNLOAD-YOUTUBE-AUDIO-

That is the spirit. You are now entering "Legend" territory. Using yt-dlp is the gold standard because it gives you control that no website ever will.

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
