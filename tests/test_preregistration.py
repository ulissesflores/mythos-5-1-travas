"""The prompts, key and harness are the ones hashed in the pre-registration.

``data/PREREGISTRO-pt-br.md`` lists the first 16 hex digits of the SHA-256 of
each file, written before any paid run. If a file here drifted from that record,
the result would no longer be the pre-registered one.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREREG = (ROOT / "data" / "PREREGISTRO-pt-br.md").read_text(encoding="utf-8")

# name in the pre-registration -> path in this repository
RENAMED = {
    "plantar.py": "harness/plant.py",
    "corrigir.py": "harness/grade_cli.py",
    "gabarito.json": "data/answer_key.json",
    "prompts/revisao.txt": "data/prompts/revisao.txt",
    "prompts/t1a-triagem.txt": "data/prompts/t1a-triagem.txt",
    "prompts/t1b-correcao.txt": "data/prompts/t1b-correcao.txt",
    "prompts/t1c-teste.txt": "data/prompts/t1c-teste.txt",
    "prompts/t1d-modelo-de-ameaca.txt": "data/prompts/t1d-modelo-de-ameaca.txt",
}


def _prefix(path):
    """Return the first 16 hex digits of a file's SHA-256.

    Parameters
    ----------
    path : str
        Path relative to the repository root.

    Returns
    -------
    str
        The digest prefix.
    """
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()[:16]


def test_frozen_files_match_the_preregistration():
    """Prompts, key, planter and grader are byte-identical to the registered ones."""
    for name, path in RENAMED.items():
        recorded = re.search(rf"`{re.escape(name)}` `([0-9a-f]{{16}})`", PREREG)
        assert recorded, name
        assert _prefix(path) == recorded[1], name


def test_runner_matches_its_last_registered_version():
    """The runner equals the last version logged (1.2), before any paid run."""
    versions = re.findall(r"`rodar\.py` `([0-9a-f]{16})`", PREREG)
    assert versions, "runner hash missing from the pre-registration"
    assert _prefix("harness/run_one.py") == versions[-1]
