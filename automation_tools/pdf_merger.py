"""
PDF Merger / ادغام‌کننده فایل‌های PDF
------------------------------------
A tool to merge multiple PDF files into a single PDF document.
ابزاری برای ادغام چندین فایل PDF در یک سند واحد
"""

import os
import argparse
from pathlib import Path
from typing import List, Optional, Set, Dict, Union
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import logging

# Configure logging / تنظیمات لاگ‌گیری
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class PDFMerger:
    """
    A class to merge multiple PDF files into a single PDF document.
    
    This class provides functionality to combine multiple PDF files while
    preserving bookmarks and metadata.
    """
    
    def __init__(self, output_path: str):
        """
        Initialize the PDFMerger with an output file path.
        
        Args:
            output_path (str): Path where the merged PDF will be saved
        """
        self.output_path = Path(output_path).expanduser().resolve()
        self.merger = PdfMerger()
    
    def add_file(self, file_path: str, bookmark: Optional[str] = None):
        """
        Add a PDF file to be merged.
        
        Args:
            file_path (str): Path to the PDF file to add
            bookmark (str, optional): Bookmark name for the PDF
        """
        file_path = Path(file_path).expanduser().resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Verify it's a valid PDF
            with open(file_path, 'rb') as f:
                PdfReader(f)
                
            # Add to merger
            with open(file_path, 'rb') as f:
                if bookmark:
                    self.merger.append(f, bookmark)
                else:
                    self.merger.append(f)
                
            logger.info(f"Added: {file_path.name} {'(Bookmarked as: ' + bookmark + ')' if bookmark else ''}")
            
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            raise
    
    def add_directory(self, directory: str, recursive: bool = False, pattern: str = "*.pdf"):
        """
        Add all PDF files from a directory.
        
        Args:
            directory (str): Directory containing PDF files
            recursive (bool): If True, search for PDFs in subdirectories
            pattern (str): File pattern to match (default: "*.pdf")
        """
        directory = Path(directory).expanduser().resolve()
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Find all matching PDF files
        if recursive:
            pdf_files = list(directory.rglob(pattern))
        else:
            pdf_files = list(directory.glob(pattern))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in {directory}")
            return
        
        # Add each PDF file
        for pdf_file in sorted(pdf_files):
            if pdf_file.is_file():
                try:
                    self.add_file(str(pdf_file), pdf_file.stem)
                except Exception as e:
                    logger.error(f"Skipping {pdf_file.name}: {e}")
    
    def merge(self, output_path: Optional[str] = None, delete_originals: bool = False) -> str:
        """
        Merge all added PDF files and save the result.
        
        Args:
            output_path (str, optional): Override the output path
            delete_originals (bool): If True, delete original files after merging
            
        Returns:
            str: Path to the merged PDF file
        """
        if output_path:
            self.output_path = Path(output_path).expanduser().resolve()
        
        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Write the merged PDF to the output file
            with open(self.output_path, 'wb') as f:
                self.merger.write(f)
            
            logger.info(f"Successfully created merged PDF: {self.output_path}")
            
            # Optionally delete original files
            if delete_originals:
                self._delete_original_files()
                
            return str(self.output_path)
            
        except Exception as e:
            logger.error(f"Error merging PDFs: {e}")
            raise
        finally:
            self.merger.close()
    
    def _delete_original_files(self):
        """Delete original PDF files that were merged."""
        # This is a simplified example - in a real implementation, you'd track original files
        logger.warning("Deleting original files is not implemented in this example")

def merge_pdfs(
    input_paths: List[str],
    output_path: str,
    recursive: bool = False,
    delete_originals: bool = False
) -> str:
    """
    Convenience function to merge multiple PDFs.
    
    Args:
        input_paths (List[str]): List of file paths or directories containing PDFs
        output_path (str): Path where the merged PDF will be saved
        recursive (bool): If True, search for PDFs in subdirectories
        delete_originals (bool): If True, delete original files after merging
        
    Returns:
        str: Path to the merged PDF file
    """
    merger = PDFMerger(output_path)
    
    for path in input_paths:
        path = Path(path).expanduser().resolve()
        
        if path.is_file() and path.suffix.lower() == '.pdf':
            try:
                merger.add_file(str(path))
            except Exception as e:
                logger.error(f"Skipping {path.name}: {e}")
        elif path.is_dir():
            merger.add_directory(str(path), recursive=recursive)
    
    return merger.merge(delete_originals=delete_originals)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Merge multiple PDF files into a single PDF.')
    parser.add_argument('input_paths', nargs='+', 
                       help='PDF files or directories containing PDFs to merge')
    parser.add_argument('-o', '--output', default='merged.pdf',
                       help='Output PDF file path (default: merged.pdf)')
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='Recursively search for PDFs in subdirectories')
    parser.add_argument('--delete-originals', action='store_true',
                       help='Delete original files after merging (use with caution!)')
    
    args = parser.parse_args()
    
    try:
        result = merge_pdfs(
            args.input_paths,
            args.output,
            recursive=args.recursive,
            delete_originals=args.delete_originals
        )
        print(f"Merged PDF created: {result}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        exit(1)
