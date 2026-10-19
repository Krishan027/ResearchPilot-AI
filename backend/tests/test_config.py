
from app.core.config import Settings


def test_default_app_name():
    settings = Settings()

    assert settings.app_name == "ResearchPilot AI"


def test_default_app_version():
    settings = Settings()

    assert settings.app_version == "0.1.0"


def test_default_debug_mode():
    settings = Settings()

    assert settings.debug is False
