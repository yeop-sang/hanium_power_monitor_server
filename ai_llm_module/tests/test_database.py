import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.database import Database

class TestDatabase:
    """Test cases for Database class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Initialize database with test configuration
        self.db = Database(
            host='test_host',
            user='test_user',
            password='test_password',
            database='test_database'
        )
    
    def test_initialization(self):
        """Test database initialization."""
        assert self.db.config['host'] == 'test_host'
        assert self.db.config['user'] == 'test_user'
        assert self.db.config['password'] == 'test_password'
        assert self.db.config['database'] == 'test_database'
        assert self.db.config['port'] == 3306
    
    def test_initialization_with_env_vars(self):
        """Test initialization with environment variables."""
        with patch.dict(os.environ, {
            'MYSQL_HOST': 'env_host',
            'MYSQL_USER': 'env_user',
            'MYSQL_PASSWORD': 'env_password',
            'MYSQL_DATABASE': 'env_database',
            'MYSQL_PORT': '3307'
        }):
            db = Database()
            assert db.config['host'] == 'env_host'
            assert db.config['user'] == 'env_user'
            assert db.config['password'] == 'env_password'
            assert db.config['database'] == 'env_database'
            assert db.config['port'] == 3307
    
    @patch('modules.database.mysql.connector.connect')
    def test_connect_success(self, mock_connect):
        """Test successful database connection."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        result = self.db.connect()
        
        mock_connect.assert_called_once_with(**self.db.config)
        assert result == mock_connection
    
    @patch('modules.database.mysql.connector.connect')
    def test_connect_failure(self, mock_connect):
        """Test database connection failure."""
        mock_connect.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception):
            self.db.connect()
    
    @patch('modules.database.mysql.connector.connect')
    def test_get_recent_data(self, mock_connect):
        """Test retrieving recent power data."""
        # Mock database connection and cursor
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        # Mock data returned from database
        mock_data = [
            {
                'id': 1,
                'timestamp': datetime.now(),
                'device_code': 'ESP32_001',
                'temperature': 22.5,
                'humidity': 45.0,
                'brightness': 300,
                'electric': 150.0,
                'created_at': datetime.now()
            },
            {
                'id': 2,
                'timestamp': datetime.now() - timedelta(hours=1),
                'device_code': 'ESP32_001',
                'temperature': 23.0,
                'humidity': 47.0,
                'brightness': 320,
                'electric': 160.0,
                'created_at': datetime.now()
            }
        ]
        mock_cursor.fetchall.return_value = mock_data
        
        # Call method
        result = self.db.get_recent_data(months=3)
        
        # Verify results
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'electric' in result.columns
        assert 'temperature' in result.columns
        
        # Verify SQL query was called
        mock_cursor.execute.assert_called_once()
        query, params = mock_cursor.execute.call_args
        assert 'power_readings' in query[0]
        assert 'timestamp >=' in query[0]
        
        # Verify connection cleanup
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()
    
    @patch('modules.database.mysql.connector.connect')
    def test_get_daily_summaries(self, mock_connect):
        """Test retrieving daily summaries."""
        # Mock database connection
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        # Mock daily summary data
        mock_data = [
            {
                'date': datetime.now().date(),
                'avg_temp': 22.5,
                'min_temp': 18.0,
                'max_temp': 27.0,
                'avg_humidity': 45.0,
                'min_humidity': 40.0,
                'max_humidity': 50.0,
                'avg_brightness': 300,
                'min_brightness': 200,
                'max_brightness': 400,
                'avg_electric': 150.0,
                'min_electric': 100.0,
                'max_electric': 200.0,
                'total_electric': 3600.0,
                'reading_count': 24
            }
        ]
        mock_cursor.fetchall.return_value = mock_data
        
        # Call method
        result = self.db.get_daily_summaries(months=3)
        
        # Verify results
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert 'avg_temp' in result.columns
        assert 'total_electric' in result.columns
        assert 'reading_count' in result.columns
        
        # Verify SQL query includes aggregation
        query = mock_cursor.execute.call_args[0][0]
        assert 'AVG(' in query
        assert 'SUM(' in query
        assert 'GROUP BY DATE(timestamp)' in query
    
    @patch('modules.database.mysql.connector.connect')
    def test_get_monthly_summaries(self, mock_connect):
        """Test retrieving monthly summaries."""
        # Mock database connection
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        # Mock monthly summary data
        mock_data = [
            {
                'year': 2024,
                'month': 1,
                'year_month': '2024-01',
                'avg_temp': 22.5,
                'avg_humidity': 45.0,
                'avg_brightness': 300,
                'avg_electric': 150.0,
                'total_electric': 108000.0,
                'reading_count': 720,
                'period_start': datetime(2024, 1, 1),
                'period_end': datetime(2024, 1, 31)
            }
        ]
        mock_cursor.fetchall.return_value = mock_data
        
        # Call method
        result = self.db.get_monthly_summaries(months=3)
        
        # Verify results
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert 'year_month' in result.columns
        assert 'total_electric' in result.columns
        
        # Verify SQL query includes monthly grouping
        query = mock_cursor.execute.call_args[0][0]
        assert 'YEAR(timestamp)' in query
        assert 'MONTH(timestamp)' in query
        assert 'GROUP BY YEAR(timestamp), MONTH(timestamp)' in query
    
    @patch('modules.database.mysql.connector.connect')
    def test_save_esg_report(self, mock_connect):
        """Test saving ESG report metadata."""
        # Mock database connection
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.lastrowid = 123
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        # Call method
        result = self.db.save_esg_report('/path/to/report.json')
        
        # Verify results
        assert result == 123
        
        # Verify SQL query
        mock_cursor.execute.assert_called_once()
        query, params = mock_cursor.execute.call_args
        assert 'INSERT INTO esg_reports' in query[0]
        assert params[0] == '/path/to/report.json'
        assert isinstance(params[1], datetime)
    
    @patch('modules.database.mysql.connector.connect')
    def test_get_device_statistics(self, mock_connect):
        """Test retrieving device statistics."""
        # Mock database connection
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        # Mock device statistics data
        mock_data = [
            {
                'device_code': 'ESP32_001',
                'total_readings': 1000,
                'avg_power': 150.5,
                'total_power': 150500.0,
                'first_reading': datetime.now() - timedelta(days=30),
                'last_reading': datetime.now(),
                'active_days': 30
            }
        ]
        mock_cursor.fetchall.return_value = mock_data
        
        # Call method
        result = self.db.get_device_statistics(months=3)
        
        # Verify results
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert 'device_code' in result.columns
        assert 'total_power' in result.columns
        
        # Verify SQL query includes device grouping
        query = mock_cursor.execute.call_args[0][0]
        assert 'GROUP BY device_code' in query
        assert 'COUNT(*)' in query
        assert 'AVG(electric)' in query
    
    @patch('modules.database.mysql.connector.connect')
    def test_test_connection_success(self, mock_connect):
        """Test connection test success."""
        # Mock successful connection
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1,)
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        result = self.db.test_connection()
        
        assert result is True
        mock_cursor.execute.assert_called_once_with("SELECT 1")
    
    @patch('modules.database.mysql.connector.connect')
    def test_test_connection_failure(self, mock_connect):
        """Test connection test failure."""
        mock_connect.side_effect = Exception("Connection failed")
        
        result = self.db.test_connection()
        
        assert result is False
    
    @patch('modules.database.mysql.connector.connect')
    def test_database_error_handling(self, mock_connect):
        """Test database error handling in data retrieval."""
        mock_connect.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            self.db.get_recent_data()


if __name__ == '__main__':
    pytest.main([__file__]) 