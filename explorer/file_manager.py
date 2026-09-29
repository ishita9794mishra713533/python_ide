"""Filesystem operations and manager for SmartIDE using pathlib."""
import os
import shutil
import re
from pathlib import Path
from typing import List, Optional, Tuple
from utils.logger import get_logger

logger = get_logger("file_manager")

INVALID_FILENAME_CHARS = r'[\\/:*?"<>|]'


class FileManager:
    """Handles non-GUI file and directory operations with error handling."""

    @staticmethod
    def is_valid_directory(path: Path | str) -> bool:
        """Check if path is an existing directory."""
        try:
            p = Path(path)
            return p.exists() and p.is_dir()
        except Exception as e:
            logger.error("Error checking directory %s: %s", path, e)
            return False

    @staticmethod
    def is_valid_file(path: Path | str) -> bool:
        """Check if path is an existing file."""
        try:
            p = Path(path)
            return p.exists() and p.is_file()
        except Exception as e:
            logger.error("Error checking file %s: %s", path, e)
            return False

    @staticmethod
    def list_directory(path: Path) -> List[Path]:
        """List children sorted by directory first, then name."""
        try:
            if not path.is_dir():
                return []
            items = list(path.iterdir())
            items.sort(key=lambda p: (not p.is_dir(), p.name.lower()))
            return items
        except PermissionError as e:
            logger.warning("Permission denied listing %s: %s", path, e)
            return []
        except Exception as e:
            logger.error("Failed to list directory %s: %s", path, e)
            return []

    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """Validate filename or folder name against illegal characters and empty names."""
        clean = name.strip()
        if not clean:
            return False, "Name cannot be empty."
        if re.search(INVALID_FILENAME_CHARS, clean):
            return False, 'Name cannot contain characters: \\ / : * ? " < > |'
        if clean in {".", ".."}:
            return False, "Invalid name."
        return True, ""

    @staticmethod
    def can_delete(target_path: Path | str, root_path: Optional[Path | str] = None) -> Tuple[bool, str]:
        """Check if an item can be safely deleted."""
        target = Path(target_path).resolve()
        if not target.exists():
            return False, f"Item does not exist:\n{target}"

        # Cannot delete drive root
        if str(target).lower() in ("c:\\", "d:\\", "c:/", "d:/", "/"):
            return False, "Cannot delete drive root."

        # Cannot delete project root folder
        if root_path is not None:
            r = Path(root_path).resolve()
            if target == r:
                return False, "Cannot delete the project root directory."

        # Cannot delete SmartIDE source repo directly
        if target.name.lower() == "smartide" or "smartide" in target.name.lower():
            if root_path and Path(root_path).resolve() == target:
                return False, "Cannot delete SmartIDE source folder."

        return True, ""

    @staticmethod
    def create_file(parent_or_path: Path | str, file_name: Optional[str] = None) -> Tuple[bool, str, Optional[Path]]:
        """Create a new file safely without overwriting existing files."""
        if file_name is None:
            target_file = Path(parent_or_path).resolve()
            parent = target_file.parent
            file_name = target_file.name
        else:
            parent = Path(parent_or_path).resolve()
            target_file = parent / file_name.strip()

        valid, msg = FileManager.validate_name(file_name)
        if not valid:
            return False, msg, None

        if not parent.is_dir():
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"Cannot create parent directory:\n{e}", None

        if target_file.exists():
            return False, f"A file or folder named '{file_name}' already exists in this directory.", None

        try:
            target_file.touch(exist_ok=False)
            logger.info("Created file: %s", target_file)
            return True, "File created successfully.", target_file
        except PermissionError:
            msg = f"Permission denied creating file at: {target_file}"
            logger.error(msg)
            return False, msg, None
        except Exception as e:
            msg = f"Error creating file: {e}"
            logger.error(msg)
            return False, msg, None

    @staticmethod
    def create_folder(parent_or_path: Path | str, folder_name: Optional[str] = None) -> Tuple[bool, str, Optional[Path]]:
        """Create a new folder safely."""
        if folder_name is None:
            target_folder = Path(parent_or_path).resolve()
            parent = target_folder.parent
            folder_name = target_folder.name
        else:
            parent = Path(parent_or_path).resolve()
            target_folder = parent / folder_name.strip()

        valid, msg = FileManager.validate_name(folder_name)
        if not valid:
            return False, msg, None

        if not parent.is_dir():
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"Cannot create parent directory:\n{e}", None

        if target_folder.exists():
            return False, f"A file or folder named '{folder_name}' already exists in this directory.", None

        try:
            target_folder.mkdir(parents=True, exist_ok=False)
            logger.info("Created directory: %s", target_folder)
            return True, "Folder created successfully.", target_folder
        except PermissionError:
            msg = f"Permission denied creating folder at: {target_folder}"
            logger.error(msg)
            return False, msg, None
        except Exception as e:
            msg = f"Error creating folder: {e}"
            logger.error(msg)
            return False, msg, None

    @staticmethod
    def create_directory(parent_or_path: Path | str, folder_name: Optional[str] = None) -> Tuple[bool, str, Optional[Path]]:
        """Alias for create_folder."""
        return FileManager.create_folder(parent_or_path, folder_name)

    @staticmethod
    def rename_item(target_path: Path | str, new_name_or_dest: Path | str) -> Tuple[bool, str, Optional[Path]]:
        """Rename a file or directory safely."""
        target = Path(target_path).resolve()
        if not target.exists():
            return False, f"Item does not exist:\n{target}", None

        dest_candidate = Path(new_name_or_dest)
        if dest_candidate.is_absolute() or len(dest_candidate.parts) > 1:
            destination = dest_candidate.resolve()
            valid, msg = FileManager.validate_name(destination.name)
        else:
            valid, msg = FileManager.validate_name(str(new_name_or_dest))
            destination = target.parent / str(new_name_or_dest).strip()

        if not valid:
            return False, msg, None

        if destination == target:
            return True, "Name unchanged.", target

        if destination.exists():
            return False, f"An item named '{destination.name}' already exists.", None

        try:
            target.rename(destination)
            logger.info("Renamed '%s' to '%s'", target, destination)
            return True, "Item renamed successfully.", destination
        except PermissionError:
            msg = f"Permission denied renaming '{target.name}'."
            logger.error(msg)
            return False, msg, None
        except Exception as e:
            msg = f"Failed to rename item: {e}"
            logger.error(msg)
            return False, msg, None

    @staticmethod
    def delete_item(target_path: Path | str, root_path: Optional[Path | str] = None) -> Tuple[bool, str]:
        """Delete a file or directory recursively with critical protections."""
        can_del, reason = FileManager.can_delete(target_path, root_path)
        if not can_del:
            return False, reason

        target = Path(target_path).resolve()
        try:
            if target.is_dir():
                shutil.rmtree(target)
                logger.info("Deleted directory: %s", target)
            else:
                target.unlink()
                logger.info("Deleted file: %s", target)
            return True, f"'{target.name}' deleted successfully."
        except PermissionError:
            msg = f"Permission denied deleting '{target.name}'. Check if it is in use."
            logger.error(msg)
            return False, msg
        except Exception as e:
            msg = f"Failed to delete '{target.name}': {e}"
            logger.error(msg)
            return False, msg

    @staticmethod
    def read_file_content(path: Path | str) -> str:
        """Read text from file with utf-8 fallback."""
        p = Path(path).resolve()
        try:
            with open(p, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            with open(p, "r", encoding="latin-1") as f:
                return f.read()

    @staticmethod
    def write_file_content(path: Path | str, content: str) -> bool:
        """Write text to file."""
        p = Path(path).resolve()
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error("Error writing to file %s: %s", p, e)
            return False

    @staticmethod
    def get_file_info(path: Path) -> dict:
        """Return basic metadata of a file."""
        try:
            stat = path.stat()
            return {
                "name": path.name,
                "is_dir": path.is_dir(),
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "suffix": path.suffix.lower(),
            }
        except Exception as e:
            logger.warning("Error reading file info for %s: %s", path, e)
            return {"name": path.name, "is_dir": False, "size": 0, "modified": 0, "suffix": ""}
