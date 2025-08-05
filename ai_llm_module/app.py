from flask import Flask, jsonify, request
from datetime import datetime
import os
import logging
import traceback
from modules.database import Database
from modules.claude_api import ClaudeAPI
from modules.carbon_calculator import CarbonCalculator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize components
try:
    # Database connection
    db = Database()
    
    # Claude API client
    claude_api = ClaudeAPI()
    
    # Carbon calculator
    carbon_calculator = CarbonCalculator()
    
    logger.info("AI/LLM module initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize components: {e}")
    raise

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        db_status = db.test_connection()
        
        # Test Claude API connection
        claude_status = claude_api.test_api_connection()
        
        status = {
            'status': 'healthy' if db_status and claude_status else 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'database': 'connected' if db_status else 'disconnected',
                'claude_api': 'connected' if claude_status else 'disconnected',
                'carbon_calculator': 'initialized'
            },
            'version': '1.0.0'
        }
        
        return jsonify(status), 200 if status['status'] == 'healthy' else 503
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/generate_report', methods=['POST'])
def generate_esg_report():
    """Generate comprehensive ESG report based on power consumption data."""
    try:
        # Get request parameters
        data = request.get_json() or {}
        months = data.get('months', 3)
        report_type = data.get('type', 'full')  # 'full' or 'summary'
        
        logger.info(f"Generating ESG report: type={report_type}, months={months}")
        
        # Step 1: Retrieve data from database
        daily_data = db.get_daily_summaries(months=months)
        monthly_data = db.get_monthly_summaries(months=months)
        
        if daily_data.empty:
            return jsonify({
                'error': 'No data available for the specified period',
                'months_requested': months,
                'timestamp': datetime.now().isoformat()
            }), 404
        
        # Step 2: Calculate carbon emissions
        carbon_data = carbon_calculator.calculate_daily_emissions(daily_data)
        monthly_carbon_data = carbon_calculator.calculate_monthly_emissions(monthly_data)
        
        # Step 3: Generate report using Claude API
        if report_type == 'summary':
            # Generate summary report
            data_summary = claude_api._prepare_report_data(daily_data, carbon_data, monthly_carbon_data)
            report = claude_api.generate_summary_report(data_summary)
        else:
            # Generate full ESG report
            report = claude_api.generate_esg_report(daily_data, carbon_data, monthly_carbon_data)
        
        # Step 4: Add metadata and statistics
        report['request_info'] = {
            'months_analyzed': months,
            'report_type': report_type,
            'data_points': len(daily_data),
            'generated_at': datetime.now().isoformat()
        }
        
        # Calculate carbon trends
        carbon_trends = carbon_calculator.calculate_carbon_trends(carbon_data, 'daily')
        report['carbon_trends'] = carbon_trends
        
        logger.info(f"ESG report generated successfully: {len(daily_data)} days analyzed")
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"Error generating ESG report: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Failed to generate ESG report',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/data_summary', methods=['GET'])
def get_data_summary():
    """Get summary of available data for ESG analysis."""
    try:
        months = request.args.get('months', 3, type=int)
        
        # Get data summaries
        daily_data = db.get_daily_summaries(months=months)
        monthly_data = db.get_monthly_summaries(months=months)
        device_stats = db.get_device_statistics(months=months)
        
        # Calculate basic statistics
        if not daily_data.empty:
            carbon_data = carbon_calculator.calculate_daily_emissions(daily_data)
            carbon_trends = carbon_calculator.calculate_carbon_trends(carbon_data, 'daily')
        else:
            carbon_trends = {}
        
        summary = {
            'data_availability': {
                'daily_records': len(daily_data),
                'monthly_records': len(monthly_data),
                'devices_tracked': len(device_stats),
                'period_start': daily_data['date'].min().strftime('%Y-%m-%d') if not daily_data.empty else None,
                'period_end': daily_data['date'].max().strftime('%Y-%m-%d') if not daily_data.empty else None
            },
            'power_statistics': {
                'total_energy_kwh': float(daily_data['daily_energy_kwh'].sum()) if 'daily_energy_kwh' in daily_data.columns else 0,
                'avg_daily_kwh': float(daily_data['daily_energy_kwh'].mean()) if 'daily_energy_kwh' in daily_data.columns else 0,
                'peak_day': daily_data.loc[daily_data['daily_energy_kwh'].idxmax()].to_dict() if 'daily_energy_kwh' in daily_data.columns and not daily_data.empty else None
            },
            'carbon_summary': carbon_trends,
            'device_statistics': device_stats.to_dict('records') if not device_stats.empty else [],
            'environmental_averages': {
                'temperature': float(daily_data['avg_temp'].mean()) if 'avg_temp' in daily_data.columns else 0,
                'humidity': float(daily_data['avg_humidity'].mean()) if 'avg_humidity' in daily_data.columns else 0,
                'brightness': float(daily_data['avg_brightness'].mean()) if 'avg_brightness' in daily_data.columns else 0
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Error getting data summary: {e}")
        return jsonify({
            'error': 'Failed to get data summary',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/carbon_factors', methods=['GET'])
def get_carbon_factors():
    """Get available carbon emission factors."""
    try:
        factors_info = carbon_calculator.get_emission_factor_info()
        return jsonify(factors_info)
    except Exception as e:
        logger.error(f"Error getting carbon factors: {e}")
        return jsonify({
            'error': 'Failed to get carbon factors',
            'details': str(e)
        }), 500

@app.route('/test_components', methods=['GET'])
def test_all_components():
    """Test all module components."""
    try:
        results = {
            'database': {
                'status': 'connected' if db.test_connection() else 'disconnected',
                'test_query': False
            },
            'claude_api': {
                'status': 'connected' if claude_api.test_api_connection() else 'disconnected'
            },
            'carbon_calculator': {
                'status': 'initialized',
                'factor_info': carbon_calculator.get_emission_factor_info()
            }
        }
        
        # Test database query
        try:
            test_data = db.get_daily_summaries(months=1)
            results['database']['test_query'] = True
            results['database']['sample_records'] = len(test_data)
        except Exception as e:
            results['database']['test_query'] = False
            results['database']['query_error'] = str(e)
        
        overall_status = all([
            results['database']['status'] == 'connected',
            results['claude_api']['status'] == 'connected',
            results['carbon_calculator']['status'] == 'initialized'
        ])
        
        results['overall_status'] = 'all_systems_operational' if overall_status else 'some_issues_detected'
        results['timestamp'] = datetime.now().isoformat()
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Component test failed: {e}")
        return jsonify({
            'error': 'Component test failed',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            'GET /health',
            'POST /generate_report',
            'GET /data_summary',
            'GET /carbon_factors',
            'GET /test_components'
        ],
        'timestamp': datetime.now().isoformat()
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting AI/LLM module on port {port}, debug={debug}")
    app.run(host='0.0.0.0', port=port, debug=debug) 