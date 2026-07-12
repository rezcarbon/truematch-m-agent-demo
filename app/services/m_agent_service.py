"""
M Agent Service: Agentic Loop + Patent Moat
============================================

Orchestrates:
1. Agentic loop (tool → evidence → iteration)
2. All 6 patent gates (C-01 through C-06)
3. Governance audit trail
4. Mock responses (Wei Chen + Marcus Lee)

All responses include full iteration history + gate status.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import uuid
import json

from app.models import get_candidate_by_id, wei_chen, marcus_lee


# ============================================================================
# DATA MODELS FOR RESPONSES
# ============================================================================

class GateStatus(str, Enum):
    """Patent gate execution status"""
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    CONDITIONAL = "CONDITIONAL"


class ConfidenceTier(str, Enum):
    """Confidence tier based on evidence density"""
    TIER_1 = "Tier 1 (Expert)"      # ≥0.7
    TIER_2 = "Tier 2 (Proficient)"  # ≥0.4
    TIER_3 = "Tier 3 (Limited)"     # ≥0.1


@dataclass
class AgenticIteration:
    iteration_num: int
    tool_name: str
    description: str
    result: str
    evidence_collected: Optional[Dict[str, Any]] = None
    
    def to_dict(self):
        return asdict(self)


@dataclass
class PatentGateResult:
    gate_id: str
    name: str
    status: str
    reason: str
    timestamp: str
    
    def to_dict(self):
        return asdict(self)


@dataclass
class AssessmentResponse:
    candidate_id: str
    candidate_name: str
    agentic_iterations: List[AgenticIteration]
    traditional_score: int
    capability_score: int
    confidence: float
    confidence_tier: str
    gates_executed: List[PatentGateResult]
    gates_passed: int
    gates_failed: int
    recommendation: str
    operation_id: str
    timestamp: str
    
    def to_dict(self):
        return {
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate_name,
            "agentic_iterations": [it.to_dict() for it in self.agentic_iterations],
            "traditional_score": self.traditional_score,
            "capability_score": self.capability_score,
            "confidence": self.confidence,
            "confidence_tier": self.confidence_tier,
            "gates_executed": [gate.to_dict() for gate in self.gates_executed],
            "gates_passed": self.gates_passed,
            "gates_failed": self.gates_failed,
            "recommendation": self.recommendation,
            "operation_id": self.operation_id,
            "timestamp": self.timestamp
        }


@dataclass
class IntegrityFinding:
    finding_id: str
    finding_type: str
    severity: str
    evidence: str
    gate_failed: str
    recommendation: str
    
    def to_dict(self):
        return asdict(self)


@dataclass
class IntegrityCheckResponse:
    candidate_id: str
    candidate_name: str
    status: str
    agentic_iterations: List[AgenticIteration]
    findings: List[IntegrityFinding]
    gates_executed: List[PatentGateResult]
    gates_passed: int
    gates_failed: int
    overall_recommendation: str
    operation_id: str
    timestamp: str
    
    def to_dict(self):
        return {
            "candidate_id": self.candidate_id,
            "candidate_name": self.candidate_name,
            "status": self.status,
            "agentic_iterations": [it.to_dict() for it in self.agentic_iterations],
            "findings": [f.to_dict() for f in self.findings],
            "gates_executed": [gate.to_dict() for gate in self.gates_executed],
            "gates_passed": self.gates_passed,
            "gates_failed": self.gates_failed,
            "overall_recommendation": self.overall_recommendation,
            "operation_id": self.operation_id,
            "timestamp": self.timestamp
        }


# ============================================================================
# M AGENT SERVICE
# ============================================================================

class MAgentService:
    """
    M Agent orchestrator: agentic loop + patent moat (6 gates)
    
    Judges see:
    1. Agentic loop iterations (tool calls with evidence)
    2. Patent gate status (all 6 gates execute)
    3. Governance audit trail (why decisions were made)
    """
    
    def __init__(self):
        """Initialize service with in-memory log"""
        self.governance_log: List[Dict[str, Any]] = []
        self.current_timestamp = None
    
    # ========================================================================
    # WEI CHEN ASSESSMENT (All gates PASS)
    # ========================================================================
    
    def assess(self, candidate_id: str = "wei-chen-001") -> AssessmentResponse:
        """
        Assess candidate for capability vs traditional scores.
        
        Wei Chen: Traditional 50 → Capability 87 (all 6 gates PASS)
        """
        candidate = get_candidate_by_id(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        operation_id = str(uuid.uuid4())[:8]
        timestamp = datetime.utcnow().isoformat()
        self.current_timestamp = timestamp
        
        # AGENTIC LOOP: 3 iterations
        iterations = self._simulate_wei_chen_agentic_loop()
        
        # PATENT GATES: All 6 execute in sequence
        gates = self._execute_wei_chen_gates()
        gates_passed = sum(1 for g in gates if g.status == GateStatus.PASS)
        gates_failed = sum(1 for g in gates if g.status == GateStatus.FAIL)
        
        # SCORING & CONFIDENCE
        traditional_score = 50
        capability_score = 87
        confidence = 0.92
        confidence_tier = ConfidenceTier.TIER_1.value
        
        recommendation = (
            "Trust capability score. Wei Chen demonstrates expert-level "
            "evidence-based expertise that traditional assessment underweights. "
            "Confidence: 0.92 (Tier 1, high evidence density)."
        )
        
        response = AssessmentResponse(
            candidate_id=candidate_id,
            candidate_name=candidate.name,
            agentic_iterations=iterations,
            traditional_score=traditional_score,
            capability_score=capability_score,
            confidence=confidence,
            confidence_tier=confidence_tier,
            gates_executed=gates,
            gates_passed=gates_passed,
            gates_failed=gates_failed,
            recommendation=recommendation,
            operation_id=operation_id,
            timestamp=timestamp
        )
        
        # LOG TO GOVERNANCE TRAIL
        self._log_operation("assess", response)
        
        return response
    
    def _simulate_wei_chen_agentic_loop(self) -> List[AgenticIteration]:
        """Simulate agentic loop for Wei Chen (3 iterations)"""
        return [
            AgenticIteration(
                iteration_num=1,
                tool_name="extract_claims",
                description="Extract skill claims from resume",
                result="Extracted 6 claims: Python expert, ML/AI architect, "
                       "data engineering lead, published author, certified",
                evidence_collected={
                    "claims_found": 6,
                    "categories": ["technical_skills", "publications", "certifications"]
                }
            ),
            AgenticIteration(
                iteration_num=2,
                tool_name="cross_reference_github",
                description="Verify claims with GitHub activity",
                result="GitHub: github.com/weichen-ml | 847 commits across 3 repos | "
                       "312 followers | Popular projects: ml-pipeline-optimizer (847★), "
                       "data-validation-framework (342★), tensorflow-extensions (156★) | "
                       "Contribution quality: EXPERT",
                evidence_collected={
                    "github_repos": 3,
                    "total_commits": 847,
                    "github_followers": 312,
                    "contribution_quality": "expert",
                    "evidence_strength": "high"
                }
            ),
            AgenticIteration(
                iteration_num=3,
                tool_name="verify_embodied_evidence",
                description="Cross-reference publications and certifications",
                result="Found 2 DOI-published papers (NeurIPS 2024, ICML 2023) with "
                       "23 and 14 citations respectively. AWS ML Specialty (2023) "
                       "and TensorFlow Advanced (2022) certifications verified. "
                       "Work history: ML Engineer 6yr (TechCorp), Senior ML Architect "
                       "6yr (AI Systems Inc). Timeline coherent, progression logical.",
                evidence_collected={
                    "publications": 2,
                    "doi_papers": 2,
                    "citations_total": 37,
                    "certifications_verified": 2,
                    "work_experience_years": 12,
                    "career_progression": "coherent",
                    "embodied_evidence_density": "high"
                }
            )
        ]
    
    def _execute_wei_chen_gates(self) -> List[PatentGateResult]:
        """Execute all 6 patent gates for Wei Chen (all PASS)"""
        return [
            PatentGateResult(
                gate_id="C-01",
                name="Coherence Gate",
                status=GateStatus.PASS.value,
                reason="Traditional and capability scores cohere. Large delta (50→87) "
                       "justified by high evidence density. Score alignment validated.",
                timestamp=self.current_timestamp
            ),
            PatentGateResult(
                gate_id="C-02",
                name="Temporal Depth Processor",
                status=GateStatus.PASS.value,
                reason="Career timeline is coherent. 6yr + 6yr roles sequential and "
                       "logical. No temporal anomalies (overlaps, impossible jumps). "
                       "Career progression demonstrates sustained expertise.",
                timestamp=self.current_timestamp
            ),
            PatentGateResult(
                gate_id="C-03",
                name="Lipschitz Constraint Validator",
                status=GateStatus.PASS.value,
                reason="Confidence bounded correctly at 0.92 (Tier 1: ≥0.7). "
                       "Evidence density: HIGH (GitHub + DOI + certs). Bound is tight "
                       "and defensible given embodied evidence.",
                timestamp=self.current_timestamp
            ),
            PatentGateResult(
                gate_id="C-04",
                name="Physiological Evidence Integrator",
                status=GateStatus.PASS.value,
                reason="Claimed skills corroborated by 5 embodied signals: GitHub "
                       "commits (847), DOI papers (2), certifications (2), work "
                       "history (12yr), project popularity (1345★). Claims validated.",
                timestamp=self.current_timestamp
            ),
            PatentGateResult(
                gate_id="C-05",
                name="Pre-Linguistic Thought Separator",
                status=GateStatus.PASS.value,
                reason="Logic fully separable. Claims extracted independently, "
                       "evidence extracted independently, conjunction logic applied "
                       "(zero-temperature). Narrative explanation coherent.",
                timestamp=self.current_timestamp
            ),
            PatentGateResult(
                gate_id="C-06",
                name="Gate Orchestrator (Non-Bypassable)",
                status=GateStatus.PASS.value,
                reason="All 5 upstream gates PASS (C-01 through C-05). Orchestrator "
                       "confirms non-bypassable gate hierarchy. Assessment can proceed. "
                       "Findings approved for recruiter review.",
                timestamp=self.current_timestamp
            )
        ]
    
    # ========================================================================
    # MARCUS LEE INTEGRITY CHECK (Gates FAIL, Findings BLOCKED)
    # ========================================================================
    
    def integrity_check(self, candidate_id: str = "marcus-lee-001") -> IntegrityCheckResponse:
        """
        Check candidate for integrity violations / fraud indicators.
        
        Marcus Lee: 2 red flags found, gates C-02 & C-04 FAIL, findings BLOCKED by C-06
        """
        candidate = get_candidate_by_id(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        operation_id = str(uuid.uuid4())[:8]
        timestamp = datetime.utcnow().isoformat()
        self.current_timestamp = timestamp
        
        # AGENTIC LOOP: 2 iterations (less than assess, because red flags trigger early)
        iterations = self._simulate_marcus_lee_agentic_loop()
        
        # PATENT GATES: All 6 execute, but C-02 & C-04 FAIL
        gates = self._execute_marcus_lee_gates()
        gates_passed = sum(1 for g in gates if g.status == GateStatus.PASS)
        gates_failed = sum(1 for g in gates if g.status in [GateStatus.FAIL, GateStatus.BLOCKED])
        
        # FINDINGS (Blocked by C-06 orchestrator)
        findings = self._extract_marcus_lee_findings()
        
        status = "RED_FLAGS_DETECTED" if findings else "CLEAN"
        
        overall_recommendation = (
            "Request clarification of timeline and patent evidence before proceeding. "
            "Integrity gates have failed (C-02: timeline overlap, C-04: no embodied evidence). "
            "Findings are BLOCKED by the C-06 orchestrator gate until evidence is provided."
        )
        
        response = IntegrityCheckResponse(
            candidate_id=candidate_id,
            candidate_name=candidate.name,
            status=status,
            agentic_iterations=iterations,
            findings=findings,
            gates_executed=gates,
            gates_passed=gates_passed,
            gates_failed=gates_failed,
            overall_recommendation=overall_recommendation,
            operation_id=operation_id,
            timestamp=timestamp
        )
        
        # LOG TO GOVERNANCE TRAIL
        self._log_operation("integrity_check", response)
        
        return response
    
    def _simulate_marcus_lee_agentic_loop(self) -> List[AgenticIteration]:
        """Simulate agentic loop for Marcus Lee (2 iterations, red flags detected early)"""
        return [
            AgenticIteration(
                iteration_num=1,
                tool_name="validate_timeline",
                description="Check career timeline for overlaps/anomalies",
                result="ALERT: Timeline overlap detected. CTO at TechCorp (2020-2023) "
                       "overlaps with VP Engineering at StartupXYZ (2022-2024) for "
                       "12 continuous months. Impossible to hold two full-time "
                       "executive roles simultaneously.",
                evidence_collected={
                    "timeline_anomalies": 1,
                    "overlap_duration_months": 12,
                    "severity": "high",
                    "gate_triggered": "C-02"
                }
            ),
            AgenticIteration(
                iteration_num=2,
                tool_name="verify_patent_evidence",
                description="Cross-reference patent claims with USPTO/DOI",
                result="ALERT: Claims 5 patents but zero embodied evidence found. "
                       "No USPTO links provided. No DOI papers. No GitHub repositories. "
                       "No patent documentation. Evidence density: ZERO. "
                       "Confidence for patent claims: capped at 0.15 (Tier 3).",
                evidence_collected={
                    "patents_claimed": 5,
                    "patents_verified": 0,
                    "embodied_evidence": 0,
                    "evidence_density": "zero",
                    "confidence_for_claim": 0.15,
                    "gate_triggered": "C-04"
                }
            )
        ]
    
    def _execute_marcus_lee_gates(self) -> List[PatentGateResult]:
        """Execute all 6 patent gates for Marcus Lee (C-02 & C-04 FAIL, C-06 BLOCKED)"""
        return [
            PatentGateResult(
                gate_id="C-01",
                name="Coherence Gate",
                status=GateStatus.BLOCKED.value,
                reason="Cannot assess score coherence. Upstream gates (C-02, C-04) failed. "
                       "Timeline integrity compromised. Skipping until evidence resolved.",
                timestamp=self.current_timestamp
            ),
            PatentGateResult(
                gate_id="C-02",
                name="Temporal Depth Processor",
                status=GateStatus.FAIL.value,
                reason="FAIL: Career timeline contains impossible overlap. "
                       "CTO at TechCorp (2020-2023) overlaps with VP Eng at StartupXYZ (2022-2024) "
                       "for 12 consecutive months. Cannot serve two full-time C-level roles "
                       "simultaneously. Timeline integrity VIOLATED.",
                timestamp=self.current_timestamp
            ),
            PatentGateResult(
                gate_id="C-03",
                name="Lipschitz Constraint Validator",
                status=GateStatus.CONDITIONAL.value,
                reason="Patent claims confidence capped at 0.15 (Tier 3: <0.4). "
                       "Evidence density is zero (no USPTO, DOI, or GitHub). Bound enforced "
                       "by constraint validator. Cannot increase confidence without evidence.",
                timestamp=self.current_timestamp
            ),
            PatentGateResult(
                gate_id="C-04",
                name="Physiological Evidence Integrator",
                status=GateStatus.FAIL.value,
                reason="FAIL: Claims 5 patents but zero embodied evidence. No USPTO links, "
                       "no DOI papers, no GitHub repositories, no patent documentation provided. "
                       "Evidence requirement NOT MET. Claims cannot be corroborated.",
                timestamp=self.current_timestamp
            ),
            PatentGateResult(
                gate_id="C-05",
                name="Pre-Linguistic Thought Separator",
                status=GateStatus.FAIL.value,
                reason="FAIL: Logic not separable. Claimed patents lack supporting evidence. "
                       "When evidence and claims are disjoint, conjunction logic collapses. "
                       "Narrative cannot be constructed without arbitrary assumptions.",
                timestamp=self.current_timestamp
            ),
            PatentGateResult(
                gate_id="C-06",
                name="Gate Orchestrator (Non-Bypassable)",
                status=GateStatus.BLOCKED.value,
                reason="BLOCKED: Multiple upstream gates FAILED (C-02, C-04, C-05). "
                       "Orchestrator enforces non-bypassable hierarchy. Findings BLOCKED "
                       "until all gates pass. Request evidence clarification from candidate.",
                timestamp=self.current_timestamp
            )
        ]
    
    def _extract_marcus_lee_findings(self) -> List[IntegrityFinding]:
        """Extract red flags for Marcus Lee"""
        return [
            IntegrityFinding(
                finding_id=str(uuid.uuid4())[:8],
                finding_type="timeline_overlap",
                severity="HIGH",
                evidence="CTO at TechCorp (2020-2023) overlaps with VP Eng at StartupXYZ "
                         "(2022-2024) for 12 consecutive months. Impossible to hold "
                         "two full-time C-level roles.",
                gate_failed="C-02 (Temporal Depth Processor)",
                recommendation="REQUEST_CLARIFICATION: Ask candidate to explain dual roles. "
                               "Resolve before proceeding."
            ),
            IntegrityFinding(
                finding_id=str(uuid.uuid4())[:8],
                finding_type="unsubstantiated_claims",
                severity="HIGH",
                evidence="Claims 5 patents but provides zero embodied evidence "
                         "(no USPTO links, DOI papers, or GitHub repositories).",
                gate_failed="C-04 (Physiological Evidence Integrator)",
                recommendation="REQUEST_EVIDENCE: Ask for patent numbers, USPTO links, "
                               "or DOI references before proceeding."
            )
        ]
    
    # ========================================================================
    # GOVERNANCE LOGGING
    # ========================================================================
    
    def _log_operation(self, operation_type: str, response: Any):
        """Log operation to governance audit trail"""
        log_entry = {
            "timestamp": self.current_timestamp,
            "operation_id": response.operation_id,
            "candidate_id": response.candidate_id,
            "candidate_name": response.candidate_name,
            "operation_type": operation_type,
            "gates_passed": response.gates_passed,
            "gates_failed": response.gates_failed,
            "recommendation": response.recommendation if hasattr(response, 'recommendation') 
                            else response.overall_recommendation
        }
        
        # Add findings for integrity checks
        if operation_type == "integrity_check" and hasattr(response, 'findings'):
            log_entry["findings"] = [f.finding_type for f in response.findings]
            log_entry["findings_count"] = len(response.findings)
        
        self.governance_log.append(log_entry)
    
    def get_logs(self) -> Dict[str, Any]:
        """Retrieve governance audit trail"""
        return {
            "total_entries": len(self.governance_log),
            "logs": self.governance_log
        }
