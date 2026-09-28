"""General helper functions for filesystem, path formatting, and icons."""
from pathlib import Path
from typing import Optional


def format_file_size(size_in_bytes: int) -> str:
    """Format bytes into human-readable size."""
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_in_bytes)
    unit_index = 0
    while size >= 1024.0 and unit_index < len(units) - 1:
        size /= 1024.0
        unit_index += 1
    return f"{size:.1f} {units[unit_index]}"


def is_safe_path(base_dir: Path, target_path: Path) -> bool:
    """Check if target_path is within base_dir to avoid directory traversal."""
    try:
        base_dir_resolved = base_dir.resolve()
        target_resolved = target_path.resolve()
        return target_resolved == base_dir_resolved or base_dir_resolved in target_resolved.parents
    except Exception:
        return False


def get_relative_display_path(file_path: Path, project_root: Optional[Path]) -> str:
    """Return a relative path string if file_path is under project_root, otherwise absolute."""
    if project_root:
        try:
            return str(file_path.relative_to(project_root))
        except ValueError:
            pass
    return str(file_path)
