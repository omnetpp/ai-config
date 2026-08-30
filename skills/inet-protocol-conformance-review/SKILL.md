---
name: inet-protocol-conformance-review
description: >
  MANUAL START ONLY. Do not invoke this skill on your own initiative, and do not offer to run it
  unprompted. Start it only when the user asks for a protocol conformance review in their own
  words, or names this skill. A question about a protocol, a request to look at some protocol
  code, or a bug in a protocol is NOT a trigger — answer those directly. A full run costs about
  32 agents and several hours, so it is always the user's decision to begin.
  What it does: review one INET protocol family against its standards (RFC, IEEE, 3GPP, ITU-T) and produce a
  living in-repo conformance report: a scope statement, a coverage matrix, findings graded by
  class/impact/confidence, a defaults section, and an accepted-omissions ledger. Use when asked
  to review, audit, or find missing features, implementation gaps, or spec violations in an INET
  protocol, or to check an INET protocol against its RFC or IEEE standard. This is a conformance
  pass, not a general bug hunt — for that use /code-review.
---

# INET protocol conformance review

> **Manual start only.** Never begin a run without an explicit request. If a task merely touches a
> protocol, do that task. If you believe a review would help, say so in one sentence and stop.

Produce, for one **protocol family**, a report that a maintainer uses to plan work: what the
standard requires, what INET implements, and where the two disagree.

The reader is a maintainer who decides what to build next. The report is not user documentation.

## Hard rules

These are not negotiable. A run that breaks one of them is invalid.

1. **No finding from memory.** Every finding cites document, version, and clause. You must have
   read that clause *in this run*, from the cached document. Model knowledge of a protocol is a
   search aid, never evidence. See [spec-sources.md](spec-sources.md).
2. **Enumerate the spec before you read the code.** Phase P3 runs before P4. If you read the
   implementation first, the implementation defines the question, and missing features stay
   invisible.
3. **No `Incorrect` without a reproduction.** A behavior claim needs a simulation run that shows
   it. Without one, the status is `Suspect`. See [finding-classes.md](finding-classes.md).
4. **You never write the ledger.** An agent may propose that a gap is a deliberate simplification.
   Only the user moves a row into `accepted-omissions.md`, at the P8 checkpoint. The ledger
   silences a row in every future run, so it is the user's decision alone.
5. **Never modify `src/`.** This workflow writes documentation and tests. P6 adds tests under
   `tests/protocol/conformance/`, and they stay. Nothing else in the repository changes.
6. **Never commit spec text.** Documents stay in the cache outside the repository. The report
   cites document, title, version, and clause. It quotes at most a short normative fragment, and
   only where the exact wording carries the finding.

## The unit of work

A **protocol family** is the set of directories, NED files, MSG files, and specifications that
make one usable capability. Examples: IPv4 with ARP and ICMP; MPLS with LDP, RSVP-TE, TED, and
PCEP; Ethernet.

A family whose spec-side enumeration passes about **200 rows** splits into **slices**. Each slice
gets its own report file and its own ID prefix, for example `IEEE80211-MAC`, `IEEE80211-MGMT`,
`IEEE80211-PHY`. The index lists each slice as its own row.

**Do not split protocols that generate each other's traffic.** The threshold serves report
usability, and it loses to coupling. The IPv4 pilot enumerated 221 rows and stayed as one report,
because IP forwarding is what triggers ICMP errors, and an ARP failure is what produces a
Destination Unreachable. Splitting them would have cut those findings in half. Subsection the
matrix instead. Split when the parts are genuinely independent, as the 802.11 MAC, management, and
PHY layers are.

`doc/protocols/index.md` is the index and the work queue. See [index-template.md](index-template.md).

## Phases

| # | Phase | Output | Checkpoint |
|---|---|---|---|
| P0 | Inventory entry | Family definition, directory list, proposed spec set | **User approves the spec set** |
| P1 | Spec pack | Documents and errata in the cache, plus a spec manifest | — |
| P2 | Scope statement | Section 1 of the report | **User approves the intent, and approves the agent run** |
| P3 | Spec-only enumeration | Matrix skeleton, one row per spec feature | — |
| P3b | Completeness critic | Requirements P3 missed, and a coverage number | — |
| P4 | Implementation mapping | Status, impact, confidence, evidence, `checked:` per row | — |
| P4b | Catch-up mapping | The P3b rows, mapped | — |
| P5 | Deep pass | Rows for the state machine, the packet formats, the timers | — |
| P6 | Reproduction | Every candidate `Incorrect` confirmed or downgraded | — |
| P7 | Refutation of `Missing` and `Partial` | A recorded verdict per finding | — |
| P7b | False-`Full` hunt | A blind second opinion on the rows nothing else checks | — |
| P8 | Assembly | Report, ledger, index update, commits | **User signs off, then commit** |

