# Course and video recommendations

Match resources to the user's detected gaps, do not dump the whole list. Two or three well-aimed recommendations beat ten. Pick based on the analyzer output, then say why each one fits them specifically.

Links change over time. If a link looks stale, point the user to the Anthropic Academy catalog (anthropic.skilljar.com) and the docs, and consider a quick web search for the current best video rather than asserting a dead URL.

## Gap to resource matrix

- **No leverage layer** (empty `slash_command_usage`, `custom_setup_present` false): the highest-value learning. Point to **Introduction to agent skills** and **Introduction to subagents** (Anthropic Academy, free, short), and the Anthropic blog post **"Steering Claude Code: skills, hooks, subagents and more"**.
- **Weak planning / direction** (few detailed kickoff prompts, lots of tiny vague nudges): **Claude Code best practices** (Anthropic's own talk) and **"How Claude Code's Creator Starts EVERY Project"**. Also teach plan mode (Shift+Tab).
- **General level-up for an already-competent user**: **Claude Code in Action** (the workflow course, not the 101), and a dense tips video such as **"32 Tricks to Level Up Claude Code"**.
- **Building an AI product / API work** (their history shows model routing, evals, prompts-as-data): **Building with the Claude API** (Anthropic Academy).
- **Runs out of context on long sessions** (very long sessions, lots of compaction): a short **context-management** video, plus teach `/context` and `/compact`.
- **Lots of revert/undo friction**: teach the rewind feature (double-tap Esc) directly, no course needed.

## Curated resources (verify before asserting a URL)

Anthropic official:
- Anthropic Academy catalog: https://anthropic.skilljar.com/ (free, email to enroll; includes Claude Code 101, Claude Code in Action, Introduction to agent skills, Introduction to subagents, Building with the Claude API, MCP courses)
- Claude Code best practices talk: https://www.youtube.com/watch?v=gv0WHhKelSE
- Steering Claude Code blog: https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more
- Slash commands docs: https://code.claude.com/docs/en/slash-commands
- Claude Code power user tips: https://support.claude.com/en/articles/14554000-claude-code-power-user-tips

Community videos (good but third-party, check they still exist):
- "How Claude Code's Creator Starts EVERY Project" (Austin Marchese)
- "32 Tricks to Level Up Claude Code in 16 Mins" (Nate Herk)
- "Claude Skills Tutorial (2026)" (Kevin Stratvert)

## Match to level, not just topic

If the analyzer shows a strong user (detailed kickoff prompts, healthy plan-then-approve rhythm, heavy usage), explicitly tell them to SKIP the 101 / beginner courses and go straight to skills, subagents, and API depth. Sending an advanced user to "Claude 101" reads as if you did not look at their data. If the analyzer shows a beginner (short vague prompts, high friction, little structure), start them with the fundamentals talk and Claude Code 101.
