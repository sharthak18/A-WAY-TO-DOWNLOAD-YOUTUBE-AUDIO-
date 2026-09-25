# youtubedl-android bundles native libs and Python; keep everything intact.
-keep class com.yausername.** { *; }
-keep class io.github.junkfood02.youtubedl_android.** { *; }
-dontwarn com.yausername.**
-dontwarn org.apache.commons.**
-dontwarn com.fasterxml.jackson.**
