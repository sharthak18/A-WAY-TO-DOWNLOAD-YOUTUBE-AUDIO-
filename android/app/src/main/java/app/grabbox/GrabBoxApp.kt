package app.grabbox

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import android.util.Log
import com.yausername.ffmpeg.FFmpeg
import com.yausername.youtubedl_android.YoutubeDL

/** Boots the bundled engine: Python runtime + yt-dlp + ffmpeg, all inside the APK. */
class GrabBoxApp : Application() {

    /** False when the native engine failed to unpack (showed in the UI). */
    var engineReady: Boolean = false
        private set
    var engineError: String? = null
        private set

    override fun onCreate() {
        super.onCreate()
        instance = this
        try {
            YoutubeDL.getInstance().init(this)
            FFmpeg.getInstance().init(this)
            engineReady = true
        } catch (e: Exception) {
            engineError = e.message ?: e.toString()
            Log.e("GrabBox", "engine init failed", e)
        }
        createNotificationChannel()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_DOWNLOADS,
                getString(R.string.channel_downloads),
                NotificationManager.IMPORTANCE_LOW,
            ).apply {
                description = getString(R.string.channel_downloads_desc)
            }
            getSystemService(NotificationManager::class.java)
                ?.createNotificationChannel(channel)
        }
    }

    companion object {
        const val CHANNEL_DOWNLOADS = "grabbox-downloads"
        lateinit var instance: GrabBoxApp
            private set
    }
}
