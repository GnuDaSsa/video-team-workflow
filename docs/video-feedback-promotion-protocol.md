# Video Workflow Feedback Promotion Protocol

## Purpose

Keep every video project on the user's canonical video-team workflow while
turning validated process feedback into one version-controlled improvement in
`GnuDaSsa/video-team-workflow`. This is a synchronous, main-task practice; it
never authorizes an extra agent, scheduler, monitor, or automatic Git writer.

## Intake

When a user correction or a material process failure occurs, the owning lane
records a concise evidence note under `lanes/<lane>/logs/` and links it from
that lane's `result.md`/`status.json` when relevant. The note contains:

1. observed behavior and artifact/GUI evidence;
2. impact on quality, safety, or delivery;
3. root-cause hypothesis and correction; and
4. whether the scope is project-only or candidate for promotion.

Do not store passwords, tokens, personal form data, private message bodies, or
unnecessary provider/account details in the note or the repository.

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

1. Make the smallest correction at the single canonical owner.
2. Update a test, template, or checklist when that is the appropriate durable
   enforcement point.
3. Run the smallest relevant verification plus `git diff --check`.
4. Update harness state and durable decision/memory records when applicable.
5. Stage and commit **only** the feedback change; never sweep unrelated dirty
   working-tree files into the commit.
6. Push the verified, self-contained commit to
   `GnuDaSsa/video-team-workflow` (or report the exact blocker).
7. Deploy only through the repository deployment path and only after its
   preflight passes; deployment is separate from recording a rule.

The next video project reads the deployed canonical workflow and its project
state, so a promoted rule becomes default behavior rather than a chat-only
promise.
