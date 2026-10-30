"""Unit tests for audit URL and audit logs API endpoints."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from RevOpsAI.src.api.routes import (
    AuditUrlRequest,
    audit_prospect_url,
    get_audit_logs,
)
from RevOpsAI.src.core.models import Prospect, ProspectState
from RevOpsAI.src.core.pipeline import PipelineResult


def test_audit_prospect_url_success():
    """Verify live audit URL endpoint fetches HTML, runs pipeline, and returns result."""
    mock_orch = MagicMock()
    mock_lead = Prospect(
        tenant_id="tenant_clinicas_madrid",
        name="Clínica Dental Mock",
        url="https://dentalmock.es/",
        state=ProspectState.PENDING_APPROVAL,
        score=85,
    )
    mock_orch.process_prospect.return_value = PipelineResult(prospect=mock_lead)

    fake_html = "<html><body><h1>Clínica Dental Mock</h1></body></html>"

    with patch("RevOpsAI.src.api.routes.fetch_remote_html", return_value=fake_html):
        req = AuditUrlRequest(
            tenant_id="tenant_clinicas_madrid",
            name="Clínica Dental Mock",
            url="https://dentalmock.es/",
        )
        res = audit_prospect_url(req=req, orch=mock_orch)

    assert res.prospect.name == "Clínica Dental Mock"
    assert res.prospect.score == 85
    assert res.prospect.state == ProspectState.PENDING_APPROVAL
    mock_orch.process_prospect.assert_called_once()


def test_audit_prospect_url_invalid_url():
    """Verify endpoint rejects invalid scheme or unreachable domain with 400."""
    mock_orch = MagicMock()
    req = AuditUrlRequest(
        tenant_id="tenant_clinicas_madrid",
        name="Clínica Fail",
        url="ftp://invalid.com",
    )
    with pytest.raises(HTTPException) as exc_info:
        audit_prospect_url(req=req, orch=mock_orch)
    assert exc_info.value.status_code == 400


def test_get_audit_logs_tenant_scoped():
    """Verify audit logs are queried through the tenant-scoped repository."""
    mock_repo = MagicMock()
    mock_repo.list_audit_logs.return_value = [
        {
            "id": "audit_123",
            "tenant_id": "tenant_clinicas_madrid",
            "lead_id": "lead_abc",
            "actor": "human_operator",
            "action": "APPROVE",
            "reason": "",
            "timestamp": "2026-10-29T15:00:00",
        }
    ]

    logs = get_audit_logs(tenant_id="tenant_clinicas_madrid", lead_id=None, repo=mock_repo)
    assert len(logs) == 1
    assert logs[0]["action"] == "APPROVE"
    mock_repo.list_audit_logs.assert_called_once_with(lead_id=None)

