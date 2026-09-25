//! The downloaded-files view: list, open, reveal, delete — with the same
//! safety rule as the Python server (delete only inside the download folder).

use serde_json::{json, Value};
use std::fs;
use std::path::{Path, PathBuf};
use std::time::UNIX_EPOCH;
use tauri::Manager as _;
use tauri_plugin_opener::OpenerExt;

pub fn list_files(dir: &str) -> Vec<Value> {
    let mut out: Vec<(f64, Value)> = Vec::new();
    let entries = match fs::read_dir(dir) {
        Ok(e) => e,
        Err(_) => return Vec::new(),
    };
    for entry in entries.flatten() {
        let name = entry.file_name().to_string_lossy().into_owned();
        if name.starts_with('.') {
            continue;
        }
        let path = entry.path();
        let meta = match entry.metadata() {
            Ok(m) if m.is_file() => m,
            _ => continue,
        };
        let size = meta.len();
        let mtime = meta
            .modified()
            .ok()
            .and_then(|t| t.duration_since(UNIX_EPOCH).ok())
            .map(|d| d.as_secs_f64())
            .unwrap_or(0.0);
        let kind = crate::engine::kind_of_public(&name);
        out.push((
            mtime,
            json!({
                "name": name,
                "path": path.to_string_lossy(),
                "size": size,
                "size_h": human_size(size),
                "mtime": mtime,
                "kind": kind,
                "icon": kind_icon(&kind),
            }),
        ));
    }
    out.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap_or(std::cmp::Ordering::Equal));
    out.into_iter().take(200).map(|(_, v)| v).collect()
}

pub fn open_file(app: &tauri::AppHandle, path: &str) -> bool {
    app.opener()
        .open_path(path, None::<&str>)
        .map(|_| true)
        .unwrap_or(false)
}

pub fn reveal(app: &tauri::AppHandle, path: &str) -> bool {
    if Path::new(path).is_file() {
        if app.opener().reveal_item_in_dir(path).is_ok() {
            return true;
        }
    }
    let dir = if Path::new(path).is_dir() {
        PathBuf::from(path)
    } else {
        Path::new(path)
            .parent()
            .map(PathBuf::from)
            .unwrap_or_else(|| PathBuf::from(path))
    };
    app.opener()
        .open_path(dir.to_string_lossy(), None::<&str>)
        .is_ok()
}

pub fn delete(path: &str, root: &str) -> bool {
    let real = fs::canonicalize(path).unwrap_or_else(|_| PathBuf::from(path));
    let real_root = fs::canonicalize(root).unwrap_or_else(|_| PathBuf::from(root));
    if !real.starts_with(&real_root) || real == real_root {
        return false;
    }
    fs::remove_file(real).is_ok()
}

pub fn open_extension_folder(app: &tauri::AppHandle) -> bool {
    let resource = app
        .path()
        .resource_dir()
        .map(|d| d.join("extension"))
        .unwrap_or_default();
    let candidates = [
        resource,
        std::env::current_dir()
            .map(|d| d.join("extension"))
            .unwrap_or_default(),
    ];
    for dir in candidates {
        if dir.is_dir() {
            return app
                .opener()
                .open_path(dir.to_string_lossy(), None::<&str>)
                .is_ok();
        }
    }
    false
}

fn human_size(n: u64) -> String {
    if n == 0 {
        return "0 B".to_string();
    }
    let mut size = n as f64;
    for unit in ["B", "KB", "MB", "GB", "TB"] {
        if size < 1024.0 || unit == "TB" {
            return if unit == "B" {
                format!("{} B", n)
            } else {
                format!("{:.1} {}", size, unit)
            };
        }
        size /= 1024.0;
    }
    String::new()
}

fn kind_icon(kind: &str) -> &'static str {
    match kind {
        "video" => "🎬",
        "audio" => "🎵",
        "image" => "🖼️",
        "app" => "📦",
        "archive" => "🗜️",
        "document" => "📄",
        _ => "⬇️",
    }
}
