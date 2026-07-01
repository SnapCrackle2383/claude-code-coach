# Claude Code Coach

Get better at Claude Code, using your own history as the evidence.

`prompt-coach` reads the prompts you have actually typed in Claude Code, then gives you an honest, personalized review: a prompt score, the habits that are costing you, rewrites of your real prompts, and the setup that would make you faster. It runs entirely on your machine and nothing leaves it.

## Install

```
/plugin marketplace add SnapCrackle2383/claude-code-coach
/plugin install prompt-coach@claude-code-coach
```

Then just ask, in any session:

> review how I have been prompting in Claude Code

## What you get

- **A prompt score out of 100**, with a transparent breakdown across Direction, Specificity, Decisiveness, Efficiency, and Leverage.
- **Named anti-patterns** with real counts from your history (the Trailing Question, the Blind Retry, the Vague-It, the Mega-Bundle, the Silent Paste-Dump).
- **Before and after rewrites of your own prompts**, so the advice is concrete, not generic.
- **Custom slash commands and subagents to create**, mined from the workflows you repeat most.
- **Matched courses and videos**, aimed at your actual gaps and skipping anything below your level.
- **A local security check** that flags credentials you may have pasted into past prompts (masked), so you can rotate them.

## Privacy

This is the core promise, not a footnote:

- The analyzer is **read-only** and uses only the Python standard library. It never modifies your history.
- It makes **no network calls** and sends **nothing off your machine**. Your prompts, your score, and any flagged secrets stay local.
- The secret scan only ever shows **masked** previews, never the full credential.

## How it works

The skill runs a bundled Python analyzer over `~/.claude/projects`, extracts only the prompts you actually typed, computes the diagnostics above, and hands them to Claude to turn into the review. Everything is deterministic and grounded in your real data.

## Maintainer notes (optional job listings)

This plugin can show a small, clearly labelled "partner roles" block to high-scoring users. It ships **off** by default and shows nothing unless you turn it on.

- Listings live in `roles.json` at the repo root (a JSON array of `{company, title, location, url, sponsored}`). Editing that one file updates what every installed user sees, with no re-release.
- To advertise a role, companies use the intake form linked in the skill.
- To activate the block, set `enabled: true` in the skill's `assets/partners.json` and bump the plugin `version`. See `plugins/prompt-coach/skills/prompt-coach/references/partners-and-ads.md` for the full rules, including the privacy line (the block fetches your public `roles.json` and never sends user data).

## License and privacy

Licensed under the MIT License (see [LICENSE](LICENSE)). See the [Privacy Policy](PRIVACY.md) for how the skill handles your data. Short version: it all stays on your machine.
