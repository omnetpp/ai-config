# Conformance report — template

One file per family or slice, at `doc/protocols/<family>/conformance-review.md`. It is a living
document. A fix commit updates it in the same commit.

The report directory holds:

| Path | Content |
|---|---|
| `conformance-review.md` | the report: scope, summary, findings, defaults, observations, closed |
| `conformance-matrix.md` | the census, when it is too large to live inside the report (about 300 rows and up). Below that, keep it as section 3 of the report. |
| `spec-manifest.md` | the documents reviewed, with version and errata |
| `accepted-omissions.md` | the ledger. Only the user writes it. |
| `findings/<id>/` | one directory per finding, holding the working material a later agent needs. See *Context directories* below. |

Copy the structure below. Keep the section order. Keep the column order.

---

```markdown
# <Family> — conformance review

- **Family:** <name>
- **Directories:** `src/inet/<dir>`, `src/inet/<dir>`
- **Specs:** see [spec-manifest.md](spec-manifest.md)
- **Reviewed at:** `<commit>` (<date>)
- **Workflow:** v<n> (<date>)
- **Method:** <N> matrix rows from <M> spec documents. <K> findings. <R> refuted at P7 and
  dropped. <P> errors reproduced. <S> rows spot-checked by <who>, <W> wrong.

## 1. Scope statement

What this family intends to model, and at what fidelity. What it deliberately leaves out.

Cite `doc/src/developers-guide/ch-<name>.rst` for anything the guide already states. Do not
repeat it.

This section decides what counts as a gap. The user approved it at the P2 checkpoint.

## 2. Summary

Three to six sentences. What is solid, what is the largest gap, and what a maintainer should do
first. Name finding IDs.

**Lead with root causes, not with the row count.** One defect commonly spans several requirements,
so counting rows makes the code look worse than it is. "9 root causes" is the honest headline; the
requirement count belongs in the coverage table below. The reader is a maintainer planning work, and
work is planned per root cause.

### Verification coverage

What was checked, and what was not. A reader cannot judge how far to trust a report that does not
say what it left unchecked.

| Status | Rows | Verified | By what | Unverified |
|---|---|---|---|---|
| `Incorrect` | 12 | 12 | reproduced in a simulation (P6) | 0 |
| `Missing`, `Partial` | 65 | 65 | adversarial refutation (P7) | 0 |
| `Full` | 125 | 53 | blind duplication (P7b), two-obligation rows | 72 |
| `Non-gap` | 16 | 16 | blind duplication (P7b) | 0 |

Also state what the completeness critic found: how many requirements P3 had missed. That number is
what says whether the enumeration itself was any good.

Counts by status and impact:

| | `results` | `scope` | `cosmetic` |
|---|---|---|---|
| `Incorrect` | | | |
| `Missing` | | | |
| `Partial` | | | |
| `Suspect` | | | |

## 3. Coverage matrix

One row per spec feature. `Full` rows carry no ID. Every other row carries one. When the census is
too large for one document, this section holds the per-area row counts and links to
`conformance-matrix.md`, which carries the rows in the same format.

| ID | Feature | Spec clause | Level | Status | Impact | Confidence | Evidence |
|---|---|---|---|---|---|---|---|
| — | Header checksum | [RFC 791 §3.1](https://www.rfc-editor.org/rfc/rfc791#section-3.1) | MUST | `Full` | — | high | [Ipv4Header.cc:120](../../../src/inet/networklayer/ipv4/Ipv4Header.cc#L120) |
| <a id="ipv4-001"></a>[IPV4-001](#f1) | Reassembly timeout | [RFC 791 §3.2](https://www.rfc-editor.org/rfc/rfc791#section-3.2) | MUST | `Partial` | results | high | [Ipv4.cc:812](../../../src/inet/networklayer/ipv4/Ipv4.cc#L812) |

Group rows under subheadings that follow the spec's own structure, for example
`### 3a. Header format`, `### 3b. Fragmentation`, `### 3c. Options`.

## 4. Findings

**One entry per root cause, ordered by priority, then by ID.** A root cause commonly spans several
matrix rows. The entry lists every row it explains, and every non-`Full` row appears in exactly one
entry. Priority is derived from status, impact, and level by the table in
[finding-classes.md](finding-classes.md). Do not order by ID and do not order by judgment.

