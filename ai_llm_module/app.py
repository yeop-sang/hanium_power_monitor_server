from flask import Flask, jsonify, request
from datetime import datetime
import os
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global variables for components - will be initialized safely
db = None
claude_api = None
carbon_calculator = None

def initialize_components():
    """Initialize components with proper error handling"""
    global db, claude_api, carbon_calculator
    
    try:
        # Initialize Database
        try:
            from modules.database import Database
            db = Database()
            logger.info("Database component initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Database: {e}")
            db = None
        
        # Initialize Claude API
        try:
            from modules.claude_api import ClaudeAPI
            claude_api = ClaudeAPI()
            logger.info("Claude API component initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Claude API: {e}")
            claude_api = None
        
        # Initialize Carbon Calculator  
        try:
            from modules.carbon_calculator import CarbonCalculator
            carbon_calculator = CarbonCalculator()
            logger.info("Carbon Calculator component initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Carbon Calculator: {e}")
            carbon_calculator = None
            
        logger.info("Component initialization completed")
        
    except Exception as e:
        logger.error(f"Critical error during component initialization: {e}")
        logger.error(traceback.format_exc())

# Initialize components
initialize_components()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with component status"""
    try:
        status = {
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'database': db is not None,
                'claude_api': claude_api is not None and claude_api.client is not None,
                'carbon_calculator': carbon_calculator is not None
            },
            'environment': {
                'has_anthropic_key': bool(os.environ.get('ANTHROPIC_API_KEY')),
                'mysql_host': os.environ.get('MYSQL_HOST', 'not_set')
            }
        }
        
        # Overall health based on critical components
        critical_components = ['database', 'carbon_calculator']
        healthy = all(status['components'][comp] for comp in critical_components)
        
        status['overall_health'] = 'healthy' if healthy else 'degraded'
        
        http_status = 200 if healthy else 503
        return jsonify(status), http_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """Generate ESG report with optional test mode to save API tokens"""
    try:
        data = request.get_json()
        months = data.get('months', 3)
        report_type = data.get('report_type', 'comprehensive')
        test_mode = data.get('test_mode', False)  # Add test mode flag
        
        if not db:
            return jsonify({
                'error': 'Database not available',
                'details': 'Database component failed to initialize'
            }), 503
            
        if not claude_api and not test_mode:
            return jsonify({
                'error': 'Claude API not available',
                'details': 'Claude API component failed to initialize'
            }), 503
            
        # Get data from database
        daily_data = db.get_daily_summaries(months)
        monthly_data = db.get_monthly_summaries(months)
        
        if carbon_calculator:
            carbon_data = carbon_calculator.calculate_daily_emissions(daily_data)
        else:
            return jsonify({
                'error': 'Carbon calculator not available',
                'details': 'Carbon calculator component failed to initialize'
            }), 503
        
        # Test mode: return mock response without calling Claude API
        if test_mode:
            mock_report = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'model_used': 'test-mode',
                    'usage': {'input_tokens': 0, 'output_tokens': 0},
                    'data_period': {
                        'months': months,
                        'daily_records': len(daily_data) if daily_data is not None else 0,
                        'monthly_records': len(monthly_data) if monthly_data is not None else 0
                    }
                },
                'input_data': {
                    'daily_summary': daily_data.to_dict('records') if daily_data is not None else [],
                    'monthly_summary': monthly_data.to_dict('records') if monthly_data is not None else [],
                    'carbon_data': carbon_data.to_dict('records') if carbon_data is not None else []
                },
                'raw_esg_report': 'TEST MODE: ESG report generation successful. Database queries completed without errors. Claude API integration ready.',
                'report_metrics': {
                    'character_count': 123,
                    'word_count': 20,
                    'estimated_reading_time_minutes': 0.1
                }
            }
            
            return jsonify({
                'status': 'success',
                'report': mock_report,
                'message': 'Report generated in test mode (no API tokens used)'
            }), 200
        
        # Production mode: call Claude API
        report_data = claude_api._prepare_report_data(daily_data, carbon_data, monthly_data)
        esg_report = claude_api.generate_esg_report(daily_data, carbon_data, monthly_data)
        
        return jsonify({
            'status': 'success',
            'report': esg_report
        }), 200
        
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