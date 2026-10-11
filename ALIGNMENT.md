# Alignment Audit (Rules 85-100 / 16 items) — awesome-funnel-design

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | Safety/Ethics section | N/A | Non-security-domain toolkit. Ethics surface (disclosure integrity, no covert tracking) is addressed in Design Trade-offs and Limits. |
| 2 | Privacy de-identification | PASS | grep `(sk-\|ghp_\|api[_-]?key\s*=\s*['"][A-Za-z0-9])` = 0 hits; no real names/emails; zero tracking beacons/cookies; fixture URLs use example domains. |
| 3 | Copyright boundary | PASS | Source repo referenced only as a paraphrased one-sentence pattern description; no list content, ad text, or >50-word copied text anywhere; test fixtures invented. LICENSE (MIT) present. |
| 4 | Fact-check labeling | PASS | "2026 state of the art" claim stamped as of 2026-10-11; three-event-type sufficiency labeled `[estimated]`; no unmeasured perf numbers. |
| 5 | Confidence grading | PASS | README Confidence block: High (contract implementation, tested) + Medium (event vocabulary sufficiency), each with rationale. |
| 6 | Plan B built-in | PASS | README "Minimal Fallback": grep-based counting + plain-JSON validate output for any CI. |
| 7 | Timeout preset | PASS | Quickstart: ~1 s per step + full self-test ~15 s, staged path. |
| 8 | Rule conflict arbitration | PASS | README "Design Trade-offs": disclosure integrity > metric comparability > simplicity > coverage. |
| 9 | Version changelog | PASS | CHANGELOG.md: v0.1.0 + v0.1.1 with improvements traced. |
| 10 | Exemption instruction | N/A | Session-level governance rule; static repo N/A. |
| 11 | External knowledge cutoff | PASS | "as of 2026-10-11" stamped in header and funnel report output. |
| 12 | Assumptions explicit | PASS | README `[Core Assumptions]`: 4 items (minimal event vocabulary, low-cost disclosure adoption, self-reported logs, conversion-over-stars priority). |
| 13 | Logic-check trio | PASS | self_test.py: functional 4 / error-path 4 / edge 5 (empty events, corrupt lines, unknown event type, 100k-char entry name, corrupt manifest) — all PASS. |
| 14 | Socratic FAQ | PASS | FAQ "When NOT to use this toolkit?" with 3 concrete anti-cases; 5 FAQ entries total after round 2. |
| 15 | Pareto iteration | PASS | v0.1.1: README completeness +25% (FAQ 4→5, tracker-free exposure guidance); data-quality reporting fix; typo fix; tests re-run PASS. |
| 16 | Ultimate fallback (60-word entry) | PASS | Intro paragraph = 43 words, states what it does and what it deliberately excludes. |

Audit date: 2026-10-11. Auditor: zhengming W5 (self-audit, round 2).
