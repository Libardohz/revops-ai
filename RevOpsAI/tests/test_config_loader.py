import pytest
from pathlib import Path
from pydantic import ValidationError
from RevOpsAI.src.core.config_loader import load_sector_config, SectorConfig

def test_loads_clinicas_config_successfully():
    config = load_sector_config("RevOpsAI/config/sectors/clinicas.yaml")
    assert isinstance(config, SectorConfig)
    assert config.sector_id == "clinicas_salud_v1"
    assert "diagnosticos_medicos_especificos" in config.compliance.strictly_forbidden_topics
    assert config.scoring.min_qualification_score == 65
    assert "google_maps" in config.research.primary_sources
    assert config.scoring.weights["digital_gap"] == 0.5

def test_load_sector_config_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_sector_config("RevOpsAI/config/sectors/non_existent.yaml")

def test_load_sector_config_invalid_schema(tmp_path):
    invalid_file = tmp_path / "invalid.yaml"
    invalid_file.write_text("sector_id: invalid_sample\ncompliance: {}\n", encoding="utf-8")
    with pytest.raises(ValidationError):
        load_sector_config(invalid_file)

def test_load_sector_config_invalid_yaml_structure(tmp_path):
    not_a_dict_file = tmp_path / "not_dict.yaml"
    not_a_dict_file.write_text("- item1\n- item2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="expected mapping"):
        load_sector_config(not_a_dict_file)

