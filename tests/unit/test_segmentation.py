from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from bvm.vision.segmentation import (
    ForegroundSegmenter,
    PersonSegmenter,
    clean_mask,
    confidence_to_binary_mask,
    convert_bgr_to_rgb,
)


def test_person_segmenter_returns_binary_mask() -> None:
    """Verify that person confidence is converted into a cleaned binary mask."""
    confidence_mask = np.zeros((9, 9, 1), dtype=np.float32)
    confidence_mask[3:6, 3:6, 0] = 0.9

    confidence_image = MagicMock()
    confidence_image.numpy_view.return_value = confidence_mask

    result = MagicMock()
    result.confidence_masks = [confidence_image]

    with patch(
        "bvm.vision.segmentation.mp.tasks.vision.ImageSegmenter.create_from_options"
    ) as create_segmenter:
        mediapipe_segmenter = create_segmenter.return_value
        mediapipe_segmenter.segment.return_value = result

        segmenter = PersonSegmenter(Path("fake-model.tflite"))
        frame = np.zeros((9, 9, 3), dtype=np.uint8)

        mask = segmenter.apply(frame)

    expected = np.zeros((9, 9), dtype=np.uint8)
    expected[3:6, 3:6] = 255

    assert np.array_equal(mask, expected)
    assert mask.shape == frame.shape[:2]
    assert mask.dtype == np.uint8


def test_person_segmenter_raises_when_confidence_mask_is_missing() -> None:
    """Verify that a missing confidence mask produces a clear error."""
    result = MagicMock()
    result.confidence_masks = None

    with patch(
        "bvm.vision.segmentation.mp.tasks.vision.ImageSegmenter.create_from_options"
    ) as create_segmenter:
        mediapipe_segmenter = create_segmenter.return_value
        mediapipe_segmenter.segment.return_value = result

        segmenter = PersonSegmenter(Path("fake-model.tflite"))
        frame = np.zeros((9, 9, 3), dtype=np.uint8)

        with pytest.raises(
            RuntimeError,
            match="person segmentation returned no confidence mask",
        ):
            segmenter.apply(frame)


def test_convert_bgr_to_rgb() -> None:
    """Verify that the conversion of bgr to rgb works"""
    bgr_frame = np.array([[[10, 20, 30]]], dtype=np.uint8)
    rgb_frame = convert_bgr_to_rgb(bgr_frame)
    expected = np.array([[[30, 20, 10]]], dtype=np.uint8)

    assert np.array_equal(rgb_frame, expected)


def test_confidence_to_binary_mask() -> None:
    """Verify that the confidence of the binary masks"""
    confidence_mask = np.array(
        [
            [[0.10], [0.49], [0.50]],
            [[0.90], [1.00], [0.20]],
        ],
        dtype=np.float32,
    )
    mask = confidence_to_binary_mask(confidence_mask)
    expected = np.array([[0, 0, 255], [255, 255, 0]], dtype=np.uint8)

    assert np.array_equal(mask, expected)
    assert mask.shape == (2, 3)
    assert mask.dtype == np.uint8


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
