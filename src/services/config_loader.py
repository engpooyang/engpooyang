"""Loads and caches YAML configuration files."""

from __future__ import annotations

import pathlib

import yaml

from src.models.schemas import CompanyConfig, DirectoryConfig, SpamRulesConfig

CONFIG_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "config"

_company_config: CompanyConfig | None = None
_directory_config: DirectoryConfig | None = None
_spam_rules_config: SpamRulesConfig | None = None


def _load_yaml(filename: str) -> dict:
    path = CONFIG_DIR / filename
    with open(path) as f:
        return yaml.safe_load(f)


def get_company_config() -> CompanyConfig:
    global _company_config
    if _company_config is None:
        _company_config = CompanyConfig(**_load_yaml("company.yml"))
    return _company_config


def get_directory_config() -> DirectoryConfig:
    global _directory_config
    if _directory_config is None:
        _directory_config = DirectoryConfig(**_load_yaml("directory.yml"))
    return _directory_config


def get_spam_rules_config() -> SpamRulesConfig:
    global _spam_rules_config
    if _spam_rules_config is None:
        _spam_rules_config = SpamRulesConfig(**_load_yaml("spam_rules.yml"))
    return _spam_rules_config


def reload_configs() -> None:
    """Force reload all configurations from disk."""
    global _company_config, _directory_config, _spam_rules_config
    _company_config = None
    _directory_config = None
    _spam_rules_config = None
