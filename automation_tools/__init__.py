"""
Python Automation Tools / ابزارهای اتوماسیون پایتون
--------------------------------------------------
A collection of useful automation scripts for various tasks.
مجموعه‌ای از اسکریپت‌های اتوماسیون مفید برای کاربردهای مختلف
"""

__version__ = "0.1.0"  # نسخه کنونی بسته

# Import main classes for easier access
# وارد کردن کلاس‌های اصلی برای دسترسی آسان‌تر
from .file_organizer import FileOrganizer
from .pdf_merger import PDFMerger
from .image_resizer import ImageResizer

__all__ = [
    'FileOrganizer',  # برای سازماندهی فایل‌ها
    'PDFMerger',      # برای ادغام فایل‌های PDF
    'ImageResizer'    # برای تغییر اندازه تصاویر
]
