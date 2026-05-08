"""
Shared utilities for the Prompting Strategy experiment pipeline.

Provides model backend configuration, result schemas, and helper functions
used across filter_dataset.py, run_experiment.py, and analyze_results.py.
"""

import json
import os
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Model Backend Configuration
# ──────────────────────────────────────────────

@dataclass
class ModelConfig:
    """Configuration for a model backend."""
    name: str
    api_base: str
    model_id: str
    env_key: Optional[str]
    cost_per_1m_input: float
    cost_per_1m_output: float
    max_output_tokens: int = 4096
    temperature: float = 0.0
    top_p: float = 1.0
    is_local: bool = False


# Registry of supported models
MODEL_REGISTRY: dict[str, ModelConfig] = {
    "deepseek-v4-flash": ModelConfig(
        name="deepseek-v4-flash",
        api_base="https://openrouter.ai/api/v1",
        model_id="deepseek/deepseek-v4-flash",
        env_key="OPENROUTER_API_KEY",
        cost_per_1m_input=0.30,
        cost_per_1m_output=0.90,
    ),
    "llama-3.3-70b": ModelConfig(
        name="llama-3.3-70b",
        api_base="https://api.groq.com/openai/v1",
        model_id="llama-3.3-70b-versatile",
        env_key="GROQ_API_KEY",
        cost_per_1m_input=0.0,
        cost_per_1m_output=0.0,
    ),
    "nemotron-3-super-120b": ModelConfig(
        name="nemotron-3-super-120b",
        api_base="https://openrouter.ai/api/v1",
        model_id="nvidia/nemotron-3-super-120b-a12b",
        env_key="OPENROUTER_API_KEY",
        cost_per_1m_input=0.30,
        cost_per_1m_output=0.90,
    ),
}


def get_model_config(model_name: str) -> ModelConfig:
    """Get model configuration by name."""
    if model_name not in MODEL_REGISTRY:
        available = ", ".join(MODEL_REGISTRY.keys())
        raise ValueError(f"Unknown model: {model_name}. Available: {available}")
    return MODEL_REGISTRY[model_name]


def get_api_key(model_config: ModelConfig) -> Optional[str]:
    """Retrieve API key from environment for a given model."""
    if model_config.env_key is None:
        return None
    key = os.getenv(model_config.env_key)
    if key is None:
        raise EnvironmentError(
            f"API key not found. Set environment variable: {model_config.env_key}"
        )
    return key


# ──────────────────────────────────────────────
# Prompt Strategy Management
# ──────────────────────────────────────────────

STRATEGY_NAMES = [
    "baseline",
    "chain_of_thought",
    "few_shot",
    "persona",
    "structured_decomposition",
]

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def load_prompt(strategy: str) -> str:
    """Load prompt template for a given strategy."""
    if strategy not in STRATEGY_NAMES:
        available = ", ".join(STRATEGY_NAMES)
        raise ValueError(f"Unknown strategy: {strategy}. Available: {available}")

    prompt_path = PROMPTS_DIR / strategy / "prompt.txt"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8").strip()


# ──────────────────────────────────────────────
# Experiment Result Schema
# ──────────────────────────────────────────────

@dataclass
class ExperimentResult:
    """Schema for a single experiment run result."""
    task_id: str
    strategy: str
    model: str
    repetition: int
    success: bool
    exit_code_prepatch: Optional[int] = None
    exit_code_postpatch: Optional[int] = None
    runtime_seconds: float = 0.0
    tokens_input: int = 0
    tokens_output: int = 0
    cost_usd: float = 0.0
    poc_hash: Optional[str] = None
    poc_size_bytes: Optional[int] = None
    agent_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, d: dict) -> "ExperimentResult":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ──────────────────────────────────────────────
# Task Subset Schema
# ──────────────────────────────────────────────

@dataclass
class TaskEntry:
    """Schema for a filtered task in the subset."""
    task_id: str
    project: str
    vulnerability_type: str
    access_type: str
    poc_size_bytes: Optional[int] = None
    description_preview: str = ""


# ──────────────────────────────────────────────
# File I/O Helpers
# ──────────────────────────────────────────────

def save_json(data: dict | list, path: Path, indent: int = 2) -> None:
    """Save data to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str)
    logger.info(f"Saved: {path}")


def load_json(path: Path) -> dict | list:
    """Load data from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_task_subset(path: Path) -> list[dict]:
    """Load the filtered task subset."""
    data = load_json(path)
    if isinstance(data, dict) and "tasks" in data:
        return data["tasks"]
    return data


def get_result_path(
    results_dir: Path, strategy: str, task_id: str, model: str, rep: int
) -> Path:
    """Generate the path for a result file."""
    safe_task_id = task_id.replace(":", "_")
    return results_dir / strategy / f"{safe_task_id}_{model}_{rep}.json"


# ──────────────────────────────────────────────
# Cost Estimation
# ──────────────────────────────────────────────

def estimate_cost(
    model_config: ModelConfig, tokens_input: int, tokens_output: int
) -> float:
    """Estimate API cost for a single run."""
    input_cost = (tokens_input / 1_000_000) * model_config.cost_per_1m_input
    output_cost = (tokens_output / 1_000_000) * model_config.cost_per_1m_output
    return input_cost + output_cost


# ──────────────────────────────────────────────
# Logging Setup
# ──────────────────────────────────────────────

def setup_logging(level: int = logging.INFO) -> None:
    """Configure logging for experiment scripts."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
