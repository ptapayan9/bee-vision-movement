import cv2
import numpy as np
from numpy.typing import NDArray


def clean_mask(mask: NDArray[np.uint8]) -> NDArray[np.uint8]:
    """Removes small isolated foreground noise from a binary mask"""
    kernel = np.ones((3, 3), dtype=np.uint8)
    cleaned_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return np.asarray(cleaned_mask, dtype=np.uint8)


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
