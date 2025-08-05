import mysql.connector
from mysql.connector import pooling
import os
import datetime
from typing import Union
import logging

class Database:
    """MySQL database helper class.

    Uses a connection pool for efficient reuse across threads.
    Provides helper methods to insert and query power readings.
    """

    def __init__(self,
                 host: Union[str, None] = None,
                 user: Union[str, None] = None,
                 password: Union[str, None] = None,
                 database: Union[str, None] = None,
                 pool_name: str = "flask_app_pool",
                 pool_size: int = 5):
        self.db_config = {
            "host": host or os.environ.get("MYSQL_HOST", "mysql"),
            "user": user or os.environ.get("MYSQL_USER", "power_user"),
            "password": password or os.environ.get("MYSQL_PASSWORD", "password"),
            "database": database or os.environ.get("MYSQL_DATABASE", "power_measurement"),
            "auth_plugin": os.environ.get("MYSQL_AUTH_PLUGIN", "mysql_native_password"),
        }

        try:
            self.cnx_pool = pooling.MySQLConnectionPool(
                pool_name=pool_name,
                pool_size=pool_size,
                pool_reset_session=True,
                **self.db_config,
            )
            logging.info("MySQL connection pool created.")
        except mysql.connector.Error as err:
            logging.critical(f"Error creating connection pool: {err}", exc_info=True)
            raise

    # Context manager for getting a connection
    def _get_connection(self):
        return self.cnx_pool.get_connection()

    # --- CRUD Methods -----------------------------------------------------
    def insert_reading(
        self,
        device_code: str,
        timestamp: Union[str, datetime.datetime],
        temperature: Union[float, None] = None,
        humidity: Union[float, None] = None,
        brightness: Union[int, None] = None,
        electric: Union[float, None] = None,
    ) -> None:
        """Insert a power reading row into the database."""
        if isinstance(timestamp, str):
            # Handle ISO format with 'Z' suffix (UTC timezone)
            if timestamp.endswith('Z'):
                timestamp = timestamp[:-1] + '+00:00'
            timestamp = datetime.datetime.fromisoformat(timestamp)

        query = (
            "INSERT INTO power_readings (timestamp, device_code, temperature, humidity, brightness, electric) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        params = (timestamp, device_code, temperature, humidity, brightness, electric)

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    conn.commit()
        except mysql.connector.Error as err:
            logging.error(f"Error inserting reading: {err}", exc_info=True)
            raise

    def fetch_power_data(self, limit: int = 100):
        """Fetch recent power data."""
        query = (
            "SELECT id, timestamp, device_code, temperature, humidity, brightness, electric "
            "FROM power_readings ORDER BY timestamp DESC LIMIT %s"
        )
        try:
            with self._get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query, (limit,))
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logging.error(f"Error fetching data: {err}", exc_info=True)
            return []

    # Convenience function for migrations/checks
    def ping(self):
        try:
            with self._get_connection() as conn:
                conn.cmd_ping()
            return True
        except mysql.connector.Error:
            return False

    def create_esg_report(self):
        """Generate dummy ESG report entry and return id, url."""
        query = (
            "INSERT INTO esg_reports (file_path, created_at) VALUES (%s, NOW())"
        )
        file_path = f"/reports/esg_report_{int(datetime.datetime.utcnow().timestamp())}.csv"
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (file_path,))
                    conn.commit()
                    report_id = cursor.lastrowid
                    return report_id, file_path
        except mysql.connector.Error as err:
            logging.error(f"Error inserting esg report: {err}", exc_info=True)
            raise

    def fetch_esg_reports(self):
        """Fetch list of ESG reports."""
        query = "SELECT id, file_path AS url, created_at FROM esg_reports ORDER BY created_at DESC"
        try:
            with self._get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()
        except mysql.connector.Error as err:
            logging.error(f"Error fetching esg reports: {err}", exc_info=True)
            return []

    def get_summary_data(self, time_range: str = '24h'):
        """
        Fetch summary statistics for the given time range.
        
        Args:
            time_range: '1h', '6h', '24h', '7d', '30d'
        
        Returns:
            dict with aggregated data (avg, min, max, total readings)
        """
        # 시간 범위에 따른 INTERVAL 설정
        interval_map = {
            '1h': 'INTERVAL 1 HOUR',
            '6h': 'INTERVAL 6 HOUR',
            '24h': 'INTERVAL 24 HOUR',
            '7d': 'INTERVAL 7 DAY',
            '30d': 'INTERVAL 30 DAY'
        }
        
        interval = interval_map.get(time_range, 'INTERVAL 24 HOUR')
        
        query = f"""
        SELECT 
            COUNT(*) as total_readings,
            AVG(temperature) as avg_temperature,
            MIN(temperature) as min_temperature,
            MAX(temperature) as max_temperature,
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
            MIN(timestamp) as period_start,
            MAX(timestamp) as period_end
        FROM power_readings 
        WHERE timestamp >= NOW() - {interval}
        """
        
        try:
            with self._get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    result = cursor.fetchone()
                    
                    if result and result['total_readings'] > 0:
                        return {
                            'time_range': time_range,
                            'total_readings': result['total_readings'],
                            'period_start': result['period_start'],
                            'period_end': result['period_end'],
                            'temperature': {
                                'avg': float(result['avg_temperature']) if result['avg_temperature'] else 0,
                                'min': float(result['min_temperature']) if result['min_temperature'] else 0,
                                'max': float(result['max_temperature']) if result['max_temperature'] else 0,
                                'unit': '°C'
                            },
                            'humidity': {
                                'avg': float(result['avg_humidity']) if result['avg_humidity'] else 0,
                                'min': float(result['min_humidity']) if result['min_humidity'] else 0,
                                'max': float(result['max_humidity']) if result['max_humidity'] else 0,
                                'unit': '%'
                            },
                            'brightness': {
                                'avg': float(result['avg_brightness']) if result['avg_brightness'] else 0,
                                'min': float(result['min_brightness']) if result['min_brightness'] else 0,
                                'max': float(result['max_brightness']) if result['max_brightness'] else 0,
                                'unit': 'lx'
                            },
                            'electric': {
                                'avg': float(result['avg_electric']) if result['avg_electric'] else 0,
                                'min': float(result['min_electric']) if result['min_electric'] else 0,
                                'max': float(result['max_electric']) if result['max_electric'] else 0,
                                'total': float(result['total_electric']) if result['total_electric'] else 0,
                                'unit': 'mA'
                            }
                        }
                    else:
                        return {
                            'time_range': time_range,
                            'total_readings': 0,
                            'message': '해당 기간에 데이터가 없습니다.',
                            'period_start': None,
                            'period_end': None
                        }
                        
        except mysql.connector.Error as err:
            logging.error(f"Error fetching summary data: {err}", exc_info=True)
            return {
                'time_range': time_range,
                'error': f'데이터 조회 중 오류가 발생했습니다: {str(err)}'
            }

    def get_hourly_trend(self, time_range: str = '24h'):
        """
        Fetch hourly aggregated data for trend analysis.
        
        Args:
            time_range: '24h', '7d', '30d'
        
        Returns:
            list of hourly aggregated readings
        """
        interval_map = {
            '24h': 'INTERVAL 24 HOUR',
            '7d': 'INTERVAL 7 DAY', 
            '30d': 'INTERVAL 30 DAY'
        }
        
        interval = interval_map.get(time_range, 'INTERVAL 24 HOUR')
        
        query = f"""
        SELECT 
            DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') as hour_start,
            COUNT(*) as readings_count,
            AVG(temperature) as avg_temperature,
            AVG(humidity) as avg_humidity,
            AVG(brightness) as avg_brightness,
            AVG(electric) as avg_electric,
            SUM(electric) as total_electric
        FROM power_readings 
        WHERE timestamp >= NOW() - {interval}
        GROUP BY DATE_FORMAT(timestamp, '%Y-%m-%d %H')
        ORDER BY hour_start ASC
        """
        
        try:
            with self._get_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    
                    # 데이터 형식 정리
                    formatted_results = []
                    for row in results:
                        formatted_results.append({
                            'timestamp': row['hour_start'],
                            'readings_count': row['readings_count'],
                            'temperature': float(row['avg_temperature']) if row['avg_temperature'] else 0,
                            'humidity': float(row['avg_humidity']) if row['avg_humidity'] else 0,
                            'brightness': float(row['avg_brightness']) if row['avg_brightness'] else 0,
                            'electric_avg': float(row['avg_electric']) if row['avg_electric'] else 0,
                            'electric_total': float(row['total_electric']) if row['total_electric'] else 0
                        })
                    
                    return formatted_results
                    
        except mysql.connector.Error as err:
            logging.error(f"Error fetching hourly trend: {err}", exc_info=True)
            return []
