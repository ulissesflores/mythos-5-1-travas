# Changelog

All notable changes to this project are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning: [SemVer](https://semver.org/).

## [1.0.0] - 2026-10-10

### Changed
- First citable version: metadata bumped to 1.0.0 and the Zenodo deposit opened, immediately before the release that mints the DOI.
- DOI minted by the `v1.0.0-rc1` release: concept DOI [10.5281/zenodo.23287128](https://doi.org/10.5281/zenodo.23287128), version DOI [10.5281/zenodo.23287129](https://doi.org/10.5281/zenodo.23287129); embedded in README, CITATION.cff and codemeta.json.

## [0.1.0] - 2026-10-10

### Added
- Pre-registration (pt-BR, binding) and English summary.
- Frozen run records: 24 test-1 runs, 9 test-2 runs, 2 rehearsal runs; 6 quota readings.
- `code/` derivation (`runs.py`, `grading.py`, `results.py`), `run_all.py`, `make_provenance.py`.
- Test suite: article numbers, grader (positive and negative cases), pre-registration hashes, determinism.
- Harness frozen as pre-registered: `plant.py`, `run_one.py`, `grade_cli.py`, `read_usage.sh`.
- Figure `output/figures/safeguard_stops.{png,svg}`; README, REPRODUCIBILITY, findings, metadata (CITATION.cff, codemeta.json, .zenodo.json closed).
