# Coaching rubric

How to turn the analyzer's numbers into coaching that is honest, specific, and grounded in the user's own history. The script measures; you judge. Never invent a number the script did not produce, and never quote a prompt the user did not actually write.

## The prime directive: calibrate to evidence, do not flatter

The fastest way to lose a user's trust is to tell them they are great when the data says otherwise, or to scold a strong user with generic tips. Read the numbers first, then decide what kind of user this is. Two users with the same short-prompt count can be opposite cases:

- Someone whose short prompts are `yes fix it all`, `merge`, `push to main` is running a healthy **plan-then-approve** workflow. That is a sign of skill, not weakness. Praise it.
- Someone whose short prompts are `fix it`, `still broken`, `no that's wrong`, `try again` is under-specifying and paying for it in rework. That needs coaching.

The `top_short_prompts` field is what tells these apart. Look at it before you say a single word about prompt length.

## Reading each metric

- **length.buckets / pct_tiny_le40 / pct_detailed_ge300**, a bimodal spread (many tiny AND many detailed) is usually healthy: short nudges when steering, real briefs when kicking off work. Worry only when tiny prompts dominate AND `top_short_prompts` shows vague nudges rather than approvals.
- **pct_ending_in_question**, high (say 25%+) means the user often deliberates out loud. This is fine for exploration, but when they have already decided, a trailing `?` makes the model stop and ask back instead of acting. This is the single most common fixable habit. Coach it only if the number is genuinely high.
- **friction_signals**, `still`, `again`, `revert/undo`, `that's wrong` in prose are rework signals. A high `revert/undo` count is a strong hint they should learn the rewind feature (double-Esc). Note these are counted on prose only, but some noise remains, so treat them as directional, not exact.
- **workflow_vocabulary**, the top few verbs are the user's real, repeated work. Any verb with a high count is a candidate for a custom command or subagent (see command-patterns.md).
- **slash_command_usage**, if this is nearly empty (only `/model`, `/clear`, etc.), the user has not discovered the leverage layer. This is almost always the biggest single opportunity, because it converts repeated typing into one word.
- **custom_setup_present**, if `user_commands_dir` / `user_agents_dir` are false, they have no custom commands or subagents at all. Say so plainly and make building them the headline recommendation.
- **file_at_mentions**, high is good; it means they anchor references to real files. If low, coach the specificity dimension harder.

## The coaching dimensions

Cover these, but only the ones the data supports. Do not lecture on specificity if their prompts are already specific.

1. **Planning / direction.** Do they set a goal and a definition of done, or just a verb? The best prompts say what, why, and how the model will know it is finished. If their detailed prompts already do this, praise it and show one as a model. If not, teach it.
2. **Specificity / anchoring.** Do they name files, functions, and exact strings, or lean on "the thing", "that button", "the KPI view"? Vague references force the model to hunt. Use their `file_at_mentions` and a real vague example to make the point.
3. **Question vs instruction.** Separate "think with me" (a real question, keep the `?`) from "go do it" (an imperative). Only raise this if `pct_ending_in_question` is high.
4. **Examples.** For generation or transformation tasks, one worked example (input then desired output) beats a paragraph of description. If their history shows format-sensitive work with no examples, suggest it.
5. **One prompt, one mission.** Do they bundle a decision, a musing, and a question into one message? If the sample shows this, suggest numbering distinct asks or splitting them.

## Before/after rewrites: the highest-value part

Generic advice is forgettable. Rewriting the user's OWN prompts is what lands. Pull 3 to 5 real prompts from `prose_sample` and `top_short_prompts`, and for each show:

```
Before (yours): "<their exact prompt>"
Why it costs you: <the specific round-trip or hunt it causes>
After: "<a concrete rewrite that keeps their voice>"
```

Rules for good rewrites:
- Keep their voice and intent. You are sharpening, not replacing.
- Change one thing per example so the lesson is legible.
- Prefer real, plausible file paths and specifics drawn from their own context over invented ones. If you do not know the real path, say "<path>" rather than fabricating.
- Never invent a failure that the data does not support.

## Tone

Direct, warm, specific. Lead with the honest verdict (are they good or not, per the data). No horoscope generalities. If they are already strong, say so and aim the advice at the next level (leverage), not at basics they have clearly mastered.
