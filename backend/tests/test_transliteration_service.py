import pytest

from backend.transliteration.transliteration_service import TransliterationService, LLMClient


class DummyLLM(LLMClient):
    def __init__(self, response: str):
        self.response = response
        self.last_prompt = None

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.response


def test_normalize_script_aliases_and_codes():
    svc = TransliterationService(llm_client=DummyLLM("x|y"))

    assert svc.normalize_script_code("latin") == "Latn"
    assert svc.normalize_script_code("Latin") == "Latn"
    assert svc.normalize_script_code("Cyrillic") == "Cyrl"
    assert svc.normalize_script_code("Cyrl") == "Cyrl"

    with pytest.raises(ValueError):
        svc.normalize_script_code("unknown-script")


def test_transliterate_parses_response_and_includes_context():
    dummy = DummyLLM("privet|Preserved hard sign for fidelity")
    svc = TransliterationService(llm_client=dummy)

    result = svc.transliterate("привет", source_script="Cyrillic", target_script="Latin", context="formal")

    assert result["transliteration"] == "privet"
    assert "Preserved" in result["explanation"]
    assert result["source_script"] == "Cyrl"
    assert result["target_script"] == "Latn"

    # ensure context is present in the constructed prompt
    assert dummy.last_prompt is not None
    assert "Context: formal" in dummy.last_prompt
