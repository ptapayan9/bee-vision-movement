from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python.vision import RunningMode
from numpy.typing import NDArray


def clean_mask(mask: NDArray[np.uint8]) -> NDArray[np.uint8]:
    """Removes small isolated foreground noise from a binary mask"""
    kernel = np.ones((3, 3), dtype=np.uint8)
    cleaned_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return np.asarray(cleaned_mask, dtype=np.uint8)


def convert_bgr_to_rgb(frame: NDArray[np.uint8]) -> NDArray[np.uint8]:
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return np.asarray(rgb_frame, dtype=np.uint8)


def confidence_to_binary_mask(
    confidence_mask: NDArray[np.float32], threshold: float = 0.5
) -> NDArray[np.uint8]:
    person_pixel = confidence_mask[..., 0] >= threshold
    binary_mask = person_pixel.astype(np.uint8) * 255
    return binary_mask


# Deprecated
class ForegroundSegmenter:
    def __init__(self) -> None:
        self._subtractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=False,
        )

    def apply(self, frame: NDArray[np.uint8]) -> NDArray[np.uint8]:
        """Update the background model and return a binary ForegroundSegmenter mask."""
        raw_mask = self._subtractor.apply(frame)
        binary_mask = np.asarray(raw_mask, dtype=np.uint8)
        return clean_mask(binary_mask)


class PersonSegmenter:
    def __init__(self, model_path: Path) -> None:

        base_options = mp.tasks.BaseOptions(model_asset_path=str(model_path))
        options = mp.tasks.vision.ImageSegmenterOptions(
            base_options=base_options,  # contains the models configurations
            running_mode=RunningMode.IMAGE,  # proccesses one frame synchronously
            output_confidence_masks=True,  # requests a floating point person confidence value for every pixel
            output_category_mask=False,  # avoids outputs we dont need
        )
        self._segmenter = mp.tasks.vision.ImageSegmenter.create_from_options(options)

    def apply(self, frame: NDArray[np.uint8]) -> NDArray[np.uint8]:

        rgb_frame = convert_bgr_to_rgb(frame)
        mediapipe_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        result = self._segmenter.segment(mediapipe_image)
        confidence_masks = result.confidence_masks

        if not confidence_masks:
            raise RuntimeError("person segmentation returned no confidence mask")

        confidence_mask = np.asarray(
            confidence_masks[0].numpy_view(),
            dtype=np.float32,
        )

        binary_mask = confidence_to_binary_mask(confidence_mask)
        return clean_mask(binary_mask)

    def close(self) -> None:
        """Releases MediaPipe segmentation resource"""
        self._segmenter.close()