Numbering is stable. Phases added later get a letter suffix, because the plain numbers are cited by
reports and plans already on disk.

### P0 — Inventory entry

Name the family. List its directories under `src/inet/`, plus its NED and MSG files. Propose the
spec set: base documents, updates, and the errata page for each. Present the set to the user and
wait. Add or update the row in `doc/protocols/index.md` with status `spec-pack`.

### P1 — Spec pack

Fetch every document into `~/w/ai/spec-cache/<family>/`, by the method in
[spec-sources.md](spec-sources.md). Write `spec-manifest.md` in the report directory: document id,
title, version or date, retrieval date, and local cache filename. The manifest goes into the
repository. The documents do not.

If a document cannot be obtained, **stop**. Set the index status to `spec-blocked`, record what is
missing and why, and tell the user what they must supply. Do not start P3.

### P2 — Scope statement

Read the family's NED files, its chapter in `doc/src/developers-guide/`, and enough of the code to
state what the model intends to cover. Write section 1 of the report: what this family models, at
what fidelity, and what it deliberately leaves out. Cite the developers-guide chapter instead of
repeating it.

Present the scope statement to the user. This decides what counts as a gap, so it must be settled
before enumeration. Ask, in the same message, for approval to run the agents for phases P3 to P7.
That single approval covers the whole family run. Set the index status to `in-review`.

### P3 — Spec-only enumeration

**Do not read the implementation in this phase.**

Fan out 2 to 5 agents, split by document or by clause block. Each agent reads its assigned clauses
from the cache and returns rows in this exact schema:

| field | content |
|---|---|
| `feature` | short name, stable across runs |
| `spec` | document id, for example `RFC 791` |
| `clause` | section number |
| `level` | `MUST`, `SHOULD`, or `MAY`, taken from the spec text |
| `summary` | one sentence stating what the spec requires |
| `observable` | how a conforming node shows it: a frame at an interface, an internal state, or a timer |

`observable` is mandatory. It forces a checkable claim, and it hands the row to the
`generic-protocol-test-authoring` skill nearly unchanged. A requirement with no observable
manifestation is still a row — write `none` and say why.

Target 60 to 200 rows. Merge the agent outputs. Remove duplicates by clause plus feature name.

### P3b — Completeness critic

P3 sets a ceiling nobody measures. A requirement it never enumerated cannot be found by any later
phase, and it leaves no trace — the report looks complete either way. This is the one error class a
spot check cannot detect, because you can only sample rows that exist.

One agent per document group. Each receives the specification and the finished matrix rows for that
document, and answers one question: **which normative statements have no row?** It does not judge
the implementation, and it must not see any code.

**Check its input against the manifest before you launch it.** The critic can only report on
documents it is shown. In the IPv4 pilot the orchestrator grouped the documents by hand and dropped
three of fifteen, so the critic reported them as having no rows at all — they had eleven. A
set-difference between the manifest and the critics' inputs is one line, and without it the critic's
number is wrong in the direction that looks like thoroughness.

Its output is two things: new rows in the P3 schema, and a count. Put the count in the method line —
"the critic found 9 requirements P3 missed" is the only number in the report that says what the
enumeration was worth.

Do not gate P8 on the critic returning nothing. Its own recall is unknown, so a hard gate can loop
without converging.

**Run it again after the catch-up round, and publish whether it converged.** In the IPv4 pilot the
second critic pass still found about 26 requirements, including whole sections of RFC 1812 and
RFC 1122 that both rounds had skipped. Two rounds were not enough, and the report says so. A review
that stops when it runs out of energy should say that, rather than let its row count imply the
document was exhausted.

### P4 — Implementation mapping

One agent per matrix section, over row batches. For each row, find the implementing code and any
existing test. Assign `status`, `impact`, `confidence`, and `evidence`, as defined in
[finding-classes.md](finding-classes.md).

Evidence is a `file:line` reference, a test name, or both. Test evidence comes from `tests/module`,
`tests/unit`, `tests/protocol`, and `tests/fingerprint`. Coverage is uneven, so a missing test is
not evidence of a missing feature.

Agents return plain `file:line` text. P8 turns it into links — do not ask an agent to write markdown
links, because a wrong relative path is harder to spot than a wrong path.

