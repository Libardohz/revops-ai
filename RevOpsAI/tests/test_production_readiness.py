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

    with patch.dict(os.environ, {"CRON_SECRET_TOKEN": "test_token"}):
        report = process_cron_followups(
            tenant_id="tenant_clinicas_madrid",
            days_elapsed=4,
            cron_token="test_token",
            repo=mock_repo,
        )

    assert report["processed_count"] == 1
    assert len(report["results"]) == 1
    assert report["results"][0]["should_send"] is True


def test_health_check_and_landing_page():
    """Verify /health returns 200 OK and root / serves the hzSaaS landing page."""
    from fastapi.testclient import TestClient
    from RevOpsAI.src.api.main import app

    client = TestClient(app)
    
    # Test /health
    health_res = client.get("/health")
    assert health_res.status_code == 200
    assert health_res.json()["status"] == "healthy"

    # Test /api/v1/health
    v1_health_res = client.get("/api/v1/health")
    assert v1_health_res.status_code == 200
    assert v1_health_res.json()["status"] == "healthy"

    # Test root / landing page
    root_res = client.get("/")
    assert root_res.status_code == 200
    assert "hzSaaS" in root_res.text
    assert "3135108101" in root_res.text
    assert "GymSaaS" in root_res.text


def test_list_sectors_endpoint():
    """Verify GET /api/v1/sectors returns all 4 configured business verticals."""
    from fastapi.testclient import TestClient
    from RevOpsAI.src.api.main import app

    client = TestClient(app)
    res = client.get("/api/v1/sectors")
    assert res.status_code == 200
    sectors = res.json()
    sector_ids = [s["id"] for s in sectors]
    assert "clinicas" in sector_ids
    assert "inmobiliarias" in sector_ids
    assert "abogados" in sector_ids
    assert "turismo_medico" in sector_ids
