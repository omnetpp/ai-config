# Calibration

How often this workflow has been wrong, measured per family. Read this before you assign
confidence values. Update it after every family review.

## Why this file exists

The pilot family has no hand-made report to compare against. Without a measured error rate, a
confidence label is a guess. This file turns it into a record.

## Workflow versions

| Version | Date | What changed |
|---|---|---|
| v1 | 2026-08-25 | The original nine phases. Verified only its accusations: `Incorrect` by reproduction, `Missing` and `Partial` by refutation. |
| v2 | 2026-08-25 | Added P3b completeness critic, P4b catch-up mapping, P7b false-`Full` hunt by blind duplication, the per-obligation `checked:` field with mechanical enforcement, `level` as a separate audit verdict, and a published verification-coverage table. Budget 20 → 32 agents. Driven by the v1 pilot: 64% of rows were never adversarially checked, and the one confirmed error was in that 64%. |
| v3 | 2026-08-30 | Report changes only, no new phase. Findings are root-cause entries ordered by a derived priority (`P1`–`P6`, from status, impact and level). Every finding carries a `Context` field of three to five sentences written for the agent that plans the fix, and a `findings/<id>/` directory holding the run's working material for that finding. `STRUCTURAL` added as a level. `validate-report.py` enforces the fields and the links. Driven by the IPv6 review: 823 row-level IDs in 40 root causes gave a planner nothing to start from, and the agent reasoning that would have helped was left in the scratchpad. A v2 report is `method-stale` for the P8 changes only, and can be retrofitted from its working data without re-running any agent. |

A report records the version that produced it. A family whose report predates a pass is
`method-stale`, and needs only the phases that are new — not a fresh review.

## Method

After P8, the user spot-checks a random sample of matrix rows. For each sampled row they answer:
is the status right, is the clause citation right, is the evidence right?

Sample size: 10 rows for the pilot. For later families, 10 rows, or fewer once the rate is stable
across three families.

**Acceptance bar for the pilot:** 2 or fewer wrong rows out of 10. Above that, repair the
workflow before starting family two.

## Record

| Family | Date | Rows in matrix | Findings | Refuted at P7 | Sampled | Wrong | Notes |
|---|---|---|---|---|---|---|---|
| IPv4 with ARP and ICMP | 2026-08-25 | 287 | 147 | 3 refuted, 7 weakened, 2 miscited | 10 | 1 clear, 1 taxonomy | Self-check, not a human check — see the caveat below |
| IPv6 with ICMPv6 and ND | 2026-08-30 | 1747 | 823 | 37 refuted, 77 weakened, 8 miscited, 29 mis-levelled | 568 blind | 14 graded too generously | Blind duplication replaced the spot check; see below |

**Caveat on the pilot number.** The orchestrator that built this workflow also ran its spot check, so
this is a self-check. It is weaker evidence than a human check and the next family should not treat
it as settled. It was made as independent as the setup allows: three fresh agents received only the
requirement and the clause, with the status and the evidence withheld, and derived each answer from
scratch. Their verdicts were then compared with the report's.

**Result: 8 of 10 agreed. Of the two disagreements, one was a real error in the report and one was a
defect in this skill's taxonomy.**

- **A false `Full`.** "Parameter Problem trigger and discard" (RFC 792) was graded `Full` because
  both trigger sites were found and both discard correctly. The blind checker noticed that the
  clause's *other* half — discard on a bad header parameter — is not met: a bad version or short IHL
  is flagged at parse time and then falls through the same `&&` guard that finding F1 is about. The
  row became `Partial` (`IPV4-147`). The mapping agent graded the part of the clause it had gone
  looking for, and did not re-read the clause for the rest.
- **A taxonomy defect,** not a data error. See the permissive-clause rule below.

Both survived six enumeration agents, six mapping agents, a deep pass, and an adversarial refutation
pass. Ten sampled rows then found one. **Extrapolate with care: one error in ten sampled rows is not
one error in the report.** Treat the sample as a floor on the error rate, not a measurement of it.

## IPv6, 2026-08-30 — what the second family measured

The IPv6 run was 4x the pilot: 1747 rows, 21 documents, 47 agents. It replaced the 10-row spot
check with the P7b blind pass over 568 rows, which is a stronger instrument and should be the
standard from now on.