Open the section with the work queue, so a reader sees the order without scrolling:

| Priority | Finding | Rows | Status |
|---|---|---|---|
| P1 | [F1](#f1) A legal packet aborts the simulation | 5 | `Incorrect` |
| P1 | [F3](#f3) Overlapping fragments are merged and delivered | 2 | `Incorrect` |
| P3 | [F2](#f2) The receive path performs no address validation | 8 | `Missing` |

### <a id="f1"></a>F1 — A legal packet aborts the simulation

**Priority:** `P1` · **Status:** `Incorrect` · **Impact:** `results` · **Level:** MUST · **Rows:** 5

- **Spec:** [RFC 8200 §4.4](https://www.rfc-editor.org/rfc/rfc8200#section-4.4), "must discard the packet and send an ICMP Parameter Problem"
- **Observable:** ICMPv6 type 4 code 0 frame whose Pointer addresses the Routing Type octet
- **Implementation:** [Ipv6.cc:1219](../../../src/inet/networklayer/ipv6/Ipv6.cc#L1219), [Icmpv6Header.msg:64](../../../src/inet/networklayer/icmpv6/Icmpv6Header.msg#L64)
- **What is wrong:** <one or two sentences>
- **Consequence:** <what a simulation gets wrong because of this>
- **Reproduced by:** [Ipv6MalformedHeaderDiscard.test](../../../tests/protocol/conformance/Ipv6MalformedHeaderDiscard.test) — reports `EXPECTEDFAIL`, turns `PASS` when fixed
- **P7 verdict:** CONFIRMED — <one line>
- **Rows:** [`IPV6-044`](conformance-matrix.md#ipv6-044), [`IPV6-243`](conformance-matrix.md#ipv6-243), …
- **Context:** <three to five sentences, see below>
- **Context files:** [findings/f1/](findings/f1/)

**Status** and **Impact** are the strongest among the entry's rows, and **Level** the strongest
level. **Rows** is the count. Keep each entry short. The matrix carries the census. An entry
explains only what the row cannot.

### The `Context` field

Three to five sentences, written for an agent that will plan the fix and has read nothing else. A
later agent builds a plan from this field and the context directory, so it must stand alone. It
answers, in this order:

1. **Where the mechanism lives.** The module, the function, and the message class, by name.
2. **What a fix touches, and what it must not break.** Callers, sibling findings that share the
   code, parameters and NED interfaces that expose the behaviour, and existing tests that pin the
   current behaviour.
3. **What "done" looks like.** The reproduction test that flips to `PASS`, or the test to write
   when none exists.
4. **What was tried.** Anything from P6 that did not reproduce, and any refuted claim about the same
   code, so the planner does not repeat it.

Write it as prose, not as a list. Name files, do not link them — the links are in the fields above.
Do not restate the spec clause or the consequence. Those fields exist already.

**Aim at about 150 words.** The sentence count alone does not bound length: the IPv6 review's agents
wrote compliant five-sentence fields of 270 words. Past roughly 200 words the surplus belongs in the
context directory, and the validator warns. A long list of call sites is the one thing worth the
words, because it is what a planner cannot reconstruct cheaply.

### Context directories

`doc/protocols/<family>/findings/<id>/`, where `<id>` is the finding anchor, for example `f7`. It
holds everything the run produced about that finding that is too long for the entry: agent reports,
`checked:` lists, reproduction notes, refutation verdicts, and test recommendations. A planning
agent receives this directory as its initial context, so write for that reader.

Conventional files. Create only the ones that have content:

| File | Content |
|---|---|
| `rows.md` | every matrix row in the finding, with its full `checked:` list and evidence. This is where `checked:` lands in the repository. |
| `mapping.md` | the P4, P4b, and P5 agent notes on those rows, verbatim or lightly trimmed |
| `reproduction.md` | P6: the configuration run, what was observed, and every attempt that did not reproduce. A `Suspect` entry must have this file. |
| `refutation.md` | P7 and P7b: each verdict with its reason, including claims that were refuted or weakened about the same code |
| `test-recommendations.md` | tests to write, one per row `observable` that no committed test covers, with the assertion stated from the standard's side |
| `notes.md` | anything else: related observations, code-reading notes, open questions for the user |

Rules:

- Every file starts with one line naming the finding and the family.
- No spec text. Hard rule 6 applies here as it applies everywhere. Cite clause numbers.
- Agent output goes in as the agent wrote it, with a heading that says which phase and which agent
  produced it. Do not summarise it into something shorter than the entry — the entry is the summary.
- A planning agent will read these files without the report. Do not write "see above".

## 5. Defaults and configuration

Parameters whose default disables a spec-mandated or widely deployed behavior. The code here is
conformant. Only the default is questionable, so these stay out of the matrix.

| ID | Parameter | Default | Spec / practice | Consequence |
|---|---|---|---|---|
| IPV4-040 | `Tcp.windowScalingSupport` | `false` | RFC 7323, on by default in Linux | Every default simulation caps the window at 64 KiB. |

## 6. Observations

Implementation defects with no spec content, found while reading. One line each. Not investigated.

- `Ipv4.cc:455` — the loop index may pass the array bound when the option list is empty. Not
  chased. Route to `/code-review`.

## 7. Closed

Findings that a later commit fixed. Never delete a finding. Move it here with its commit.

| ID | Feature | Closed by | Date |
|---|---|---|---|
| IPV4-003 | Broadcast address check | `a1b2c3d4` | 2026-09-01 |

## 8. Accepted omissions

See [accepted-omissions.md](accepted-omissions.md). Rows there are not reported again.
```

---

## Cross-references — everything is a link

A report that makes the reader search is a report nobody checks. Three link kinds, all mandatory.

### 1. Identifiers

Each matrix row carries an anchor in its ID cell, and links on to the finding that explains it:

    | <a id="ipv4-002"></a>[IPV4-002](#f2) | ... |

Each finding heading carries its own explicit anchor, so the link survives a reworded heading:

    ### <a id="f2"></a>F2 — Three legal packets abort the simulation

Every mention of an identifier anywhere in the prose links back to its matrix row:

    [`IPV4-002`](#ipv4-002)

Anchors are lower case. Verify before you commit: every `](#ipv4-nnn)` must have a matching
`<a id="ipv4-nnn">`, exactly one of each.

### 2. Spec clauses

One uniform rule:

    [RFC 1122 §3.2.1.2](https://www.rfc-editor.org/rfc/rfc1122#section-3.2.1.2)

The anchor is `#section-<clause>` with the clause verbatim. Modern RFCs rendered by xml2rfc carry
deep anchors, so `#section-2.1.1` lands exactly. Older text RFCs carry only top-level anchors, and
an unmatched fragment lands at the top of the document — harmless, so do not special-case it. A
clause with no number, as in RFC 792, links to the document with no fragment. An errata reference
links to `https://www.rfc-editor.org/errata/eid<N>`.

For a document that is not an RFC, link to wherever the review can actually reach it, and never to a
paywalled page that returns nothing without a login.

### 3. Evidence

A `file:line` links to the file at that line, relative to the report:

    [Ipv4.cc:282](../../../src/inet/networklayer/ipv4/Ipv4.cc#L282)

The prefix is `../../../` from `doc/protocols/<family>/`. Use the first line of a range for the
anchor. Keep the display text short — the path tail and the line — and put the full path only in
the link target.

### Before you commit

Run [validate-report.py](validate-report.py) over the report directory:

    validate-report.py doc/protocols/<family>

It fails on: a dangling `](#...)` link, an anchor defined twice, a relative file path that does not
exist, a finding entry with no `Priority` or `Context` or `Context files`, a `Context` outside three
to five sentences, a `Context files` directory that does not exist, a priority that does not match
its derivation from status, impact and level, and a findings section out of priority order. Fix what
fails. A dangling link is worse than no link, because it teaches the reader to stop clicking.

## Writing rules for the report

1. **The matrix is the census.** Every spec feature appears, including the ones INET gets right.
   A report that lists only problems cannot show coverage, and cannot be diffed usefully.
2. **Evidence, not assertion.** A `file:line` or a test name. "Appears to be implemented" is not
   evidence.
3. **Quote the spec only where the wording carries the finding.** A short fragment. Never a
   clause in full, and never a spec PDF's text in bulk.
4. **State the consequence.** A maintainer prioritizes by what a simulation gets wrong, not by
   the clause number.
5. **Keep the method line honest.** It says how many findings were refuted and dropped. That
   number is what makes the surviving ones credible.
