# Privacy Policy for prompt-coach

Last updated: 1 July 2026

prompt-coach is a Claude Code skill that reviews how you use Claude Code and coaches you to improve. This policy explains, in plain terms, what it does with your data. The short version: your data stays on your machine.

## What it accesses

To review your prompting, the skill reads your local Claude Code transcript files in `~/.claude/projects` on your own device. It reads them **read-only** and never modifies, moves, or deletes them. It only looks at the prompts you typed, in order to compute your prompt score, your anti-patterns, and your coaching.

## What leaves your machine

By default, **nothing**. The analysis runs entirely on your device using a local script. The skill does not transmit your prompts, your transcripts, your report, your score, or anything the security scan finds. There is no analytics, no telemetry, and no tracking.

## Security scan

The skill checks your past prompts for credentials you may have accidentally pasted (API keys, database passwords, and the like), so that you can rotate them. This runs entirely on your device and only ever shows **masked** previews. It never records or transmits the full value of any secret.

## Optional partner roles

The skill can display a small, clearly labelled block of sponsored job listings to strong scorers. This feature is **off by default**. If the maintainer turns it on, the skill downloads a public listings file over HTTPS to show current roles. That request is a one-way public download and sends none of your personal or usage data. As with any web request, the host serving that public file can see your IP address and the time of the request; no other information is shared.

There is currently no feature that sends your data anywhere. Any future opt-in feature (for example, sharing your numeric score to see matched roles) would require your explicit consent, would send only that single number, and would never include your prompts or history.

## Data retention

The skill stores nothing of its own. Your report exists only within your Claude Code session. Your transcripts are managed by Claude Code, not by this skill.

## Children

This skill is intended for developers and is not directed at children.

## Changes

If this policy changes, the updated version will be posted in this repository with a new date above.

## Contact

Questions about privacy? Open an issue on this repository: https://github.com/SnapCrackle2383/claude-code-coach/issues
