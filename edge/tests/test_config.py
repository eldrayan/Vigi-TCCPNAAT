import contextlib
import io
import unittest

from edge.config import parse_collection_config


class CollectionConfigTests(unittest.TestCase):
    def test_defaults_target_picamera2(self):
        config = parse_collection_config([])
        self.assertEqual(config.backend, "picamera2")
        self.assertEqual((config.width, config.height), (1280, 720))

    def test_headless_flag_is_preserved(self):
        config = parse_collection_config(["--headless", "--camera", "1"])
        self.assertTrue(config.headless)
        self.assertEqual(config.camera, 1)

    def test_removed_rpicam_backend_is_rejected(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parse_collection_config(["--backend", "rpicam"])


if __name__ == "__main__":
    unittest.main()
