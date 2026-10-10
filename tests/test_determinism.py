"""Deriving the results twice gives byte-identical output."""

from __future__ import annotations

import json

import results


def test_build_is_deterministic():
    """Two builds serialize to the same bytes."""
    first = json.dumps(results.build(), sort_keys=True)
    second = json.dumps(results.build(), sort_keys=True)
    assert first == second
