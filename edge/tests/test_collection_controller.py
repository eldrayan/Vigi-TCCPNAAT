import unittest

from edge.collection.controller import DatasetCollectionController
from edge.config import parse_collection_config


class FakeView:
    headless = True

    def __init__(self):
        self.notifications = []

    def notify(self, category, message):
        self.notifications.append((category, message))


class FakeStore:
    def __init__(self):
        self.calls = []

    def save(self, *args):
        self.calls.append(args)
        raise AssertionError("A imagem desfocada não deveria ser persistida")


class CollectionControllerTests(unittest.TestCase):
    def create_controller(self):
        view = FakeView()
        store = FakeStore()
        controller = DatasetCollectionController(
            config=parse_collection_config([]),
            cv2=None,
            camera=None,
            view=view,
            image_store=store,
            backend="picamera2",
        )
        return controller, view, store

    def test_class_control_updates_state(self):
        controller, view, _ = self.create_controller()
        should_stop = controller._handle_control_key(ord("3"))
        self.assertFalse(should_stop)
        self.assertEqual(controller.state.class_name, "03_tampa_torta")
        self.assertIn(
            ("INFO", "Classe selecionada: 03_tampa_torta"), view.notifications
        )

    def test_quit_control_stops_loop(self):
        controller, _, _ = self.create_controller()
        self.assertTrue(controller._handle_control_key(ord("q")))

    def test_blurry_image_is_rejected_before_storage(self):
        controller, view, store = self.create_controller()
        controller._capture_when_requested(
            key=ord(" "),
            frame=object(),
            guide=(0, 0, 10, 10),
            score=10.0,
        )
        self.assertEqual(controller.state.rejected_blurry, 1)
        self.assertEqual(store.calls, [])
        self.assertEqual(view.notifications[-1][0], "CAPTURA")


if __name__ == "__main__":
    unittest.main()
