from __future__ import annotations
import yaml
from pathlib import Path
from typing import Any, Dict

CONFIG_PATH = Path("agent.config.yaml")

def load_agent_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}
