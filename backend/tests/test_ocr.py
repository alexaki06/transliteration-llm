import pytest
pytest.importorskip("pytesseract")
from backend.ocr.ocr_utils import ocr_from_image


def test_ocr_import_and_callable():
    assert callable(ocr_from_image)
