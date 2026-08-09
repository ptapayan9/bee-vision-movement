"""Live camera capture helpers."""

from collections.abc import Callable

import cv2  # pylint: disable=import-error
import numpy as np
from numpy.typing import NDArray

FrameProcessor = Callable[[NDArray[np.uint8]], NDArray[np.uint8]]


def show_camera(
    camera_index: int = 0,
    frame_processor: FrameProcessor | None = None,
) -> None:
    """Open the selected camera and validate the connection."""
    camera_connection = cv2.VideoCapture(camera_index)

    try:
        if not camera_connection.isOpened():
            raise RuntimeError(f"unable to open camera: {camera_index}")

        while True:
            ready, frame = camera_connection.read()
            if not ready:
                raise RuntimeError(
                    f"unable to capture frame from camera: {camera_index}"
                )

            display_frame = frame
            if frame_processor is not None:
                camera_frame = np.asarray(frame, dtype=np.uint8)
                display_frame = frame_processor(camera_frame)

            cv2.imshow("bvm", display_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera_connection.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    show_camera()
