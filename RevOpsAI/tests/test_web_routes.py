"""Tests for Web Dashboard route, template serving, and static asset delivery."""

import pytest
from pathlib import Path
from RevOpsAI.src.api.routes import serve_dashboard
from RevOpsAI.src.api.main import root_landing


def test_dashboard_files_exist():
    html_path = Path("RevOpsAI/src/web/templates/dashboard.html")
    landing_path = Path("RevOpsAI/src/web/templates/landing.html")
    tokens_path = Path("RevOpsAI/src/web/static/tokens.css")
    css_path = Path("RevOpsAI/src/web/static/dashboard.css")
    js_path = Path("RevOpsAI/src/web/static/dashboard.js")

    assert html_path.exists()
    assert landing_path.exists()
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
    assert "tokens.css" in content
    assert "bento-grid" in content
    assert "calculadora-roi" in content


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
