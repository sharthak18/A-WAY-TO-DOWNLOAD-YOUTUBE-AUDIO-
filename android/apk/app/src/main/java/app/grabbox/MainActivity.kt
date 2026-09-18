package app.grabbox

import android.annotation.SuppressLint
import android.content.Intent
import android.os.Bundle
import android.webkit.WebResourceRequest
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity

/**
 * GrabBox Android front-end.
 *
 * The *server* runs on the phone via Termux (see ../termux-install.sh); this
 * app is a native-feeling WebView over the same UI the desktop uses, plus a
 * "Share to GrabBox" target so you can hand any link from any app to it.
 */
class MainActivity : AppCompatActivity() {

    private lateinit var web: WebView
    private var base = "http://127.0.0.1:8765"

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        web = WebView(this)
        setContentView(web)

        web.settings.javaScriptEnabled = true
        web.settings.domStorageEnabled = true
        web.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(v: WebView?, r: WebResourceRequest?) = false
        }

        // "Share -> GrabBox" hands us the link as EXTRA_TEXT.
        val shared: String? = when (intent?.action) {
            Intent.ACTION_SEND -> intent.getStringExtra(Intent.EXTRA_TEXT)
            else -> null
        }
        val url = if (shared.isNullOrBlank()) base
                  else "$base/?url=" + android.net.Uri.encode(shared.trim())
        web.loadUrl(url)
    }

    @Deprecated("use onBackPressedDispatcher")
    override fun onBackPressed() {
        if (web.canGoBack()) web.goBack() else super.onBackPressed()
    }
}
