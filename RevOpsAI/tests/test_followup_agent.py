"""Tests for FollowUpAgent cadence, attempt ceilings, and anti-spam compliance."""

import pytest
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.agents.followup_agent import FollowUpAgent, FollowUpResult


def test_followup_agent_generates_first_bump():
    agent = FollowUpAgent(max_followups=2)
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Almagro",
        url="https://almagro.es",
        score=82,
        research_summary="Sin WhatsApp directo",
        state=ProspectState.SENT,
    )
    result = agent.evaluate_and_generate(lead, days_since_last_contact=3, current_attempt=0)
    assert result.should_send is True
    assert result.attempt_number == 1
    assert "Clínica Dental Almagro" in result.message
    assert "WhatsApp" in result.message
    assert "Aviso Legal" in result.message


def test_followup_agent_generates_second_and_final_bump():
    agent = FollowUpAgent(max_followups=2)
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Almagro",
        url="https://almagro.es",
        state=ProspectState.SENT,
    )
    result = agent.evaluate_and_generate(lead, days_since_last_contact=5, current_attempt=1)
    assert result.should_send is True
    assert result.attempt_number == 2
    assert "último seguimiento" in result.message.lower() or "cerrar el contacto" in result.message.lower()


def test_followup_agent_exhausts_and_transitions_to_discarded():
    agent = FollowUpAgent(max_followups=2)
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Almagro",
        url="https://almagro.es",
        state=ProspectState.SENT,
    )
    result = agent.evaluate_and_generate(lead, days_since_last_contact=4, current_attempt=2)
    assert result.should_send is False
    assert result.is_exhausted is True
    assert lead.state == ProspectState.DISCARDED


def test_followup_agent_blocks_blacklisted_or_opt_out():
    agent = FollowUpAgent()
    lead = Prospect(
        tenant_id="tenant_dental",
        name="Clínica Dental Almagro",
        url="https://almagro.es",
        state=ProspectState.OPT_OUT,
        is_blacklisted=True,
    )
    result = agent.evaluate_and_generate(lead, days_since_last_contact=10, current_attempt=0)
    assert result.should_send is False
    assert result.reason == "blacklisted_or_opt_out"
