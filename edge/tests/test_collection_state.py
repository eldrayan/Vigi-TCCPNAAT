import unittest

from edge.collection.state import CaptureState, class_from_key, safe_component


class CaptureStateTests(unittest.TestCase):
    def test_numeric_keys_select_the_four_classes(self):
        self.assertEqual(class_from_key(ord("1")), 1)
        self.assertEqual(class_from_key(ord("4")), 4)
        self.assertIsNone(class_from_key(ord("5")))

    def test_changing_class_stops_burst(self):
        state = CaptureState("teste", burst_enabled=True)
        state.select_class(3)
        self.assertEqual(state.class_name, "03_tampa_torta")
        self.assertFalse(state.burst_enabled)

    def test_next_bottle_creates_a_new_group(self):
        state = CaptureState("coleta bancada")
        first_group = state.group_id
        state.next_physical_sample()
        self.assertNotEqual(state.group_id, first_group)
        self.assertTrue(state.group_id.endswith("frasco_002"))

    def test_sample_counters_are_independent_per_class(self):
        state = CaptureState("teste")
        state.next_physical_sample()
        state.select_class(2)
        self.assertEqual(state.physical_sample, 1)
        state.select_class(1)
        self.assertEqual(state.physical_sample, 2)

    def test_session_is_safe_for_file_names(self):
        state = CaptureState("sessão/a 1")
        self.assertEqual(state.session_id, "sessão_a_1")
        self.assertEqual(safe_component("///"), "sessao")


if __name__ == "__main__":
    unittest.main()
