"""Filesystem operations and manager for SmartIDE using pathlib."""

from pathlib import Path
from typing import List, Optional

from utils.logger import get_logger


logger = get_logger("file_manager")


class FileManager:
    """Handles non-GUI file and directory operations with error handling."""

    # Characters not allowed in Windows file/folder names.
    ILLEGAL_CHARACTERS = '\\/:*?"<>|'

    # Reserved Windows device names.
    RESERVED_NAMES = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }

    @staticmethod
    def is_valid_directory(path: Path | str) -> bool:
        """Check if path is an existing directory."""

        try:
            p = Path(path)
            return p.exists() and p.is_dir()

        except Exception as e:
            logger.error(
                "Error checking directory %s: %s",
                path,
                e
            )
            return False

    @staticmethod
    def is_valid_file(path: Path | str) -> bool:
        """Check if path is an existing file."""

        try:
            p = Path(path)
            return p.exists() and p.is_file()

        except Exception as e:
            logger.error(
                "Error checking file %s: %s",
                path,
                e
            )
            return False

    @staticmethod
    def list_directory(path: Path) -> List[Path]:
        """List children sorted by directory first, then name."""

        try:
            if not path.is_dir():
                return []

            items = list(path.iterdir())

            items.sort(
                key=lambda p: (
                    not p.is_dir(),
                    p.name.lower()
                )
            )

            return items

        except PermissionError as e:
            logger.warning(
                "Permission denied listing %s: %s",
                path,
                e
            )
            return []

        except Exception as e:
            logger.error(
                "Failed to list directory %s: %s",
                path,
                e
            )
            return []

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
            logger.warning(
                "Error reading file info for %s: %s",
                path,
                e
            )

            return {
                "name": path.name,
                "is_dir": False,
                "size": 0,
                "modified": 0,
                "suffix": "",
            }

    # ==========================================================
    # VALIDATION
    # ==========================================================

    @staticmethod
    def validate_name(name: str) -> bool:
        """
        Validate a file or folder name.

        Returns:
            True if the name is valid.

        Raises:
            ValueError if the name is invalid.
        """

        if name is None:
            raise ValueError(
                "File or folder name cannot be empty."
            )

        name = name.strip()

        # Empty name
        if not name:
            raise ValueError(
                "File or folder name cannot be empty."
            )

        # Illegal characters
        illegal_characters = [
            character
            for character in FileManager.ILLEGAL_CHARACTERS
            if character in name
        ]

        if illegal_characters:
            illegal = ", ".join(
                repr(character)
                for character in illegal_characters
            )

            raise ValueError(
                f"Name contains illegal character(s): {illegal}"
            )

        # Windows does not allow names ending
        # with a space or period.
        if name.endswith(" ") or name.endswith("."):
            raise ValueError(
                "File or folder name cannot end "
                "with a space or period."
            )

        # Windows reserved names.
        base_name = Path(name).stem.upper()

        if base_name in FileManager.RESERVED_NAMES:
            raise ValueError(
                f"'{name}' is a reserved system name."
            )

        return True

    # ==========================================================
    # CREATE FILE
    # ==========================================================

    @staticmethod
    def create_file(
        directory: Path | str,
        file_name: str
    ) -> Path:
        """
        Create a new empty file.

        The file will NOT overwrite an existing file.

        Raises:
            ValueError:
                Invalid file name.

            FileNotFoundError:
                Parent directory does not exist.

            FileExistsError:
                File/folder with same name already exists.
        """

        FileManager.validate_name(file_name)

        directory_path = Path(directory)

        if not directory_path.exists():
            raise FileNotFoundError(
                f"Directory does not exist: {directory_path}"
            )

        if not directory_path.is_dir():
            raise NotADirectoryError(
                f"Path is not a directory: {directory_path}"
            )

        file_name = file_name.strip()

        file_path = directory_path / file_name

        # Prevent duplicate file/folder names.
        if file_path.exists():
            raise FileExistsError(
                f"A file or folder named "
                f"'{file_name}' already exists."
            )

        try:
            # exist_ok=False ensures that an existing
            # file is never overwritten.
            file_path.touch(
                exist_ok=False
            )

            logger.info(
                "File created: %s",
                file_path
            )

            return file_path

        except FileExistsError:
            logger.warning(
                "File already exists: %s",
                file_path
            )
            raise

        except PermissionError:
            logger.error(
                "Permission denied creating file: %s",
                file_path
            )
            raise

        except OSError as e:
            logger.error(
                "Failed to create file %s: %s",
                file_path,
                e
            )
            raise

    # ==========================================================
    # CREATE FOLDER
    # ==========================================================

    @staticmethod
    def create_folder(
        directory: Path | str,
        folder_name: str
    ) -> Path:
        """
        Create a new directory.

        The folder will NOT overwrite an existing
        file or folder with the same name.
        """

        FileManager.validate_name(folder_name)

        directory_path = Path(directory)

        if not directory_path.exists():
            raise FileNotFoundError(
                f"Directory does not exist: {directory_path}"
            )

        if not directory_path.is_dir():
            raise NotADirectoryError(
                f"Path is not a directory: {directory_path}"
            )

        folder_name = folder_name.strip()

        folder_path = (
            directory_path / folder_name
        )

        # Prevent duplicate names.
        if folder_path.exists():
            raise FileExistsError(
                f"A file or folder named "
                f"'{folder_name}' already exists."
            )

        try:
            folder_path.mkdir(
                exist_ok=False
            )

            logger.info(
                "Folder created: %s",
                folder_path
            )

            return folder_path

        except FileExistsError:
            logger.warning(
                "Folder already exists: %s",
                folder_path
            )
            raise

        except PermissionError:
            logger.error(
                "Permission denied creating folder: %s",
                folder_path
            )
            raise

        except OSError as e:
            logger.error(
                "Failed to create folder %s: %s",
                folder_path,
                e
            )
            raise

    # ==========================================================
    # RENAME FILE / FOLDER
    # ==========================================================

    @staticmethod
    def rename(
        path: Path | str,
        new_name: str
    ) -> Path:
        """
        Rename a file or folder.

        The new name is validated and the destination
        is checked before renaming.
        """

        FileManager.validate_name(new_name)

        source_path = Path(path)

        if not source_path.exists():
            raise FileNotFoundError(
                f"File or folder does not exist: "
                f"{source_path}"
            )

        new_name = new_name.strip()

        new_path = (
            source_path.parent / new_name
        )

        # Check if another file/folder already
        # exists at the new location.
        if new_path.exists():

            # Allow renaming to the same name.
            if new_path.resolve() != source_path.resolve():
                raise FileExistsError(
                    f"A file or folder named "
                    f"'{new_name}' already exists."
                )

            return source_path

        try:
            source_path.rename(
                new_path
            )

            logger.info(
                "Renamed '%s' to '%s'",
                source_path,
                new_path
            )

            return new_path

        except PermissionError:
            logger.error(
                "Permission denied renaming: %s",
                source_path
            )
            raise

        except OSError as e:
            logger.error(
                "Failed to rename %s: %s",
                source_path,
                e
            )
            raise

    # ==========================================================
    # DELETE FILE / FOLDER
    # ==========================================================

    @staticmethod
    def delete(
        path: Path | str
    ) -> bool:
        """
        Delete a file or an entire folder.

        Files are deleted using unlink().
        Folders are deleted recursively.

        Returns:
            True when deletion succeeds.
        """

        path_obj = Path(path)

        if not path_obj.exists():
            raise FileNotFoundError(
                f"File or folder does not exist: "
                f"{path_obj}"
            )

        try:

            # Delete file
            if path_obj.is_file():
                path_obj.unlink()

                logger.info(
                    "File deleted: %s",
                    path_obj
                )

                return True

            # Delete directory recursively
            if path_obj.is_dir():
                FileManager._delete_directory(
                    path_obj
                )

                logger.info(
                    "Folder deleted: %s",
                    path_obj
                )

                return True

            raise OSError(
                f"Unsupported filesystem object: "
                f"{path_obj}"
            )

        except PermissionError:
            logger.error(
                "Permission denied deleting: %s",
                path_obj
            )
            raise

        except OSError as e:
            logger.error(
                "Failed to delete %s: %s",
                path_obj,
                e
            )
            raise

    @staticmethod
    def _delete_directory(
        directory: Path
    ) -> None:
        """Recursively delete a directory."""

        for item in directory.iterdir():

            if item.is_dir() and not item.is_symlink():

                FileManager._delete_directory(
                    item
                )

            else:
                item.unlink()

        directory.rmdir()