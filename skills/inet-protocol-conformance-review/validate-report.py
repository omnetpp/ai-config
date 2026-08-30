#!/usr/bin/env python3
"""Validate a conformance report directory before the P8 checkpoint.

    validate-report.py doc/protocols/<family> [--no-context]

Checks, per finding entry in conformance-review.md:
  - Priority, Context and Context files fields are present
  - Context is three to five sentences
  - the Context files directory exists
  - Priority equals its derivation from Status, Impact and Level
  - entries appear in non-decreasing priority order
And over every .md file in the directory:
  - every ](#anchor) link resolves to exactly one <a id="anchor"> in the target file
  - no anchor is defined twice in one file
  - every relative file link exists on disk

--no-context skips the per-finding field checks, for a report that predates workflow v3.
"""
import argparse
import os
import re
import sys

PRIORITY_RULES = [
    ("P6", lambda st, im, lv: im == "cosmetic"),
    ("P1", lambda st, im, lv: st == "Incorrect"),
    # A finding whose Status is Suspect reached that status only if Suspect is its most
    # common gap status; the report's grouping rule enforces that, not this table.
    ("P2", lambda st, im, lv: st == "Suspect"),
    ("P3", lambda st, im, lv: st in ("Missing", "Partial") and lv in ("MUST", "STRUCTURAL") and im == "results"),
    ("P4", lambda st, im, lv: st in ("Missing", "Partial") and lv in ("MUST", "STRUCTURAL") and im == "scope"),
    ("P5", lambda st, im, lv: st in ("Missing", "Partial") and lv == "SHOULD"),
]


NEGATIVE = {"MUST NOT": "MUST", "SHOULD NOT": "SHOULD"}


