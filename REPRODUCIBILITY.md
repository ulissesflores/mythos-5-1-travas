# Reproducibility

## Two seals

| Kind | What it means | Where it lives |
|---|---|---|
| **Derivation** | Counting and grading over the frozen run records. Reproducible forever, offline, no model called. | `code/`, `tests/`, `output/results.json` |
| **Frozen evidence** | What each model answered on 2026-10-10, through Claude Code 2.1.296 on a Claude Max subscription, inside the Defense Access tier of Anthropic's Cyber Verification Program. Cannot be re-run identically: models, safeguards and quota accounting change, and the access tier is account-specific. | `data/runs/`, `data/usage/` |

## Track 1 - offline replication (seconds)

```bash
pip install -r requirements.txt
python run_all.py                    # derive -> test -> reseal
python make_provenance.py --verify   # check the committed seal without rebuilding
```

## Track 2 - re-running the experiment (needs your own access)

1. Regenerate the sealed target: `python3 harness/plant.py <clone of ai-energy-claim-provenance at d279806> <dest> <key.json>`. The key it writes must equal `data/answer_key.json`.
2. Run each prompt: `python3 harness/run_one.py <dest> <model> data/prompts/<prompt>.txt <out.json>`.
3. Grade reviews: `python3 harness/grade_cli.py data/answer_key.json <out>.json ...`.
4. Read quota between blocks: `harness/read_usage.sh <label> <dir>`.

Your numbers will differ. Safeguards are retuned over time, and a different tier (or no tier) changes test 1 by design. Mythos 5.1 needs a verification-program grant.

## What cannot be re-run, and other limits

- **Same-day, single target, three repetitions.** Small sample; read test 1 as a contrast on this target, not a rate.
- **Test 2 hit the ceiling.** Textbook bugs; it cannot rank the models.
- **Quota readings have 1% resolution** and other Claude sessions were open on the machine. The reading before the first Mythos block was lost (`harness/read_usage.sh` had a relative path; fixed and logged before the following blocks).
- **`total_cost_usd` is the tool's list-price estimate.** The account is a subscription.
- **Usage captures were trimmed** to the four quota lines; the rest of the `/usage` screen describes unrelated local activity of the author.
- **`harness/` is frozen verbatim** as pre-registered (asserted by `tests/test_preregistration.py`), so it is excluded from lint.
