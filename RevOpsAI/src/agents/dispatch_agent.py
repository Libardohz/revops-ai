"""Dispatch Agent and Prospect Reply Intent Classifier for RevOpsAI pipeline."""

import re
import unicodedata
from enum import Enum
from RevOpsAI.src.core.models import Prospect, ProspectState


class ReplyIntent(str, Enum):
    """Categorized intent of an incoming prospect reply."""

    INTERESTED = "INTERESTED"
    OPT_OUT = "OPT_OUT"
    DEFERRED = "DEFERRED"
    UNKNOWN = "UNKNOWN"


class DispatchAgent:
    """Agent responsible for outbound message dispatch and inbound reply processing."""

    OPT_OUT_PATTERNS = [
        r"no\s+(me\s+)?contacten",
        r"baja",
        r"borren",
        r"no\s+(me\s+)?interesa",
        r"spam",
        r"desuscribir",
    ]

    INTEREST_PATTERNS = [
        r"reunion",
        r"llamada",
        r"interesad[oa]",
        r"interesa\b",
        r"hablemos",
        r"precio",
        r"disponibilidad",
    ]

    DEFERRED_PATTERNS = [
        r"mas\s+adelante",
        r"el\s+proximo\s+mes",
        r"ahora\s+no",
        r"otro\s+momento",
        r"despues",
    ]

    def _normalize_text(self, text: str) -> str:
        """Strip accents and lowercase text for robust regex matching."""
        normalized = unicodedata.normalize("NFKD", text)
        ascii_text = normalized.encode("ASCII", "ignore").decode("utf-8")
        return ascii_text.lower()

    def dispatch_message(self, lead: Prospect) -> bool:
        """Execute outbound dispatch for an approved prospect.

        Args:
            lead: Prospect instance to dispatch.

        Returns:
            bool: True if dispatch was executed and state transitioned to SENT, False otherwise.
        """
        if lead.is_blacklisted or lead.state != ProspectState.APPROVED:
            return False

        lead.transition_to(ProspectState.SENT)
        return True

    def handle_incoming_reply(self, lead: Prospect, reply_text: str) -> ReplyIntent:
        """Process incoming prospect reply and enforce compliance and commercial classification.

        Args:
            lead: Prospect receiving the reply.
            reply_text: Raw message text sent by the prospect.

        Returns:
            ReplyIntent: Classified intent.
        """
        cleaned_text = self._normalize_text(reply_text)

        # 1. Absolute Priority: Compliance Opt-Out (Immediate Blacklisting)
        for pattern in self.OPT_OUT_PATTERNS:
            if re.search(pattern, cleaned_text):
                lead.is_blacklisted = True
                if lead.state == ProspectState.SENT:
                    lead.transition_to(ProspectState.OPT_OUT)
                else:
                    lead.state = ProspectState.OPT_OUT
                return ReplyIntent.OPT_OUT

        # 2. Commercial Interest
        for pattern in self.INTEREST_PATTERNS:
            if re.search(pattern, cleaned_text):
                return ReplyIntent.INTERESTED

        # 3. Deferred Follow-up
        for pattern in self.DEFERRED_PATTERNS:
            if re.search(pattern, cleaned_text):
                return ReplyIntent.DEFERRED

        return ReplyIntent.UNKNOWN
