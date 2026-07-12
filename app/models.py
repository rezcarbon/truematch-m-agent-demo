"""
M Agent Demo: Test Data Models
================================
Two test candidates that showcase M Agent capabilities:

1. Wei Chen (clean): All gates pass, high capability + embodied evidence
2. Marcus Lee (fraud): Red flags, gates fail, findings blocked

These are in-memory dataclasses (no database needed).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class Resume:
    """Resume/candidate profile"""
    claims: List[str]
    github: Optional[str] = None
    github_stats: Optional[Dict[str, Any]] = None
    certifications: List[str] = field(default_factory=list)
    publications: List[Dict[str, str]] = field(default_factory=list)
    work_history: List[Dict[str, str]] = field(default_factory=list)
    patents: Optional[List[Dict[str, str]]] = None


@dataclass
class Candidate:
    """Candidate profile"""
    id: str
    name: str
    resume: Resume
    
    def __repr__(self):
        return f"Candidate(id={self.id}, name={self.name})"


# ============================================================================
# WEI CHEN - CLEAN CANDIDATE (All gates PASS)
# ============================================================================

wei_chen = Candidate(
    id="wei-chen-001",
    name="Wei Chen",
    resume=Resume(
        claims=[
            "Python expert (10+ years)",
            "ML/AI architecture specialist",
            "Data engineering team lead",
            "Published 2 papers in top-tier venues",
            "AWS ML Specialist certified",
            "TensorFlow Advanced certified"
        ],
        github="github.com/weichen-ml",
        github_stats={
            "repositories": 3,
            "total_commits": 847,
            "followers": 312,
            "popular_projects": [
                "ml-pipeline-optimizer (847 stars)",
                "data-validation-framework (342 stars)",
                "tensorflow-extensions (156 stars)"
            ],
            "contribution_quality": "expert"
        },
        certifications=[
            "AWS ML Specialty (2023)",
            "TensorFlow Advanced Certification (2022)"
        ],
        publications=[
            {
                "title": "Scalable Feature Engineering for ML Systems",
                "venue": "NeurIPS 2024",
                "doi": "10.48550/arXiv.2406.12847",
                "citations": 23
            },
            {
                "title": "Temporal Consistency in Distributed Training",
                "venue": "ICML 2023",
                "doi": "10.48550/arXiv.2307.08219",
                "citations": 14
            }
        ],
        work_history=[
            {
                "title": "ML Engineer",
                "company": "TechCorp",
                "start_date": "2014-01-15",
                "end_date": "2019-12-31",
                "duration_years": 6
            },
            {
                "title": "Senior ML Architect",
                "company": "AI Systems Inc",
                "start_date": "2020-02-01",
                "end_date": "2026-06-30",
                "duration_years": 6
            }
        ]
    )
)


# ============================================================================
# MARCUS LEE - FRAUD CANDIDATE (Gates FAIL, Findings BLOCKED)
# ============================================================================

marcus_lee = Candidate(
    id="marcus-lee-001",
    name="Marcus Lee",
    resume=Resume(
        claims=[
            "CTO at TechCorp (2020-2023)",
            "VP Engineering at StartupXYZ (2022-2024)",  # OVERLAP!
            "5 patents filed",  # NO EVIDENCE
            "AWS Solutions Architect",
            "Deep expertise in cloud architecture"
        ],
        github=None,  # No GitHub
        certifications=[
            "AWS Solutions Architect (unverified)"
        ],
        publications=[],  # No publications
        patents=[
            # Claims 5 patents but no USPTO/DOI links
            "Patent claim 1",
            "Patent claim 2",
            "Patent claim 3",
            "Patent claim 4",
            "Patent claim 5"
        ],
        work_history=[
            {
                "title": "CTO",
                "company": "TechCorp",
                "start_date": "2020-01-15",
                "end_date": "2023-12-31",
                "duration_years": 4
            },
            {
                "title": "VP Engineering",
                "company": "StartupXYZ",
                "start_date": "2022-06-01",  # OVERLAPS with CTO role!
                "end_date": "2024-12-31",
                "duration_years": 2.5
            }
        ]
    )
)


# ============================================================================
# EXPECTED OUTPUTS (For testing + debugging)
# ============================================================================

WEI_CHEN_EXPECTED = {
    "profile_type": "clean",
    "traditional_score": 50,
    "capability_score": 87,
    "confidence": 0.92,
    "confidence_tier": "Tier 1 (Expert)",
    "gates_passed": 6,
    "gates_failed": 0,
    "gates_blocked": 0,
    "gate_status": {
        "C-01": "PASS",  # Coherence: scores align
        "C-02": "PASS",  # Temporal: timeline valid
        "C-03": "PASS",  # Lipschitz: confidence bounded correctly
        "C-04": "PASS",  # Physiological: embodied evidence validates claims
        "C-05": "PASS",  # Pre-Linguistic: logic separable
        "C-06": "PASS"   # Orchestrator: non-bypassable, all gates passed
    },
    "key_finding": "Large score delta justified by high embodied evidence density (GitHub + DOI papers). Traditional assessment underweights evidence-based capability.",
    "recommendation": "Trust capability score; Wei Chen demonstrates expert-level evidence-based expertise"
}

MARCUS_LEE_EXPECTED = {
    "profile_type": "fraud",
    "status": "RED_FLAGS_DETECTED",
    "confidence": 0.15,
    "confidence_tier": "Tier 3 (Low Evidence)",
    "gates_passed": 0,
    "gates_failed": 2,
    "gates_blocked": 4,  # C-06 orchestrator blocks findings
    "gate_status": {
        "C-01": "BLOCKED",   # Cannot cohere; C-02/C-04 failed
        "C-02": "FAIL",      # Timeline overlap: CTO + VP simultaneously
        "C-03": "CAPPED",    # Patent claims capped at 0.15 (no evidence)
        "C-04": "FAIL",      # No embodied evidence for 5 patent claims
        "C-05": "FAIL",      # Logic not separable; claims unsupported
        "C-06": "BLOCKED"    # Findings blocked by orchestrator due to failed gates
    },
    "red_flags": [
        {
            "type": "timeline_overlap",
            "severity": "HIGH",
            "evidence": "CTO at TechCorp (2020-2023) overlaps with VP Eng at StartupXYZ (2022-2024) for 12 months",
            "gate_failed": "C-02",
            "action": "REQUEST_CLARIFICATION"
        },
        {
            "type": "unsubstantiated_claims",
            "severity": "HIGH",
            "evidence": "Claims 5 patents but zero embodied evidence (no USPTO, DOI, or GitHub links)",
            "gate_failed": "C-04",
            "action": "REQUEST_EVIDENCE"
        }
    ],
    "recommendation": "Request clarification of timeline and patent evidence before proceeding. Findings blocked by integrity gates."
}


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

def validate_candidate(candidate: Candidate) -> bool:
    """Basic validation of candidate data"""
    if not candidate.id or not candidate.name:
        return False
    if not candidate.resume.claims:
        return False
    return True


def get_candidate_by_id(candidate_id: str) -> Optional[Candidate]:
    """Fetch candidate by ID"""
    candidates = {
        "wei-chen-001": wei_chen,
        "marcus-lee-001": marcus_lee
    }
    return candidates.get(candidate_id)


def list_all_candidates() -> List[Candidate]:
    """List all test candidates"""
    return [wei_chen, marcus_lee]
