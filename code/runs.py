"""Load the frozen run records and read the signals each one carries.

Every file under ``data/runs/`` is the JSON that ``claude -p --output-format json``
returned for one run, with the message stream kept under ``_mensagens`` and the
harness metadata under ``_meta``. Nothing here calls a model.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / "data" / "runs"


def load(path: Path) -> dict[str, Any]:
    """Read one run record.

    Parameters
    ----------
    path : pathlib.Path
        JSON file written by ``harness/run_one.py``.

    Returns
    -------
    dict
        The parsed record.
    """
    return json.loads(path.read_text(encoding="utf-8"))


def served_models(run: dict[str, Any]) -> list[str]:
    """List the models that actually served a run.

    Parameters
    ----------
    run : dict
        A run record.

    Returns
    -------
    list of str
        Model ids found in ``modelUsage``, sorted. More than one id means the
        session switched model mid-run.
    """
    return sorted((run.get("modelUsage") or {}).keys())


def fell_back(run: dict[str, Any]) -> bool:
    """Tell whether a run was moved to another model by a refusal fallback.

    Parameters
    ----------
    run : dict
        A run record.

    Returns
    -------
    bool
        ``True`` when the stream holds a ``model_refusal_fallback`` system event.
    """
    return any(
        m.get("type") == "system" and m.get("subtype") == "model_refusal_fallback"
        for m in run.get("_mensagens", [])
    )


def safeguard_stops(run: dict[str, Any]) -> int:
    """Count the safeguard interventions the client recorded for a run.

    Parameters
    ----------
    run : dict
        A run record.

    Returns
    -------
    int
        The ``safety_stops`` field, ``0`` when absent.
    """
    return int(run.get("safety_stops") or 0)


def list_cost_usd(run: dict[str, Any]) -> float:
    """Return the tool's list-price estimate for a run.

    Parameters
    ----------
    run : dict
        A run record.

    Returns
    -------
    float
        ``total_cost_usd``. The account is a subscription, so this is an
        estimate at list price, not money spent.
    """
    return float(run.get("total_cost_usd") or 0.0)
