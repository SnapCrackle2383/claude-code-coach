# Recommending custom commands and subagents

The analyzer's `workflow_vocabulary` and `top_short_prompts` reveal the work the user does over and over. Every high-frequency workflow is a chance to replace repeated typing with one word. This is usually the single highest-leverage change you can offer, especially when `custom_setup_present` shows they have none.

## How to choose what to recommend

1. Look at the top 4 to 6 workflow verbs by count. Those are real, repeated work.
2. Group synonyms into one command. `merge` + `push` + `commit` is one shipping workflow, not three commands.
3. Recommend 3 to 5 commands maximum in the first pass. A giant list is intimidating and most goes unused. Start with the ones tied to their highest counts.
4. Recommend a subagent when a task is either (a) verbose enough to pollute the main context (eval runs, large test suites, log analysis) or (b) a repeated review/checklist pass. Subagents keep the main conversation clean and can be reused.
5. Ground each recommendation in their number: "you typed some form of `merge` N times" is far more persuasive than "consider a ship command."

## Common workflow to command mappings

- **merge / push / commit** -> `/ship`: run typecheck + tests, stage only the relevant files, commit in the user's style, push. Guard against `git add -A` if they work on WIP-heavy branches.
- **eval / golden / scoreboard / benchmark** -> `/eval`: run the project's eval or test harness and report the real numbers honestly.
- **audit / review before merge** -> `/audit`: a full regression pass (gates + a hunt for the user's typical regression classes) before shipping.
- **rerun / regen / reprocess a data job** -> `/rerun <arg>`: re-run a pipeline for a named input, then verify.
- **deploy / railway / vercel / fly** -> `/deploy`: deploy and then verify health, rather than trusting an exit code.
- **review** (repeated code review) -> a `reviewer` subagent scoped to the project's real invariants.

Always adapt names and steps to the user's actual stack (read their package.json / Makefile / CI config first). Do not hardcode another project's script names.

## Command file template

User-level commands live in `~/.claude/commands/<name>.md` and work from any directory. Project-level commands live in `<repo>/.claude/commands/<name>.md`. Prefer user-level when the user juggles several clones of the same project; prefer project-level when the command is truly repo-specific.

```markdown
---
description: One line shown in the slash-command menu
argument-hint: "[optional: what an argument means]"
---

Imperative instructions for what to do when this command runs.
Use $ARGUMENTS where the user's argument should be substituted.
State the gates, the order, and what "done" looks like.
```

## Subagent file template

Subagents live in `~/.claude/agents/<name>.md` (or `<repo>/.claude/agents/`). The `description` is what makes the main agent decide to delegate, so make it concrete about when to use it.

```markdown
---
name: eval-runner
description: Runs the test/eval harness in an isolated context and returns only the scores and failures. Use when you need results without filling the main conversation with verbose output.
tools: Bash, Read, Grep, Glob
---

System prompt: the agent's single job, the exact commands it may run,
and the tight format it must return. Tell it what NOT to do (e.g. do not
fix anything, just report), so it stays a clean, reusable tool.
```

## Offer to build, do not just advise

After presenting the recommendations, offer to create the files immediately, grounded in the user's real scripts. Building a working `/ship` they can use in the next session is far more valuable than a description of one. If they accept, read their actual build/test/deploy commands first so the generated commands run for real.
