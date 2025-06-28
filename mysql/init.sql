CREATE DATABASE IF NOT EXISTS power_measurement;
USE power_measurement;

CREATE TABLE IF NOT EXISTS power_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    device_code INT NOT NULL,
    temperature FLOAT COMMENT 'Celsius',
    humidity FLOAT COMMENT 'Percentage',
    brightness INT COMMENT 'Numeric value',
    electric FLOAT COMMENT 'mA',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_timestamp (timestamp),
    INDEX idx_device_code (device_code)
);

CREATE TABLE IF NOT EXISTS esg_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_path VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL
);

-- Create user with appropriate permissions
-- Note: The user and password should be managed via environment variables in docker-compose,
-- but we ensure the user has the right grants here.
GRANT ALL PRIVILEGES ON power_measurement.* TO '${MYSQL_USER}'@'%';
FLUSH PRIVILEGES;
