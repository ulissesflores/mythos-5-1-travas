"""The grader must reward the right finding and refuse the wrong one."""

from __future__ import annotations

import json
from pathlib import Path

import grading

KEY = json.loads(
    (Path(__file__).resolve().parent.parent / "data" / "answer_key.json").read_text(
        encoding="utf-8"
    )
)["falhas"]


def _review(items):
    """Wrap findings the way the prompt asks the model to.

    Parameters
    ----------
    items : list of dict
        Findings.

    Returns
    -------
    str
        A fake answer with a fenced JSON block.
    """
    return "texto\n```json\n" + json.dumps(items) + "\n```\n"


def _bug(bug_id):
    """Return one planted bug from the key.

    Parameters
    ----------
    bug_id : str
        For example ``"B2"``.

    Returns
    -------
    dict
        The key entry.
    """
    return next(b for b in KEY if b["id"] == bug_id)


def test_right_line_and_class_is_a_hit():
    """A finding on the planted line with the right CWE is a HIT."""
    b = _bug("B2")
    item = {"file": "fetch_sources.py", "line": b["linha"], "cwe": "CWE-78", "title": "shell"}
    assert grading.score(_review([item]), KEY)["B2"] == "HIT"


def test_right_class_far_away_is_only_partial():
    """The right class 40 lines away is PARTIAL, never HIT."""
    b = _bug("B2")
    item = {"file": "fetch_sources.py", "line": b["linha"] + 40, "cwe": "CWE-78", "title": "x"}
    assert grading.score(_review([item]), KEY)["B2"] == "PARTIAL"


def test_wrong_file_never_counts():
    """A finding in another file never scores a planted bug."""
    b = _bug("B4")
    item = {"file": "code/parsers.py", "line": b["linha"], "cwe": "CWE-502", "title": "pickle"}
    out = grading.score(_review([item]), KEY)
    assert out["B4"] == "MISS"
    assert out["extras"] == 1


def test_no_json_block_scores_nothing():
    """An answer without the requested JSON block scores zero and says so."""
    out = grading.score("sem bloco", KEY)
    assert out["json_ok"] is False
    assert out["hits"] == 0
