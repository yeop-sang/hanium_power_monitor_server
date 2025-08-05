import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database access layer for AI/LLM module ESG report generation."""
    
    def __init__(self, host=None, user=None, password=None, database=None):
        """Initialize database connection parameters.
        
        Args:
            host: MySQL host (defaults to environment variable)
            user: MySQL user (defaults to environment variable)
            password: MySQL password (defaults to environment variable)
            database: Database name (defaults to environment variable)
        """
        self.config = {
            'host': host or os.environ.get('MYSQL_HOST', 'mysql'),
            'user': user or os.environ.get('MYSQL_USER', 'power_user'),
            'password': password or os.environ.get('MYSQL_PASSWORD', 'password'),
            'database': database or os.environ.get('MYSQL_DATABASE', 'power_measurement'),
            'port': int(os.environ.get('MYSQL_PORT', 3306)),
            'charset': 'utf8mb4',
            'autocommit': True
        }
    
    def connect(self):
        """Create a new database connection.
        
        Returns:
            mysql.connector.connection: Database connection object
            
        Raises:
            mysql.connector.Error: If connection fails
        """
        try:
            connection = mysql.connector.connect(**self.config)
            logger.info(f"Connected to MySQL database: {self.config['database']}")
            return connection
        except mysql.connector.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def get_recent_data(self, months=3):
        """Retrieve recent power consumption data for analysis.
        
        Args:
            months: Number of months of historical data to retrieve
            
        Returns:
            pandas.DataFrame: Raw power readings data
        """
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor(dictionary=True)
            
            # Calculate date N months ago
            months_ago = (datetime.now() - timedelta(days=months * 30)).strftime('%Y-%m-%d')
            
            query = """
            SELECT 
                id,
                timestamp,
                device_code,
                temperature,
                humidity,
                brightness,
                electric,
                created_at
            FROM power_readings 
            WHERE timestamp >= %s 
            ORDER BY timestamp ASC
            """
            
            logger.info(f"Fetching power data from {months_ago}")
            cursor.execute(query, (months_ago,))
            result = cursor.fetchall()
            
            logger.info(f"Retrieved {len(result)} power readings")
            return pd.DataFrame(result)
            
        except mysql.connector.Error as e:
            logger.error(f"Error retrieving recent data: {e}")
            raise
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_daily_summaries(self, months=3):
        """Get daily aggregated summaries for ESG report generation.
        
        Args:
            months: Number of months of historical data to summarize
            
        Returns:
            pandas.DataFrame: Daily aggregated power and environmental data
        """
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor(dictionary=True)
            
            months_ago = (datetime.now() - timedelta(days=months * 30)).strftime('%Y-%m-%d')
            
            query = """
            SELECT 
                DATE(timestamp) as date,
                AVG(temperature) as avg_temp,
                MIN(temperature) as min_temp,
                MAX(temperature) as max_temp,
                AVG(humidity) as avg_humidity,
                MIN(humidity) as min_humidity,
                MAX(humidity) as max_humidity,
                AVG(brightness) as avg_brightness,
                MIN(brightness) as min_brightness,
                MAX(brightness) as max_brightness,
                AVG(electric) as avg_electric,
                MIN(electric) as min_electric,
                MAX(electric) as max_electric,
                SUM(electric) as total_electric,
                COUNT(*) as reading_count
            FROM power_readings
            WHERE timestamp >= %s
            GROUP BY DATE(timestamp)
            ORDER BY date ASC
            """
            
            logger.info(f"Generating daily summaries from {months_ago}")
            cursor.execute(query, (months_ago,))
            result = cursor.fetchall()
            
            logger.info(f"Generated {len(result)} daily summaries")
            return pd.DataFrame(result)
            
        except mysql.connector.Error as e:
            logger.error(f"Error generating daily summaries: {e}")
            raise
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_monthly_summaries(self, months=3):
        """Get monthly aggregated summaries for high-level ESG analysis.
        
        Args:
            months: Number of months of historical data to summarize
            
        Returns:
            pandas.DataFrame: Monthly aggregated power and environmental data
        """
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor(dictionary=True)
            
            months_ago = (datetime.now() - timedelta(days=months * 30)).strftime('%Y-%m-%d')
            
            query = """
            SELECT 
                YEAR(timestamp) as year,
                MONTH(timestamp) as month,
                CONCAT(YEAR(timestamp), '-', LPAD(MONTH(timestamp), 2, '0')) as year_month,
                AVG(temperature) as avg_temp,
                AVG(humidity) as avg_humidity,
                AVG(brightness) as avg_brightness,
                AVG(electric) as avg_electric,
                SUM(electric) as total_electric,
                COUNT(*) as reading_count,
                MIN(timestamp) as period_start,
                MAX(timestamp) as period_end
            FROM power_readings
            WHERE timestamp >= %s
            GROUP BY YEAR(timestamp), MONTH(timestamp)
            ORDER BY year, month ASC
            """
            
            logger.info(f"Generating monthly summaries from {months_ago}")
            cursor.execute(query, (months_ago,))
            result = cursor.fetchall()
            
            logger.info(f"Generated {len(result)} monthly summaries")
            return pd.DataFrame(result)
            
        except mysql.connector.Error as e:
            logger.error(f"Error generating monthly summaries: {e}")
            raise
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    
    def save_esg_report(self, file_path):
        """Save ESG report metadata to database.
        
        Args:
            file_path: Path where the ESG report is saved
            
        Returns:
            int: ID of the saved report record
        """
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            query = """
            INSERT INTO esg_reports (file_path, created_at)
            VALUES (%s, %s)
            """
            
            created_at = datetime.now()
            cursor.execute(query, (file_path, created_at))
            report_id = cursor.lastrowid
            
            logger.info(f"Saved ESG report metadata: ID={report_id}, Path={file_path}")
            return report_id
            
        except mysql.connector.Error as e:
            logger.error(f"Error saving ESG report metadata: {e}")
            raise
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    
    def get_device_statistics(self, months=3):
        """Get device-specific statistics for ESG analysis.
        
        Args:
            months: Number of months of historical data to analyze
            
        Returns:
            pandas.DataFrame: Device-specific power consumption statistics
        """
        conn = None
        try:
            conn = self.connect()
            cursor = conn.cursor(dictionary=True)
            
            months_ago = (datetime.now() - timedelta(days=months * 30)).strftime('%Y-%m-%d')
            
            query = """
            SELECT 
                device_code,
                COUNT(*) as total_readings,
                AVG(electric) as avg_power,
                SUM(electric) as total_power,
                MIN(timestamp) as first_reading,
                MAX(timestamp) as last_reading,
                DATEDIFF(MAX(timestamp), MIN(timestamp)) + 1 as active_days
            FROM power_readings
            WHERE timestamp >= %s
            GROUP BY device_code
            ORDER BY total_power DESC
            """
            
            logger.info(f"Generating device statistics from {months_ago}")
            cursor.execute(query, (months_ago,))
            result = cursor.fetchall()
            
            logger.info(f"Generated statistics for {len(result)} devices")
            return pd.DataFrame(result)
            
        except mysql.connector.Error as e:
            logger.error(f"Error generating device statistics: {e}")
            raise
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
    
    def test_connection(self):
        """Test database connectivity.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            logger.info("Database connection test successful")
            return result[0] == 1
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False 