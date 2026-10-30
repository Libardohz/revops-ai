"""Unit and integration tests for production readiness: Supabase engine, auth guards, and cron runner."""

import os
from unittest.mock import patch, MagicMock
import pytest
from fastapi import HTTPException
from RevOpsAI.src.db.session import get_engine
from RevOpsAI.src.api.routes import verify_auth, process_cron_followups
from RevOpsAI.src.core.models import Prospect, ProspectState


def test_get_engine_supabase_url_normalization():
    """Verify postgres:// is normalized to postgresql:// and connection pool args are set."""
    with patch.dict(os.environ, {"DATABASE_URL": "postgres://postgres:mypass@db.supabase.co:5432/postgres"}):
        engine = get_engine()
        assert "postgresql" in engine.url.drivername
        assert engine.pool is not None


def test_auth_guard_disabled_by_default():
    """When DASHBOARD_AUTH_ENABLED is false/unset, authentication check passes silently."""
    with patch.dict(os.environ, {"DASHBOARD_AUTH_ENABLED": "false"}):
        # Should not raise exception
        result = verify_auth(credentials=None)
        assert result is True


def test_auth_guard_enabled_rejects_invalid_credentials():
    """When DASHBOARD_AUTH_ENABLED is true, invalid credentials raise HTTP 401."""
    with patch.dict(os.environ, {
        "DASHBOARD_AUTH_ENABLED": "true",
        "DASHBOARD_USERNAME": "admin",
        "DASHBOARD_PASSWORD": "secret_password",
    }):
        # Missing credentials
        with pytest.raises(HTTPException) as exc:
            verify_auth(credentials=None)
        assert exc.value.status_code == 401

        # Wrong password
        wrong_creds = MagicMock(username="admin", password="wrong")
        with pytest.raises(HTTPException) as exc:
            verify_auth(credentials=wrong_creds)
        assert exc.value.status_code == 401


def test_auth_guard_enabled_accepts_valid_credentials():
    """When DASHBOARD_AUTH_ENABLED is true, valid credentials pass."""
    with patch.dict(os.environ, {
        "DASHBOARD_AUTH_ENABLED": "true",
        "DASHBOARD_USERNAME": "admin",
        "DASHBOARD_PASSWORD": "secret_password",
    }):
        valid_creds = MagicMock(username="admin", password="secret_password")
        assert verify_auth(credentials=valid_creds) is True


def test_cron_followups_processing():
    """Verify cron follow-ups processes SENT leads and applies FollowUpAgent."""
    mock_repo = MagicMock()
    lead_sent = Prospect(
        tenant_id="tenant_clinicas_madrid",
        name="Clínica Contactada",
        url="https://contactada.es",
        state=ProspectState.SENT,
    )
    mock_repo.list_prospects.return_value = [lead_sent]

    report = process_cron_followups(
        tenant_id="tenant_clinicas_madrid",
        days_elapsed=4,
        cron_token="test_token",
        repo=mock_repo,
    )

    assert report["processed_count"] == 1
    assert len(report["results"]) == 1
    assert report["results"][0]["should_send"] is True