def derive_priority(status, impact, level):
    level = NEGATIVE.get(level, level)
    for name, rule in PRIORITY_RULES:
        if rule(status, impact, level):
            return name
    return None


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z`\[(])", text.strip())
    return [p for p in parts if p]


def field(block, name):
    m = re.search(r"\*\*" + re.escape(name) + r":\*\*\s*`?([^`·\n]+?)`?\s*(?:·|$)", block, re.M)
    return m.group(1).strip() if m else None


warnings = []


def check_findings(report_text, report_dir):
    errors = []
    heads = list(re.finditer(r'^### <a id="(f\d+)"></a>', report_text, re.M))
    if not heads:
        return ["no finding entries found (expected headings like '### <a id=\"f1\"></a>F1 — ...')"]
    order = []
    for i, h in enumerate(heads):
        fid = h.group(1)
        end = heads[i + 1].start() if i + 1 < len(heads) else len(report_text)
        block = report_text[h.start():end]
        pri, st, im, lv = (field(block, n) for n in ("Priority", "Status", "Impact", "Level"))
        if pri is None:
            errors.append(f"{fid}: no **Priority:** field")
        else:
            order.append((fid, pri))
            if st and im and lv:
                want = derive_priority(st, im, lv)
                if want is None:
                    errors.append(f"{fid}: no priority rule matches Status={st} Impact={im} Level={lv}")
                elif want != pri:
                    errors.append(f"{fid}: Priority {pri} but Status={st} Impact={im} Level={lv} derives {want}")
            else:
                errors.append(f"{fid}: cannot derive priority, missing Status/Impact/Level")
        m = re.search(r"\*\*Context:\*\*\s*(.+?)(?=\n- \*\*|\n\n|\Z)", block, re.S)
        if not m:
            errors.append(f"{fid}: no **Context:** field")
        else:
            body = m.group(1)
            n = len(sentences(body))
            if not 3 <= n <= 5:
                errors.append(f"{fid}: Context has {n} sentences, need 3 to 5")
            w = len(body.split())
            if w > 200:
                warnings.append(f"{fid}: Context is {w} words; past ~200 the surplus "
                                f"belongs in the context directory")
        m = re.search(r"\*\*Context files:\*\*\s*\[[^\]]*\]\(([^)]+)\)", block)
        if not m:
            errors.append(f"{fid}: no **Context files:** link")
        elif not os.path.isdir(os.path.join(report_dir, m.group(1))):
            errors.append(f"{fid}: Context files directory {m.group(1)} does not exist")
        else:
            d = os.path.join(report_dir, m.group(1))
            if not any(f.endswith(".md") for f in os.listdir(d)):
                errors.append(f"{fid}: Context files directory {m.group(1)} holds no .md file")
    for (a, pa), (b, pb) in zip(order, order[1:]):
        if pb < pa:
            errors.append(f"{b} ({pb}) follows {a} ({pa}): findings are not in priority order")
    return errors


ROWCELL = re.compile(r"\[`?([A-Z0-9]+-\d+)`?\]")
GAP = ("Missing", "Partial", "Incorrect", "Suspect")


def check_coverage(report_text, report_dir):
    """Every gap row belongs to exactly one finding.

    The IPv6 review shipped with 303 of its 542 gap rows attached to no finding at
    all, and two rows attached to two findings at once. Neither is visible by reading:
    the report looks complete either way.
    """
    errors = []
    owner = {}
    for m in re.finditer(r'^### <a id="(f\d+)"></a>(.*?)(?=^### |\Z)',
                         report_text, re.S | re.M):
        fid, block = m.group(1), m.group(2)
        # anchored to the bullet: the entry's summary line carries `**Rows:** <count>`
        # under the same label, and an unanchored search finds the count instead.
        rows = re.search(r"^- \*\*Rows:\*\*(.+)", block, re.M)
        if not rows:
            errors.append(f"{fid}: no **Rows:** list")
            continue
        for rid in ROWCELL.findall(rows.group(1)):
            if rid in owner:
                errors.append(f"{rid} is claimed by both {owner[rid]} and {fid}")
            owner[rid] = fid
    census = os.path.join(report_dir, "conformance-matrix.md")
    text = report_text
    if os.path.isfile(census):
        text += open(census, encoding="utf-8").read()
    gaps = set()
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        m = ROWCELL.search(line)
        if m and any("`%s`" % g in line for g in GAP):
            gaps.add(m.group(1))
    orphan = sorted(gaps - set(owner))
    if orphan:
        errors.append(f"{len(orphan)} gap rows belong to no finding: "
                      + " ".join(orphan[:12]) + (" ..." if len(orphan) > 12 else ""))
    return errors


def check_links(report_dir):
    errors = []
    md = {f: open(os.path.join(report_dir, f), encoding="utf-8").read()
          for f in os.listdir(report_dir) if f.endswith(".md")}
    anchors = {}
    for f, text in md.items():
        ids = re.findall(r'<a id="([^"]+)"></a>', text)
        dup = sorted({a for a in ids if ids.count(a) > 1})
        for a in dup:
            errors.append(f"{f}: anchor {a} defined {ids.count(a)} times")
        anchors[f] = set(ids)
    for f, text in md.items():
        for target in re.findall(r"\]\(([^)\s]+)\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            path, _, frag = target.partition("#")
            tf = f if path == "" else path
            if path:
                full = os.path.normpath(os.path.join(report_dir, path))
                if not os.path.exists(full):
                    errors.append(f"{f}: link target {path} does not exist")
                    continue
            if frag:
                if tf in anchors:
                    if frag not in anchors[tf]:
                        errors.append(f"{f}: dangling link #{frag} into {tf}")
                elif not re.fullmatch(r"L\d+", frag):
                    errors.append(f"{f}: fragment #{frag} into non-markdown {tf}")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report_dir")
    ap.add_argument("--no-context", action="store_true",
                    help="skip the per-finding field checks (pre-v3 report)")
    a = ap.parse_args()
    report = os.path.join(a.report_dir, "conformance-review.md")
    if not os.path.isfile(report):
        sys.exit(f"no conformance-review.md in {a.report_dir}")
    text = open(report, encoding="utf-8").read()
    errors = check_links(a.report_dir)
    if not a.no_context:
        errors += check_findings(text, a.report_dir)
        errors += check_coverage(text, a.report_dir)
    for e in errors:
        print("ERROR", e)
    for w in warnings:
        print("WARN ", w)
    print(f"{len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
