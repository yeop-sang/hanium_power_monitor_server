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
        """Placeholder for daily/weekly summary endpoint."""
        # TODO: Implement summary logic (e.g., daily average, min/max)
        return jsonify({"message": "Summary endpoint not yet implemented."}), 501

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
