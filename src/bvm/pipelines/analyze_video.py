from bvm.capture import camera
from bvm.capture.camera import show_camera
from bvm.vision.segmentation import ForegroundSegmenter


def show_foreground_camera(camera_index: int = 0) -> None:
    """Display a live foreground mask from the selected camera"""
    segmenter = ForegroundSegmenter()

    show_camera(
        camera_index,
        frame_processor=segmenter.apply,
    )


if __name__ == "__main__":
    show_foreground_camera()
