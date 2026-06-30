"""
conftest.py — Disables third-party pytest plugins that require unavailable
system-level dependencies (e.g., langsmith requires pydantic which is not
installed in this project's virtual environment).
"""
collect_ignore_glob = []


def pytest_configure(config):
    # Prevent langsmith's pytest plugin from loading (it requires pydantic
    # and other global dependencies not available in this project's environment)
    config.pluginmanager.set_blocked("langsmith")
