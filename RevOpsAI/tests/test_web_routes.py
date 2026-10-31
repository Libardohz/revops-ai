"""Tests for Web Dashboard route, template serving, and static asset delivery."""

import pytest
from pathlib import Path
from RevOpsAI.src.api.routes import (
    serve_dashboard,
    serve_login,
    create_session_token,
    verify_session_token,
)
from RevOpsAI.src.api.main import root_landing


def test_dashboard_files_exist():
    html_path = Path("RevOpsAI/src/web/templates/dashboard.html")
    landing_path = Path("RevOpsAI/src/web/templates/landing.html")
    login_path = Path("RevOpsAI/src/web/templates/login.html")
    logo_path = Path("RevOpsAI/src/web/static/hzsaas-shield-logo.jpg")
    tokens_path = Path("RevOpsAI/src/web/static/tokens.css")
    css_path = Path("RevOpsAI/src/web/static/dashboard.css")
    js_path = Path("RevOpsAI/src/web/static/dashboard.js")

    assert html_path.exists()
    assert landing_path.exists()
    assert login_path.exists()
    assert logo_path.exists()
    assert tokens_path.exists()
    assert css_path.exists()
    assert js_path.exists()


def test_serve_corporate_landing_endpoint():
    response = root_landing()
    assert response.status_code == 200
    content = response.body.decode("utf-8")
    assert "hzSaaS" in content
    assert "RevOps AI" in content
    assert "GymSaaS" in content
    assert "gym.hzsaas.com" in content
    assert "hzsaas-shield-logo.jpg" in content
    assert "tokens.css" in content
    assert "bento-grid" in content
    assert "calculadora-roi" in content
    # Ensure zero internal infrastructure or schema leaks in public HTML
    assert "SUPABASE" not in content
    assert "SELECT * FROM" not in content
    assert "clinicas.yaml" not in content


def test_serve_login_endpoint_and_hmac_session():
    response = serve_login()
    assert response.status_code == 200
    content = response.body.decode("utf-8")
    assert "hzsaas-shield-logo.jpg" in content
    assert "login-master-card" in content
    assert "Consola RevOps AI" in content
    # Ensure zero hardcoded passwords in login HTML
    assert "admin123" not in content
    assert "HzSaaS2026!" not in content

    token = create_session_token("admin@hzsaas.com", "REVOPS")
    assert verify_session_token(token) is True
    assert verify_session_token("forged:token:123") is False


def test_oklch_tokens_css():
    tokens_path = Path("RevOpsAI/src/web/static/tokens.css")
    tokens = tokens_path.read_text(encoding="utf-8")
    assert "oklch(" in tokens
    assert "--color-paper:" in tokens
    assert "--color-ink:" in tokens
    assert "--color-accent:" in tokens
    assert "Space Grotesk" in tokens
    assert "JetBrains Mono" in tokens


def test_serve_dashboard_endpoint():
    response = serve_dashboard()
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    content = response.body.decode("utf-8")
    assert "RevOps AI" in content
    assert "Kanban" in content or "Bandeja" in content
    assert "dashboard.css" in content
    assert "dashboard.js" in content


def test_static_css_design_tokens():
    css_path = Path("RevOpsAI/src/web/static/dashboard.css")
    css = css_path.read_text(encoding="utf-8")
    # Enforce Anti-AI design tokens
    assert "--bg-app: #09090b" in css
    assert "--border-subtle:" in css
    assert "kanban-container" in css
    assert "slide-drawer" in css


def test_static_js_functionality():
    js_path = Path("RevOpsAI/src/web/static/dashboard.js")
    js = js_path.read_text(encoding="utf-8")
    assert "tenant_clinicas_madrid" in js
    assert "refreshAll" in js
    assert "/api/v1/dashboard/stats" in js
    assert "/api/v1/approval/action" in js
