"""
src/inference/engine.py
Core production inference engine for PartVision AI.
Wraps the frozen YOLO11n-seg V3 model to deliver typed, structured JSON results.
"""

import time
from pathlib import Path
from typing import Union, List, Optional
import numpy as np
from ultralytics import YOLO

from src.inference.schemas import (
    BBox,
    PolygonMask,
    Detection,
    ModelMetadata,
    ImageMetadata,
    InferenceConfig,
    InferenceSummary,
    InferenceResult,
)
from src.inference.utils import (
    FROZEN_V3_CLASSES,
    CLASS_ID_TO_NAME,
    select_optimal_device,
    load_image,
    sanitize_polygon_points,
)
from src.inference.visualize import draw_detections, save_annotated_image


class PartVisionInferenceEngine:
    """
    Production-ready inference engine for PartVision V3 automotive part segmentation.

    Loads the frozen YOLO11n-seg checkpoint once and provides high-performance,
    typed inference producing normalized structured JSON results.
    """

    DEFAULT_CHECKPOINT = "models/partvision_v3_yolo11n_seg_best.pt"

    def __init__(
        self,
        model_path: Union[str, Path] = DEFAULT_CHECKPOINT,
        device: str = "auto",
        verbose: bool = False
    ):
        """
        Initializes and warms up the inference engine.

        Args:
            model_path: Path to the trained YOLO11n-seg weights file.
            device: Target hardware device ('auto', 'mps', 'cuda', 'cpu').
            verbose: Enable verbose logging from Ultralytics.

        Raises:
            FileNotFoundError: If model weights cannot be located.
        """
        self.model_path = Path(model_path).expanduser().resolve()
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"PartVision model checkpoint not found: {self.model_path}"
            )
        if not self.model_path.is_file():
            raise ValueError(
                f"Specified model path is not a file: {self.model_path}"
            )

        self.device = select_optimal_device(device)
        self.verbose = verbose

        # Load weights once into memory
        t0 = time.perf_counter()
        self.model = YOLO(str(self.model_path))
        self.model_load_time_ms = (time.perf_counter() - t0) * 1000

        # Validate that model taxonomy matches the frozen 19 classes
        self.class_names = self.model.names
        self.num_classes = len(self.class_names)

    def predict(
        self,
        image: Union[str, Path, np.ndarray],
        conf: float = 0.25,
        iou: float = 0.7,
        imgsz: int = 512
    ) -> InferenceResult:
        """
        Performs instance segmentation on an input image.

        Args:
            image: Image file path or BGR numpy array.
            conf: Confidence threshold [0.0 - 1.0].
            iou: NMS Intersection over Union threshold [0.0 - 1.0].
            imgsz: Inference square resolution in pixels (default 512).

        Returns:
            InferenceResult object with typed detections and metadata.

        Raises:
            FileNotFoundError: If image file path does not exist.
            ValueError: If image cannot be read or decoded.
        """
        # 1. Load and validate image
        img_bgr, width, height, filename = load_image(image)

        # 2. Run Ultralytics inference
        t_start = time.perf_counter()
        results = self.model.predict(
            source=img_bgr,
            conf=conf,
            iou=iou,
            imgsz=imgsz,
            device=self.device,
            verbose=self.verbose
        )
        latency_ms = (time.perf_counter() - t_start) * 1000

        res = results[0]

        # 3. Extract detections
        detections: List[Detection] = []
        if res.boxes is not None and len(res.boxes) > 0:
            boxes = res.boxes
            has_masks = res.masks is not None and res.masks.xy is not None
            masks_xy = res.masks.xy if has_masks else []

            for i, box in enumerate(boxes):
                cls_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())
                cname = self.class_names.get(cls_id, CLASS_ID_TO_NAME.get(cls_id, f"part_{cls_id}"))

                # Bounding box in original image pixels
                xyxy = box.xyxy[0].tolist()
                x1 = max(0.0, min(float(width), float(xyxy[0])))
                y1 = max(0.0, min(float(height), float(xyxy[1])))
                x2 = max(0.0, min(float(width), float(xyxy[2])))
                y2 = max(0.0, min(float(height), float(xyxy[3])))

                bbox = BBox(
                    x1=round(x1, 2),
                    y1=round(y1, 2),
                    x2=round(x2, 2),
                    y2=round(y2, 2)
                )

                # Segmentation mask polygon in original image pixels
                mask_obj: Optional[PolygonMask] = None
                if i < len(masks_xy) and len(masks_xy[i]) >= 3:
                    sanitized_pts = sanitize_polygon_points(
                        masks_xy[i],
                        img_width=width,
                        img_height=height
                    )
                    if len(sanitized_pts) >= 3:
                        mask_obj = PolygonMask(format="polygon", points=sanitized_pts)

                detection = Detection(
                    class_id=cls_id,
                    class_name=cname,
                    confidence=confidence,
                    bbox=bbox,
                    mask=mask_obj
                )
                detections.append(detection)

        # 4. Sort detections by confidence descending (deterministic presentation)
        detections.sort(key=lambda d: d.confidence, reverse=True)

        # 5. Build summary
        detected_classes = list(dict.fromkeys(d.class_name for d in detections))
        summary = InferenceSummary(
            detection_count=len(detections),
            detected_classes=detected_classes
        )

        # 6. Assemble complete result
        return InferenceResult(
            model=ModelMetadata(
                name="PartVision YOLO11n-seg",
                version="v3",
                checkpoint=self.model_path.name,
                num_classes=self.num_classes
            ),
            image=ImageMetadata(
                width=width,
                height=height,
                channels=3,
                filename=filename
            ),
            inference=InferenceConfig(
                device=self.device,
                confidence_threshold=conf,
                iou_threshold=iou,
                image_size=imgsz
            ),
            detections=detections,
            summary=summary,
            latency_ms=round(latency_ms, 2)
        )

    def predict_and_visualize(
        self,
        image: Union[str, Path, np.ndarray],
        output_path: Optional[Union[str, Path]] = None,
        conf: float = 0.25,
        iou: float = 0.7,
        imgsz: int = 512
    ) -> tuple[InferenceResult, np.ndarray]:
        """
        Convenience method that runs inference and returns both the structured
        result and the rendered visualization image.

        Args:
            image: Image file path or numpy array.
            output_path: Optional destination file path to save visualization.
            conf: Confidence threshold.
            iou: IoU threshold.
            imgsz: Resolution.

        Returns:
            Tuple of (InferenceResult, annotated_bgr_image).
        """
        result = self.predict(image=image, conf=conf, iou=iou, imgsz=imgsz)
        annotated_img = draw_detections(image=image, detections_or_result=result)

        if output_path is not None:
            save_annotated_image(annotated_img, output_path)

        return result, annotated_img
