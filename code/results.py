"""Derive every number the article cites from the frozen evidence.

Pure function of ``data/``: no network, no model call, no clock. Run by
``run_all.py``; asserted by ``tests/test_article_numbers.py``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import grading
import runs

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PROMPTS_T1 = ("t1a-triagem", "t1b-correcao", "t1c-teste", "t1d-modelo-de-ameaca")
MODELS_T1 = ("fable-5-1", "mythos-5-1")
MODELS_T2 = ("mythos", "fable", "opus55")


def test1() -> dict[str, Any]:
    """Count safeguard stops and model fallbacks per prompt and model.

    Returns
    -------
    dict
        ``{model: {prompt: {"runs", "stopped", "fallback"}, "total": {...}}}``.
    """
    out: dict[str, Any] = {}
    for model in MODELS_T1:
        rows: dict[str, Any] = {}
        total = {"runs": 0, "stopped": 0, "fallback": 0}
        for prompt in PROMPTS_T1:
            recs = [runs.load(p) for p in sorted(runs.RUNS.glob(f"test1/{model}-{prompt}-*.json"))]
            row = {
                "runs": len(recs),
                "stopped": sum(runs.safeguard_stops(r) > 0 for r in recs),
                "fallback": sum(runs.fell_back(r) for r in recs),
                "ended_with_answer": sum(r.get("stop_reason") == "end_turn" for r in recs),
            }
            rows[prompt] = row
            for k in total:
                total[k] += row[k]
        rows["total"] = total
        out[model] = rows
    return out


def test2() -> dict[str, Any]:
    """Grade every review run against the sealed answer key.

    Returns
    -------
    dict
        Per model: the per-run grades, served models and list-price cost.
    """
    key = json.loads((DATA / "answer_key.json").read_text(encoding="utf-8"))["falhas"]
    out: dict[str, Any] = {}
    for model in MODELS_T2:
        graded = []
        for path in sorted(runs.RUNS.glob(f"test2/{model}-revisao-*.json")):
            rec = runs.load(path)
            g = grading.score(rec.get("result") or "", key)
            g.update(
                run=path.name,
                served=runs.served_models(rec),
                list_cost_usd=round(runs.list_cost_usd(rec), 3),
            )
            graded.append(g)
        out[model] = graded
    return out


def test3() -> list[dict[str, Any]]:
    """Parse the quota readings in chronological order.

    Returns
    -------
    list of dict
        One reading per file: label, UTC stamp and the three percentages.
    """
    pat = {
        "session": r"Current session: (\d+)%",
        "week_all": r"Current week \(all models\): (\d+)%",
        "week_fable": r"Current week \(Fable\): (\d+)%",
    }
    out = []
    for path in sorted((DATA / "usage").glob("uso-*.txt"), key=lambda p: p.stem.rsplit("-", 1)[1]):
        text = path.read_text(encoding="utf-8")
        label, stamp = path.stem[len("uso-") :].rsplit("-", 1)
        out.append(
            {
                "label": label,
                "utc": stamp,
                **{k: int(re.search(v, text)[1]) for k, v in pat.items()},
            }
        )
    return out


def build() -> dict[str, Any]:
    """Assemble the full results payload.

    Returns
    -------
    dict
        Results of the three tests plus the rehearsal grade.
    """
    key = json.loads((DATA / "answer_key.json").read_text(encoding="utf-8"))["falhas"]
    rehearsal = runs.load(DATA / "runs" / "rehearsal" / "haiku-revisao.json")
    return {
        "test1_safeguards": test1(),
        "test2_planted_bugs": test2(),
        "test3_quota_readings": test3(),
        "rehearsal_haiku_review": grading.score(rehearsal.get("result") or "", key),
    }