Every row also carries a **`checked:`** list — one entry per obligation the clause imposes, each
with its own verdict:

```
checked: [emits type 12 only when the datagram was discarded -> yes, Ipv4.cc:291]
         [discards on a bad header parameter -> NO, version/IHL falls through Ipv4.cc:282]
```

This exists because of a real failure. A clause imposed two obligations, the agent found the one it
went looking for, marked the row `Full`, and never re-read the clause for the rest. Nothing in the
data recorded which half had been examined, so no later pass could see the omission.

**Enforce it mechanically at merge time, not by asking the agent to self-check.** Run
[validate-rows.py](validate-rows.py) over every batch before it enters the matrix:

    validate-rows.py --spec batch.psv --mapped mapped.psv --root <repo> --deprecated "4,17,18"

It fails the batch on: a cited line that does not exist in its file, a two-obligation clause with one
`checked:` entry, a non-`Full` row with no impact, a plain `Incorrect` from an agent, or an
agent-assigned simplification. It warns on a deprecated message type claimed `Missing`, and on a
conditional clause claimed as a gap without stating its antecedent.

**Every one of those checks exists because an agent broke the rule while the rule was in its
prompt.** Round 2 of the IPv4 pilot produced three citations to lines past the end of their files,
including one supporting a `Full` verdict. It claimed `MUST`-level gaps for message types RFC 6918
deprecates. It faulted the implementation under a clause whose antecedent it never established. All
three rules were stated in the prompt and ignored.

A rule in a prompt is advice. A rule in the validator is enforced. When you find a new failure mode,
add a check rather than a sentence.

Keep `checked:` out of the matrix, which is already eight columns wide. It rides in the working
data, it feeds P7b, and it appears in the report only inside a finding's body.

Allocate a finding ID to every row that is not `Full`. The format is `<FAMILY>-<NNN>`.

**Keep every agent's full return in the working data, keyed by row ID.** Do not reduce it to the
matrix columns. P8 files it into the finding's context directory, where a planning agent reads it.
The same applies to P4b, P5, P6, P7 and P7b: the matrix holds the verdict, and the context
directory holds the reasoning.

### P4b — Catch-up mapping

Map the rows P3b produced, by the same rules. One agent is normally enough.

### P5 — Deep pass

Feature-level rows miss detail inside the core. Run one agent per area over the normative
statements of:

- the state machine and its transitions,
- the packet formats and every field's semantics,
- the timers, their default values, and their bounds.

These agents add rows and refine existing ones. They use the same schema.

### P6 — Reproduction

**First, check whether an existing conformance test already covers the mechanism.** In round 2 of the
IPv4 pilot, seven of nine candidates were already proven by tests committed in round 1 — five shared
one root cause covered by a single test. The reproduction phase shrank from three agents to one. A
committed test does not merely record a finding; it discharges the evidence burden for every later
finding that shares its mechanism.

For every remaining row a mapping agent marked as a candidate `Incorrect`, build a minimal simulation
that shows the behavior. If it reproduces, the status stays `Incorrect`, and the evidence names the
configuration and the observation. If it does not reproduce, downgrade to `Suspect` and say what
was tried. Keep the notes of every attempt, including the failed ones. They go into the finding's
`reproduction.md` at P8, so the next agent does not repeat the attempt.

**The reproduction tests are a deliverable, not scratch work.** They are the only executable proof
the report contains, and the defects they cover are usually untested — that is often why the defect
survived. Keep every test that works.

Write them under `tests/protocol/conformance/`, one file per finding or per closely-related group:

1. **Name the test for the behavior**, not for the bug: `Ipv4HeaderValidation.test`, not
   `ReproChecksumBug.test`. It outlives the defect.
2. **Assert what the standard requires, never what the code does.** A test that asserts the
   defective behavior locks the bug in and turns green forever. This inverts the usual reproduction
   instinct, so state it explicitly to any agent you delegate to.
3. **Mark it `%expected-failure:`**, citing the finding id and the clause. The suite then reports
   `EXPECTEDFAIL` rather than `FAIL`, and the test flips to `PASS` by itself when someone fixes the
   defect. A reproduction test that reports `PASS` on arrival is asserting the wrong thing.
4. **Write a `%description:` that survives without you**: what it checks, which clause, which
   finding id, and one line on the defect.
5. **Check the relative paths.** `ned-path` is written relative to `<test folder>/work/<test name>/`.
   A test moved from `tests/module/` to `tests/protocol/conformance/` goes one level deeper, and
   `tests/protocol` has no `lib` directory.

