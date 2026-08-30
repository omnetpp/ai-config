#!/usr/bin/env python3
"""Merge-time validation for conformance-review rows.

A rule stated in an agent prompt is advice. A rule checked here is enforced.
Every check below exists because a real agent broke the rule while the rule was
in front of it.

Usage:
    validate-rows.py --spec <spec.psv> --mapped <mapped.psv> [--root <repo>]
                     [--deprecated "17,18,4"]

    spec.psv    rowid | feature | spec | clause | level | summary | observable
    mapped.psv  rowid | status | impact | confidence | evidence | checked

Exit status is 1 when any ERROR is found. WARN lines never fail the run — they
mark rows a human should look at.
"""
import argparse, os, re, sys

def load(path, n):
    rows = {}
    for i, line in enumerate(open(path), 1):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        p = line.split(" | ")
        if len(p) != n:
            print(f"ERROR {path}:{i} has {len(p)} fields, expected {n}")
            rows["__bad__"] = True
            continue
        rows[p[0]] = p[1:]
    return rows

CITE = re.compile(r"\b((?:[\w.\-]+/)+[\w.\-]+\.(?:cc|h|ned|msg|ini|test))(?::(\d+))?")
COND = re.compile(r"\b(if|unless|when|provided that|in the case)\b", re.I)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--mapped", required=True)
    ap.add_argument("--root", default=".")
    ap.add_argument("--deprecated", default="",
                    help="comma-separated message types a spec-set document deprecates")
    ap.add_argument("--post-p6", action="store_true",
                    help="the matrix has been through P6; a plain `Incorrect` is "
                         "allowed, but must cite a reproduction test")
    a = ap.parse_args()

    spec = load(a.spec, 7)
    mapped = load(a.mapped, 6)
    errors = warns = 0
    lines_cache = {}

    def nlines(path):
        if path not in lines_cache:
            try:
                with open(path, "rb") as f:
                    lines_cache[path] = sum(1 for _ in f)
            except OSError:
                lines_cache[path] = None
        return lines_cache[path]

    for rid in sorted(set(spec) - {"__bad__"}):
        if rid not in mapped:
            print(f"ERROR {rid}: enumerated but never mapped")
            errors += 1
            continue
        s, m = spec[rid], mapped[rid]
        summary, status, evidence, checked = s[4], m[0], m[3], m[4]

        # 1. Every cited line must exist. An agent once cited Arp.h:123 in a
        #    123-line file, and five siblings past end of file beside it.
        for path, ln in CITE.findall(evidence):
            full = os.path.join(a.root, path)
            if not os.path.exists(full):
                full = os.path.join(a.root, "src/inet", path)
            n = nlines(full)
            if n is None:
                print(f"ERROR {rid}: cited file does not exist: {path}")
                errors += 1
            elif ln and int(ln) > n:
                print(f"ERROR {rid}: cited {path}:{ln} but the file has {n} lines")
                errors += 1

        # 2. A clause with two obligations needs a verdict for each.
        #    " and " inside a noun list ("Flow Label, Source Address and
        #    Destination Address") is one obligation, not two. The IPv6 run
        #    raised 36 of these and only a handful were real, so a comma before
        #    the conjunction downgrades the check to a warning.
        if " and " in summary.lower() and checked.count("[") < 2:
            head = summary.lower().split(" and ")[0]
            if "," in head:
                print(f"WARN  {rid}: `and` may join a noun list rather than two "
                      f"obligations - confirm one verdict is enough")
                warns += 1
            else:
                print(f"ERROR {rid}: summary states two obligations, `checked` has "
                      f"{checked.count('[')} entry")
                errors += 1

        # 2b. A permissive clause cannot be violated, so it cannot be a gap.
        #     The IPv6 run found 11 MAY rows graded Missing or Partial. Grading
        #     an unexercised permission as a gap fills the report with rows that
        #     are not defects. See finding-classes.md, "Permissive clauses".
        if s[3] == "MAY" and status in ("Missing", "Partial", "Incorrect?",
                                        "Incorrect", "Suspect"):
            print(f"ERROR {rid}: level MAY graded {status} - a permission cannot "
                  f"be violated; use Full, or Non-gap naming the absent capability")
            errors += 1

        # 3. A status other than Full/Non-gap must carry an impact.
        if status not in ("Full", "Non-gap") and m[1] in ("--", "—", ""):
            print(f"ERROR {rid}: status {status} carries no impact")
            errors += 1

        # 4. The evidence rule: no plain Incorrect before reproduction.
        #    After P6 has run, the orchestrator promotes reproduced rows to a
        #    plain `Incorrect`, so pass --post-p6 to validate a finished matrix.
        #    Without that flag the check would make a completed matrix
        #    unvalidatable, which the IPv6 run hit at merge time.
        if status == "Incorrect" and not a.post_p6:
            print(f"ERROR {rid}: plain `Incorrect` — only P6 may set it, "
                  f"agents write `Incorrect?`")
            errors += 1
        if status == "Incorrect" and a.post_p6 and ".test" not in evidence:
            print(f"ERROR {rid}: `Incorrect` after P6 but the evidence names no "
                  f"reproduction test")
            errors += 1

        # 5. Agents never decide a simplification.
        if "simplif" in status.lower():
            print(f"ERROR {rid}: an agent may not assign a simplification")
            errors += 1

        # 6. A deprecated message type is probably Non-gap, not Missing.
        for t in filter(None, a.deprecated.split(",")):
            if re.search(rf"\btype {t.strip()}\b", summary, re.I) and status == "Missing":
                print(f"WARN  {rid}: cites deprecated type {t.strip()} and claims "
                      f"Missing — check the deprecating document")
                warns += 1

        # 7. A conditional clause must say why its antecedent holds or does not.
        if COND.search(summary) and status in ("Missing", "Partial") \
           and not COND.search(checked):
            print(f"WARN  {rid}: conditional clause claimed as {status} without "
                  f"stating the antecedent")
            warns += 1

    print(f"\n{len(spec)} rows checked: {errors} errors, {warns} warnings")
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
