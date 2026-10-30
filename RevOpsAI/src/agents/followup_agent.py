"""FollowUpAgent: Automated and compliant post-dispatch cadence engine."""

from dataclasses import dataclass
from RevOpsAI.src.core.models import Prospect, ProspectState


@dataclass
class FollowUpResult:
    """Outcome of cadence evaluation for a prospect."""

    should_send: bool
    attempt_number: int = 0
    message: str = ""
    is_exhausted: bool = False
    reason: str = ""


class FollowUpAgent:
    """Specialized agent managing consultative follow-up cadences with strict retry ceilings."""

    def __init__(self, max_followups: int = 2, min_days_cooldown: int = 3):
        self.max_followups = max_followups
        self.min_days_cooldown = min_days_cooldown

    def evaluate_and_generate(
        self,
        lead: Prospect,
        days_since_last_contact: int,
        current_attempt: int,
    ) -> FollowUpResult:
        """Evaluate cadence state and generate compliant bump copy."""
        # 1. Zero-trust security & compliance boundary checks
        if lead.is_blacklisted or lead.state in {ProspectState.OPT_OUT, ProspectState.DISCARDED}:
            return FollowUpResult(
                should_send=False,
                reason="blacklisted_or_opt_out",
            )

        # 2. Check retry ceiling exhaustion
        if current_attempt >= self.max_followups:
            lead.transition_to(ProspectState.DISCARDED)
            return FollowUpResult(
                should_send=False,
                attempt_number=current_attempt,
                is_exhausted=True,
                reason="max_followups_exhausted",
            )

        # 3. Check cooldown timing
        if days_since_last_contact < self.min_days_cooldown:
            return FollowUpResult(
                should_send=False,
                attempt_number=current_attempt,
                reason="cooldown_active",
            )

        # 4. Generate consultative bump copy based on attempt
        attempt_num = current_attempt + 1
        summary_topic = lead.research_summary if lead.research_summary else "optimización de captación"

        if attempt_num == 1:
            body = (
                f"Estimado equipo de {lead.name},\n\n"
                f"Le escribo brevemente en seguimiento a nuestra propuesta anterior sobre "
                f"la integración de {summary_topic}.\n\n"
                f"¿Tienen disponibilidad de 10 minutos esta semana para revisar cómo agilizar "
                f"la recepción de pacientes?"
            )
        else:
            body = (
                f"Estimado equipo de {lead.name},\n\n"
                f"Le contacto por este medio como último seguimiento para cerrar el contacto "
                f"en caso de que no sea prioritario en este momento.\n\n"
                f"Si desean explorar la automatización de citas y WhatsApp para su clínica en el futuro, "
                f"quedamos a su entera disposición."
            )

        # Mandatory legal disclaimer & unsubscribe link
        legal_footer = (
            f"\n\n---\n"
            f"Aviso Legal: Esta comunicación comercial es consultiva y dirigida a profesionales. "
            f"Para no recibir más comunicaciones, responda con 'baja' o haga clic en su enlace de cancelación."
        )
        full_message = f"{body}{legal_footer}"

        return FollowUpResult(
            should_send=True,
            attempt_number=attempt_num,
            message=full_message,
            is_exhausted=False,
            reason="ready_to_send",
        )

