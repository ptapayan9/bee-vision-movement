from pathlib import Path

from bvm.capture.camera import show_camera
from bvm.vision.segmentation import PersonSegmenter


def show_foreground_camera(camera_index: int = 0) -> None:
    """Display a live foreground mask from the selected camera"""
    MODEL_PATH = (
        Path(__file__).resolve().parents[1]
        / "models"
        / "selfie_segmenter_landscape.tflite"
    )
    segmenter = PersonSegmenter(MODEL_PATH)
    try:
        show_camera(
            camera_index,
            frame_processor=segmenter.apply,
        )
    finally:
        segmenter.close()


if __name__ == "__main__":
    show_foreground_camera()
