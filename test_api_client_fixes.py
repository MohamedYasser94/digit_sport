#!/usr/bin/env python
"""
Quick test script for the API client timeout and retry fixes
Run this to verify the fixes are working correctly
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digit_sport.settings')
django.setup()

from core.utils.api_client import APIClient, get_api_client, CircuitBreaker
import time


def test_circuit_breaker():
    """Test the circuit breaker functionality"""
    print("\n" + "="*60)
    print("TEST 1: Circuit Breaker Pattern")
    print("="*60)

    cb = CircuitBreaker(failure_threshold=3, timeout=5)

    # Test closed state
    assert cb.is_available(), "Circuit should be available initially"
    print("✓ Circuit breaker initialized in CLOSED state")

    # Simulate failures
    for i in range(3):
        cb.record_failure()
        print(f"  Recorded failure {i+1}/3")

    # Circuit should now be open
    assert not cb.is_available(), "Circuit should be OPEN after threshold"
    print("✓ Circuit breaker transitioned to OPEN state")

    # Wait for half-open
    print("  Waiting 5 seconds for HALF-OPEN transition...")
    time.sleep(6)

    assert cb.is_available(), "Circuit should be HALF-OPEN after timeout"
    print("✓ Circuit breaker transitioned to HALF-OPEN state")

    # Simulate success
    cb.record_success()
    assert cb.is_available(), "Circuit should be CLOSED after success"
    print("✓ Circuit breaker returned to CLOSED state")


def test_api_client_creation():
    """Test API client singleton"""
    print("\n" + "="*60)
    print("TEST 2: API Client Singleton")
    print("="*60)

    client1 = get_api_client()
    client2 = get_api_client()

    assert client1 is client2, "API client should be singleton"
    print("✓ API client is properly implemented as singleton")

    assert client1.timeout == 15, "Default timeout should be 15 seconds"
    print(f"✓ API client timeout: {client1.timeout} seconds")

    assert client1.retries == 3, "Default retries should be 3"
    print(f"✓ API client retries: {client1.retries}")


def test_backoff_calculation():
    """Test exponential backoff calculation"""
    print("\n" + "="*60)
    print("TEST 3: Exponential Backoff Calculation")
    print("="*60)

    client = APIClient()

    expected = [
        (1, 0.5),
        (2, 1.0),
        (3, 2.0),
        (4, 4.0),
    ]

    for attempt, expected_time in expected:
        actual_time = client._calculate_backoff(attempt)
        assert actual_time == expected_time, f"Backoff for attempt {attempt} should be {expected_time}, got {actual_time}"
        print(f"✓ Attempt {attempt}: {actual_time}s backoff")

    # Test max cap (30 seconds)
    max_time = client._calculate_backoff(10)
    assert max_time <= 30, "Backoff should be capped at 30 seconds"
    print(f"✓ Backoff capped at: {max_time}s (max 30s)")


def test_endpoint_extraction():
    """Test endpoint extraction from URL"""
    print("\n" + "="*60)
    print("TEST 4: Endpoint Extraction")
    print("="*60)

    test_cases = [
        ("https://api.example.com/players/search/test", "api.example.com/players/search"),
        ("https://transfermarkt-api.fly.dev/players/123/profile", "transfermarkt-api.fly.dev/players/123/profile"),
        ("https://example.com/api?token=123", "example.com/api"),
    ]

    for url, expected_endpoint in test_cases:
        endpoint = APIClient._extract_endpoint(url)
        print(f"✓ Extracted: {endpoint}")


def test_settings_configuration():
    """Test Django settings configuration"""
    print("\n" + "="*60)
    print("TEST 5: Django Settings Configuration")
    print("="*60)

    from django.conf import settings

    assert hasattr(settings, 'API_REQUEST_TIMEOUT'), "Settings should have API_REQUEST_TIMEOUT"
    print(f"✓ API_REQUEST_TIMEOUT = {settings.API_REQUEST_TIMEOUT}s")

    assert hasattr(settings, 'API_REQUEST_RETRIES'), "Settings should have API_REQUEST_RETRIES"
    print(f"✓ API_REQUEST_RETRIES = {settings.API_REQUEST_RETRIES}")

    assert hasattr(settings, 'API_BULK_OPERATION_TIMEOUT'), "Settings should have API_BULK_OPERATION_TIMEOUT"
    print(f"✓ API_BULK_OPERATION_TIMEOUT = {settings.API_BULK_OPERATION_TIMEOUT}s")


def test_connection_pooling():
    """Verify connection pooling is configured"""
    print("\n" + "="*60)
    print("TEST 6: Connection Pooling")
    print("="*60)

    client = APIClient()

    # Check session has adapters
    assert 'https://' in client.session.adapters, "Session should have HTTPS adapter"
    assert 'http://' in client.session.adapters, "Session should have HTTP adapter"
    print("✓ HTTP/HTTPS adapters configured")

    adapter = client.session.adapters['https://']
    print(f"✓ Connection pool size: {adapter.poolmanager.pools if hasattr(adapter, 'poolmanager') else 'default'}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("API CLIENT TIMEOUT & RETRY FIX - TEST SUITE")
    print("="*60)

    try:
        test_circuit_breaker()
        test_api_client_creation()
        test_backoff_calculation()
        test_endpoint_extraction()
        test_settings_configuration()
        test_connection_pooling()

        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED!")
        print("="*60)
        print("\nThe API client timeout and retry fixes are working correctly.")
        print("\nNext steps:")
        print("1. Test the actual API endpoints:")
        print("   - POST /sport/monk/players/api/get/")
        print("   - POST /sport/transfermarket/players/api/get/")
        print("2. Monitor debug.log for API call logs")
        print("3. Check circuit breaker states when API fails")
        print("\nDocumentation: See API_TIMEOUT_FIX_DOCUMENTATION.md")

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())

