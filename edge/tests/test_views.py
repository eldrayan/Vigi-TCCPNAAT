import unittest

from edge.collection.views.factory import graphical_display_available


class ViewSelectionTests(unittest.TestCase):
    def test_display_detection_accepts_x11_or_wayland(self):
        self.assertTrue(graphical_display_available({"DISPLAY": ":0"}))
        self.assertTrue(graphical_display_available({"WAYLAND_DISPLAY": "wayland-0"}))
        self.assertFalse(graphical_display_available({}))


if __name__ == "__main__":
    unittest.main()
