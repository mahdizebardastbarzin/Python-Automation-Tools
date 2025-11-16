"""
File Organizer / سازمان‌دهنده فایل‌ها
------------------------------------
Organizes files in a directory by their extensions into corresponding folders.
فایل‌های موجود در یک پوشه را بر اساس پسوندشان در پوشه‌های مربوطه مرتب می‌کند.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Set, Optional
import logging

# Configure logging / تنظیمات لاگ‌گیری
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class FileOrganizer:
    """
    A class to organize files in a directory by their extensions.
    کلاسی برای سازماندهی فایل‌ها در یک پوشه بر اساس پسوند آنها
    
    This class provides functionality to organize files into folders based on
    their file extensions, making it easier to manage large numbers of files.
    این کلاس قابلیت سازماندهی فایل‌ها را بر اساس پسوند آنها فراهم می‌کند
    و مدیریت تعداد زیادی فایل را آسان‌تر می‌سازد.
    """
    
    # Common file types and their corresponding folders
    # انواع فایل‌های رایج و پوشه‌های مربوط به آنها
    FILE_TYPES = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.pptx'],
        'videos': ['.mp4', '.mov', '.avi', '.mkv', '.wmv'],
        'audio': ['.mp3', '.wav', '.ogg', '.m4a'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.h'],
        'executables': ['.exe', '.msi', '.dmg', '.pkg', '.deb'],
    }
    
    def __init__(self, directory: str):
        """
        Initialize the FileOrganizer with a target directory.
        مقداردهی اولیه سازمان‌دهنده فایل با مسیر پوشه هدف
        
        Args:
            directory (str): Path to the directory to organize
                           مسیر پوشه‌ای که می‌خواهید سازماندهی شود
        """
        self.directory = Path(directory).expanduser().resolve()
        self._validate_directory()
    
    def _validate_directory(self) -> None:
        """
        Validate that the directory exists and is accessible.
        بررسی می‌کند که پوشه وجود دارد و قابل دسترسی است
        """
        if not self.directory.exists():
            raise FileNotFoundError(f"Directory not found: {self.directory}")
        if not self.directory.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {self.directory}")
    
    def _get_extension(self, file_path: Path) -> str:
        """
        Get the lowercase extension of a file.
        پسوند فایل را به حروف کوچک برمی‌گرداند
        """
        return file_path.suffix.lower()
    
    def _get_category(self, extension: str) -> str:
        """
        Determine the category folder for a given file extension.
        پوشه مناسب برای پسوند فایل داده شده را تعیین می‌کند
        
        Args:
            extension (str): File extension including the dot (e.g., '.jpg')
                           پسوند فایل همراه با نقطه (مثلاً '.jpg')
            
        Returns:
            str: Category name or 'other' if no match found
                 نام دسته یا 'other' در صورت عدم تطابق
        """
        for category, extensions in self.FILE_TYPES.items():
            if extension in extensions:
                return category
        return 'other'
    
    def organize(self, dry_run: bool = False) -> Dict[str, list]:
        """
        Organize files in the directory by their extensions.
        
        Args:
            dry_run (bool): If True, only show what would be done without making changes
            
        Returns:
            Dict[str, list]: A dictionary mapping categories to lists of moved files
        """
        if not dry_run:
            logger.info(f"Organizing files in: {self.directory}")
        else:
            logger.info(f"[DRY RUN] Would organize files in: {self.directory}")
        
        moved_files = {category: [] for category in self.FILE_TYPES.keys()}
        moved_files['other'] = []
        
        # Process each file in the directory
        for item in self.directory.iterdir():
            # Skip directories and hidden files
            if item.is_dir() or item.name.startswith('.'):
                continue
                
            # Get file extension and category
            extension = self._get_extension(item)
            category = self._get_category(extension)
            
            # Create category directory if it doesn't exist
            category_dir = self.directory / category
            if not category_dir.exists() and not dry_run:
                category_dir.mkdir(exist_ok=True)
                logger.info(f"Created directory: {category_dir.name}")
            
            # Prepare the destination path
            dest_path = category_dir / item.name
            
            # Handle filename conflicts
            counter = 1
            while dest_path.exists() and not dry_run:
                dest_path = category_dir / f"{item.stem}_{counter}{item.suffix}"
                counter += 1
            
            # Move the file
            if not dry_run:
                try:
                    shutil.move(str(item), str(dest_path))
                    moved_files[category].append(item.name)
                    logger.info(f"Moved: {item.name} -> {category}/{dest_path.name}")
                except Exception as e:
                    logger.error(f"Error moving {item.name}: {e}")
            else:
                moved_files[category].append(item.name)
                logger.info(f"[DRY RUN] Would move: {item.name} -> {category}/{dest_path.name}")
        
        # Log summary
        total_moved = sum(len(files) for files in moved_files.values())
        if not dry_run:
            logger.info(f"Organization complete. Moved {total_moved} files.")
        else:
            logger.info(f"[DRY RUN] Would move {total_moved} files.")
        
        return moved_files

def organize_files(directory: str, dry_run: bool = False) -> Dict[str, list]:
    """
    Convenience function to organize files in a directory.
    
    Args:
        directory (str): Path to the directory to organize
        dry_run (bool): If True, only show what would be done without making changes
        
    Returns:
        Dict[str, list]: A dictionary mapping categories to lists of moved files
    """
    organizer = FileOrganizer(directory)
    return organizer.organize(dry_run=dry_run)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Organize files in a directory by their extensions.')
    parser.add_argument('directory', nargs='?', default='.', 
                       help='Directory to organize (default: current directory)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    try:
        organize_files(args.directory, dry_run=args.dry_run)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        exit(1)
