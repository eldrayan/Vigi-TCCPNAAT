import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "coletar_dataset.py"
SPEC = importlib.util.spec_from_file_location("coletar_dataset", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CaptureStateTests(unittest.TestCase):
    def test_numeric_keys_select_the_four_classes(self):
        self.assertEqual(MODULE.class_from_key(ord("1")), 1)
        self.assertEqual(MODULE.class_from_key(ord("4")), 4)
        self.assertIsNone(MODULE.class_from_key(ord("5")))

    def test_changing_class_stops_burst(self):
        state = MODULE.CaptureState("teste", burst_enabled=True)
        state.select_class(3)
        self.assertEqual(state.class_name, "03_tampa_torta")
        self.assertFalse(state.burst_enabled)

    def test_next_bottle_creates_a_new_group(self):
        state = MODULE.CaptureState("coleta bancada")
        first_group = state.group_id
        state.next_physical_sample()
        self.assertNotEqual(state.group_id, first_group)
        self.assertTrue(state.group_id.endswith("frasco_002"))

    def test_sample_counters_are_independent_per_class(self):
        state = MODULE.CaptureState("teste")
        state.next_physical_sample()
        state.select_class(2)
        self.assertEqual(state.physical_sample, 1)
        state.select_class(1)
        self.assertEqual(state.physical_sample, 2)


class GeometryTests(unittest.TestCase):
    def test_guide_is_centered(self):
        self.assertEqual(MODULE.guide_bounds(1000, 500, 0.5, 0.8), (250, 50, 750, 450))

    def test_safe_component_removes_path_characters(self):
        self.assertEqual(MODULE.safe_component("sessão/a 1"), "sessão_a_1")


if __name__ == "__main__":
    unittest.main()
