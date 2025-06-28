import pytest
from flask import Flask
from unittest.mock import MagicMock
import json
import datetime
from decimal import Decimal

# Import the setup function from our api module
from modules.api import setup_routes

@pytest.fixture
def mock_db():
    """Fixture for a mocked Database object."""
    db = MagicMock()
    
    # Sample data for fetch_power_data
    sample_data = [
        {'id': 1, 'timestamp': datetime.datetime.now(), 'temperature': Decimal('25.5')},
        {'id': 2, 'timestamp': datetime.datetime.now(), 'temperature': Decimal('26.5')},
    ]
    db.fetch_power_data.return_value = sample_data
    return db

@pytest.fixture
def test_app(mock_db):
    """Fixture to create a Flask app for testing."""
    app = Flask(__name__)
    api_blueprint = setup_routes(mock_db)
    app.register_blueprint(api_blueprint)
    return app

@pytest.fixture  # Fixture decorator that marks a function as a test fixture - a reusable test setup function
def client(test_app):
    """Fixture to get a test client for the Flask app."""
    return test_app.test_client()

def test_get_power_data_success(client, mock_db):
    """Test the /api/power_data endpoint for a successful request."""
    response = client.get('/api/power_data?limit=2')
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert len(data) == 2
    
    # Check that the mock function was called with the correct limit
    mock_db.fetch_power_data.assert_called_once_with(limit=2)
    
    # Check if the data matches (ignoring timestamp precision)
    assert data[0]['temperature'] == 25.5

def test_get_power_data_invalid_limit(client, mock_db):
    """Test that an invalid limit defaults to 100."""
    client.get('/api/power_data?limit=invalid')
    mock_db.fetch_power_data.assert_called_once_with(limit=100)
    
    # Reset mock and test for another invalid case
    mock_db.fetch_power_data.reset_mock()
    client.get('/api/power_data?limit=-10')
    mock_db.fetch_power_data.assert_called_once_with(limit=100)

def test_not_implemented_endpoints(client):
    """Test that placeholder endpoints return 501 Not Implemented."""
    summary_response = client.get('/api/summary')
    assert summary_response.status_code == 501
    
    report_response = client.post('/api/generate_esg_report')
    assert report_response.status_code == 501

    summary_data = json.loads(summary_response.data)
    assert "not yet implemented" in summary_data['message']
    
    report_data = json.loads(report_response.data)
    assert "not yet implemented" in report_data['message']