**P7b found 14 rows graded too generously, in 568 audited — 85% agreement.** Every one had the
same cause as the pilot's single error: the mapping agent verified the half of the clause it went
looking for. The clearest is `D310`, where the entry-creation code is correct but unreachable,
because the option loop above it executes `break` under a comment that reads "skip to next prefix
option".

**P7 changed 122 of 468 claims, 26%, plus 29 requirement levels.** The pilot changed 17%. Level
corrections ran in both directions, which is why level must stay a separate verdict.

### Three systematic enumeration errors, all worth a line in the P3 prompt

Each produced multiple false findings, and each was caught only at P7.

1. **A BCP 14 keyword binds only in ALL CAPITALS** — but only in a document that carries the BCP 14
   boilerplate. RFC 9673 §5.2.2's lowercase "should" is not an obligation. RFC 8200 carries no
   boilerplate and no all-caps keywords at all: it is STD 86 using the pre-2119 convention, so its
   lowercase "must" *is* normative. State both halves, or the rule produces false refutations.
2. **Text in a section the document itself labels non-normative is not a requirement.** RFC 7048 §4
   opens "This section is NOT normative", RFC 6980 §4 is "Rationale", RFC 4862 Appendix A is
   informative, RFC 9131 says its normative changes are all in §6, and RFC 8201 §5 is prefaced "not
   a specification, but rather a set of notes". All five were graded as requirements.
3. **Text quoted from an obsoleted document is not a requirement of the quoting document.** RFC 6946
   §3 quotes RFC 2460 §5 to name it as an attack surface; RFC 8200 dropped that paragraph.

### An orchestrator error worth generalising

The existing rule says never assert what a *document* says in an agent's prompt. Extend it: **never
assert a scope conclusion either.** The P7 prompt suggested many tunnelling rows might be `Non-gap`
because `Ipv6Tunnel` mainly serves Mobile IPv6. The agent checked the scope statement and the NED
documentation, refused, and moved zero rows. A weaker agent would have moved about 35 wrongly.

### Convergence: measure the binding share, not the row count

Two critic rounds left raw coverage flat at 95%, which by the pilot's row-count metric reads as no
convergence at all. The share of `MUST` and `MUST NOT` in what each round returned tells the real
story: 32% in the original enumeration, 13% in round one, 5% in round two. **Use the binding share.**
A round that returns mostly `STRUCTURAL` and `MAY` rows has stopped finding obligations.

### A hole in the taxonomy, still open

There is no good label for "a permissive clause the implementation does not exercise". The rule
forces `Full`, which is correct — nothing is violated — but a reader scanning for "is SEND
modelled?" sees `Full` and is misled. The IPv6 report works around it by naming such features in
prose. 11 rows hit this. A `Not-exercised` status would fix it.

### Three changes to validate-rows.py after this run

- A `MAY` graded `Missing`, `Partial`, `Incorrect?` or `Suspect` is now an error. 11 rows had it.
- The `" and "` two-obligation check now downgrades to a warning when a comma precedes the
  conjunction, because a noun list is one obligation. 36 rows fired, and only about 10 were real.
- `--post-p6` lets the validator run against a finished matrix, where a plain `Incorrect` is legal
  and must cite a reproduction test. Without it a completed matrix could not be validated at all.

## The v2 to v3 retrofit — what a report format change measured

The IPv6 report was retrofitted to v3 on 2026-08-30 with **23 agents and no review phase re-run**.
The enumeration, the mapping, the reproductions and the refutations all still held; only the report
changed. A v2 report is therefore `method-stale` for P8 alone and does not need a fresh review — but
it does need its working data, so **keep the scratchpad until the report is signed off.**

### The largest finding: more than half the gaps had no finding entry

The v2 report grouped 239 of its 542 gap rows into 40 root causes and left **303 rows, 56%, attached
to no finding at all** — 82 of them `results` impact. A planner reading section 4 would have missed
over half the work. Two further rows sat in two findings at once.

Neither is visible by reading. The report looks complete either way, exactly like the P3 enumeration
hole. **`validate-report.py` now checks it**: every gap row in the matrix must be claimed by exactly
one finding entry. This is the check to run first on any older report.

Attaching the 303 rows produced 104 further root causes, 144 in all. The residue is genuinely finer
grained than the first 40 — 2.6 rows per finding against 6 — because the large clusters were found
first. Do not read the finding count as a defect count.

### Independent agents converge on the same cause under different names

