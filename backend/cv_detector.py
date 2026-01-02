#!/usr/bin/env python3
"""
CV DETECTOR - Computer Vision Brand Detection
==============================================
Uses image similarity to detect unauthorized use of brand assets.
"""

import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import os
import hashlib
from datetime import datetime
import base64

logger = logging.getLogger('CV_DETECTOR')

# Try to import image processing libraries
try:
    from PIL import Image
    import io
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    logger.warning("Pillow not installed. CV detection will be limited.")

try:
    from skimage.metrics import structural_similarity as ssim
    import numpy as np
    HAS_SKIMAGE = True
except ImportError:
    HAS_SKIMAGE = False
    logger.warning("scikit-image not installed. Using basic comparison.")


@dataclass
class BrandAsset:
    """A brand asset for comparison."""
    name: str
    brand: str
    category: str  # 'logo', 'ui', 'color_scheme'
    image_path: str
    image_hash: str


@dataclass
class DetectionResult:
    """Result of CV detection."""
    domain: str
    screenshot_path: Optional[str]
    matched_brand: Optional[str]
    similarity_score: float
    confidence: str  # 'high', 'medium', 'low', 'none'
    matched_assets: List[str]
    detection_time: str


class CVDetector:
    """
    Computer Vision detector for brand impersonation.
    
    Uses image similarity metrics to detect unauthorized use of brand logos,
    UI patterns, and color schemes commonly used by Thai banks.
    """
    
    ASSETS_DIR = "brand_assets"
    
    # Thai brand color schemes (RGB)
    THAI_BRAND_COLORS = {
        'kbank': [(0, 166, 81), (255, 255, 255)],  # Green and white
        'scb': [(75, 45, 121), (255, 255, 255)],   # Purple and white
        'bbl': [(0, 51, 160), (255, 204, 0)],      # Blue and gold
        'ktb': [(0, 102, 204), (255, 255, 255)],   # Blue and white
        'krungsri': [(255, 204, 0), (0, 0, 0)],    # Yellow and black
        'ttb': [(255, 102, 0), (255, 255, 255)],   # Orange and white
    }
    
    # Confidence thresholds
    THRESHOLD_HIGH = 0.85
    THRESHOLD_MEDIUM = 0.70
    THRESHOLD_LOW = 0.55
    
    def __init__(self):
        self.assets: List[BrandAsset] = []
        self._load_assets()
    
    def _load_assets(self):
        """Load brand assets from the assets directory."""
        if not os.path.exists(self.ASSETS_DIR):
            os.makedirs(self.ASSETS_DIR)
            logger.info(f"Created assets directory: {self.ASSETS_DIR}")
            return
        
        for filename in os.listdir(self.ASSETS_DIR):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                filepath = os.path.join(self.ASSETS_DIR, filename)
                
                # Parse filename: brand_category_name.ext
                parts = filename.rsplit('.', 1)[0].split('_')
                if len(parts) >= 2:
                    brand = parts[0]
                    category = parts[1] if len(parts) > 1 else 'logo'
                    name = '_'.join(parts[2:]) if len(parts) > 2 else parts[0]
                    
                    # Calculate hash
                    with open(filepath, 'rb') as f:
                        image_hash = hashlib.md5(f.read()).hexdigest()
                    
                    asset = BrandAsset(
                        name=name,
                        brand=brand,
                        category=category,
                        image_path=filepath,
                        image_hash=image_hash
                    )
                    self.assets.append(asset)
        
        logger.info(f"Loaded {len(self.assets)} brand assets")
    
    def _load_image(self, path_or_bytes) -> Optional['Image.Image']:
        """Load an image from path or bytes."""
        if not HAS_PIL:
            return None
        
        try:
            if isinstance(path_or_bytes, bytes):
                return Image.open(io.BytesIO(path_or_bytes))
            else:
                return Image.open(path_or_bytes)
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None
    
    def _image_to_array(self, img: 'Image.Image') -> 'np.ndarray':
        """Convert PIL Image to numpy array."""
        if not HAS_SKIMAGE:
            return None
        return np.array(img)
    
    def _calculate_ssim(self, img1: 'Image.Image', img2: 'Image.Image') -> float:
        """Calculate Structural Similarity Index between two images."""
        if not HAS_SKIMAGE:
            return self._calculate_basic_similarity(img1, img2)
        
        try:
            # Resize images to same dimensions
            size = (256, 256)
            img1_resized = img1.resize(size).convert('RGB')
            img2_resized = img2.resize(size).convert('RGB')
            
            arr1 = self._image_to_array(img1_resized)
            arr2 = self._image_to_array(img2_resized)
            
            # Calculate SSIM
            score = ssim(arr1, arr2, channel_axis=2)
            return float(score)
            
        except Exception as e:
            logger.error(f"Error calculating SSIM: {e}")
            return 0.0
    
    def _calculate_basic_similarity(self, img1: 'Image.Image', img2: 'Image.Image') -> float:
        """Basic similarity using color histogram comparison."""
        if not HAS_PIL:
            return 0.0
        
        try:
            # Resize to same size
            size = (64, 64)
            img1_small = img1.resize(size).convert('RGB')
            img2_small = img2.resize(size).convert('RGB')
            
            # Get histograms
            hist1 = img1_small.histogram()
            hist2 = img2_small.histogram()
            
            # Calculate correlation
            sum_sq_diff = sum((h1 - h2) ** 2 for h1, h2 in zip(hist1, hist2))
            max_diff = max(len(hist1) * (255 ** 2), 1)
            
            return 1.0 - (sum_sq_diff / max_diff)
            
        except Exception as e:
            logger.error(f"Error in basic similarity: {e}")
            return 0.0
    
    def _extract_dominant_colors(self, img: 'Image.Image', num_colors: int = 5) -> List[Tuple[int, int, int]]:
        """Extract dominant colors from an image."""
        if not HAS_PIL:
            return []
        
        try:
            # Resize for faster processing
            img_small = img.resize((50, 50)).convert('RGB')
            
            # Get colors
            colors = img_small.getcolors(2500)
            if not colors:
                return []
            
            # Sort by frequency
            colors.sort(key=lambda x: x[0], reverse=True)
            
            return [c[1] for c in colors[:num_colors]]
            
        except Exception as e:
            logger.error(f"Error extracting colors: {e}")
            return []
    
    def _color_distance(self, c1: Tuple[int, int, int], c2: Tuple[int, int, int]) -> float:
        """Calculate Euclidean distance between two colors."""
        return sum((a - b) ** 2 for a, b in zip(c1, c2)) ** 0.5
    
    def _match_brand_colors(self, dominant_colors: List[Tuple[int, int, int]]) -> Tuple[Optional[str], float]:
        """Match dominant colors against known brand color schemes."""
        best_match = None
        best_score = 0.0
        
        for brand, brand_colors in self.THAI_BRAND_COLORS.items():
            total_distance = 0
            matched = 0
            
            for brand_color in brand_colors:
                min_distance = float('inf')
                for dom_color in dominant_colors:
                    dist = self._color_distance(brand_color, dom_color)
                    min_distance = min(min_distance, dist)
                
                if min_distance < 100:  # Threshold for "similar" color
                    matched += 1
                    total_distance += min_distance
            
            if matched >= len(brand_colors) * 0.5:  # At least half of brand colors matched
                # Calculate similarity score (inverse of distance)
                avg_distance = total_distance / max(matched, 1)
                score = max(0, 1 - (avg_distance / 255))
                
                if score > best_score:
                    best_score = score
                    best_match = brand
        
        return best_match, best_score
    
    def compare_with_brand_assets(self, screenshot: bytes, brand: Optional[str] = None) -> float:
        """
        Compare a screenshot against brand assets.
        
        Args:
            screenshot: Screenshot bytes
            brand: Optional specific brand to compare against
            
        Returns:
            Highest similarity score found
        """
        img = self._load_image(screenshot)
        if not img:
            return 0.0
        
        assets_to_check = self.assets
        if brand:
            assets_to_check = [a for a in self.assets if a.brand == brand.lower()]
        
        max_similarity = 0.0
        for asset in assets_to_check:
            asset_img = self._load_image(asset.image_path)
            if asset_img:
                sim = self._calculate_ssim(img, asset_img)
                max_similarity = max(max_similarity, sim)
        
        return max_similarity
    
    def detect_brand(self, screenshot: bytes) -> DetectionResult:
        """
        Detect if a screenshot impersonates a known brand.
        
        Args:
            screenshot: Screenshot bytes
            
        Returns:
            DetectionResult with matched brand and confidence
        """
        img = self._load_image(screenshot)
        if not img:
            return DetectionResult(
                domain='',
                screenshot_path=None,
                matched_brand=None,
                similarity_score=0.0,
                confidence='none',
                matched_assets=[],
                detection_time=datetime.now().isoformat()
            )
        
        # Extract dominant colors and match against brands
        dominant_colors = self._extract_dominant_colors(img)
        color_matched_brand, color_score = self._match_brand_colors(dominant_colors)
        
        # Check against stored assets
        max_asset_similarity = 0.0
        matched_assets = []
        asset_matched_brand = None
        
        for asset in self.assets:
            asset_img = self._load_image(asset.image_path)
            if asset_img:
                sim = self._calculate_ssim(img, asset_img)
                if sim > 0.5:  # Threshold for potential match
                    matched_assets.append(f"{asset.brand}_{asset.name} ({sim:.2f})")
                    if sim > max_asset_similarity:
                        max_asset_similarity = sim
                        asset_matched_brand = asset.brand
        
        # Combine scores (weighted average)
        combined_score = (max_asset_similarity * 0.7) + (color_score * 0.3)
        
        # Determine matched brand
        matched_brand = asset_matched_brand or color_matched_brand
        
        # Determine confidence level
        if combined_score >= self.THRESHOLD_HIGH:
            confidence = 'high'
        elif combined_score >= self.THRESHOLD_MEDIUM:
            confidence = 'medium'
        elif combined_score >= self.THRESHOLD_LOW:
            confidence = 'low'
        else:
            confidence = 'none'
            matched_brand = None
        
        return DetectionResult(
            domain='',
            screenshot_path=None,
            matched_brand=matched_brand,
            similarity_score=round(combined_score, 3),
            confidence=confidence,
            matched_assets=matched_assets,
            detection_time=datetime.now().isoformat()
        )
    
    def get_supported_brands(self) -> List[str]:
        """Get list of brands we can detect."""
        brands = set(self.THAI_BRAND_COLORS.keys())
        for asset in self.assets:
            brands.add(asset.brand)
        return sorted(list(brands))


