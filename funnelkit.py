#!/usr/bin/env python3
"""awesome-funnel-design — turn a curated list repo into a measurable funnel.

Two tools for list maintainers:
  1. validate   — structure-check a list manifest, including the disclosure
                  fields (sponsored / owned-by-maintainer) that keep a
                  monetized list honest.
  2. track      — ingest exposure/click/conversion events and compute
                  per-entry and overall funnel metrics.
No marketing copy, no ad text, no real list data ships in this repo.
Pure standard library. No network. No secrets. Data currency: 2026-10-11.
"""
from __future__ import annotations

import argparse
import json
import sys

AS_OF = "2026-10-11"

EVENT_TYPES = ("exposure", "click", "conversion")


class InputError(ValueError):
    """Invalid input; CLI maps this to exit code 2."""


# ------------------------------- manifest QA --------------------------------

def validate_manifest(manifest):
    """Structure-check a list manifest. Returns list of issues:
    {"severity": "error"|"warning", "msg": ...}."""
    issues = []
    if not isinstance(manifest, dict):
        return [{"severity": "error", "msg": "manifest is not a JSON object"}]
    meta = manifest.get("meta")
    disc = meta.get("disclosure") if isinstance(meta, dict) else None
    if not isinstance(disc, dict):
        issues.append({"severity": "error",
                       "msg": "meta.disclosure object required (sponsored_slots, owned_products_listed)"})
    else:
        for key in ("sponsored_slots", "owned_products_listed"):
            val = disc.get(key)
            if not isinstance(val, int) or isinstance(val, bool) or val < 0:
                issues.append({"severity": "error",
                               "msg": "meta.disclosure.%s must be a non-negative integer" % key})
    categories = manifest.get("categories")
    if not isinstance(categories, list) or not categories:
        issues.append({"severity": "error", "msg": "categories must be a non-empty list"})
        return issues
    sponsored_count = 0
    for ci, cat in enumerate(categories):
        if not isinstance(cat, dict) or not isinstance(cat.get("name"), str) or not cat["name"].strip():
            issues.append({"severity": "error", "msg": "category #%d missing a name" % ci})
            continue
        entries = cat.get("entries")
        if not isinstance(entries, list) or not entries:
            issues.append({"severity": "error",
                           "msg": "category %r has no entries list" % cat["name"]})
            continue
        for ei, entry in enumerate(entries):
            label = "%s[%d]" % (cat["name"], ei)
            if not isinstance(entry, dict):
                issues.append({"severity": "error", "msg": "entry %s is not an object" % label})
                continue
            if not isinstance(entry.get("name"), str) or not entry["name"].strip():
                issues.append({"severity": "error", "msg": "entry %s missing name" % label})
            url = entry.get("url")
            if not isinstance(url, str) or not (url.startswith("http://") or url.startswith("https://")):
                issues.append({"severity": "error", "msg": "entry %s missing valid http(s) url" % label})
            for flag in ("sponsored", "owned_by_maintainer"):
                if flag not in entry:
                    issues.append({"severity": "warning",
                                   "msg": "entry %s: %s flag absent, defaults to false — make it explicit" % (label, flag)})
                elif not isinstance(entry[flag], bool):
                    issues.append({"severity": "error",
                                   "msg": "entry %s: %s must be boolean" % (label, flag)})
            if entry.get("sponsored") is True:
                sponsored_count += 1
    if isinstance(disc, dict):
        slots = disc.get("sponsored_slots")
        if isinstance(slots, int) and not isinstance(slots, bool) and slots >= 0:
            if sponsored_count > slots:
                issues.append({"severity": "warning",
                               "msg": "%d entries marked sponsored but disclosure declares %d slot(s)"
                                      % (sponsored_count, slots)})
    return issues


# ------------------------------ funnel tracking -----------------------------

def compute_funnel(events):
    """events: iterable of {"ts":..., "entry":..., "event": exposure|click|conversion}.
    Returns per-entry + total metrics. Invalid events are counted, not raised."""
    per = {}
    invalid = 0
    for ev in events:
        if (not isinstance(ev, dict) or ev.get("event") not in EVENT_TYPES
                or not isinstance(ev.get("entry"), str) or not ev["entry"].strip()):
            invalid += 1
            continue
        slot = per.setdefault(ev["entry"], {"exposure": 0, "click": 0, "conversion": 0})
        slot[ev["event"]] += 1
    for stats in per.values():
        stats["ctr"] = round(stats["click"] / stats["exposure"], 4) if stats["exposure"] else None
        stats["cvr"] = round(stats["conversion"] / stats["click"], 4) if stats["click"] else None
    totals = {"exposure": sum(s["exposure"] for s in per.values()),
              "click": sum(s["click"] for s in per.values()),
              "conversion": sum(s["conversion"] for s in per.values()),
              "invalid_events": invalid}
    totals["ctr"] = round(totals["click"] / totals["exposure"], 4) if totals["exposure"] else None
    totals["cvr"] = round(totals["conversion"] / totals["click"], 4) if totals["click"] else None
    return {"as_of": AS_OF, "per_entry": dict(sorted(per.items())),
            "totals": totals,
            "definitions": {"ctr": "click/exposure", "cvr": "conversion/click"}}


def load_events(path):
    events, corrupt = [], 0
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    corrupt += 1
    except OSError as exc:
        raise InputError("cannot read events file: %s" % exc)
    return events, corrupt


# ---------------------------------- CLI -------------------------------------

def cmd_validate(ns):
    try:
        with open(ns.manifest, "r", encoding="utf-8") as fh:
            manifest = json.load(fh)
    except json.JSONDecodeError as exc:
        raise InputError("manifest is not valid JSON: %s" % exc)
    except OSError as exc:
        raise InputError("cannot read manifest: %s" % exc)
    issues = validate_manifest(manifest)
    errors = 0
    for issue in issues:
        print("%s: %s" % (issue["severity"].upper(), issue["msg"]))
        if issue["severity"] == "error":
            errors += 1
    print("manifest validation finished: %d error(s), %d warning(s)"
          % (errors, len(issues) - errors))
    return 1 if errors else 0


def cmd_track(ns):
    events, corrupt = load_events(ns.events)
    result = compute_funnel(events)
    result["totals"]["corrupt_lines"] = corrupt
    if ns.json:
        print(json.dumps(result, indent=2))
        return 0
    t = result["totals"]
    print("Funnel report (as of %s)" % AS_OF)
    print("  totals: exposure=%d click=%d conversion=%d  ctr=%s cvr=%s"
          % (t["exposure"], t["click"], t["conversion"], t["ctr"], t["cvr"]))
    if t.get("invalid_events") or t.get("corrupt_lines"):
        print("  data quality: %d invalid event(s), %d corrupt line(s) skipped"
              % (t["invalid_events"], t["corrupt_lines"]))
    print("  per entry:")
    for entry, s in result["per_entry"].items():
        print("    %-24s exp=%-6d click=%-5d conv=%-4d ctr=%-7s cvr=%s"
              % (entry, s["exposure"], s["click"], s["conversion"], s["ctr"], s["cvr"]))
    return 0


def build_parser():
    p = argparse.ArgumentParser(prog="funnelkit", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="structure-check a list manifest")
    v.add_argument("--manifest", required=True)
    v.set_defaults(func=cmd_validate)

    t = sub.add_parser("track", help="compute funnel metrics from an events JSONL")
    t.add_argument("--events", required=True)
    t.add_argument("--json", action="store_true")
    t.set_defaults(func=cmd_track)
    return p


def main(argv=None):
    ns = build_parser().parse_args(argv)
    try:
        return ns.func(ns)
    except InputError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
