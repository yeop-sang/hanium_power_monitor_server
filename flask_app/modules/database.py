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
        device_code: int,
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