# Singleton instance
_cv_detector = None

def get_cv_detector() -> CVDetector:
    """Get the CV detector singleton."""
    global _cv_detector
    if _cv_detector is None:
        _cv_detector = CVDetector()
    return _cv_detector


# ============================================================================
# API ROUTES
# ============================================================================

def create_cv_routes(bp):
    """Create CV detection routes for a Flask blueprint."""
    from flask import request, jsonify
    from dataclasses import asdict
    
    @bp.route('/detect-brand', methods=['POST'])
    def detect_brand():
        """Detect brand impersonation from a screenshot."""
        data = request.json
        if not data or 'screenshot' not in data:
            return jsonify({'error': 'Screenshot (base64) is required'}), 400
        
        try:
            screenshot = base64.b64decode(data['screenshot'])
        except Exception:
            return jsonify({'error': 'Invalid base64 screenshot'}), 400
        
        detector = get_cv_detector()
        result = detector.detect_brand(screenshot)
        
        return jsonify(asdict(result))
    
    @bp.route('/compare', methods=['POST'])
    def compare_with_brand():
        """Compare a screenshot with a specific brand's assets."""
        data = request.json
        if not data or 'screenshot' not in data:
            return jsonify({'error': 'Screenshot (base64) is required'}), 400
        
        try:
            screenshot = base64.b64decode(data['screenshot'])
        except Exception:
            return jsonify({'error': 'Invalid base64 screenshot'}), 400
        
        brand = data.get('brand')
        
        detector = get_cv_detector()
        score = detector.compare_with_brand_assets(screenshot, brand)
        
        return jsonify({
            'brand': brand,
            'similarity_score': round(score, 3)
        })
    
    @bp.route('/supported-brands', methods=['GET'])
    def get_supported_brands():
        """Get list of supported brands for detection."""
        detector = get_cv_detector()
        return jsonify({'brands': detector.get_supported_brands()})
