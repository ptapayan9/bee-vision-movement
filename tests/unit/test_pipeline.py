from pathlib import Path
from unittest.mock import patch

from bvm.pipelines import analyze_video
from bvm.pipelines.analyze_video import show_foreground_camera


def test_show_foreground_camera_connects_segmentation_to_capture() -> None:
    """Verify that camera frames are processed by the person segmenter."""
    with (
        patch(
            "bvm.pipelines.analyze_video.PersonSegmenter",
        ) as segmenter_class,
        patch(
            "bvm.pipelines.analyze_video.show_camera",
        ) as show_camera_mock,
    ):
        show_foreground_camera(2)

    segmenter = segmenter_class.return_value
    expected_model_path = (
        Path(analyze_video.__file__).resolve().parents[1]
        / "models"
        / "selfie_segmenter_landscape.tflite"
    )

    segmenter_class.assert_called_once_with(expected_model_path)
    show_camera_mock.assert_called_once_with(2, frame_processor=segmenter.apply)
    segmenter.close.assert_called_once_with()
