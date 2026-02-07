"""
Test script for language detection and confirmation flow.

This script demonstrates the new three-step language detection workflow:
1. Detect language with confidence score
2. Confirm or correct the detected language
3. Perform transliteration with confirmed language
"""

import asyncio
import json
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_detect_cyrillic():
    """Test detecting Cyrillic script."""
    print("\n=== Test: Detect Cyrillic ===")
    response = client.post(
        "/detect-language",
        data={"text": "Привет мир"}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    assert response.status_code == 200
    assert result["detected_script"] == "Cyrillic"
    assert result["iso_code"] == "Cyrl"
    assert result["confidence"] > 0.9
    print("✓ Cyrillic detection passed")
    return result


def test_detect_latin():
    """Test detecting Latin script."""
    print("\n=== Test: Detect Latin ===")
    response = client.post(
        "/detect-language",
        data={"text": "Hello world"}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    assert response.status_code == 200
    assert result["detected_script"] == "Latin"
    assert result["iso_code"] == "Latn"
    print("✓ Latin detection passed")
    return result


def test_detect_arabic():
    """Test detecting Arabic script."""
    print("\n=== Test: Detect Arabic ===")
    response = client.post(
        "/detect-language",
        data={"text": "مرحبا بالعالم"}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    assert response.status_code == 200
    assert result["detected_script"] == "Arabic"
    assert result["iso_code"] == "Arab"
    print("✓ Arabic detection passed")
    return result


def test_confirm_language_correct():
    """Test confirming a detected language."""
    print("\n=== Test: Confirm Detected Language ===")
    response = client.post(
        "/confirm-language",
        json={
            "detected_language": "Cyrl",
            "user_confirmed": True
        }
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    assert response.status_code == 200
    assert result["confirmed_source_script"] == "Cyrl"
    print("✓ Language confirmation passed")
    return result


def test_confirm_language_corrected():
    """Test correcting a detected language."""
    print("\n=== Test: Correct Detected Language ===")
    response = client.post(
        "/confirm-language",
        json={
            "detected_language": "Latn",
            "user_confirmed": False,
            "corrected_language": "Cyrl"
        }
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    assert response.status_code == 200
    assert result["confirmed_source_script"] == "Cyrl"
    print("✓ Language correction passed")
    return result


def test_transliterate_with_detection():
    """Test transliteration with auto-detection."""
    print("\n=== Test: Transliterate with Auto-Detection ===")
    response = client.post(
        "/transliterate",
        data={
            "text": "Привет",
            "target_script": "Latn"
        }
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    assert response.status_code == 200
    assert result["detected_script"] == "Cyrillic"
    assert result["source_script"] == "Cyrl"
    assert result["detection_status"] == "auto-detected"
    print("✓ Transliteration with auto-detection passed")
    return result


def test_transliterate_with_confirmed_script():
    """Test transliteration with user-confirmed source script."""
    print("\n=== Test: Transliterate with User-Confirmed Script ===")
    response = client.post(
        "/transliterate",
        data={
            "text": "Привет",
            "source_script": "Cyrl",
            "target_script": "Latn",
            "skip_detection": "true"
        }
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    assert response.status_code == 200
    assert result["source_script"] == "Cyrl"
    assert result["detection_status"] == "user-provided"
    print("✓ Transliteration with confirmed script passed")
    return result


def test_mixed_script_detection():
    """Test detection with mixed scripts."""
    print("\n=== Test: Mixed Script Detection ===")
    response = client.post(
        "/detect-language",
        data={"text": "Hello привет"}
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    assert response.status_code == 200
    # Should detect dominant script (in this case, both equal, so alphabetically first)
    print(f"✓ Mixed script detection passed (detected: {result['detected_script']})")
    return result


def test_error_handling_no_input():
    """Test error handling when no input is provided."""
    print("\n=== Test: Error Handling - No Input ===")
    response = client.post("/detect-language")
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    assert response.status_code == 200
    assert "error" in result
    print("✓ Error handling passed")
    return result


def test_error_handling_invalid_correction():
    """Test error handling for invalid language correction."""
    print("\n=== Test: Error Handling - Invalid Language Correction ===")
    response = client.post(
        "/confirm-language",
        json={
            "detected_language": "Latn",
            "user_confirmed": False,
            "corrected_language": "InvalidScript"
        }
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    assert response.status_code == 200
    assert "error" in result
    print("✓ Invalid correction error handling passed")
    return result


def run_all_tests():
    """Run all language detection tests."""
    print("=" * 60)
    print("LANGUAGE DETECTION AND CONFIRMATION TESTS")
    print("=" * 60)
    
    try:
        test_detect_cyrillic()
        test_detect_latin()
        test_detect_arabic()
        test_confirm_language_correct()
        test_confirm_language_corrected()
        test_transliterate_with_detection()
        test_transliterate_with_confirmed_script()
        test_mixed_script_detection()
        test_error_handling_no_input()
        test_error_handling_invalid_correction()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
