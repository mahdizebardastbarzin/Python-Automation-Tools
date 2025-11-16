"""
Image Resizer
------------
A tool to resize multiple images to specified dimensions or scale.
"""

import os
import argparse
from pathlib import Path
from typing import List, Tuple, Optional, Union
from PIL import Image
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ImageResizer:
    """
    A class to resize multiple images with various options.
    
    This class provides functionality to resize images while maintaining
    aspect ratio, convert between formats, and apply quality settings.
    """
    
    # Supported image formats
    SUPPORTED_FORMATS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.gif')
    
    def __init__(self, output_dir: Optional[str] = None, output_format: Optional[str] = None):
        """
        Initialize the ImageResizer.
        
        Args:
            output_dir (str, optional): Directory to save resized images
            output_format (str, optional): Output format (e.g., 'JPEG', 'PNG')
        """
        self.output_dir = Path(output_dir) if output_dir else None
        self.output_format = output_format.upper() if output_format else None
        
        # Set default quality for lossy formats
        self.quality = 85
    
    def _validate_output_dir(self, input_path: Path) -> Path:
        """Validate and return the output directory path."""
        if self.output_dir:
            output_dir = Path(self.output_dir).expanduser().resolve()
        else:
            output_dir = input_path.parent / 'resized'
        
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    
    def _get_output_path(self, input_path: Path, output_dir: Path) -> Path:
        """Generate output path for the resized image."""
        # Determine output format
        if self.output_format:
            ext = f".{self.output_format.lower()}"
        else:
            ext = input_path.suffix.lower()
            
        # Create output filename
        output_filename = f"{input_path.stem}_resized{ext}"
        return output_dir / output_filename
    
    def resize_image(
        self,
        input_path: Union[str, Path],
        size: Optional[Tuple[int, int]] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        scale: Optional[float] = None,
        maintain_aspect_ratio: bool = True,
        quality: Optional[int] = None
    ) -> Path:
        """
        Resize a single image.
        
        Args:
            input_path: Path to the input image
            size: Target size as (width, height) in pixels
            width: Target width (height will be calculated to maintain aspect ratio)
            height: Target height (width will be calculated to maintain aspect ratio)
            scale: Scale factor (e.g., 0.5 for 50% of original size)
            maintain_aspect_ratio: Whether to maintain the aspect ratio
            quality: Output quality (1-100) for lossy formats
            
        Returns:
            Path to the resized image
        """
        input_path = Path(input_path).expanduser().resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Validate output directory
        output_dir = self._validate_output_dir(input_path)
        output_path = self._get_output_path(input_path, output_dir)
        
        try:
            # Open the image
            with Image.open(input_path) as img:
                # Convert to RGB if needed (for JPEG)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                original_size = img.size
                
                # Calculate new size
                if size:
                    new_size = size
                elif width and height:
                    new_size = (width, height)
                elif width:
                    ratio = width / img.width
                    new_size = (width, int(img.height * ratio))
                elif height:
                    ratio = height / img.height
                    new_size = (int(img.width * ratio), height)
                elif scale:
                    new_size = (int(img.width * scale), int(img.height * scale))
                else:
                    raise ValueError("No valid size, width, height, or scale provided")
                
                # Resize the image
                resized_img = img.resize(new_size, Image.LANCZOS)
                
                # Determine output format
                output_format = self.output_format or img.format or 'JPEG'
                
                # Set quality
                save_kwargs = {}
                if output_format in ('JPEG', 'WEBP'):
                    save_kwargs['quality'] = quality or self.quality
                elif output_format == 'PNG':
                    save_kwargs['compress_level'] = 6  # Default compression for PNG
                
                # Save the resized image
                resized_img.save(
                    output_path,
                    format=output_format,
                    **save_kwargs
                )
                
                logger.info(
                    f"Resized {input_path.name} from {original_size} to {new_size} "
                    f"and saved as {output_path}"
                )
                
                return output_path
                
        except Exception as e:
            logger.error(f"Error processing {input_path.name}: {e}")
            raise
    
    def resize_directory(
        self,
        directory: Union[str, Path],
        recursive: bool = False,
        **kwargs
    ) -> List[Path]:
        """
        Resize all images in a directory.
        
        Args:
            directory: Directory containing images
            recursive: If True, search for images in subdirectories
            **kwargs: Additional arguments to pass to resize_image
            
        Returns:
            List of paths to resized images
        """
        directory = Path(directory).expanduser().resolve()
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Find all image files
        if recursive:
            image_paths = []
            for ext in self.SUPPORTED_FORMATS:
                image_paths.extend(directory.rglob(f"*{ext}"))
        else:
            image_paths = []
            for ext in self.SUPPORTED_FORMATS:
                image_paths.extend(directory.glob(f"*{ext}"))
        
        if not image_paths:
            logger.warning(f"No supported image files found in {directory}")
            return []
        
        # Resize each image
        resized_paths = []
        for img_path in tqdm(image_paths, desc="Resizing images"):
            try:
                output_path = self.resize_image(img_path, **kwargs)
                resized_paths.append(output_path)
            except Exception as e:
                logger.error(f"Error processing {img_path.name}: {e}")
        
        return resized_paths

