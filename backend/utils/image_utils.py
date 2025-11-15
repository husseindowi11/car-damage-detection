"""
Image processing utilities for bounding box generation
"""
import logging
from typing import List, Dict, Any, Tuple
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Utility class for processing images with bounding boxes"""
    
    # Color scheme for bounding boxes based on severity
    SEVERITY_COLORS = {
        "minor": "#10B981",    # Green
        "moderate": "#F59E0B", # Amber
        "major": "#EF4444",    # Red
    }
    
    DEFAULT_COLOR = "#EF4444"  # Red (default for unknown severity)
    
    @staticmethod
    def draw_bounding_boxes(
        image_path: str,
        damages: List[Dict[str, Any]],
        image_index: int
    ) -> Image.Image:
        """
        Draw bounding boxes on an image for damages that appear in that image.
        
        Args:
            image_path: Path to the source image
            damages: List of damage items from AI response
            image_index: 1-based index of the current image
            
        Returns:
            PIL Image with bounding boxes drawn
        """
        try:
            # Open image
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)
            
            # Get image dimensions
            img_width, img_height = img.size
            
            # Filter damages for this specific image
            image_damages = [d for d in damages if d.get("image_index") == image_index]
            
            if not image_damages:
                logger.info(f"No damages found for image index {image_index}")
                return img
            
            logger.info(f"Drawing {len(image_damages)} bounding boxes on image index {image_index}")
            
            # Try to load a font, fall back to default if not available
            try:
                # Try to use a TrueType font with reasonable size
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            except:
                try:
                    # macOS font path
                    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
                except:
                    # Fall back to default font
                    font = ImageFont.load_default()
            
            # Draw each bounding box
            for idx, damage in enumerate(image_damages, 1):
                bbox = damage.get("bounding_box", {})
                
                # Extract percentages and convert to pixel coordinates
                x_min_pct = bbox.get("x_min_pct", 0.0)
                y_min_pct = bbox.get("y_min_pct", 0.0)
                x_max_pct = bbox.get("x_max_pct", 0.0)
                y_max_pct = bbox.get("y_max_pct", 0.0)
                
                # Validate bounding box
                if not (0 <= x_min_pct < x_max_pct <= 1.0 and 0 <= y_min_pct < y_max_pct <= 1.0):
                    logger.warning(f"Invalid bounding box for damage: {damage.get('car_part')}")
                    continue
                
                # Convert to pixel coordinates
                x1 = int(x_min_pct * img_width)
                y1 = int(y_min_pct * img_height)
                x2 = int(x_max_pct * img_width)
                y2 = int(y_max_pct * img_height)
                
                # Get color based on severity
                severity = damage.get("severity", "major").lower()
                color = ImageProcessor.SEVERITY_COLORS.get(severity, ImageProcessor.DEFAULT_COLOR)
                
                # Draw rectangle (thicker lines for better visibility)
                line_width = max(3, int(min(img_width, img_height) * 0.005))  # Adaptive line width
                draw.rectangle(
                    [(x1, y1), (x2, y2)],
                    outline=color,
                    width=line_width
                )
                
                # Prepare label text
                car_part = damage.get("car_part", "Unknown")
                label = f"{idx}. {car_part} ({severity})"
                
                # Calculate text background size
                bbox_text = draw.textbbox((0, 0), label, font=font)
                text_width = bbox_text[2] - bbox_text[0]
                text_height = bbox_text[3] - bbox_text[1]
                
                # Position label above the bounding box, or inside if no space above
                label_y = y1 - text_height - 8 if y1 > text_height + 10 else y1 + 4
                label_x = x1 + 4
                
                # Ensure label doesn't go off screen
                if label_x + text_width + 8 > img_width:
                    label_x = img_width - text_width - 8
                if label_y < 0:
                    label_y = y1 + 4
                
                # Draw label background (semi-transparent)
                bg_coords = [
                    (label_x - 4, label_y - 2),
                    (label_x + text_width + 4, label_y + text_height + 2)
                ]
                draw.rectangle(bg_coords, fill=color + "CC")  # Add alpha for semi-transparency
                
                # Draw label text
                draw.text((label_x, label_y), label, fill="white", font=font)
            
            logger.info(f"Successfully drew {len(image_damages)} bounding boxes")
            return img
            
        except Exception as e:
            logger.error(f"Error drawing bounding boxes: {str(e)}")
            raise
    
    @staticmethod
    def create_bounded_images(
        after_image_paths: List[str],
        damage_report: Dict[str, Any],
        output_dir: Path
    ) -> List[str]:
        """
        Create bounded versions of AFTER images with damage highlights.
        Only creates images that have damages on them.
        
        Args:
            after_image_paths: List of paths to AFTER images
            damage_report: Damage report from AI analysis
            output_dir: Directory to save bounded images
            
        Returns:
            List of paths to bounded images (relative to uploads directory)
        """
        bounded_paths = []
        damages = damage_report.get("new_damage", [])
        
        if not damages:
            logger.info("No damages detected, skipping bounded image generation")
            return bounded_paths
        
        # Determine which images have damages
        images_with_damages = set()
        for damage in damages:
            img_idx = damage.get("image_index", 0)
            if 1 <= img_idx <= len(after_image_paths):
                images_with_damages.add(img_idx)
        
        logger.info(f"Found damages on {len(images_with_damages)} images: {sorted(images_with_damages)}")
        
        # Create bounded images only for images with damages
        for img_idx in sorted(images_with_damages):
            try:
                # Get the source image path (convert to absolute if relative)
                source_path = after_image_paths[img_idx - 1]  # Convert to 0-based index
                
                # Resolve to absolute path if it's relative
                if not Path(source_path).is_absolute():
                    source_path = Path("uploads") / source_path
                
                logger.info(f"Processing image {img_idx}: {source_path}")
                
                # Draw bounding boxes
                bounded_img = ImageProcessor.draw_bounding_boxes(
                    str(source_path),
                    damages,
                    img_idx
                )
                
                # Convert RGBA to RGB if necessary (JPEG doesn't support transparency)
                if bounded_img.mode in ('RGBA', 'LA', 'P'):
                    # Create a white background
                    rgb_img = Image.new('RGB', bounded_img.size, (255, 255, 255))
                    # Paste the image on the white background
                    if bounded_img.mode == 'P':
                        bounded_img = bounded_img.convert('RGBA')
                    rgb_img.paste(bounded_img, mask=bounded_img.split()[-1] if bounded_img.mode == 'RGBA' else None)
                    bounded_img = rgb_img
                
                # Save bounded image
                output_path = output_dir / f"bounded_{img_idx}.jpg"
                bounded_img.save(output_path, quality=95, optimize=True)
                
                # Return relative path from uploads directory
                relative_path = str(output_path.relative_to("uploads"))
                bounded_paths.append(relative_path)
                
                logger.info(f"Saved bounded image: {relative_path}")
                
            except Exception as e:
                logger.error(f"Error creating bounded image {img_idx}: {str(e)}")
                # Continue processing other images even if one fails
                continue
        
        logger.info(f"Created {len(bounded_paths)} bounded images")
        return bounded_paths

