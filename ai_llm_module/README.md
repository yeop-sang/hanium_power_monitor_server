# AI/LLM Module for ESG Report Generation

## Overview
This module provides AI-powered ESG (Environmental, Social, Governance) report generation capabilities for the power monitoring system. It integrates with Claude API to analyze power consumption data and generate comprehensive environmental impact reports.

## Features
- **Data Analysis**: Processes power consumption and environmental sensor data
- **Carbon Calculation**: Computes carbon emissions based on electricity usage
- **AI Report Generation**: Uses Claude API to generate detailed ESG reports
- **RESTful API**: Provides endpoints for report generation requests

## Module Structure
```
ai_llm_module/
├── Dockerfile                 # Container configuration
├── requirements.txt           # Python dependencies
├── app.py                    # Main Flask application
├── README.md                 # This file
└── modules/
    ├── __init__.py           # Package initialization
    ├── database.py           # Database connection and queries
    ├── claude_api.py         # Claude API integration
    └── carbon_calculator.py  # Carbon emission calculations
```

## Dependencies
- Python 3.9+
- MySQL database
- Claude API key (Anthropic)
- Docker (for containerized deployment)

## Environment Variables
- `MYSQL_HOST`: MySQL server hostname
- `MYSQL_USER`: Database username
- `MYSQL_PASSWORD`: Database password
- `MYSQL_DATABASE`: Database name
- `ANTHROPIC_API_KEY`: Claude API key

## API Endpoints
- `POST /generate_report`: Generate ESG report based on recent power data

## High-Level Goals
1. Provide automated ESG reporting capabilities
2. Analyze environmental impact of power consumption
3. Generate actionable insights for sustainability improvements
4. Integrate seamlessly with the existing power monitoring infrastructure 