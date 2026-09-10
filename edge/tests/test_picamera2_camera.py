import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from edge.acquisition.backends.picamera2_camera import Picamera2Camera


class Picamera2CameraTests(unittest.TestCase):
    @patch("edge.acquisition.backends.picamera2_camera.importlib.import_module")
    def test_configures_main_stream_as_rgb888(self, import_module: MagicMock):
        camera = MagicMock()
        camera.camera_controls = {}
        picamera2_module = SimpleNamespace(Picamera2=MagicMock(return_value=camera))
        import_module.return_value = picamera2_module

        Picamera2Camera(
            device=0,
            width=1280,
            height=720,
            fps=30,
            warmup_seconds=0,
        )

        camera.create_video_configuration.assert_called_once_with(
            main={"size": (1280, 720), "format": "RGB888"},
            controls={"FrameRate": 30.0},
            buffer_count=4,
        )


if __name__ == "__main__":
    unittest.main()
