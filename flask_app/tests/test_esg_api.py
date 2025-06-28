import pytest, json
from flask import Flask
from unittest.mock import MagicMock
from modules.api import setup_routes

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.fetch_esg_reports.return_value = [
        {"id": 1, "url": "/reports/r1.csv", "created_at": "2025-06-28T00:00:00"}
    ]
    db.create_esg_report.return_value = (2, "/reports/r2.csv")
    return db

@pytest.fixture
def client(mock_db):
    app = Flask(__name__)
    app.register_blueprint(setup_routes(mock_db))
    return app.test_client()

def test_list_esg_reports(client, mock_db):
    res = client.get('/api/esg_reports')
    assert res.status_code == 200
    data = json.loads(res.data)
    assert len(data) == 1
    mock_db.fetch_esg_reports.assert_called_once()

def test_generate_esg_report(client, mock_db):
    res = client.post('/api/generate_esg_report')
    assert res.status_code in (200, 201)
    data = json.loads(res.data)
    assert data['id'] == 2
    mock_db.create_esg_report.assert_called_once() 