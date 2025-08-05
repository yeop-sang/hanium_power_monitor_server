import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mock the modules before importing app
with patch('modules.database.Database'), \
     patch('modules.claude_api.ClaudeAPI'), \
     patch('modules.carbon_calculator.CarbonCalculator'):
    import app as flask_app

class TestFlaskApp:
    """Test cases for Flask application endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = flask_app.app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Mock components
        self.mock_db = Mock()
        self.mock_claude = Mock()
        self.mock_carbon = Mock()
        
        flask_app.db = self.mock_db
        flask_app.claude_api = self.mock_claude
        flask_app.carbon_calculator = self.mock_carbon
    
    def test_health_check_healthy(self):
        """Test health check endpoint when all systems are healthy."""
        # Mock successful health checks
        self.mock_db.test_connection.return_value = True
        self.mock_claude.test_api_connection.return_value = True
        
        response = self.client.get('/health')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['status'] == 'healthy'
        assert data['components']['database'] == 'connected'
        assert data['components']['claude_api'] == 'connected'
        assert 'timestamp' in data
    
    def test_health_check_unhealthy(self):
        """Test health check endpoint when systems are unhealthy."""
        # Mock failed health checks
        self.mock_db.test_connection.return_value = False
        self.mock_claude.test_api_connection.return_value = False
        
        response = self.client.get('/health')
        data = json.loads(response.data)
        
        assert response.status_code == 503
        assert data['status'] == 'unhealthy'
        assert data['components']['database'] == 'disconnected'
        assert data['components']['claude_api'] == 'disconnected'
    
    def test_health_check_error(self):
        """Test health check endpoint when an error occurs."""
        # Mock error in health check
        self.mock_db.test_connection.side_effect = Exception("Database error")
        
        response = self.client.get('/health')
        data = json.loads(response.data)
        
        assert response.status_code == 500
        assert data['status'] == 'error'
        assert 'error' in data
    
    def test_generate_esg_report_success(self):
        """Test successful ESG report generation."""
        # Mock data
        sample_daily_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5),
            'avg_temp': [20, 21, 22, 23, 24],
            'total_electric': [100, 110, 120, 130, 140]
        })
        
        sample_monthly_data = pd.DataFrame({
            'year_month': ['2024-01'],
            'total_electric': [3000]
        })
        
        # Mock database calls
        self.mock_db.get_daily_summaries.return_value = sample_daily_data
        self.mock_db.get_monthly_summaries.return_value = sample_monthly_data
        
        # Mock carbon calculator
        self.mock_carbon.calculate_daily_emissions.return_value = sample_daily_data
        self.mock_carbon.calculate_monthly_emissions.return_value = sample_monthly_data
        self.mock_carbon.calculate_carbon_trends.return_value = {
            'total_emissions_kg': 50.0,
            'average_emissions_kg': 10.0
        }
        
        # Mock Claude API
        mock_report = {
            'report_sections': {
                'executive_summary': 'Test summary',
                'recommendations': 'Test recommendations'
            },
            'metadata': {
                'generated_at': datetime.now().isoformat()
            }
        }
        self.mock_claude.generate_esg_report.return_value = mock_report
        
        # Make request
        response = self.client.post('/generate_report', 
                                   json={'months': 3, 'type': 'full'})
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert 'report_sections' in data
        assert 'request_info' in data
        assert 'carbon_trends' in data
        assert data['request_info']['months_analyzed'] == 3
        assert data['request_info']['report_type'] == 'full'
    
    def test_generate_esg_report_summary(self):
        """Test summary ESG report generation."""
        # Mock data
        sample_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=3),
            'total_electric': [100, 110, 120]
        })
        
        self.mock_db.get_daily_summaries.return_value = sample_data
        self.mock_db.get_monthly_summaries.return_value = sample_data
        self.mock_carbon.calculate_daily_emissions.return_value = sample_data
        self.mock_carbon.calculate_monthly_emissions.return_value = sample_data
        self.mock_carbon.calculate_carbon_trends.return_value = {}
        
        # Mock Claude API for summary
        self.mock_claude._prepare_report_data.return_value = {'test': 'data'}
        self.mock_claude.generate_summary_report.return_value = {
            'summary': 'Brief summary',
            'generated_at': datetime.now().isoformat()
        }
        
        response = self.client.post('/generate_report', 
                                   json={'months': 1, 'type': 'summary'})
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert 'summary' in data
        assert data['request_info']['report_type'] == 'summary'
    
    def test_generate_esg_report_no_data(self):
        """Test ESG report generation with no data."""
        # Mock empty data
        self.mock_db.get_daily_summaries.return_value = pd.DataFrame()
        
        response = self.client.post('/generate_report')
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert 'error' in data
        assert 'No data available' in data['error']
    
    def test_generate_esg_report_error(self):
        """Test ESG report generation with error."""
        # Mock database error
        self.mock_db.get_daily_summaries.side_effect = Exception("Database error")
        
        response = self.client.post('/generate_report')
        data = json.loads(response.data)
        
        assert response.status_code == 500
        assert 'error' in data
        assert 'Failed to generate ESG report' in data['error']
    
    def test_get_data_summary_success(self):
        """Test data summary endpoint success."""
        # Mock data
        daily_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=3),
            'daily_energy_kwh': [10, 12, 11],
            'avg_temp': [20, 21, 22],
            'avg_humidity': [45, 46, 47],
            'avg_brightness': [300, 310, 320]
        })
        
        monthly_data = pd.DataFrame({
            'year_month': ['2024-01'],
            'total_electric': [1000]
        })
        
        device_data = pd.DataFrame({
            'device_code': ['ESP32_001'],
            'total_power': [500]
        })
        
        self.mock_db.get_daily_summaries.return_value = daily_data
        self.mock_db.get_monthly_summaries.return_value = monthly_data
        self.mock_db.get_device_statistics.return_value = device_data
        
        # Mock carbon calculator
        self.mock_carbon.calculate_daily_emissions.return_value = daily_data
        self.mock_carbon.calculate_carbon_trends.return_value = {
            'total_emissions_kg': 30.0
        }
        
        response = self.client.get('/data_summary?months=3')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert 'data_availability' in data
        assert 'power_statistics' in data
        assert 'carbon_summary' in data
        assert 'device_statistics' in data
        assert 'environmental_averages' in data
        assert data['data_availability']['daily_records'] == 3
        assert data['data_availability']['monthly_records'] == 1
    
    def test_get_carbon_factors(self):
        """Test carbon factors endpoint."""
        # Mock carbon calculator info
        self.mock_carbon.get_emission_factor_info.return_value = {
            'factor_value': 0.478,
            'factor_source': 'korea_grid',
            'available_factors': {'korea_grid': 0.478, 'renewable': 0.048}
        }
        
        response = self.client.get('/carbon_factors')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert 'factor_value' in data
        assert 'available_factors' in data
    
    def test_test_all_components_success(self):
        """Test component testing endpoint success."""
        # Mock successful tests
        self.mock_db.test_connection.return_value = True
        self.mock_db.get_daily_summaries.return_value = pd.DataFrame([{'test': 1}])
        self.mock_claude.test_api_connection.return_value = True
        self.mock_carbon.get_emission_factor_info.return_value = {
            'factor_value': 0.478
        }
        
        response = self.client.get('/test_components')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['overall_status'] == 'all_systems_operational'
        assert data['database']['status'] == 'connected'
        assert data['database']['test_query'] is True
        assert data['claude_api']['status'] == 'connected'
        assert data['carbon_calculator']['status'] == 'initialized'
    
    def test_test_all_components_with_issues(self):
        """Test component testing endpoint with issues."""
        # Mock failed tests
        self.mock_db.test_connection.return_value = False
        self.mock_claude.test_api_connection.return_value = False
        self.mock_carbon.get_emission_factor_info.return_value = {}
        
        response = self.client.get('/test_components')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert data['overall_status'] == 'some_issues_detected'
        assert data['database']['status'] == 'disconnected'
        assert data['claude_api']['status'] == 'disconnected'
    
    def test_404_handler(self):
        """Test 404 error handler."""
        response = self.client.get('/nonexistent')
        data = json.loads(response.data)
        
        assert response.status_code == 404
        assert 'Endpoint not found' in data['error']
        assert 'available_endpoints' in data
    
    def test_500_handler(self):
        """Test 500 error handler (simulated via component failure)."""
        # Force an exception in a component test
        self.mock_carbon.get_emission_factor_info.side_effect = Exception("Test error")
        
        response = self.client.get('/carbon_factors')
        data = json.loads(response.data)
        
        assert response.status_code == 500
        assert 'error' in data


if __name__ == '__main__':
    pytest.main([__file__]) 