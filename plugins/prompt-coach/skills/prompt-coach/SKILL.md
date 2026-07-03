---
name: prompt-coach
description: >-
  Analyze the user's OWN Claude Code history and coach them to prompt better. Reads their real typed
  prompts from ~/.claude/projects, measures prompt quality (length, question-vs-instruction ratio,
  vague references, plan-then-approve rhythm, repeated workflows), then delivers an honest, personalized
  review with before/after rewrites of their actual prompts, custom slash commands and subagents to
  create, and matched Claude Code courses. Use this whenever the user wants to get better at Claude Code,
  improve their prompting, review or audit their prompt history, level up their Claude Code workflow, set
  up custom commands or subagents, or asks things like "how am I doing", "am I using Claude Code well",
  "look at my prompts", or "why do I keep having to correct you". Also use it proactively when a user
  expresses frustration that Claude keeps misunderstanding their requests. Do NOT use it for improving a
  single one-off prompt for the user's own LLM product (that is prompt engineering for their app, not
  coaching their Claude Code usage).
---

# Prompt Coach

Turn a user's real Claude Code history into an honest, specific coaching report. The value is that every observation is grounded in their own data, and the coaching ends in things you can build for them, not just advice.

## The method

1. **Measure (deterministic).** Run the bundled analyzer. It is read-only, uses only the Python standard library, makes no network calls, and prints a JSON summary. Nothing leaves the machine.

   ```bash
   python3 scripts/analyze_prompts.py
   ```

   Useful flags: `--project <name>` to scope to one project (substring match), `--sample <n>` for how many real prompts to surface (default 30), `--root <path>` if history lives somewhere non-standard. On a large history (hundreds of sessions) it can take a minute; run it in the background and wait.

   If it returns an `error` field (no history found), tell the user plainly and stop, do not invent numbers.

   The analyzer also emits `prompt_score` (deterministic 0-100 with a component breakdown), `anti_patterns` (named failure modes with counts), and `secret_scan` (masked credential findings). Use those directly rather than recomputing them.

2. **Interpret (judgment).** Read `references/coaching-rubric.md` and apply it to the JSON. The script gives numbers; you decide what kind of user this is and what actually helps them. The cardinal rule: calibrate praise and criticism to the evidence. Look at `top_short_prompts` before saying anything about prompt length, because approvals (`yes`, `merge`) mean a healthy plan-then-approve workflow, while vague nudges (`fix it`, `still broken`) mean under-specification.

3. **Mine the leverage layer.** Read `references/command-patterns.md`. Use `workflow_vocabulary` and `custom_setup_present` to recommend 3 to 5 concrete custom commands and 1 to 2 subagents, each tied to a real repeated workflow and its count.

4. **Match resources.** Read `references/courses.md` and recommend 2 to 3 courses or videos matched to the detected gaps. Skip beginner material for clearly advanced users.

5. **Surface security first (non-negotiable).** If `secret_scan.found` is true, lead the report with it: the credential types, the masked samples, and a direct instruction to rotate them now and stop pasting secrets. This safety duty outranks coaching. Never print an unmasked secret. If nothing was found, say so in one reassuring line.

6. **Score and (optional) roles.** Present the deterministic `prompt_score` (out of 100) and `anti_patterns` as written. Only if you intend to render the sponsored roles block, first read `references/partners-and-ads.md` and honor the privacy line there. It is off by default.

7. **Report, then offer to build.** Produce the report below, then offer to actually create the recommended commands, subagents, and a CLAUDE.md. Building them beats describing them.

## Report structure

Use this shape. Keep it scannable. Every claim cites a real number or a real prompt.

```
# Your Claude Code prompting, reviewed

## One big takeaway
One bold sentence: the single change that would help this user most. It is the
headline and the shareable caption, so make it specific to them, not generic.

## Prompt score
The number out of 100 and the band (Expert / Advanced / Proficient / Developing /
Beginner), then the component breakdown from `prompt_score`. It is a score, not a
percent-correct, so do not write it with a % sign.

## Security check
Only if `secret_scan.found`: the credential types and masked samples, and a direct
instruction to rotate now and stop pasting secrets. Otherwise, one reassuring line.
Never print an unmasked secret.

## By the numbers
A compact profile: active span and prompt count, the length shape (lead with the
MEDIAN, note the mean is paste-inflated), % of prompts that end in a question,
slash-command usage, and whether they have a custom command/subagent/skill setup.

## The honest verdict
One or two sentences. Are they strong, mixed, or struggling, per the data? No hedging.

## What you're already doing well
2 to 4 bullets, each tied to a real number or a real quoted prompt.

## Your anti-patterns
The named patterns from `anti_patterns` with meaningful counts, each with its count
and the one-line fix. Skip any that are near zero.

## Where you got frustrated (and what to type instead)
2 to 4 real moments from `frustration_moments`, addressed directly: quote the
prompt, name the upstream cause, then give the exact replacement prompt to use
next time. Per the rubric: empathy is the hook, the replacement prompt is the
payload. Skip this section only if the list is empty.

## The machinery you're not using
From `advanced_features`: for each near-zero capability (subagents, plan mode,
background tasks) that their workload actually needed, show the real workload
from their history that belonged there, with its count, and the concrete way to
use the feature next time. Credit what they DO use. Skip capabilities where
their workload genuinely would not benefit.

## Highest-leverage changes
The 2 to 4 biggest levers, ranked. If they have no custom commands/subagents, that
leverage layer is almost always lever #1.

## Before / after (your own prompts)
3 to 5 rewrites of THEIR actual prompts. Before (theirs, quoted) -> why it costs
them -> After (a sharper version in their voice). See the rubric for the rules.

## Custom commands and subagents to create
3 to 5 commands and 1 to 2 subagents, mined from their top workflow verbs, each
justified by its count ("you typed some form of `deploy` 63 times").

## Courses worth your time
2 to 3, matched to gaps. Tell an advanced user which beginner ones to skip.

## Want me to build these?
Offer to create the commands / subagents / CLAUDE.md now, grounded in their real
build and test scripts (read those first so the generated files actually run).

## (If enabled) Roles for strong prompters
Only when the score band qualifies AND partner roles are enabled. Render per
`references/partners-and-ads.md`: labeled Sponsored, opt-in for any contact, and
the user's prompts never leave the machine.
```

## Principles

- **Honest over flattering.** A user who is told the truth about their weak spots and shown the exact fix will trust the strong-points praise too. Generic flattery reads as not having looked.
- **Their words, not invented ones.** Only quote prompts the analyzer surfaced. Only cite numbers it produced. If you need a file path for a rewrite and do not know the real one, write `<path>` rather than fabricating.
- **End in artifacts.** The report is the setup; the payoff is offering to build the leverage layer. Follow through if they say yes.
- **Read-only on history.** Never modify or move anything under `~/.claude/projects`. The analyzer only reads.
