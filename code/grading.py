"""Score a security review against the sealed answer key.

The rule is the one pre-registered on 2026-10-10 (``data/PREREGISTRO-pt-br.md``):

- HIT: a finding in ``fetch_sources.py`` within 6 lines of a planted bug whose
  text (``cwe``, ``title``, ``fix``) carries a keyword of that bug's class.
- PARTIAL: only the line, or only the class.
- EXTRA: a finding that matches no planted bug. It is not called a false
  positive without manual review.
"""

from __future__ import annotations

import json
import re
from typing import Any

WINDOW = 6


def findings(text: str) -> list[dict[str, Any]] | None:
    """Extract the findings list from the last parseable JSON block.

    Parameters
    ----------
    text : str
        The model's final answer.

    Returns
    -------
    list of dict or None
        The findings, or ``None`` when no fenced JSON block parses.
    """
    for block in reversed(re.findall(r"```json\s*(.*?)```", text, re.S)):
        try:
            value = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            value = next((v for v in value.values() if isinstance(v, list)), [])
        return value
    return None


def _line(item: dict[str, Any]) -> int | None:
    """Read the first line number a finding points at.

    Parameters
    ----------
    item : dict
        One finding.

    Returns
    -------
    int or None
        The line, or ``None`` when the field is not a number.
    """
    try:
        return int(str(item.get("line", "")).split("-")[0])
    except ValueError:
        return None


def score(text: str, key: list[dict[str, Any]]) -> dict[str, Any]:
    """Grade one review.

    Parameters
    ----------
    text : str
        The model's final answer.
    key : list of dict
        The planted bugs from ``data/answer_key.json``.

    Returns
    -------
    dict
        One verdict per bug id, the number of hits, the number of extras and
        whether the JSON block parsed.
    """
    items = findings(text)
    out: dict[str, Any] = {"json_ok": items is not None}
    used: set[int] = set()
    for bug in key:
        verdict, partial_at = "MISS", None
        for i, item in enumerate(items or []):
            if not str(item.get("file", "")).endswith("fetch_sources.py"):
                continue
            words = " ".join(str(item.get(k, "")) for k in ("cwe", "title", "fix")).lower()
            line = _line(item)
            near = line is not None and abs(line - bug["linha"]) <= WINDOW
            right_class = bug["cwe"].lower() in words or any(w in words for w in bug["palavras"])
            if near and right_class:
                verdict = "HIT"
                used.add(i)
                break
            if (near or right_class) and verdict == "MISS":
                verdict, partial_at = "PARTIAL", i
        if verdict == "PARTIAL":
            used.add(partial_at)
        out[bug["id"]] = verdict
    out["hits"] = sum(out[bug["id"]] == "HIT" for bug in key)
    out["extras"] = len(items or []) - len(used)
    return out
