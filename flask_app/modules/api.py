from flask import Blueprint, jsonify, request
from decimal import Decimal
import datetime

# Helper to serialize Decimal and Datetime objects
def json_serializer(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    # Let jsonify handle other basic types like int, str, float, bool
    if isinstance(obj, (int, float, str, type(None))):
        return obj
    raise TypeError(f"Type {type(obj)} not serializable")

def setup_routes(db):
    """Creates and configures the Flask Blueprint for the API."""
    # Flask Blueprint를 생성합니다. 
    # 'api'라는 이름으로 Blueprint를 만들고 모든 라우트에 '/api' 접두사를 추가합니다.
    # 예: '/api/power_data', '/api/summary' 등의 엔드포인트가 생성됩니다.
    api_blueprint = Blueprint('api', __name__, url_prefix='/api')

    @api_blueprint.route('/power_data', methods=['GET'])
    def get_power_data():
        """
        Fetches power data from the database.
        Accepts a 'limit' query parameter.
        """
        try:
            limit = int(request.args.get('limit', 100))
            if limit <= 0 or limit > 1000:
                limit = 100
        except (ValueError, TypeError):
            limit = 100

        data = db.fetch_power_data(limit=limit)
        
        # Manually serialize to handle Decimal and Datetime
        serialized_data = []
        for row in data:
            serialized_row = {k: json_serializer(v) for k, v in row.items()}
            serialized_data.append(serialized_row)

        return jsonify(serialized_data)

    @api_blueprint.route('/summary', methods=['GET'])
    def get_summary():
        """Get summary statistics for the specified time range."""
        time_range = request.args.get('timeRange', '24h')
        
        # 유효한 시간 범위인지 확인
        valid_ranges = ['1h', '6h', '24h', '7d', '30d']
        if time_range not in valid_ranges:
            return jsonify({
                "error": "Invalid time range", 
                "valid_ranges": valid_ranges
            }), 400
        
        try:
            if not db:
                return jsonify({"error": "Database not available"}), 500
                
            summary_data = db.get_summary_data(time_range)
            
            # 데이터 직렬화 (이미 database.py에서 처리했지만 안전을 위해)
            serialized_data = {k: json_serializer(v) for k, v in summary_data.items()}
            
            return jsonify(serialized_data)
            
        except Exception as e:
            return jsonify({
                "error": "Failed to fetch summary data",
                "details": str(e)
            }), 500

    @api_blueprint.route('/trend', methods=['GET'])
    def get_trend():
        """Get hourly trend data for the specified time range."""
        time_range = request.args.get('timeRange', '24h')
        
        # 유효한 시간 범위인지 확인
        valid_ranges = ['24h', '7d', '30d']
        if time_range not in valid_ranges:
            return jsonify({
                "error": "Invalid time range for trend data", 
                "valid_ranges": valid_ranges
            }), 400
        
        try:
            if not db:
                return jsonify({"error": "Database not available"}), 500
                
            trend_data = db.get_hourly_trend(time_range)
            
            # 데이터 직렬화
            serialized_data = []
            for row in trend_data:
                serialized_row = {k: json_serializer(v) for k, v in row.items()}
                serialized_data.append(serialized_row)
            
            return jsonify({
                "time_range": time_range,
                "data": serialized_data,
                "total_hours": len(serialized_data)
            })
            
        except Exception as e:
            return jsonify({
                "error": "Failed to fetch trend data",
                "details": str(e)
            }), 500

    @api_blueprint.route('/esg_reports', methods=['GET'])
    def list_esg_reports():
        """Returns list of available ESG reports."""
        data = db.fetch_esg_reports() if db else []
        serialized = [{k: json_serializer(v) for k, v in row.items()} for row in data]
        return jsonify(serialized)

    @api_blueprint.route('/generate_esg_report', methods=['POST'])
    def generate_esg():
        """Generates a dummy ESG report and returns its info."""
        if not db:
            return jsonify({"message": "Database not available"}), 500
        report_id, url = db.create_esg_report()
        return jsonify({"id": report_id, "url": url}), 201

    return api_blueprint
