"""Live camera capture helpers."""

import cv2  # pylint: disable=import-error


def show_camera(camera_index: int = 0) -> None:
    """Open the selected camera and validate the connection."""
    camera_connection = cv2.VideoCapture(camera_index)

    try:
        if not camera_connection.isOpened():
            raise RuntimeError(f"unable to open camera selection :{camera_index}")

        while True:
            ready, frame = camera_connection.read()
            if not ready:
                raise RuntimeError(
                    f"unable to capture frame from camera: {camera_index}"
                )

            cv2.imshow("bvm", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera_connection.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    show_camera()
