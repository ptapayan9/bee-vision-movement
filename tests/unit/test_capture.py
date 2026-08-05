"""Tests for live camera capture."""

from unittest.mock import Mock, call, patch

import pytest  # pylint: disable=import-error

from bvm.capture.camera import show_camera


def test_show_camera_rejects_unavailable_camera() -> None:
    """Verify that an unavailable camera raises an error."""
    camera_connection = Mock()
    camera_connection.isOpened.return_value = False

    with (
        patch(
            "bvm.capture.camera.cv2.VideoCapture",
            return_value=camera_connection,
        ) as video_capture,
        patch("bvm.capture.camera.cv2.destroyAllWindows") as destroy_all_windows,
        pytest.raises(RuntimeError, match="7"),
    ):
        show_camera(7)

    video_capture.assert_called_once_with(7)
    camera_connection.release.assert_called_once_with()
    destroy_all_windows.assert_called_once_with()
    camera_connection.read.assert_not_called()


def test_show_camera_displays_frames_until_q() -> None:
    """Verify that the camera displays frames"""
    camera_connection = Mock()
    camera_connection.isOpened.return_value = True

    first_frame = object()
    second_frame = object()

    camera_connection.read.side_effect = [(True, first_frame), (True, second_frame)]

    with (
        patch(
            "bvm.capture.camera.cv2.VideoCapture", return_value=camera_connection
        ) as video_capture,
        patch("bvm.capture.camera.cv2.imshow") as imshow,
        patch("bvm.capture.camera.cv2.waitKey", side_effect=[-1, ord("q")]) as wait_key,
        patch("bvm.capture.camera.cv2.destroyAllWindows") as destroy_all_windows,
    ):
        show_camera(3)

    video_capture.assert_called_once_with(3)
    camera_connection.isOpened.assert_called_once_with()
    assert camera_connection.read.call_count == 2

    assert imshow.call_args_list == [
        call("bvm", first_frame),
        call("bvm", second_frame),
    ]

    assert wait_key.call_args_list == [
        call(1),
        call(1),
    ]

    camera_connection.release.assert_called_once_with()
    destroy_all_windows.assert_called_once_with()


def test_show_camera_rejects_failed_frame_read() -> None:
    """Verify that a failed frame read raises an error and cleans up"""
    camera_connection = (
        Mock()
    )  # we need a fake object because this test shouldnt require a physical hardware
    camera_connection.isOpened.return_value = True  # this forces production past the first failure to continue as if it was True
    camera_connection.read.return_value = (
        False,
        None,
    )  # False -> openCV did not capture a valid frame and None -> there is no usable Frame

    with (
        patch(
            "bvm.capture.camera.cv2.VideoCapture", return_value=camera_connection
        ) as video_capture,
        patch("bvm.capture.camera.cv2.imshow") as imshow,
        patch("bvm.capture.camera.cv2.waitKey") as wait_key,
        patch("bvm.capture.camera.cv2.destroyAllWindows") as destroy_all_windows,
        pytest.raises(
            RuntimeError, match="camera: 4"
        ),  # this states the failure is expected behavior
    ):
        show_camera(4)

    video_capture.assert_called_once_with(4)
    camera_connection.isOpened.assert_called_once_with()
    camera_connection.read.assert_called_once_with()
    imshow.assert_not_called()
    wait_key.assert_not_called()
    camera_connection.release.assert_called_once_with()
    destroy_all_windows.assert_called_once_with()
