"""
src/inference/visualize.py
Visualization utility for rendering PartVision V3 segmentation predictions
and bounding boxes with clear class badges and confidences.
"""

from pathlib import Path
from typing import Union, List, Optional
import cv2
import numpy as np

from src.inference.schemas import Detection, InferenceResult
from src.inference.utils import CLASS_COLORS_BGR, load_image


def draw_detections(
    image: Union[str, Path, np.ndarray],
    detections_or_result: Union[List[Detection], InferenceResult],
    alpha: float = 0.45,
    line_thickness: int = 2,
    font_scale: float = 0.45
) -> np.ndarray:
    """
    Renders segmentation polygon masks, bounding boxes, and label tags onto an image.
    Never modifies the original input in-place.

    Args:
        image: File path or existing BGR image numpy array.
        detections_or_result: List of Detection objects or a full InferenceResult.
        alpha: Opacity of the segmentation polygon mask fill [0.0 - 1.0].
        line_thickness: Border line width in pixels.
        font_scale: Font size for label text.

    Returns:
        New BGR numpy array with rendered visualizations.
    """
    # 1. Load image safely without modifying original
    img_bgr, width, height, _ = load_image(image)
    canvas = img_bgr.copy()
    overlay = canvas.copy()

    # Extract detections list
    if isinstance(detections_or_result, InferenceResult):
        detections = detections_or_result.detections
    else:
        detections = detections_or_result

    # 2. Draw segmentation polygon fills onto overlay layer
    for det in detections:
        color_bgr = CLASS_COLORS_BGR[det.class_id % len(CLASS_COLORS_BGR)]
        if det.mask and len(det.mask.points) >= 3:
            pts = np.array(det.mask.points, dtype=np.int32).reshape((-1, 1, 2))
            cv2.fillPoly(overlay, [pts], color_bgr)

    # 3. Blend overlay with canvas to achieve semi-transparency
    cv2.addWeighted(overlay, alpha, canvas, 1.0 - alpha, 0, canvas)

    # 4. Draw polygon contours, bounding boxes, and label banners on top
    for det in detections:
        color_bgr = CLASS_COLORS_BGR[det.class_id % len(CLASS_COLORS_BGR)]

        # Polygon contour line
        if det.mask and len(det.mask.points) >= 3:
            pts = np.array(det.mask.points, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(canvas, [pts], isClosed=True, color=color_bgr, thickness=line_thickness)

        # Bounding box
        x1 = int(round(det.bbox.x1))
        y1 = int(round(det.bbox.y1))
        x2 = int(round(det.bbox.x2))
        y2 = int(round(det.bbox.y2))
        cv2.rectangle(canvas, (x1, y1), (x2, y2), color_bgr, max(1, line_thickness - 1))

        # Text banner: e.g. "front_bumper 94.2%"
        conf_pct = f"{det.confidence * 100:.1f}%"
        label = f"{det.class_name} {conf_pct}"
        (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)

        # Ensure label banner does not clip above the image
        text_y = max(y1, th + 4)
        cv2.rectangle(
            canvas,
            (x1, text_y - th - 4),
            (x1 + tw + 6, text_y + 2),
            color_bgr,
            -1
        )
        # White text with crisp drop contrast
        cv2.putText(
            canvas,
            label,
            (x1 + 3, text_y - 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

    return canvas


def save_annotated_image(
    annotated_img: np.ndarray,
    output_path: Union[str, Path]
) -> Path:
    """
    Saves an annotated image array to disk, creating parent directories if needed.

    Args:
        annotated_img: BGR image numpy array.
        output_path: Destination path on disk.

    Returns:
        Resolved Path to the saved file.
    """
    out_p = Path(output_path).expanduser().resolve()
    out_p.parent.mkdir(parents=True, exist_ok=True)
    success = cv2.imwrite(str(out_p), annotated_img)
    if not success:
        raise IOError(f"Failed to write image to disk: {out_p}")
    return out_p