Seven grouping agents, none of which saw another's output, named **five identical root causes with
five different slugs** — the Parameter Problem Pointer field, the flow label, the Router Alert
option, the incomplete first fragment, and the interface identifier. That convergence is
corroboration and worth recording as such. The orchestrator must alias them at merge time, by
reading the rows on both sides, and say in the finding's notes that two agents reached it
independently.

### One unreproduced row must not reorder a capability gap

Deriving a finding's priority from its worst row put **14 findings covering 121 rows into `P2`** —
"reproduce first" — because each held a single `Suspect` row among thirty `Missing` ones. For
`f30`, whose whole subject is an absent policy table, the first action is to build the table, not to
reproduce anything. The rule now reads: `Suspect` counts as the worst status only when it is the
finding's most common gap status. The distribution moved from 15/14/36/46/21/12 to
15/6/43/47/21/12, and every large absent capability landed in `P3` or `P4` where a planner expects it.

### A sentence count does not bound length

The `Context` field was specified as three to five sentences. Agents complied and wrote fields of up
to **279 words**, median 190, with 52 of 144 over 200. The words are not padding — the call-site
lists are the part a planner cannot reconstruct cheaply — but the rule needed a word budget beside
the sentence count. The template now aims at 150 words and the validator warns past 200.

### A label collision worth avoiding

The finding entry carries `**Rows:** <count>` in its summary line and `- **Rows:** <list>` as a
bullet. An unanchored search for the label finds the count and silently returns no rows, which made
the coverage check pass vacuously on its first run. The validator anchors to the bullet. If the
template is ever reworked, give the two fields different names.

## Prompt-writing rules learned during the pilot

**Never assert what a document says in an agent's prompt.** Name the topic to cover, and let the
agent read. During the IPv4 pilot the orchestrator's prompt told the ICMP agent that RFC 792
forbids generating errors about broadcast destinations, and asked for a row per prohibition. That
prohibition is in RFC 1122 and RFC 1812, not RFC 792. The agent checked and refused to write the
row. A weaker agent would have written it, and the false row would have carried a citation to a
clause that does not exist.

Write "cover the prohibitions on generating ICMP errors", not "RFC 792 forbids X, Y and Z".

**A stated fact in a prompt must be marked as unverified.** Where the orchestrator has already
looked at the code and wants the agent to start from that, phrase it as "a known starting fact,
which you must verify rather than trust". The pilot used this for the IP option classes, and it
kept the anchoring visible.

## Enumeration convergence — IPv6

| Pass | Enumerated before | Found missing | Coverage | Binding share of the new rows |
|---|---|---|---|---|
| Critic 1 | 1589 | 78 | 95.3% | 13% |
| Critic 2 | 1666 | 80 | 95.4% | 5% |

Flat by coverage, converging by binding share. All three round-two critics independently judged the
operative behaviour enumerated and the residue non-behavioural, and the mapping bore them out: of
the 80 round-two rows, 75 mapped to `Full` or `Non-gap`.

## Enumeration convergence — IPv4 pilot

| Pass | Enumerated before | Found missing | Coverage of what it saw |
|---|---|---|---|
| Critic 1 | 210 (of 221 — three documents were omitted from its input) | 193 | 52% |
| Critic 2 | 403 | ~26 real, 35 claimed | ~94% |

**Two rounds did not converge.** The second pass still found whole sections, not stragglers —
RFC 1812 5.3.9 and 5.3.12, and the RFC 1122 3.2.2.8 recipient duties. Plan for a third round on a
document set this size, or say in the report that the enumeration is still open.

The nine-row discrepancy in critic 2 is an orchestrator error, not an agent error: three of the
fifteen manifest documents were left out of the critics' input, so their existing rows were invisible
and the critic reported them as absent. Check the critics' input against the manifest.

## What a wrong row teaches

Record the cause, not just the count. Causes seen so far:

- **A clause with two halves, graded on one.** The IPv4 pilot's only clear error. The mapping agent
  found the behavior it was looking for, marked `Full`, and never re-read the clause for the rest of
  the obligation. Counter-measure: when a summary contains "and" or names two actions, check both,
  and say in the note which halves you checked.
- **A root cause hiding inside an unrelated row.** The same defect surfaced under a feature name
  that gives no hint of it. A per-row search cannot find that. This is what the deep pass and the
  spot check are for.

Typical causes to watch for:

- The agent searched for a feature under one name, and INET calls it another.
- The clause was read in an obsoleted RFC.
- The code path exists but is unreachable in any shipped configuration.
- A test exists that the mapping agent did not find, so a `Missing` should have been `Full`.
