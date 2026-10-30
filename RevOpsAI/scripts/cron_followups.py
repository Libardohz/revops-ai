"""Automated daily Cron worker executing FollowUpAgent cadences across all active tenants."""

import os
import sys
from RevOpsAI.src.db.session import get_engine, get_session_factory
from RevOpsAI.src.db.repository import TenantScopedRepository
from RevOpsAI.src.agents.followup_agent import FollowUpAgent
from RevOpsAI.src.core.models import ProspectState


def run_daily_followups(days_elapsed: int = 3, tenants: list[str] | None = None) -> None:
    """Evaluate and trigger follow-up bump messages across sent prospects."""
    active_tenants = tenants or ["tenant_clinicas_madrid", "tenant_dental_bcn", "tenant_default"]
    engine = get_engine()
    factory = get_session_factory(engine)
    agent = FollowUpAgent()

    print(f"[*] Iniciando ejecución de FollowUpAgent (Ciclo diario, días transcurridos: {days_elapsed})...")

    total_processed = 0
    total_drafted = 0
    total_exhausted = 0

    with factory() as session:
        for tenant_id in active_tenants:
            repo = TenantScopedRepository(session, tenant_id)
            sent_leads = repo.list_prospects(state=ProspectState.SENT)

            for lead in sent_leads:
                total_processed += 1
                res = agent.evaluate_and_generate(
                    lead=lead,
                    days_since_last_contact=days_elapsed,
                    current_attempt=1,
                )

                if res.should_send:
                    lead.draft_message = res.message
                    repo.save_prospect(lead)
                    repo.log_audit(
                        lead_id=lead.id,
                        actor="cron_followup_worker",
                        action="FOLLOWUP_DRAFTED",
                        reason=f"Cadencia activa: Seguimiento #{res.attempt_number} redactado.",
                    )
                    total_drafted += 1
                    print(f"  [+] {tenant_id} | {lead.name} -> Seguimiento #{res.attempt_number} redactado.")

                elif res.is_exhausted:
                    repo.save_prospect(lead)
                    repo.log_audit(
                        lead_id=lead.id,
                        actor="cron_followup_worker",
                        action="FOLLOWUP_EXHAUSTED",
                        reason="Techo de 2 intentos alcanzado sin respuesta. Lead descartado.",
                    )
                    total_exhausted += 1
                    print(f"  [-] {tenant_id} | {lead.name} -> Expirado (DISCARDED).")

    print(f"[*] Fin de ciclo: {total_processed} evaluados, {total_drafted} seguimientos preparados, {total_exhausted} descartados.")


if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    run_daily_followups(days_elapsed=days)