Commit them **before** the report, as their own commit:

    docs(<family>): protocol conformance tests for <family>

Known gap: `inet_run_protocol_tests` globs `tests/protocol/*.test` non-recursively
(`python/inet/test/all.py`, `get_opp_test_tasks`), so a subdirectory is not discovered. Run the
tests directly with `opp_test`, and tell the user the runner needs a registration if they want the
suite in CI.

### P7 — Refutation of `Missing` and `Partial`

One agent per finding, batched when findings are many. Each agent receives the finding and the
cited clause, and tries to **disprove** it. It answers `CONFIRMED`, `REFUTED`, `WEAKENED`, or
`MISCITED`, with a reason. `MISCITED` means the conclusion may stand but a cited line does not
support it — a claim resting on a misread line is a wrong claim even when its conclusion is right.

**Judge `level` as a separate verdict, not as a detail of the status.** An agent asked only "is the
status right" will not question the modal. The IPv4 pilot mis-levelled in both directions.

Record the verdict and its reason per finding, and keep the refuted ones in the working data. A
refuted claim about a piece of code is useful context for a surviving finding about the same code,
and it goes into that finding's `refutation.md` at P8. Drop refuted findings from the matrix, and
note the counts in the method line. That number is what makes the surviving findings credible: the pilot changed 12 of the
70 claims this pass examined.

### P7b — False-`Full` hunt

**The review verifies its accusations and trusts its acquittals.** In the pilot, P6 and P7 together
covered 36% of rows. The other 64% — every `Full` and every `Non-gap` — went unchecked, and that is
where the one confirmed error was. A false `Full` hides a real gap and is invisible, because nobody
re-reads a row that says the code is fine.

**Which rows.** `MUST` is not a useful filter — 105 of the pilot's 125 `Full` rows were `MUST`.
Audit instead:

- every `Full` row whose requirement summary contains " and ", or otherwise imposes two obligations
  (53 rows in the pilot), and
- every `Non-gap` row, without exception. `Non-gap` is a judgment call, and an agent should not be
  making it alone.

**By blind duplication, not refutation.** A second agent maps the row from scratch, seeing the
requirement and the clause but **not** the first verdict, not its evidence, and not the report. Then
compare. Do not show an agent a verdict and ask it to disprove that verdict: it anchors on what it
is shown, which is the same weakness that let the row through the first time.

Blind duplication is the only method whose effectiveness this project has measured. Ten blind rows
found what twelve mapping and refutation agents had missed across 221.

**Adjudication.** The orchestrator reads the disputed line itself. Both pilot adjudications took one
command. Do not add a third agent to break a tie — a vote adds no evidence, and it is how a wrong
answer acquires a majority. Escalate to the user only when the dispute is about what the clause
means, not about what the code does.

### P8 — Assembly

Write the report from [report-template.md](report-template.md). Update the index.

**Group rows into root-cause findings, then order the findings by priority.** One defect commonly
spans several rows. The finding entry is the unit a maintainer plans against, so it names every row
it explains. Priority is derived from status, impact, and level by the table in
[finding-classes.md](finding-classes.md). Never let an agent set it and never adjust it by hand: the
order must be reproducible from the matrix alone.

**Write a `Context` field for every finding**, three to five sentences, for an agent that will plan
the fix and has read nothing else. [report-template.md](report-template.md) says what it must
answer. This is the one part of the report written for a machine reader rather than a maintainer, and
it is the part later agents will actually act on. Do not delegate it to an agent that has not seen
the code: write it from the mapping and reproduction notes, or give the agent those notes.

**File the working data into context directories**, one per finding at
`doc/protocols/<family>/findings/<id>/`. Everything the run produced about the finding goes there:
the rows with their `checked:` lists, the mapping notes, the reproduction attempts, the refutation
verdicts, and test recommendations for rows no committed test covers. The template names the files.
A planning agent receives this directory as its initial context. Nothing in it is spec text.

**Run [validate-report.py](validate-report.py) before the checkpoint.** It enforces the priority
order, the `Context` field, the context directories, and every link. Dangling links and a missing
`Context` fail the checkpoint.

**Publish the report's own verification coverage**, as a table in section 2: per status, how many
rows exist, how many were verified, by what method, and how many were not. A reader cannot judge how
far to trust a document that does not say what it left unchecked. The pilot's first draft would have
read `Full` 0 of 125 — and publishing that number is what sent the next pass to the right place.

