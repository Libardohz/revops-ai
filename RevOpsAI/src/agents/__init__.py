"""Agents module for RevOpsAI pipeline."""

from RevOpsAI.src.agents.research_agent import ResearchAgent, ResearchSummary
from RevOpsAI.src.agents.audit_agent import CommercialAuditAgent, CommercialAuditResult
from RevOpsAI.src.agents.scoring_agent import ScoringAgent, ScoringResult
from RevOpsAI.src.agents.copywriter_agent import CopywriterAgent
from RevOpsAI.src.agents.dispatch_agent import DispatchAgent, ReplyIntent
from RevOpsAI.src.agents.followup_agent import FollowUpAgent, FollowUpResult

__all__ = [
    "ResearchAgent",
    "ResearchSummary",
    "CommercialAuditAgent",
    "CommercialAuditResult",
    "ScoringAgent",
    "ScoringResult",
    "CopywriterAgent",
    "DispatchAgent",
    "ReplyIntent",
    "FollowUpAgent",
    "FollowUpResult",
]
