package app.grabbox

import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.provider.Settings
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AlertDialog
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.core.content.ContextCompat
import androidx.lifecycle.ViewModelProvider
import app.grabbox.ui.GrabBoxTheme
import app.grabbox.ui.HomeScreen
import java.util.regex.Pattern

class MainActivity : ComponentActivity() {

    private lateinit var viewModel: GrabViewModel

    private val notifyPermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { /* downloads run regardless; notifications are just nicer */ }

    private val storagePermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        viewModel = ViewModelProvider(this)[GrabViewModel::class.java]

        setContent {
            val engine by (application as GrabBoxApp).engineState.collectAsState()
            GrabBoxTheme {
                HomeScreen(
                    viewModel = viewModel,
                    engineState = engine,
                    onRetryEngine = { (application as GrabBoxApp).startEngine() },
                )
            }
        }

        handleShareIntent(intent)
        askForPermissions()
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleShareIntent(intent)
    }

    /** Share sheet ("Share → GrabBox") and open-with entries land here. */
    private fun handleShareIntent(intent: Intent?) {
        val text = when (intent?.action) {
            Intent.ACTION_SEND -> intent.getStringExtra(Intent.EXTRA_TEXT)
            Intent.ACTION_VIEW -> intent.dataString
            else -> null
        } ?: return
        val matcher = Pattern.compile("https?://\\S+").matcher(text)
        if (matcher.find()) {
            viewModel.pasteAndAnalyze(matcher.group())
        }
    }

    /**
     * Permission philosophy: ask once, early, explain why. Downloads to
     * shared storage on API 30+ need the manage-files grant; older Androids
     * use the legacy write permission; notifications on 33+ are opt-in.
     */
    private fun askForPermissions() {
        if (Build.VERSION.SDK_INT >= 33) {
            notifyPermission.launch(android.Manifest.permission.POST_NOTIFICATIONS)
        }
        when {
            Build.VERSION.SDK_INT >= 30 -> {
                if (!Environment.isExternalStorageManager()) {
                    AlertDialog.Builder(this)
                        .setTitle("Let GrabBox save files")
                        .setMessage(
                            "Downloaded files go into your Downloads folder, " +
                                "next to everything else you keep. Allow file access?"
                        )
                        .setPositiveButton("Allow") { _, _ ->
                            startActivity(
                                Intent(
                                    Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION,
                                    Uri.parse("package:$packageName"),
                                )
                            )
                        }
                        .setNegativeButton("Later", null)
                        .show()
                }
            }
            Build.VERSION.SDK_INT <= 28 -> {
                if (ContextCompat.checkSelfPermission(
                        this, android.Manifest.permission.WRITE_EXTERNAL_STORAGE
                    ) != android.content.pm.PackageManager.PERMISSION_GRANTED
                ) {
                    storagePermission.launch(android.Manifest.permission.WRITE_EXTERNAL_STORAGE)
                }
            }
            // API 29: requestLegacyExternalStorage covers the Downloads folder.
        }
    }

    fun toast(text: String) = Toast.makeText(this, text, Toast.LENGTH_SHORT).show()
}
