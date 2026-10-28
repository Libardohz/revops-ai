"""Lead Scoring Agent for RevOpsAI pipeline.

Computes a weighted qualification score combining digital gap analysis,
market reputation, and estimated company size based on dynamic sector config.
Transitions prospect lifecycle to QUALIFIED or DISCARDED.
"""

from pydantic import BaseModel, Field
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.core.config_loader import SectorConfig
from RevOpsAI.src.agents.audit_agent import CommercialAuditResult


class ScoringResult(BaseModel):
    """Output schema for lead scoring and qualification evaluation."""

    score: int = Field(..., description="Overall calculated score (0-100).")
    is_qualified: bool = Field(..., description="Whether score meets minimum threshold.")
    breakdown: dict[str, float] = Field(
        default_factory=dict,
        description="Detailed score components used in the weighted formula."
    )


class ScoringAgent:
    """Agent responsible for computing weighted lead score and qualifying prospects."""

    def __init__(self, config: SectorConfig) -> None:
        """Initialize the scoring agent with sector configuration.

        Args:
            config: SectorConfig containing scoring weights and qualification thresholds.
        """
        self.config = config

    def evaluate(
        self,
        lead: Prospect,
        audit: CommercialAuditResult,
        estimated_size_score: float = 50.0,
        reputation_score: float = 70.0,
    ) -> ScoringResult:
        """Evaluate prospect qualification based on sector weights and audit findings.

        Args:
            lead: Prospect instance (must be in AUDITING or SCORING state).
            audit: CommercialAuditResult containing detected gaps and opportunities.
            estimated_size_score: Normalized size score (0.0 to 100.0). Default 50.0.
            reputation_score: Normalized reputation score (0.0 to 100.0). Default 70.0.

        Returns:
            ScoringResult: Computed score, qualification decision, and score breakdown.

        Raises:
            ValueError: If lead state transition is invalid.
        """
        # Ensure lead is transitioned to SCORING before deciding qualification
        if lead.state != ProspectState.SCORING:
            lead.transition_to(ProspectState.SCORING)

        weights = self.config.scoring.weights

        # Digital gap score: operational friction represents commercial opportunity (max 100.0)
        gap_score = min(
            100.0,
            len(audit.commercial_gaps) * 45.0 + len(audit.growth_opportunities) * 10.0,
        )

        final_score = int(
            gap_score * weights.get("digital_gap", 0.5)
            + reputation_score * weights.get("market_reputation", 0.3)
            + estimated_size_score * weights.get("estimated_size", 0.2)
        )

        is_qualified = final_score >= self.config.scoring.min_qualification_score
        lead.score = final_score

        if is_qualified:
            lead.transition_to(ProspectState.QUALIFIED)
        else:
            lead.transition_to(ProspectState.DISCARDED)

        return ScoringResult(
            score=final_score,
            is_qualified=is_qualified,
            breakdown={
                "digital_gap_score": gap_score,
                "reputation_score": reputation_score,
                "size_score": estimated_size_score,
            },
        )
