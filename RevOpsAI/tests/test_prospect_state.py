import pytest
from pydantic import ValidationError
from RevOpsAI.src.core.models import Prospect, ProspectState

def test_initial_state_is_ingested():
    p = Prospect(tenant_id="tenant_clinica_1", name="Clinica Dental Norte", url="https://dentalnorte.es")
    assert p.state == ProspectState.INGESTED
    assert p.score == 0
    assert p.id.startswith("lead_")
    assert p.research_summary == ""
    assert p.draft_message == ""
    assert p.is_blacklisted is False

def test_cannot_skip_to_sent_without_approval():
    p = Prospect(tenant_id="tenant_clinica_1", name="Clinica Dental Norte", url="https://dentalnorte.es")
    with pytest.raises(ValueError, match="Transición inválida"):
        p.transition_to(ProspectState.SENT)

def test_valid_full_lifecycle_transitions():
    p = Prospect(tenant_id="tenant_clinica_1", name="Clinica Dental Norte", url="https://dentalnorte.es")
    assert p.state == ProspectState.INGESTED

    p.transition_to(ProspectState.RESEARCHING)
    assert p.state == ProspectState.RESEARCHING

    p.transition_to(ProspectState.AUDITING)
    assert p.state == ProspectState.AUDITING

    p.transition_to(ProspectState.SCORING)
    assert p.state == ProspectState.SCORING

    p.transition_to(ProspectState.QUALIFIED)
    assert p.state == ProspectState.QUALIFIED

    p.transition_to(ProspectState.DRAFTING)
    assert p.state == ProspectState.DRAFTING

    p.transition_to(ProspectState.PENDING_APPROVAL)
    assert p.state == ProspectState.PENDING_APPROVAL

    p.transition_to(ProspectState.APPROVED)
    assert p.state == ProspectState.APPROVED

    p.transition_to(ProspectState.SENT)
    assert p.state == ProspectState.SENT

    p.transition_to(ProspectState.OPT_OUT)
    assert p.state == ProspectState.OPT_OUT

def test_discard_transitions_from_allowed_states():
    # From INGESTED
    p1 = Prospect(tenant_id="tenant_1", name="C1", url="https://c1.es")
    p1.transition_to(ProspectState.DISCARDED)
    assert p1.state == ProspectState.DISCARDED

    # From RESEARCHING
    p2 = Prospect(tenant_id="tenant_1", name="C2", url="https://c2.es")
    p2.transition_to(ProspectState.RESEARCHING)
    p2.transition_to(ProspectState.DISCARDED)
    assert p2.state == ProspectState.DISCARDED

    # From AUDITING
    p3 = Prospect(tenant_id="tenant_1", name="C3", url="https://c3.es")
    p3.transition_to(ProspectState.RESEARCHING)
    p3.transition_to(ProspectState.AUDITING)
    p3.transition_to(ProspectState.DISCARDED)
    assert p3.state == ProspectState.DISCARDED

    # From SCORING
    p4 = Prospect(tenant_id="tenant_1", name="C4", url="https://c4.es")
    p4.transition_to(ProspectState.RESEARCHING)
    p4.transition_to(ProspectState.AUDITING)
    p4.transition_to(ProspectState.SCORING)
    p4.transition_to(ProspectState.DISCARDED)
    assert p4.state == ProspectState.DISCARDED

    # From PENDING_APPROVAL
    p5 = Prospect(tenant_id="tenant_1", name="C5", url="https://c5.es")
    p5.transition_to(ProspectState.RESEARCHING)
    p5.transition_to(ProspectState.AUDITING)
    p5.transition_to(ProspectState.SCORING)
    p5.transition_to(ProspectState.QUALIFIED)
    p5.transition_to(ProspectState.DRAFTING)
    p5.transition_to(ProspectState.PENDING_APPROVAL)
    p5.transition_to(ProspectState.DISCARDED)
    assert p5.state == ProspectState.DISCARDED

def test_terminal_states_cannot_transition():
    # DISCARDED is terminal
    p_disc = Prospect(tenant_id="tenant_1", name="C1", url="https://c1.es")
    p_disc.transition_to(ProspectState.DISCARDED)
    with pytest.raises(ValueError, match="Transición inválida"):
        p_disc.transition_to(ProspectState.RESEARCHING)

    # OPT_OUT is terminal
    p_opt = Prospect(tenant_id="tenant_1", name="C2", url="https://c2.es")
    p_opt.transition_to(ProspectState.RESEARCHING)
    p_opt.transition_to(ProspectState.AUDITING)
    p_opt.transition_to(ProspectState.SCORING)
    p_opt.transition_to(ProspectState.QUALIFIED)
    p_opt.transition_to(ProspectState.DRAFTING)
    p_opt.transition_to(ProspectState.PENDING_APPROVAL)
    p_opt.transition_to(ProspectState.APPROVED)
    p_opt.transition_to(ProspectState.SENT)
    p_opt.transition_to(ProspectState.OPT_OUT)
    with pytest.raises(ValueError, match="Transición inválida"):
        p_opt.transition_to(ProspectState.INGESTED)

def test_required_fields_validation():
    with pytest.raises(ValidationError):
        Prospect(name="Clinica Dental", url="https://dental.es")  # Missing tenant_id

    with pytest.raises(ValidationError):
        Prospect(tenant_id="tenant_1", url="https://dental.es")  # Missing name

    with pytest.raises(ValidationError):
        Prospect(tenant_id="tenant_1", name="Clinica Dental")  # Missing url

def test_blacklist_tracking():
    p = Prospect(
        tenant_id="tenant_1",
        name="Clinica Dental",
        url="https://dental.es",
        is_blacklisted=True
    )
    assert p.is_blacklisted is True
