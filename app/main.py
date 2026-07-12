"""
M Agent Hackathon Demo: Flask Backend
=====================================
3 endpoints for judges to interact with M Agent moat

POST /api/v1/assess - Wei Chen grounding query
POST /api/v1/integrity-check - Marcus Lee fraud detection
GET /api/v1/logs - Governance audit trail

All patent gates (C-01–C-06) execute on every call.
Mock responses (no real Claude API).
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from datetime import datetime
import os
import json

from app.models import wei_chen, marcus_lee
from app.services.m_agent_service import MAgentService

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Enable CORS
CORS(app, origins="*")

# Initialize M Agent service
agent_service = MAgentService()

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def root():
    """Serve frontend HTML"""
    return send_from_directory('../frontend', 'index.html')


@app.route('/api/v1/assess', methods=['POST'])
def assess_candidate():
    """
    Assess a candidate for capability vs traditional scores

    Wei Chen (wei-chen-001):
    - Traditional score: 50
    - Capability score: 87 (driven by embodied evidence)
    - All 6 gates PASS
    """
    try:
        candidate_id = request.args.get('candidate_id', 'wei-chen-001')
        result = agent_service.assess(candidate_id)
        return jsonify(result.__dict__ if hasattr(result, '__dict__') else result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Assessment failed: {str(e)}"}), 500


@app.route('/api/v1/integrity-check', methods=['POST'])
def integrity_check():
    """
    Check candidate for red flags / fraud indicators

    Marcus Lee (marcus-lee-001):
    - Timeline overlap (CTO + VP Eng simultaneously)
    - Unsubstantiated claims (5 patents, 0 evidence)
    - Gates C-02, C-04 FAIL → Findings BLOCKED
    """
    try:
        candidate_id = request.args.get('candidate_id', 'marcus-lee-001')
        result = agent_service.integrity_check(candidate_id)
        return jsonify(result.__dict__ if hasattr(result, '__dict__') else result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"Integrity check failed: {str(e)}"}), 500


@app.route('/api/v1/logs', methods=['GET'])
def get_governance_logs():
    """
    Retrieve governance audit trail

    Shows all operations, gates executed, findings, decisions.
    Judges use this to verify M Agent's decision logic.
    """
    try:
        logs = agent_service.get_logs()
        return jsonify(logs.__dict__ if hasattr(logs, '__dict__') else logs)
    except Exception as e:
        return jsonify({"error": f"Log retrieval failed: {str(e)}"}), 500


@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "M Agent Demo",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/api/v1/candidates', methods=['GET'])
def list_candidates():
    """List available test candidates"""
    return jsonify({
        "candidates": [
            {
                "id": wei_chen.id,
                "name": wei_chen.name,
                "profile_type": "clean",
                "description": "All gates pass; capability score significantly exceeds traditional score"
            },
            {
                "id": marcus_lee.id,
                "name": marcus_lee.name,
                "profile_type": "fraud",
                "description": "Multiple red flags; integrity gates fail; findings blocked"
            }
        ]
    })


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "status": "error",
        "message": "Not found",
        "timestamp": datetime.utcnow().isoformat()
    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "status": "error",
        "message": "Server error",
        "timestamp": datetime.utcnow().isoformat()
    }), 500


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.before_request
def before_request():
    """Initialize on first request"""
    pass


@app.teardown_appcontext
def teardown_db(exception):
    """Cleanup on shutdown"""
    pass


# ============================================================================
# RUN LOCALLY: python -m flask --app app.main run
# ============================================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
