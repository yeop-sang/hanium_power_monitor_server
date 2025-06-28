import pytest
from unittest.mock import MagicMock
from modules.database import Database
import datetime

@pytest.fixture
def mock_db(mocker):
    """Fixture to create a mocked Database instance."""
    # Mock the connection pool so __init__ doesn't try to connect
    mocker.patch('mysql.connector.pooling.MySQLConnectionPool', return_value=MagicMock())
    
    db = Database()
    
    # Mock the connection and cursor
    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    
    # Configure the context manager behavior
    db.cnx_pool.get_connection.return_value.__enter__.return_value = mock_connection
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    
    # Attach mocks for inspection in tests
    db.mock_cursor = mock_cursor
    db.mock_connection = mock_connection
    
    return db

def test_insert_reading(mock_db):
    """Test that insert_reading constructs and executes the correct SQL query."""
    device_code = 1
    timestamp = datetime.datetime.now()
    temp = 25.5
    humidity = 60.1
    brightness = 500
    electric = 1.2
    
    mock_db.insert_reading(device_code, timestamp, temp, humidity, brightness, electric)
    
    expected_query = (
        "INSERT INTO power_readings (timestamp, device_code, temperature, humidity, brightness, electric) "
        "VALUES (%s, %s, %s, %s, %s, %s)"
    )
    expected_params = (timestamp, device_code, temp, humidity, brightness, electric)
    
    # Assert that the cursor was used to execute the query
    mock_db.mock_cursor.execute.assert_called_once_with(expected_query, expected_params)
    # Assert that the connection was committed
    mock_db.mock_connection.commit.assert_called_once()

def test_fetch_power_data(mock_db):
    """Test that fetch_power_data executes the query and returns data."""
    # Define some sample data to be returned by the mock cursor
    sample_data = [
        {'id': 1, 'timestamp': datetime.datetime.now(), 'temperature': 25.0},
        {'id': 2, 'timestamp': datetime.datetime.now(), 'temperature': 26.0},
    ]
    mock_db.mock_cursor.fetchall.return_value = sample_data
    
    result = mock_db.fetch_power_data(limit=2)
    
    expected_query = (
        "SELECT id, timestamp, device_code, temperature, humidity, brightness, electric "
        "FROM power_readings ORDER BY timestamp DESC LIMIT %s"
    )
    
    # Assert that the query was executed with the correct limit
    mock_db.mock_cursor.execute.assert_called_once_with(expected_query, (2,))
    # Assert that the fetched data matches our sample data
    assert result == sample_data
    mock_db.mock_cursor.fetchall.assert_called_once()
