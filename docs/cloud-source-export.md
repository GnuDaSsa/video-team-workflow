# Reproducible cloud source export

Run from a clean, reviewed source checkout, with an explicit full commit SHA:

```bash
python3 tools/export_cloud_source.py --commit <full-sha> --output <new-directory>
```

The tool reads `git ls-tree`, `git show` and `git archive` from that exact commit;
it never copies the working tree, installed skills, projects, user media, browser
state or credentials. It refuses symlink/submodule/media/credential-file entries
and existing output files. Review source text for sensitive content before push;
a filename check is not a content-secret scanner.

Outputs: deterministic `source.tar.gz` rooted at `workflow/`, exhaustive exact
Git-tracked `files.txt`, and `manifest.json` with source commit, file-list and
archive hashes. The full tracked source tree is the smallest reliable export
unit for the existing configured checks, which load runtime, other skill contract
fixtures, Aside code and deployment test fixtures. Do not trim that tree while
claiming configured verifyQuick/verifyFull remain reproducible. Actual live-wiki
and installed-deployment parity depend on external state and remain unverified
by any source archive.

Minimum harness dependency closure (included and checked, never synthesized):

- `AGENTS.md`, `AGENTS.harness.md`
- `runtime/AGENTS.md`, `runtime/AGENTS.harness.md`
- `docs/harness-config.json`
- `docs/harness-state.json` (`paths.stateFile`)
- `docs/decisions.md` (`paths.decisionsFile`)
- `docs/project-memory.md` (`paths.memoryFile`)
- `docs/contracts/2026-10-06-cloud-cua-profile.md` (currentContract for this change;
  exporter resolves it from the pinned state rather than freezing this example)
- `docs/video-feedback-promotion-protocol.md`

The cloud profile source is `codex-skills/seedance-prompt-en/execution-profiles.md`
and `scripts/cloud_cua_preflight.py` under that skill. Its unchanged compiler,
registry and duration dependencies are in `runtime/scripts/`. All are included
as tracked bytes. No runtime AGENTS/config relocation is necessary: preserve
repository layout and resolve harness paths from the extracted `workflow/` root.

Export is not a deployment or permission grant. Do not execute local Aside/macOS
commands in cloud or silently fall back to personal installed skills/wiki.
Set `VIDEO_TEAM_RUNTIME_SCRIPTS` to the extracted runtime scripts for cloud checks.
A project with required external knowledge must carry its legitimately selected
hash-bound evidence; if absent, report it rather than disabling knowledge gates.

## Official project creation in an authorized workspace

Run with the tool's working-directory argument set to the actual authorized task
workspace (not `/`, the source installation directory by accident, or a path
chosen to escape a denial):

```bash
python3 <extracted-workflow>/runtime/scripts/video_codex_runtime.py init \
  --project-root ./video-projects --slug example --brief '<approved brief>' \
  --mode no_i2v_reference_native
```

The explicit root is resolved under process cwd, including symlinks, and rejected
if it escapes. An absolute path is allowed only if it resolves inside that same
workspace. Filesystem/tool permissions still apply. Without `--project-root`,
the existing local Mac default is unchanged. No monkeypatch/env override is
needed. A timestamped project is created without replacing an existing one.

This does not port every runtime dependency: the existing required knowledge
catalog/wiki path and receipts must be resolved through their authorized workflow
before attestation; do not disable them to make a cloud project pass.

After creating the real project and bounded input files, run the unchanged
`runtime/scripts/author_handoff.py request` with the already authorized scope.
Retain its real output and generation time before a new authoring turn. It builds
JSON and checks file/scope integrity; it neither launches a model nor verifies
identity. Record actual external author execution separately. Never backdate an
old authoring turn or label pre-request work as a post-request handoff.
