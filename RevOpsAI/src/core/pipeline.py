"""Pipeline Orchestrator for end-to-end multi-agent prospect processing."""

from pydantic import BaseModel
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.core.config_loader import SectorConfig
from RevOpsAI.src.core.approval_store import ApprovalStore
from RevOpsAI.src.integrations.web_scraper import SecureWebScraper
from RevOpsAI.src.agents.research_agent import ResearchAgent
from RevOpsAI.src.agents.audit_agent import CommercialAuditAgent, CommercialAuditResult
from RevOpsAI.src.agents.scoring_agent import ScoringAgent, ScoringResult
from RevOpsAI.src.agents.copywriter_agent import CopywriterAgent


class PipelineResult(BaseModel):
    """Result object summarizing the execution of the pipeline for a prospect."""

    prospect: Prospect
    audit: CommercialAuditResult | None = None
    scoring: ScoringResult | None = None


class PipelineOrchestrator:
    """Central orchestrator sequencing scraper, research, audit, scoring, and copywriting agents."""

    def __init__(self, config: SectorConfig, approval_store: ApprovalStore) -> None:
        """Initialize orchestrator with sector configuration and approval store."""
        self.config = config
        self.approval_store = approval_store
        self.scraper = SecureWebScraper()
        self.research_agent = ResearchAgent()
        self.audit_agent = CommercialAuditAgent(config)
        self.scoring_agent = ScoringAgent(config)
        self.copywriter_agent = CopywriterAgent(config, approval_store)

    def process_prospect(
        self,
        lead: Prospect,
        html_content: str,
        estimated_size_score: float = 60.0,
        reputation_score: float = 70.0,
    ) -> PipelineResult:
        """Run the sequential agent pipeline on a prospect given its raw HTML website content."""
        if lead.is_blacklisted:
            lead.transition_to(ProspectState.DISCARDED)
            return PipelineResult(prospect=lead)

        # 1. Zero-trust extraction and sanitization
        scrape = self.scraper.parse_html(lead.url, html_content)

        # 2. Operational research
        summary = self.research_agent.analyze(lead, scrape)

        # 3. Commercial audit & compliance checks
        audit = self.audit_agent.audit(lead, summary)

        # 4. Weighted scoring and qualification
        scoring = self.scoring_agent.evaluate(
            lead,
            audit,
            estimated_size_score=estimated_size_score,
            reputation_score=reputation_score,
        )

        # 5. If qualified, draft outreach message and queue in HITL store
        if scoring.is_qualified:
            self.copywriter_agent.generate_proposal(lead, audit)

        return PipelineResult(prospect=lead, audit=audit, scoring=scoring)
