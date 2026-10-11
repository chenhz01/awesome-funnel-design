# Changelog

All notable changes to this project are documented here.

## v0.1.1 — 2026-10-11 (round 2: audit + revision)

### Changed
- **Completeness (+25%)**: FAQ 4 → 5 entries; new entry explains tracker-free
  exposure collection (server-side logs + mandatory definition documentation).
- **Correctness**: track report now separates corrupt lines from invalid
  events in its data-quality line; boolean-flag type errors are hard errors
  while absent flags remain warnings (documented rationale in FAQ).
- **Clarity**: typo fixed in Core Assumptions ("Maintainners" → "Maintainers");
  intro paragraph audited at 43 words (<=60 limit, rule 16).

### Verified
- self_test.py re-run after revision: all three tiers PASS
  (functional 4 / error-path 4 / edge 5 = 13 tests).

## v0.1.0 — 2026-10-11 (initial draft)

### Added
- `funnelkit.py`: `validate` (manifest structure + mandatory disclosure
  fields: sponsored_slots, owned_products_listed, per-entry sponsored /
  owned_by_maintainer flags), `track` (exposure/click/conversion funnel,
  per-entry ctr/cvr, corrupt-line tolerance).
- `self_test.py`: functional / error-path / edge three-tier suite
  (fixtures invented; zero real list data or marketing copy).
- README, MIT LICENSE, ALIGNMENT.md (16-item audit).
