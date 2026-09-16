"""
Descrição: Testa o armazenamento opcional das capturas de inspeção.
Autor: Leôncio Ferreira
"""

from unittest.mock import MagicMock

from edge.orchestration.capture_store import InspectionCaptureStore


def test_store_writes_latest_and_auditable_capture(tmp_path) -> None:
    cv2 = MagicMock()
    cv2.COLOR_RGB2BGR = 7
    frame = MagicMock()
    frame.ndim = 3
    frame.shape = (720, 1280, 3)
    converted = MagicMock()
    cv2.cvtColor.return_value = converted
    store = InspectionCaptureStore(tmp_path, cv2=cv2)

    store.save(frame, inspection_id=42, result="NAO_CONFORME")

    cv2.cvtColor.assert_called_once_with(frame, 7)
    assert cv2.imwrite.call_args_list == [
        ((str(tmp_path / "ultima_inspecao.jpg"), converted),),
        ((str(tmp_path / "inspecao_42_NAO_CONFORME.jpg"), converted),),
    ]
