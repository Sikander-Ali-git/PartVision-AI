"""
src/inference/utils.py
Utilities and constants for PartVision V3 inference, device resolution,
image loading, and coordinate transformation.
"""

from pathlib import Path
from typing import List, Tuple, Union, Optional
import cv2
import numpy as np
import torch

# 19 Frozen Taxonomy Classes for PartVision V3
FROZEN_V3_CLASSES = [
    "back_bumper",    # 0
    "back_door",      # 1
    "back_glass",     # 2
    "back_light",     # 3
    "fender",         # 4
    "front_bumper",   # 5
    "front_door",     # 6
    "front_glass",    # 7
    "front_light",    # 8
    "grille",         # 9
    "hood",           # 10
    "mirror",         # 11
    "quarter_panel",  # 12
    "rocker_panel",   # 13
    "roof",           # 14
    "side_window",    # 15
    "tailgate",       # 16
    "trunk",          # 17
    "wheel",          # 18
]

CLASS_NAME_TO_ID = {name: idx for idx, name in enumerate(FROZEN_V3_CLASSES)}
CLASS_ID_TO_NAME = {idx: name for idx, name in enumerate(FROZEN_V3_CLASSES)}

# Distinct RGB color palette for 19 classes
CLASS_COLORS_RGB: List[Tuple[int, int, int]] = [
    (230, 25, 75),    # 0: back_bumper (Red)
    (60, 180, 75),    # 1: back_door (Green)
    (255, 225, 25),   # 2: back_glass (Yellow)
    (0, 130, 200),    # 3: back_light (Blue)
    (245, 130, 48),   # 4: fender (Orange)
    (145, 30, 180),   # 5: front_bumper (Purple)
    (70, 240, 240),   # 6: front_door (Cyan)
    (240, 50, 230),   # 7: front_glass (Magenta)
    (210, 245, 60),   # 8: front_light (Lime)
    (250, 190, 212),  # 9: grille (Pink)
    (0, 128, 128),    # 10: hood (Teal)
    (220, 190, 255),  # 11: mirror (Lavender)
    (170, 110, 40),   # 12: quarter_panel (Brown)
    (255, 250, 200),  # 13: rocker_panel (Beige)
    (128, 0, 0),      # 14: roof (Maroon)
    (170, 255, 195),  # 15: side_window (Mint)
    (128, 128, 0),    # 16: tailgate (Olive)
    (255, 215, 180),  # 17: trunk (Apricot)
    (0, 0, 128),      # 18: wheel (Navy)
]

# OpenCV BGR color palette
CLASS_COLORS_BGR: List[Tuple[int, int, int]] = [
    (c[2], c[1], c[0]) for c in CLASS_COLORS_RGB
]


def select_optimal_device(requested: str = "auto") -> str:
    """
    Selects the optimal compute device.
    
    Priority when 'auto':
    1. 'mps' (Apple Silicon GPU)
    2. 'cuda' (NVIDIA GPU)
    3. 'cpu' (Universal fallback)

    Args:
        requested: 'auto', 'mps', 'cuda', or 'cpu'.

    Returns:
        String representing the active PyTorch device ('mps', 'cuda', or 'cpu').
    """
    requested_lower = requested.strip().lower()
    if requested_lower not in ("auto", "mps", "cuda", "cpu"):
        raise ValueError(
            f"Invalid device '{requested}'. Must be one of 'auto', 'mps', 'cuda', 'cpu'."
        )

    if requested_lower == "auto":
        if torch.backends.mps.is_available():
            return "mps"
        elif torch.cuda.is_available():
            return "cuda"
        else:
            return "cpu"

    if requested_lower == "mps":
        if not torch.backends.mps.is_available():
            return "cpu"
        return "mps"

    if requested_lower == "cuda":
        if not torch.cuda.is_available():
            return "cpu"
        return "cuda"

    return "cpu"


def load_image(
    image_input: Union[str, Path, np.ndarray]
) -> Tuple[np.ndarray, int, int, Optional[str]]:
    """
    Loads, validates, and extracts dimensions from an image input.

    Args:
        image_input: File path (str or Path) or pre-loaded BGR numpy array.

    Returns:
        Tuple of (bgr_image, width, height, filename_or_none).

    Raises:
        FileNotFoundError: If image_input is a path and the file does not exist.
        ValueError: If image_input is invalid or unreadable.
    """
    if isinstance(image_input, (str, Path)):
        img_path = Path(image_input).expanduser().resolve()
        if not img_path.exists():
            raise FileNotFoundError(f"Input image not found: {img_path}")
        if not img_path.is_file():
            raise ValueError(f"Specified path is not a file: {img_path}")

        img = cv2.imread(str(img_path))
        if img is None:
            raise ValueError(f"Unable to decode image file (corrupted or unsupported format): {img_path}")

        h, w = img.shape[:2]
        return img, w, h, img_path.name

    elif isinstance(image_input, np.ndarray):
        if image_input.size == 0 or len(image_input.shape) < 2:
            raise ValueError("Provided image numpy array is empty or has invalid shape.")
        h, w = image_input.shape[:2]
        return image_input, w, h, None

    else:
        raise TypeError(
            f"Unsupported image input type: {type(image_input)}. Expected str, Path, or np.ndarray."
        )


def sanitize_polygon_points(
    points: np.ndarray,
    img_width: int,
    img_height: int
) -> List[List[float]]:
    """
    Clamps polygon vertices to [0, width] and [0, height] and rounds to 2 decimal places.

    Args:
        points: (N, 2) array of [x, y] coordinates.
        img_width: Image width in pixels.
        img_height: Image height in pixels.

    Returns:
        List of [x, y] coordinates.
    """
    sanitized: List[List[float]] = []
    for pt in points:
        x = max(0.0, min(float(img_width), float(pt[0])))
        y = max(0.0, min(float(img_height), float(pt[1])))
        sanitized.append([round(x, 2), round(y, 2)])
    return sanitized
