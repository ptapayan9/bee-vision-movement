import numpy as np

from bvm.vision.segmentation import ForegroundSegmenter, clean_mask


def test_foreground_segmenter_returns_binary_mask() -> None:
    """Verify that segmentation returns a binary mask matching the frame"""

    frame = np.zeros((4, 6, 3), dtype=np.uint8)
    segmenter = ForegroundSegmenter()

    mask = segmenter.apply(frame)

    assert isinstance(mask, np.ndarray)
    assert mask.shape == frame.shape[:2]
    assert mask.dtype == np.uint8
    assert set(np.unique(mask)).issubset({0, 255})


def test_foreground_segmenter_detects_new_object() -> None:
    """Verify that a new object is separated from a learned background"""
    background = np.zeros((40, 60, 3), dtype=np.uint8)

    frame_with_object = background.copy()
    frame_with_object[10:30, 20:40] = 255

    segmenter = ForegroundSegmenter()

    for _ in range(10):
        segmenter.apply(background)

    mask = segmenter.apply(frame_with_object)

    # checks if the mask sees any change/white pixels - marking the foreground
    assert np.all(mask[10:30, 20:40] == 255)
    # checks if the unchanged background is still black
    assert np.all(mask[:10, :20] == 0)


def test_clean_mask_removes_isolated_noise() -> None:
    mask = np.zeros((9, 9), dtype=np.uint8)
    mask[1, 1] = 255
    mask[4:7, 4:7] = 255

    cleaned_mask = clean_mask(mask)

    assert cleaned_mask[1, 1] == 0
    assert np.all(cleaned_mask[4:7, 4:7] == 255)
