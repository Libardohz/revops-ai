import sys
import importlib
import importlib.util

def test_python_version():
    assert sys.version_info >= (3, 11), "Python 3.11+ es requerido para RevOpsAI"

def test_critical_dependencies_installed():
    required_modules = ["pydantic", "yaml", "pytest"]
    for mod in required_modules:
        assert importlib.util.find_spec(mod) is not None, f"Módulo {mod} debe estar disponible"
