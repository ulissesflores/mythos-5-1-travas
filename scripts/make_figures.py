"""Draw the repository's figures from ``output/results.json``.

Claim map (no figure without a claim):

- ``safeguard_stops.png/.svg`` -> "On the same defensive prompts, Fable 5.1 was
  stopped in 4 of 12 runs and Mythos 5.1 in 0 of 12" (test 1).

Figures are informational and are not part of the hash chain; matplotlib is
needed only here.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "figures"
LABELS = {
    "t1a-triagem": "triage",
    "t1b-correcao": "fix",
    "t1c-teste": "regression test",
    "t1d-modelo-de-ameaca": "threat model",
}


def main() -> None:
    """Write the safeguard-stop figure as PNG and SVG."""
    res = json.loads((ROOT / "output" / "results.json").read_text(encoding="utf-8"))
    t1 = res["test1_safeguards"]
    prompts = list(LABELS)
    fable = [t1["fable-5-1"][p]["stopped"] for p in prompts]
    mythos = [t1["mythos-5-1"][p]["stopped"] for p in prompts]
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=150)
    x = range(len(prompts))
    for offset, values, name, color in (
        (-0.2, fable, "Fable 5.1", "#c2410c"),
        (0.2, mythos, "Mythos 5.1", "#1d4ed8"),
    ):
        xs = [i + offset for i in x]
        ax.bar(xs, values, width=0.4, label=name, color=color)
        for xi, v in zip(xs, values, strict=True):  # label zeros too: a 0 bar is invisible
            ax.text(xi, v + 0.06, str(v), ha="center", va="bottom", color=color, fontsize=10)
    ax.set_xticks(list(x), [LABELS[p] for p in prompts])
    ax.set_ylim(0, 3.4)
    ax.set_yticks([0, 1, 2, 3])
    ax.set_ylabel("runs with a safeguard stop (of 3)")
    ax.set_title("Same defensive prompts: Fable 5.1 stopped in 4 of 12 runs, Mythos 5.1 in 0")
    ax.legend(frameon=False)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(OUT / f"safeguard_stops.{ext}")


if __name__ == "__main__":
    main()
