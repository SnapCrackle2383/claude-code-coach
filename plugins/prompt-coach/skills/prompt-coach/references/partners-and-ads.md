# Partner roles and advertising

This is optional and OFF by default (`assets/partners.json` ships with `enabled: false`), so the skill shows no ads unless the owner turns them on. That default matters: a coaching skill that reads private history must never surprise the user with monetization. Read this whole file before rendering anything sponsored.

## The two sides of the marketplace

- **Seekers** (the people running the skill): a strong score means a skilled Claude Code operator. Above a score band, the report can show clearly-labeled partner roles.
- **Advertisers** (companies with roles): they want their roles shown to high scorers. The report carries a single "advertise here" link so they can reach the owner.

## The hard privacy line (do not cross it)

All analysis stays on the user's machine. The report never sends the user's prompts, history, or score anywhere as a side effect. The ONLY outbound data allowed is an explicit, opt-in action the user chooses ("share my score to see matched roles"), and even then it sends the score number alone, never prompt text. If `opt_in_required` is true, do not transmit anything without a clear yes.

## How to render the seeker block

Show it only when ALL of these are true:
1. `partners.enabled` is true, and
2. the user's `prompt_score.band` is at or above `min_score_band`, and
3. the resolved roles list is non-empty. If it is empty (no current inventory), render nothing at all, never an empty sponsored section.

Then render a block that is unmistakably labeled as sponsored, for example:

```
## Partner roles for strong prompters  (Sponsored)
You scored 82/100 (Advanced). These partners are hiring people who work like this:
- Senior AI Engineer, Example Co, Remote → <url>
Want your roles shown here? → <advertise_contact_url>
```

Never imply the user is "top X%" unless there is a real score distribution to back the claim (there is not, locally). Lead with the raw score and band instead. Never imply affiliation or endorsement by Anthropic or anyone else; example listings must be labeled as examples.

## Advertiser onboarding: the better way than a raw email

A raw email address baked into a public skill file gets scraped and cannot capture structured detail. Prefer, in order:

1. **A link to a short intake form** (Tally, Typeform, a page on your site) at `advertise_contact_url`. It captures company, role, link, and budget, changes without republishing the skill, and shields your inbox. This is the recommended default.
2. **A role-based address** (e.g. `partners@yourdomain`) only if you must show an email. Never a personal address.

## Keeping listings fresh without republishing (the `roles_url` seam)

Editing `assets/partners.json` and re-publishing the skill for every roles change does not scale. The clean upgrade is a small remote config, and the field for it already exists: `roles_url` in `partners.json`.

How it resolves when rendering the sponsored block:
1. If `roles_url` is set and reachable, fetch it (a plain public GET) and use those roles.
2. If it is empty, unreachable, or returns invalid JSON, fall back to the bundled `roles` array. Never error the report over a failed ad fetch.

The hosted file is just a JSON array of the same role objects (`company`, `title`, `location`, `url`, `sponsored`). Host it anywhere you can edit without a deploy: a GitHub Gist raw URL, a file in a repo via `raw.githubusercontent.com`, or a public object on your own domain / S3 / R2. Editing that one file changes what every user sees, with no skill republish.

Two rules that keep this honest and safe:
- **Keep the analyzer offline.** `analyze_prompts.py` makes no network calls and that is the privacy core. The `roles_url` fetch happens only in the report step, only when `enabled` is true and the score band qualifies, and it sends no user data (it is a GET of your public file). Disclose the fetch in the rendered block.
- **Fetch roles, never push prompts.** Pulling your public ad file is fine. The user's prompts, history, and score still never leave the machine unless they take the separate opt-in action.

Build this only when you actually have inventory; the bundled file is fine to launch with.

## Honesty and compliance

- Label sponsored content as sponsored. Do not disguise ads as coaching.
- Do not make hiring or income claims you cannot support.
- Get explicit consent before any contact or data transmission.
- The coaching itself must be identical whether or not the user qualifies for the sponsored block. The advice is never pay-to-alter.
