# Finding classes, impact, and confidence

Three independent fields grade every matrix row. There is no combined score. A reviewer sorts by
impact, and skips everything below high confidence.

## Status

The conformance verdict for one spec feature.

| Status | Meaning | Requires |
|---|---|---|
| `Full` | INET implements the feature as the clause requires. | Evidence that points at the implementing code. No finding ID. |
| `Partial` | The feature exists, but a required element of it is absent. | The absent element named explicitly. |
| `Missing` | The feature is not modeled at all. | A search that shows it is absent, not just hard to find. |
| `Incorrect` | The behavior contradicts a normative statement. | **A reproduction.** See P6. |
| `Suspect` | The behavior probably contradicts a normative statement, and no reproduction exists. | A statement of what was tried and why it did not reproduce. |
| `Simplification` | A deliberate, accepted omission. | A row in `accepted-omissions.md`. **Only the user may assign this.** |
| `Non-gap` | The spec item is obsolete, deprecated, or outside INET's declared scope. | The clause or scope statement that makes it so. |

Rules:

- An agent **proposes** `Simplification`. It never assigns it. The row stays `Missing` or
  `Partial` until the user accepts it into the ledger.
- `Incorrect` without a reproduction is invalid. Downgrade to `Suspect`.
- `Non-gap` needs a source. "It feels outdated" is not a source.

## Impact

What the gap costs a simulation user.

| Impact | Meaning |
|---|---|
| `results` | The gap changes simulation results for a normal configuration. |
| `scope` | The gap blocks a whole class of study, but does not corrupt results the user can run today. |
| `cosmetic` | The gap affects neither results nor the range of possible studies. |

## Confidence

How well the evidence supports the row.

| Confidence | Meaning |
|---|---|
| `high` | The clause was read this run, the code was read, and P7 confirmed the finding. For `Incorrect`, a reproduction also exists. |
| `medium` | One leg is weak: the source is a draft, the code path is complex, or the search for the feature was not exhaustive. |
| `low` | The row rests on inference. Report it, and say what would settle it. |

Read [calibration.md](calibration.md) before you set confidence. It records how often each level
has been wrong.

## Requirement level

`level` comes from the spec text: `MUST`, `SHOULD`, or `MAY`. Keep it. A `MUST` violation outranks
a `SHOULD` violation, and the two must never merge into one severity number.

`MUST NOT` and `SHOULD NOT` are the negative forms of `MUST` and `SHOULD`. They bind exactly as
strongly, and every rule that names `MUST` or `SHOULD` covers them.

A fourth value, `STRUCTURAL`, marks a wire format, a constant, or a field definition that the text
states without a modal verb. A format admits no alternative, so `STRUCTURAL` binds like `MUST`. Use
it only where the clause defines a format or a value. Prose with an implied obligation is `MUST`.

### Permissive clauses

A `MAY`, and anything from an Informational document, grants latitude rather than imposing an
obligation. It cannot be violated, so it cannot be `Missing`.

- The implementation exercises the permission, or does the thing another permitted way → **`Full`**.
- The implementation cannot exercise it because the surrounding capability is absent → **`Non-gap`**,
  and name the missing capability.

Do **not** reach for `Non-gap` merely because a clause imposes no obligation. `Non-gap` means
obsolete, deprecated, or outside the declared scope. The IPv4 pilot's spot check split on exactly
this point — one reviewer answered `Full` and another `Non-gap` for RFC 1071 §2, and both readings
were defensible. That is why this rule exists.

### Conditional clauses

A `MUST` whose antecedent is false in this model is **`Non-gap`**, not `Missing`. State the
antecedent and say why it does not hold. RFC 1812 §5.3.6 binds only where precedence-ordered queue
service is implemented and enabled. INET implements none, so the rule cannot be broken.

### Clauses with two halves

Many clauses impose two obligations in one sentence: send *this* message **and** discard *that*
datagram. Grade every half, and say in the note which halves you checked. A row is `Partial` when
one half holds and the other does not, however well the first half is implemented.

This produced the pilot's only confirmed wrong row. Watch for a summary containing "and", or naming
two actions.

## Priority

The report orders findings for a maintainer who fixes the worst thing first. `priority` is
**derived, not judged**. Compute it from status, impact, and level with this table. Never adjust it
by hand, and never let an agent set it. A finding that groups several rows takes the priority of its
strongest row.

| Priority | Rule | What it means to a planner |
|---|---|---|
| `P1` | `Incorrect`, impact `results` or `scope` | The code contradicts the standard, and a committed test proves it. Fix first. |
| `P2` | `Suspect`, impact `results` or `scope` | The code probably contradicts the standard. Nobody reproduced it. Reproduce first, then fix. |
| `P3` | `Missing` or `Partial`, level `MUST` or `STRUCTURAL`, impact `results` | A binding requirement is absent, and a normal simulation that touches it gives wrong results. |
| `P4` | `Missing` or `Partial`, level `MUST` or `STRUCTURAL`, impact `scope` | A binding requirement is absent. A study that needs it cannot run. |
| `P5` | `Missing` or `Partial`, level `SHOULD`, impact `results` or `scope` | A recommendation is absent. |
| `P6` | any finding with impact `cosmetic` | Housekeeping. Affects neither results nor the range of studies. |

A finding that groups several rows takes the **worst** status, the **strongest** impact, and the
**strongest** level among its rows, and derives one priority from those three.

One exception, and it exists for a measured reason. **`Suspect` counts as the worst status only when
it is the finding's most common gap status.** Otherwise the finding takes the worst status among its
remaining rows, and its row-status line still shows how many `Suspect` rows it carries. Without this
rule one unreproduced row promotes a thirty-row capability gap to `P2` and tells the planner to
reproduce first, when the first action is to implement the capability. The IPv6 review had 14
findings in that position, covering 121 rows.

Within one priority, order by ID. The order says nothing about effort. A `P1` may be a one-line fix
and a `P4` may be a new module. Effort belongs in the plan, not in the report.

`Non-gap` and `Full` rows carry no finding and no priority.

## Finding identifiers

Format `<FAMILY>-<NNN>`, for example `IPV4-017`.

- Allocated once, in matrix order, at P4.
- Never reused. Never renumbered.
- A row's identity is its spec clause plus its feature name.
- A closed finding keeps its ID and moves to the report's `Closed` section.
