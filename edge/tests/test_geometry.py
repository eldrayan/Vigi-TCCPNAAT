import unittest

from edge.collection.geometry import guide_bounds


class GeometryTests(unittest.TestCase):
    def test_guide_is_centered(self):
        self.assertEqual(guide_bounds(1000, 500, 0.5, 0.8), (250, 50, 750, 450))

    def test_guide_stays_inside_frame(self):
        self.assertEqual(guide_bounds(10, 10, 1.0, 1.0), (0, 0, 10, 10))


if __name__ == "__main__":
    unittest.main()
