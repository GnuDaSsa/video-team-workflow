# Workflow change provenance and branch publication

## Classification, reason and acceptance

Documentation-only workflow governance change, explicitly requested on 2026-10-06.
Extend the existing promotion protocol; do not change Seedance prompting,
production, reference syntax, language, lengths or creative defaults. Future
prompting uses the existing workflow; reusable logic changes are tracked on
separate GitHub branches. No new framework, worker, scheduler or production run.

Acceptance: source/version provenance, scoped change classification, reason and
impact, checks and unverified/experimental status, staged-diff review and remote
branch SHA verification. Preserve all pre-existing source/live changes.

## Repository and baseline

- Project/runtime destination: `video-team-runtime` is not a Git repository.
- Canonical repository: `GnuDaSsa/video-team-workflow`.
- Existing remote: https://github.com/GnuDaSsa/video-team-workflow
- Confirmed default branch: `main`; viewer permission: ADMIN. Visibility unchanged.
- Work branch: `codex/workflow-change-provenance-20261006`.
- Base: `d79ecbca97cd4ca37a849f8708d7eedee860a579` (remote main, 2026-10-06 check).
- Original local main: `32c60f46cd3a300b8e7c667a5ea4886ae160df45`;
  4 local-only / 23 remote-only commits at inspection. No reconciliation attempted.
- Original checkout: 8 tracked modified files plus existing untracked files;
  none copied into this branch. Root `.agents` is absent in both canonical and
  runtime roots; home `.agents/skills` contains no Seedance owner.
- Installed Seedance owner: `~/.codex/skills/seedance-prompt-en/`; not a Git repo.
  Installed files differ from this base; no wholesale sync/deploy is authorized.
- Runtime `AGENTS.md` declares `2026-07-31-sequential-media-v4`.

## Applied reference versions

Hashes below are read-only observations on 2026-10-06. Repo paths are relative to
this base; installed paths are relative to `~/.codex/skills/seedance-prompt-en/`.
They identify the reference versions, not a claim that remote main is the
currently deployed skill or a decision to roll back later local instructions.

| Reference | Base SHA-256 | Installed SHA-256 |
| --- | --- | --- |
| `codex-skills/seedance-prompt-en/SKILL.md` | `6fcb173ddbb8821c09d573a127dc166565b83255b20c67f56717bec9a7a5b0b8` | `f98b6407587601080bb5df16a401286bcc8320cca037396601b4c7d0c4010c0b` |
| `codex-skills/seedance-prompt-en/seedance-shared-contract.md` | `754c6a29a6366079cac13cb60c70db6b31c4df6b61da86a8828634ddf6663d82` | `087e696b4734234b61cad400e88f16ac42b382333b567797bbcd5d91a6c37ddb` |
| `codex-skills/seedance-prompt-en/seedance-prompting.md` | `1a1eab4c92c9984582ad5832f039c111a06cb3dff262a066962d4c4070fd44be` | `b82d59c059e63391cd4fdfa6259dff098e291a15c06cb097b3d59bbc627f95cc` |
| `codex-skills/seedance-prompt-en/seedance-production.md` | `2eef27f667bedd42e42f551d73068ba797440d56ff800861c6a6fb3f00d17981` | `18ea6c00f0f9be22339b54d98a527959980d209596ee53f28adfa251203395d1` |
| `codex-skills/seedance-prompt-en/seedance-field-lessons.md` | `b73502c5ff7604203f94b75e2aee55a7db1f28b06b4ec74b8c52cb8fe727aaec` | `ce744d20200528c912409c31d1e8e000fbbd0428efe628aa0a1204e7764f9fb6` |
| `codex-skills/seedance-prompt-en/prompt-review.md` | `619b9c53028614ffe51bfd136ec2037b1bfbd2fa8efb1a1186f4842c7cb5fbba` | `52ad2e1ce96b6d74746bfc43c8e459dda15e031a94a0af04aba9c971b99c46d0` |

Other baseline owners: `runtime/AGENTS.md`, `docs/video-feedback-promotion-protocol.md`,
`docs/harness-config.json` at the base commit above. The source/local language
contract differs; this change deliberately does not pick or rewrite that policy.

## Evidence and limitations

The delegated request supplied the failure account: storyboard/shots were
rewritten as ordinary English prose without consistent Seedance reference,
slot and shot-contract handling; later recovery introduced unsupported length
and padding assumptions, then lost required detail through over-shortening.
This is supplied incident context, not an independently replayed production test.
No private conversation transcript or project media is included.

The request also reports local `@ImageN` spelling versus a Runway asset-bound
chip whose internal text is `@Image 1`. Source role-map and visible-deck checks
were inspected. No live Runway UI was opened here; the exact chip serialization
and any broader no-space restriction were not independently reproduced.
Status: platform observation supplied, live revalidation UNVERIFIED. Do not
normalize strings and claim attachment validation; preserve this as a scoped
verification requirement, not a new token syntax implementation.

## Impact and rollback

Only repository governance docs and harness records change. The AGENTS pointer
makes the existing protocol discoverable to future repository work. Installed
personal skills/runtime and project packages remain untouched. Branch presence
alone does not activate these additions in deployed production environments.
Rollback before merge is to leave this branch unapplied; any later integrated
change can be reverted by its dedicated commit. No merge/deployment in this task.

## Verification

- Configured `verifyFull` invoked (it includes all `verifyQuick` checks): stopped
  at Node failures. Remaining commands were then run individually.
- With canonical real-path TMPDIR/JEV_QC_TEST_TMP: Node 489 tests, 407 pass,
  82 fail with `Knowledge: source hash drift`. Initial temp symlink fixture
  failures disappeared. The unchanged `knowledge.mjs` reads installed live wiki
  when present and rejects its mismatch with the base catalog; no source hashes
  were refreshed and no wiki or catalog was changed to make tests pass.
- Python unittest discovery: 217 tests PASS; shell syntax PASS.
- Python compilation: initial cache-write sandbox error; PASS with
  `PYTHONPYCACHEPREFIX=/tmp/workflow-provenance-pycache`.
- Both read-only deployment checks run: Aside reports installed extras/changes;
  Codex reports installed hash mismatches. Full parity FAIL, consistent with
  observed source/live drift. No apply, freeze, install, delete or repair run.
- `git diff --check` PASS. Manual diff/file review: six governance Markdown/JSON
  files only, no executable or skill changes. All `aside-skills`, `runtime` and
  `tools` files are byte-identical to the base; these pre-existing environment
  mismatches are outside this documentation change. No full-suite PASS claimed.
- Existing original checkout dirty file list remains unchanged.
- Local raw logs retained outside the repository in the task workspace
  `workflow-verification/`; no account paths/raw logs uploaded.
- Remote branch SHA verification is performed after committing/pushing and
  reported in the task result; no self-referential commit hash is embedded here.
No browser production, media generation, chip-binding test, new prompt
attestation or generated-output QC is in scope.
