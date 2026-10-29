"""Tests for production packaging files, Docker configurations, and environment templates."""

from pathlib import Path


def test_packaging_files_exist():
    dockerfile = Path("RevOpsAI/Dockerfile")
    compose = Path("RevOpsAI/docker-compose.yml")
    env_example = Path("RevOpsAI/.env.example")
    readme = Path("RevOpsAI/README.md")

    assert dockerfile.exists()
    assert compose.exists()
    assert env_example.exists()
    assert readme.exists()


def test_dockerfile_and_compose_content():
    dockerfile = Path("RevOpsAI/Dockerfile").read_text(encoding="utf-8")
    compose = Path("RevOpsAI/docker-compose.yml").read_text(encoding="utf-8")
    env_example = Path("RevOpsAI/.env.example").read_text(encoding="utf-8")

    assert "python:3.11-slim" in dockerfile
    assert "uvicorn" in dockerfile
    assert "postgres:16" in compose
    assert "DATABASE_URL" in compose
    assert "META_WA_TOKEN" in env_example
