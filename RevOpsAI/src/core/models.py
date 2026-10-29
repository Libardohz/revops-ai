"""Data models and finite state machine for prospect lifecycle tracking."""

from enum import Enum
import uuid
from typing import ClassVar
from pydantic import BaseModel, Field


class ProspectState(str, Enum):
    """Lifecycle states for a prospect in the RevOpsAI pipeline."""

    INGESTED = "INGESTED"
    RESEARCHING = "RESEARCHING"
    AUDITING = "AUDITING"
    SCORING = "SCORING"
    QUALIFIED = "QUALIFIED"
    DISCARDED = "DISCARDED"
    DRAFTING = "DRAFTING"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    SENT = "SENT"
    OPT_OUT = "OPT_OUT"
    INTERESTED = "INTERESTED"


class Prospect(BaseModel):
    """Prospect entity with tenant isolation and strict state machine transitions."""

    id: str = Field(default_factory=lambda: f"lead_{uuid.uuid4().hex[:8]}")
    tenant_id: str
    name: str
    url: str
    state: ProspectState = ProspectState.INGESTED
    score: int = 0
    research_summary: str = ""
    draft_message: str = ""
    is_blacklisted: bool = False

    VALID_TRANSITIONS: ClassVar[dict[ProspectState, set[ProspectState]]] = {
        ProspectState.INGESTED: {ProspectState.RESEARCHING, ProspectState.DISCARDED},
        ProspectState.RESEARCHING: {ProspectState.AUDITING, ProspectState.DISCARDED},
        ProspectState.AUDITING: {ProspectState.SCORING, ProspectState.DISCARDED},
        ProspectState.SCORING: {ProspectState.QUALIFIED, ProspectState.DISCARDED},
        ProspectState.QUALIFIED: {ProspectState.DRAFTING},
        ProspectState.DRAFTING: {ProspectState.PENDING_APPROVAL},
        ProspectState.PENDING_APPROVAL: {ProspectState.APPROVED, ProspectState.DISCARDED},
        ProspectState.APPROVED: {ProspectState.SENT},
        ProspectState.SENT: {ProspectState.OPT_OUT, ProspectState.INTERESTED},
        ProspectState.INTERESTED: {ProspectState.OPT_OUT},
        ProspectState.DISCARDED: set(),
        ProspectState.OPT_OUT: set(),
    }

    def transition_to(self, new_state: ProspectState) -> None:
        """Safely transition prospect to a new state if valid.

        Args:
            new_state: The target ProspectState.

        Raises:
            ValueError: If the transition from current state to new_state is not permitted.
        """
        valid_targets = self.VALID_TRANSITIONS.get(self.state, set())
        if new_state not in valid_targets:
            raise ValueError(f"Transición inválida: de {self.state} a {new_state}")
        self.state = new_state