def resize_images(
    paths: List[Union[str, Path]],
    output_dir: Optional[str] = None,
    output_format: Optional[str] = None,
    recursive: bool = False,
    **kwargs
) -> List[Path]:
    """
    Resize one or more images or directories of images.
    
    Args:
        paths: List of file paths or directories containing images
        output_dir: Directory to save resized images
        output_format: Output format (e.g., 'JPEG', 'PNG')
        recursive: If True, search for images in subdirectories
        **kwargs: Additional arguments to pass to resize_image
        
    Returns:
        List of paths to resized images
    """
    resizer = ImageResizer(output_dir, output_format)
    all_resized = []
    
    for path in paths:
        path = Path(path).expanduser().resolve()
        
        if path.is_file():
            try:
                output_path = resizer.resize_image(path, **kwargs)
                all_resized.append(output_path)
            except Exception as e:
                logger.error(f"Error processing {path.name}: {e}")
        elif path.is_dir():
            resized = resizer.resize_directory(path, recursive=recursive, **kwargs)
            all_resized.extend(resized)
    
    return all_resized

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Resize one or more images.')
    
    # Input/output options
    parser.add_argument('paths', nargs='+', help='Image files or directories to resize')
    parser.add_argument('-o', '--output-dir', help='Output directory for resized images')
    parser.add_argument('--output-format', help='Output format (e.g., JPEG, PNG, WEBP)')
    parser.add_argument('-r', '--recursive', action='store_true', 
                       help='Recursively search for images in subdirectories')
    
    # Resize options
    size_group = parser.add_mutually_exclusive_group()
    size_group.add_argument('--size', nargs=2, type=int, metavar=('WIDTH', 'HEIGHT'),
                          help='Target size as WIDTH HEIGHT')
    size_group.add_argument('--width', type=int, help='Target width (maintains aspect ratio)')
    size_group.add_argument('--height', type=int, help='Target height (maintains aspect ratio)')
    size_group.add_argument('--scale', type=float, help='Scale factor (e.g., 0.5 for 50%%)')
    
    # Quality options
    parser.add_argument('--quality', type=int, choices=range(1, 101), metavar='1-100',
                      help='Output quality (1-100) for lossy formats')
    
    args = parser.parse_args()
    
    # Prepare resize arguments
    resize_kwargs = {}
    if args.size:
        resize_kwargs['size'] = tuple(args.size)
    if args.width:
        resize_kwargs['width'] = args.width
    if args.height:
        resize_kwargs['height'] = args.height
    if args.scale:
        resize_kwargs['scale'] = args.scale
    if args.quality:
        resize_kwargs['quality'] = args.quality
    
    try:
        resized = resize_images(
            args.paths,
            output_dir=args.output_dir,
            output_format=args.output_format,
            recursive=args.recursive,
            **resize_kwargs
        )
        
        if resized:
            print(f"\nSuccessfully resized {len(resized)} images:")
            for path in resized:
                print(f"- {path}")
        else:
            print("No images were resized.")
            
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        exit(1)
