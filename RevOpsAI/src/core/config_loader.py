"""Sector configuration loader and schema validation for RevOpsAI."""

from pathlib import Path
import yaml
from pydantic import BaseModel, Field


class ComplianceConfig(BaseModel):
    """Compliance constraints and required disclaimers for the sector."""

    strictly_forbidden_topics: list[str]
    required_disclaimer: str


class ResearchConfig(BaseModel):
    """Research data sources and signals to detect for the sector."""

    primary_sources: list[str]
    signals_to_detect: list[str]


class ScoringConfig(BaseModel):
    """Lead scoring parameters and weight distributions."""

    weights: dict[str, float]
    min_qualification_score: int


class SectorConfig(BaseModel):
    """Root configuration model representing the 30% adaptable sector layer."""

    sector_id: str
    compliance: ComplianceConfig
    research: ResearchConfig
    scoring: ScoringConfig


def load_sector_config(filepath: str | Path) -> SectorConfig:
    """Load and validate sector configuration from a YAML file.

    Args:
        filepath: Path to the YAML configuration file.

    Returns:
        SectorConfig: Validated sector configuration instance.

    Raises:
        FileNotFoundError: If the specified configuration file does not exist.
        pydantic.ValidationError: If the configuration schema is invalid.
    """
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"Sector configuration file not found: {filepath}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Invalid YAML structure in {filepath}: expected mapping")

    return SectorConfig(**data)
