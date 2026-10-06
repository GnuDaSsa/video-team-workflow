# Video Workflow Feedback Promotion Protocol

## Purpose

Keep every video project on the user's canonical video-team workflow while
turning validated process feedback into one version-controlled improvement in
`GnuDaSsa/video-team-workflow`. This is a synchronous, main-task practice; it
never authorizes an extra agent, scheduler, monitor, or automatic Git writer.

## Intake

An explicit request to "reflect this in the guidelines" or "improve the workflow"
means change the canonical shared owner by default, unless the user explicitly
limits it to this project. First locate the existing task evidence; reference it
from the existing lane result/status where needed. Do not require a new nested
reconciliation JSON or wrapper for every correction. Project evidence records
what happened; it is not the procedure and is not proof of a deployed fix.

For a process improvement, delivery must distinguish canonical source change,
installed deployment, validation, and actual live behavior still unverified.
Project-local changes alone do not satisfy a common-workflow request. Preserve
user holds and existing specific-surface approval requirements.

Do not store passwords, tokens, personal form data, private message bodies, or
unnecessary provider/account details in the note or the repository.

## Workflow baseline before authoring

Every prompt starts from the applicable existing workflow and approved project
shot contract. Read the selected version dispatcher and its shared contract,
prompting/production branch as applicable, field lessons and prompt-review;
keep their ownership and precedence. Storyboard/shots are authoring inputs, not
a substitute for the final reference-bound, reviewed and attested package.
Use existing package/knowledge receipt fields for the applied source paths and
revision (Git commit or installed-file SHA-256). No extra per-shot rule file is
required. Source, installed skill and platform behavior may differ: record the
actual versions used; do not silently resolve drift by copying one over another.

| Classification | Where to record / what changes |
| --- | --- |
| Ordinary project prompt | Existing package, revision, attestation and project evidence; apply current rules without changing shared defaults. |
| Project-only exception | Existing project overrides with governing clause and explicit scope; not a shared rule. |
| Workflow change | A changed reusable default, gate, routing, validator, template, shared skill or interpretation that affects future authoring/execution; canonical owner plus a separate Git branch and change record. |
| New knowledge / experiment | Source and applicable scope plus observed result; mark unverified or experimental until the promotion threshold and relevant checks are met. |

A shared workflow change cannot be hidden in a one-off rewritten prompt.
Conversely, routine prompt revisions do not require a workflow release.

## Small change record

Use the existing `docs/contracts/<change>.md` (or its linked release record),
not a second framework. Before editing, record:

- classification, reason, intended effect and canonical owner;
- repository/remote, separate branch, exact base commit and reference paths at
  that revision; for installed/external sources record version or SHA-256,
  provenance, retrieval/observation date and applicability;
- the proposed delta, preserved behavior, affected consumers and rollback;
- acceptance checks and the distinction between source inspection, automated
  fixtures, platform observation and generated-output QC.

After checking, append commands/results, evidence location, remaining failures,
and explicit `unverified` / `experimental` status where appropriate. Report
source commit, remote branch/SHA, installed deployment status and live verification
separately. An explicit user preference can authorize a rule without proving a
quality improvement; label that distinction. Keep private source evidence local
and publish only the minimum sanitized finding necessary for the change.

For platform-specific reference changes, distinguish token spelling, ordered
asset/slot mapping and actual asset-bound UI chips. Record the provider/surface,
model/mode, observation date, approved asset-to-slot/role match and visible
binding evidence in the existing local production evidence. A string replacement,
text hash or validator PASS alone cannot prove chip binding. A reported UI
observation is not a fresh live check or a universal cross-platform syntax rule.

Do not turn unsupported recovery heuristics into standing defaults: an invented
150–230-word target, mandatory hold/breath/material padding, or aggressive
shortening that removes required composition/action is not validated knowledge.
Keep existing authored shot, identity, reference and camera details; remove only
redundancy/conflict under the owning review contract. This adds no new prompt
length limit and does not replace the current language/length authority.

## Promotion threshold

Promote feedback only when **either** condition holds:

- the user explicitly requests that it become a standing workflow rule; or
- it is a repeated, verified failure that will affect more than the current
  project.

One-off creative taste, an unverified diagnosis, temporary login/provider
state, and project-specific facts remain in the project evidence or
`docs/project_overrides.md`; they do not become global workflow rules.

## Canonical routing

| Feedback scope | Canonical owner |
| --- | --- |
| Global execution default, cross-project safety, or authority order | `GLOBAL_AGENTS.md` |
| Runtime rails, gates, media registry, or lane sequencing | `runtime/AGENTS.md` and the owning runtime code/test |
| Seedance prompt authoring or Runway UI operation | `codex-skills/seedance-prompt-en/` only |
| Story, editing, typography, image, music, or QC practice | Owning skill/reference and its targeted check/template |
| Reusable research or knowledge selection | `/Users/gnudas/wiki` plus the repository extract/catalog when applicable |
| Project exception | `docs/project_overrides.md` in that project, with the governing clause cited |

Never duplicate an active rule across lanes, project folders, or role skills.
The authority order remains: runtime rails/safety, the single Seedance contract
within its scope, team policies, then creative direction.

## Release loop

1. Confirm the existing owned remote, default branch and write permission.
   Snapshot dirty status; create an isolated worktree on a separate descriptive
   branch from an explicitly recorded base. Preserve all unrelated working
   changes, local branches and installed skills. If remote ownership or required
   permission is unclear, report it before creating a repository or publishing.
   Write the small change record, then correct the single canonical owner.
2. Update a test, template, or checklist when that is the appropriate durable
   enforcement point.
3. Read the repository validation instructions; run the configured checks and
   relevant targeted verification plus `git diff --check`. Record failures and
   checks not run; never relabel source/fixture PASS as live verification.
4. Update harness state and durable decision/memory records when applicable.
5. Stage and commit **only** the feedback change; never sweep unrelated dirty
   working-tree files into the commit.
6. Review the staged diff and file list for unrelated changes, secrets, private
   conversations, account/session details and media. Push only the self-contained
   commit to its separate branch on the confirmed existing remote; verify its
   remote SHA equals local HEAD. Never write directly to the default branch,
   force push or merge as part of this loop. A PR, if requested/created, is draft.
   Report the exact blocker if push or remote verification fails.
7. Deployment is a separate scoped action, not implied by a branch push.
   When authorized, use the repository deployment path after its preflight
   passes. Never globally patch/move personal skills to hide source/live drift.

The next video project reads the deployed canonical workflow and its project
state, so a promoted rule becomes default behavior rather than a chat-only
promise.
