import pytest
from unittest.mock import MagicMock
import json

# The function to test
from app import on_message_callback

# Since app.py initializes db globally, we need to mock it before import.
# This is tricky, so we will use mocker from pytest-mock to patch it inside the test.

@pytest.fixture
def mock_db_global(mocker):
    """Mocks the global 'db' object in the 'app' module."""
    mock_db = MagicMock()
    mocker.patch('app.db', mock_db)
    return mock_db

def test_on_message_callback_success(mock_db_global):
    """Test the callback with a valid JSON payload."""
    payload = {
        "deviceCode": 101,
        "timestamp": "2024-01-01T12:00:00",
        "temp": 22.5,
        "humidity": 55.0,
        "brightness": 700,
        "electric": 3.14
    }
    
    on_message_callback(json.dumps(payload))
    
    # Check if insert_reading was called with the correct arguments
    mock_db_global.insert_reading.assert_called_once_with(
        101, "2024-01-01T12:00:00", 22.5, 55.0, 700, 3.14
    )

def test_on_message_callback_missing_fields(mock_db_global):
    """Test that messages with missing required fields are skipped."""
    # Missing timestamp
    payload_no_ts = {"deviceCode": 102}
    on_message_callback(json.dumps(payload_no_ts))
    
    # Missing deviceCode
    payload_no_dc = {"timestamp": "2024-01-01T13:00:00"}
    on_message_callback(json.dumps(payload_no_dc))

    # Assert that insert_reading was never called
    mock_db_global.insert_reading.assert_not_called()

def test_on_message_callback_invalid_json(mock_db_global, caplog):
    """Test the callback with a malformed JSON string."""
    malformed_payload = "this is not json"
    
    on_message_callback(malformed_payload)
    
    # Assert that insert_reading was not called
    mock_db_global.insert_reading.assert_not_called()
    
    # Assert that an error was logged
    assert len(caplog.records) == 1
    assert "Error decoding JSON" in caplog.text
    assert caplog.records[0].levelname == 'ERROR'