Record the **workflow version** in the report header, as `Workflow: v<n> (<date>)`. Bump it whenever
a phase is added or an evidence rule changes, and say what changed in
[calibration.md](calibration.md). Without it, nobody can tell which reports predate which pass.

**Every reference in the report is a link.** An identifier jumps to its matrix row and on to its
finding, a spec clause opens the document at that clause, and an evidence reference opens the file
at that line. A reader who must search will not check the report at all.
[report-template.md](report-template.md) gives the exact form of all three, and the four checks to
run before committing. Dangling links fail the checkpoint.

Present to the user:

- the report,
- every row the agents proposed as a deliberate simplification, for the user's decision,
- the method line: how many rows, how many refuted, how many reproduced.

After sign-off, move accepted simplifications into `accepted-omissions.md`
([ledger-template.md](ledger-template.md)), set the index status to `reviewed`, record the
reviewed-at commit, and commit.

## Agent budget

About **32 agents** per family, plus 3 for the spot check. Launch none before the P2 approval.

| Phase | Agents |
|---|---|
| P3 enumeration | 6 |
| P3b completeness critic | 4 |
| P4 mapping | 6 |
| P4b catch-up mapping | 1 |
| P5 deep pass | 1 |
| P6 reproduction | 3 |
| P7 refutation | 3 |
| P7b false-`Full` hunt | 6 |
| adjudication | 1 |
| test conversion | 1 |

The pilot ran 20 in-run agents under an estimate of 15. Budget from this table, not from a guess.

## Version control

The repository is a colocated jj repo. Use `jj`.

One bookmark per family, named `protocol-review/<family>`. Four commits:

1. `docs(<family>): protocol review spec manifest`
2. `docs(<family>): protocol review scope statement`
3. `docs(<family>): protocol conformance tests for <family>`
4. `docs(<family>): protocol conformance review report` — the report, the matrix, the
   `findings/` directories, and the index update

Commits 1, 2, and 4 touch documentation only. Commit 3 adds tests, and every test in it must report
`EXPECTEDFAIL` before it lands. Do not push without asking.

Commit 2 is optional when the scope statement is written as section 1 of the report file and that
file grows into the full report before the tests exist. The IPv6 run folded it into commit 4. Either
way, the scope statement must be on disk and approved before P3 starts.

`jj split` needs an interactive editor and fails in this environment ("Standard output is not a
terminal"). To separate files into their own commit, move them out of the tree to `$TMPDIR`, run
`jj new -m "<message>"`, and move them back.

## Identity across re-runs

A finding ID is allocated once. Never reuse it. Never renumber. A row's identity is its spec
clause plus its feature name.

When a fix lands, the fixing commit updates the matrix row **in the same commit**, and moves the
finding to the report's `Closed` section with the commit id. Closed findings are never deleted.
The report carries its own history.

## Scope edges

- **In:** conformance gaps, spec violations, and defaults that disable a spec-mandated or
  widely-deployed behavior. Defaults go in their own report section, not the matrix, because the
  code is conformant and only the default is questionable.
- **Out:** ordinary implementation defects with no spec content. Record one line in `Observations`
  and move on. Do not investigate. Route serious ones to `/code-review`.

## What the report feeds

Only when the user asks:

- workstream plans in `~/w/ai/ai-plans/plans/pending/`, grouped by theme, each item citing its
  finding ID. The planning agent receives the finding entry — above all its `Context` field — and
  the finding's `findings/<id>/` directory as initial context. Write both for that reader.
- conformance test cases through the `generic-protocol-test-authoring` skill, for rows with status
  `Partial`, `Incorrect`, or `Suspect`.

## Two rules the pilot paid for

**Never give a row target.** Not per family, not per document, and never across documents. Round 1
of the IPv4 pilot told one agent to produce "25 to 32 rows across all six documents". It produced 32
and stopped, and that group came back 68% complete. The group told "30 to 40 rows" for RFC 1122 —
a document with hundreds of numbered requirements — came back 37% complete. Coverage tracked the
targets almost exactly. A target set to bound cost bounds coverage instead. Budget agents per
document; let the document decide how many rows it has.

**Enumerate both sides of every message.** Round 1 enumerated what a sender must put in each ICMP
message and omitted what a receiver owes on getting one, because specification message-format
sections are written from the sender's side. That single blind spot accounted for a large share of
the 193 requirements the critic later found. For every message a protocol defines, write a sender
row and a recipient row.

## Calibration

[calibration.md](calibration.md) records the measured false-positive rate per family. Read it
before you set confidence values. Update it after every family review.
