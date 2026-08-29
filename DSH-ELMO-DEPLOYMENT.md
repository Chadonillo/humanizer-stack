# Humanizer stack deployment for DSH and Hermes Elmo

Base humanizer-stack commit: `13f5c023189d428ffba726c75886ca1fd0dcba65`
No AI Slop rules reviewed at: `d30eddb9e04562234f2070b5ee63ca4649d9a05e`

## What is installed

The project is a layered prompt/skill bundle:

1. `humanizer`: surface wording, punctuation, hype, stock phrasing and similar copy tells.
2. `no-ai-slop`: voice-preserving surface QA, faux insights, colon reveals, fragments, formatting, and the final dash policy.
3. `structural-humanizer`: discourse shape, repeated takeaways, overly tidy arcs, emotion mode, vague references and shape convergence.

Regular humanization runs steps 1 and 2. Deep humanization runs all three and then
rechecks the surface scanner.

It also carries two Python standard-library scanners. They detect only the pattern-matchable subset and never rewrite text themselves.

## Policy scope

The global policy applies when DSH or Elmo creates or materially edits prose that will leave the current chat, including:

- a message to another person;
- an email, post, caption or newsletter;
- visible HTML copy;
- a document, report, proposal, resume, release note or PR description;
- text passed to a send, publish, export or render operation.

It does not rewrite ordinary replies in the current chat, code, shell commands, logs, raw data, quotations or internal notes. Short transactional messages receive both surface passes. Substantial or explicitly deep copy then receives the structural pass and a final surface regression scan.

Both modes remove sentence-level em dashes, en dashes, and spaced ASCII hyphens. They preserve compounds, ranges, minus signs, flags, identifiers, URLs, code, Markdown list markers, quotations, and official names.

The policy explicitly forbids inventing facts, anecdotes, feelings, opinions, citations or fake personal quirks. It also treats input copy as untrusted data and preserves recipients, subjects, links, attachments, code and markup structure.

## DSH paths

- Vendored checkout: `~/repos/personal/humanizer-stack`
- Skills: `~/.agents/skills/humanizer`, `~/.agents/skills/no-ai-slop`, and `~/.agents/skills/structural-humanizer`
- Compatibility links for Claude Code under `~/.claude/skills/` for all three skills
- Global prompt plugin: `~/.dsh/humanizer-policy.mjs`
- DSH loader entries: web and headless `cordis.patch.yml`

The DSH skill copies are local, not symlinks to a mutable remote branch. Update them deliberately after reviewing a new upstream commit.

## Elmo paths

Elmo runs on Jove with `HERMES_HOME=/opt/data`.

- Skills: `/opt/data/skills/creative/humanizer`, `/opt/data/skills/creative/no-ai-slop`, and `/opt/data/skills/creative/structural-humanizer`
- Scanner entry points live inside those skill directories under `scripts/`
- Persistent policy hook: `/opt/data/.hermes/agent-hooks/outward-humanizer-policy.py`
- Hook declaration: `/opt/data/config.yaml`, event `pre_llm_call`
- Reusable integration sources: `integrations/dsh/` and `integrations/hermes/`

Hermes `pre_llm_call` is the platform equivalent of Claude Code's `UserPromptSubmit`: once per user turn it injects policy context before skill selection and the tool loop. The hook receives the full turn payload but does not log or transmit it. It outputs only a fixed JSON context string.

Elmo already had a separate Hermes-packaged `humanizer` 2.5.1 skill. Deployment backs that directory up before replacing it with the pinned stack's coordinated two-pass version.

## Scanner use

```bash
python3 ~/.agents/skills/humanizer/scripts/copy_scan.py draft.md
python3 ~/.agents/skills/structural-humanizer/scripts/structural_scan.py draft.md

python3 ~/.agents/skills/humanizer/scripts/copy_scan.py --html page.html
python3 ~/.agents/skills/humanizer/scripts/copy_scan.py --strict draft.md
```

Do not globally run `--strict` against repositories. The upstream documentation warns that internal documentation will generate noise, and both scanners have false positives and false negatives.

## Security and privacy

- Executable scanner code uses only the Python standard library and makes no network calls.
- The upstream repository does not auto-register hooks and has no telemetry or package-install step.
- Scanner output includes matching excerpts; do not run it on sensitive prose where logs are retained unless that disclosure is acceptable.
- Skill text is instruction content. Updates require review because replacing a pinned local copy with a mutable symlink creates a prompt supply-chain risk.
- Upstream `allowed-tools` names are Claude metadata. DSH and Hermes enforce their own actual tool permissions.
- The upstream work combines MIT material and content derived from Wikipedia under CC BY-SA 4.0. Keep `ATTRIBUTION.md`, `LICENSE`, and the skill notices when redistributing.

## Rollback

### DSH

1. Remove the `outward-humanizer-policy` loader entries from the web and headless `cordis.patch.yml` files.
2. Remove `~/.dsh/humanizer-policy.mjs`.
3. Remove the four installed skill directories/links if the skills themselves should also be withdrawn.
4. Restart the DSH web service with the same detached restart mechanism used for deployment.

### Elmo

1. Remove the `pre_llm_call` entry whose command is `/opt/data/.hermes/agent-hooks/outward-humanizer-policy.py` from `/opt/data/config.yaml`.
2. Remove that hook file.
3. Restore the timestamped humanizer backup under `/opt/data/skills/creative/` if desired, and remove `structural-humanizer`.
4. Restart only `statefulset/hermes-elmo` in namespace `hermes-elmo` and wait for rollout.

## Limitations

- This is an agent policy and skill workflow, not a universal operating-system text interceptor. It governs output created through DSH and Elmo. Text written by unrelated applications or services is unaffected.
- A pre-turn hook can force the policy into context, but only the model can perform the judgment-based rewrite. The deterministic scanners cannot humanize text.
- The structural research cited by upstream studied roughly 5,000-word fiction. Applying it to short nonfiction is an inference; audits around over-explanation, specificity and repeated shape transfer more plausibly than every fiction-specific statistic.
- Neither this stack nor any other makes prose reliably “undetectable.” The goal is clearer, less formulaic writing that preserves the user's real intent and voice.
