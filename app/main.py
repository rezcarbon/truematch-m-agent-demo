"""
M Agent Hackathon Demo: FastAPI Backend
================================
3 endpoints for judges to interact with M Agent moat

POST /api/v1/assess - Wei Chen grounding query
POST /api/v1/integrity-check - Marcus Lee fraud detection  
GET /api/v1/logs - Governance audit trail

All patent gates (C-01–C-06) execute on every call.
Mock responses (no real Claude API).
"""

from fastapi import FastAPI, HTTPException, staticfiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import json

from app.models import wei_chen, marcus_lee
from app.services.m_agent_service import MAgentService

# Initialize FastAPI app
app = FastAPI(
    title="TrueMatch M Agent Demo",
    description="Recruiter expertise infrastructure for the AI era",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize M Agent service
agent_service = MAgentService()

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class PatentGateResult(BaseModel):
    gate_id: str  # C-01, C-02, etc.
    name: str
    status: str  # PASS, FAIL, BLOCKED
    reason: str
    timestamp: str


class AgenticIteration(BaseModel):
    iteration_num: int
    tool_name: str
    description: str
    result: str
    evidence_collected: Optional[Dict[str, Any]] = None


class AssessmentResponse(BaseModel):
    candidate_id: str
    candidate_name: str
    agentic_iterations: List[AgenticIteration]
    traditional_score: int
    capability_score: int
    confidence: float
    confidence_tier: str  # Tier 1, Tier 2, Tier 3
    gates_executed: List[PatentGateResult]
    gates_passed: int
    gates_failed: int
    recommendation: str
    operation_id: str
    timestamp: str


class IntegrityFinding(BaseModel):
    finding_id: str
    finding_type: str  # timeline_overlap, unsubstantiated_claims, etc.
    severity: str  # HIGH, MEDIUM, LOW
    evidence: str
    gate_failed: str  # Which gate triggered this
    recommendation: str


class IntegrityCheckResponse(BaseModel):
    candidate_id: str
    candidate_name: str
    status: str  # CLEAN, RED_FLAGS, BLOCKED
    agentic_iterations: List[AgenticIteration]
    findings: List[IntegrityFinding]
    gates_executed: List[PatentGateResult]
    gates_passed: int
    gates_failed: int
    overall_recommendation: str
    operation_id: str
    timestamp: str


class GovernanceLogEntry(BaseModel):
    timestamp: str
    operation_id: str
    candidate_id: str
    candidate_name: str
    operation_type: str  # assess, integrity_check
    gates_passed: int
    gates_failed: int
    recommendation: str
    findings: Optional[List[str]] = None


class GovernanceLogsResponse(BaseModel):
    total_entries: int
    logs: List[GovernanceLogEntry]


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/")
async def root():
    """Serve frontend HTML"""
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "M Agent Demo API. Visit /docs for API docs."}


@app.post("/api/v1/assess", response_model=AssessmentResponse)
async def assess_candidate(candidate_id: str = "wei-chen-001"):
    """
    Assess a candidate for capability vs traditional scores
    
    Wei Chen (wei-chen-001):
    - Traditional score: 50
    - Capability score: 87 (driven by embodied evidence)
    - All 6 gates PASS
    """
    try:
        result = agent_service.assess(candidate_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assessment failed: {str(e)}")


@app.post("/api/v1/integrity-check", response_model=IntegrityCheckResponse)
async def integrity_check(candidate_id: str = "marcus-lee-001"):
    """
    Check candidate for red flags / fraud indicators
    
    Marcus Lee (marcus-lee-001):
    - Timeline overlap (CTO + VP Eng simultaneously)
    - Unsubstantiated claims (5 patents, 0 evidence)
    - Gates C-02, C-04 FAIL → Findings BLOCKED
    """
    try:
        result = agent_service.integrity_check(candidate_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Integrity check failed: {str(e)}")


@app.get("/api/v1/logs", response_model=GovernanceLogsResponse)
async def get_governance_logs():
    """
    Retrieve governance audit trail
    
    Shows all operations, gates executed, findings, decisions.
    Judges use this to verify M Agent's decision logic.
    """
    try:
        logs = agent_service.get_logs()
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Log retrieval failed: {str(e)}")


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "M Agent Demo",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# STATIC FILE SERVING (Frontend)
# ============================================================================

@app.get("/api/v1/candidates")
async def list_candidates():
    """List available test candidates"""
    return {
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
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "status": "error",
        "message": exc.detail,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize on app startup"""
    print("M Agent Demo starting...")
    print(f"Test candidates loaded:")
    print(f"  - Wei Chen (clean, all gates pass)")
    print(f"  - Marcus Lee (fraud, gates fail)")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown"""
    print("M Agent Demo shutting down...")


# ============================================================================
# RUN LOCALLY: uvicorn app.main:app --reload
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
