package app.grabbox.ui

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext

// Brand fallback palette (pre-Android 12 devices without dynamic color).
private val BrandDark = darkColorScheme(
    primary = Color(0xFFA8C7FA),
    onPrimary = Color(0xFF0A305F),
    primaryContainer = Color(0xFF2A4670),
    onPrimaryContainer = Color(0xFFD7E3FF),
    secondary = Color(0xFFB9A5F5),
    surface = Color(0xFF111318),
    onSurface = Color(0xFFE4E6EC),
    surfaceContainer = Color(0xFF1B1D23),
    surfaceContainerHigh = Color(0xFF23262D),
    surfaceContainerLow = Color(0xFF16181D),
    outline = Color(0xFF3C4048),
    outlineVariant = Color(0xFF2A2D34),
)

private val BrandLight = lightColorScheme(
    primary = Color(0xFF365FA8),
    onPrimary = Color.White,
    primaryContainer = Color(0xFFD7E3FF),
    onPrimaryContainer = Color(0xFF0A305F),
    secondary = Color(0xFF5B48A8),
    surface = Color(0xFFF7F8FC),
    onSurface = Color(0xFF1A1C21),
)

/** Material You where available (Android 12+), brand palette elsewhere. */
@Composable
fun GrabBoxTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    val context = LocalContext.current
    val colors = when {
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.S ->
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        darkTheme -> BrandDark
        else -> BrandLight
    }
    MaterialTheme(colorScheme = colors, content = content)
}
