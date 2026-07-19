"""
Central configuration loader.

Priority (highest → lowest):
  1. Environment variables / .env  — secrets and per-environment overrides
  2. config.json                   — non-secret defaults and structured inputs

Usage:
    from utils.config import cfg
    print(cfg.BASE_URL)
    print(cfg.OPENAI_API_KEY)
    print(cfg.raw["test_data"]["users"])   # access full JSON tree
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Load config.json ──────────────────────────────────────────────────────────
_CONFIG_JSON_PATH = Path(__file__).parent.parent / "config.json"

def _load_json() -> dict:
    if _CONFIG_JSON_PATH.exists():
        with open(_CONFIG_JSON_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}

_json = _load_json()


def _jget(keys: str, default=None):
    """Dot-separated key path into the JSON dict, e.g. 'core.base_url'."""
    node = _json
    for key in keys.split("."):
        if not isinstance(node, dict):
            return default
        node = node.get(key, default)
    return node if node is not None else default


def _resolve(env_key: str, json_path: str, default: str = "", required: bool = False):
    """Return env var if set, else JSON value, else default."""
    value = os.getenv(env_key, "").strip()
    if value:
        return value
    value = str(_jget(json_path, default)).strip()
    if required and not value:
        raise EnvironmentError(
            f"Required config '{env_key}' is not set in .env or config.json ({json_path})."
        )
    return value


# ── Config dataclass ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Config:
    # ── Core ──────────────────────────────────────────────
    BASE_URL: str = field(default_factory=lambda: _resolve("BASE_URL", "core.base_url", required=True))
    IMPLICIT_WAIT: int = field(default_factory=lambda: int(_resolve("IMPLICIT_WAIT", "core.implicit_wait", "10")))
    EXPLICIT_WAIT: int = field(default_factory=lambda: int(_resolve("EXPLICIT_WAIT", "core.explicit_wait", "20")))

    # ── Browser ───────────────────────────────────────────
    BROWSER: str = field(default_factory=lambda: _resolve("BROWSER", "browser.default", "chrome"))
    HEADLESS: bool = field(default_factory=lambda: _resolve("HEADLESS", "browser.headless", "false").lower() == "true")

    # ── AI / LLM ─────────────────────────────────────────
    OPENAI_API_KEY: str = field(default_factory=lambda: _resolve("OPENAI_API_KEY", "ai.openai_api_key"))
    OPENAI_MODEL: str = field(default_factory=lambda: _resolve("OPENAI_MODEL", "ai.openai_model", "gpt-4o"))
    ANTHROPIC_API_KEY: str = field(default_factory=lambda: _resolve("ANTHROPIC_API_KEY", "ai.anthropic_api_key"))
    ANTHROPIC_MODEL: str = field(default_factory=lambda: _resolve("ANTHROPIC_MODEL", "ai.anthropic_model", "claude-sonnet-4-5"))

    # ── Test API ─────────────────────────────────────────
    TEST_API_KEY: str = field(default_factory=lambda: _resolve("TEST_API_KEY", "test_api.api_key"))
    TEST_API_BASE_URL: str = field(default_factory=lambda: _resolve("TEST_API_BASE_URL", "test_api.base_url"))

    # ── Auth credentials ─────────────────────────────────
    TEST_USER_EMAIL: str = field(default_factory=lambda: _resolve("TEST_USER_EMAIL", "credentials.test_user.email"))
    TEST_USER_PASSWORD: str = field(default_factory=lambda: _resolve("TEST_USER_PASSWORD", "credentials.test_user.password"))
    ADMIN_USER_EMAIL: str = field(default_factory=lambda: _resolve("ADMIN_USER_EMAIL", "credentials.admin_user.email"))
    ADMIN_USER_PASSWORD: str = field(default_factory=lambda: _resolve("ADMIN_USER_PASSWORD", "credentials.admin_user.password"))

    # ── Database ─────────────────────────────────────────
    DB_HOST: str = field(default_factory=lambda: _resolve("DB_HOST", "database.host", "localhost"))
    DB_PORT: int = field(default_factory=lambda: int(_resolve("DB_PORT", "database.port", "5432")))
    DB_NAME: str = field(default_factory=lambda: _resolve("DB_NAME", "database.name"))
    DB_USER: str = field(default_factory=lambda: _resolve("DB_USER", "database.user"))
    DB_PASSWORD: str = field(default_factory=lambda: _resolve("DB_PASSWORD", "database.password"))

    # ── Reporting / notifications ─────────────────────────
    HTML_REPORT_PATH: str = field(default_factory=lambda: _resolve("HTML_REPORT_PATH", "reporting.html_report_path", "reports/report.html"))
    SCREENSHOT_DIR: str = field(default_factory=lambda: _resolve("SCREENSHOT_DIR", "reporting.screenshot_dir", "reports/screenshots"))
    SLACK_WEBHOOK_URL: str = field(default_factory=lambda: _resolve("SLACK_WEBHOOK_URL", "reporting.slack_webhook_url"))
    EMAIL_NOTIFICATION_ADDRESS: str = field(default_factory=lambda: _resolve("EMAIL_NOTIFICATION_ADDRESS", "reporting.email_notification_address"))

    # ── Raw JSON tree (for structured data like test_data.users) ─────────────
    raw: dict = field(default_factory=lambda: _json)

    # ── Device (SFTP / EWS) ──────────────────────────────
    DEVICE_HOST: str = field(default_factory=lambda: _resolve("DEVICE_HOST", "device.host", "15.77.36.63"))
    DEVICE_SFTP_PORT: int = field(default_factory=lambda: int(_resolve("DEVICE_SFTP_PORT", "device.sftp_port", "22")))
    DEVICE_SFTP_USER: str = field(default_factory=lambda: _resolve("DEVICE_SFTP_USER", "device.sftp_user", "root"))
    DEVICE_SFTP_PASSWORD: str = field(default_factory=lambda: _resolve("DEVICE_SFTP_PASSWORD", "device.sftp_password"))

    # ── Stratus Signal Management ─────────────────────────
    SIGNAL_CLIENT_CREDENTIALS: str = field(default_factory=lambda: _resolve("SIGNAL_CLIENT_CREDENTIALS", "signal.client_credentials"))


# Singleton — import this everywhere
cfg = Config()
