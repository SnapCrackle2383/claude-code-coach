#!/usr/bin/env python3
"""
analyze_prompts.py, the deterministic engine behind the prompt-coach skill.

Reads a Claude Code user's OWN transcript history (~/.claude/projects/**/*.jsonl),
extracts only the prompts the human actually typed, and computes objective
diagnostics plus a curated sample of real prompts for the model to coach on.

Read-only. No network. Nothing leaves the machine. It only ever prints a JSON
summary to stdout so the calling model can interpret it.

Usage:
  python3 analyze_prompts.py                 # analyze all projects
  python3 analyze_prompts.py --project NAME   # substring-match one project dir
  python3 analyze_prompts.py --root PATH       # custom projects root
  python3 analyze_prompts.py --sample 30       # how many prose prompts to surface
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import Counter

# Content that is NOT a human-authored prompt (system injections, slash-command
# expansions, tool plumbing). If a string prompt starts with one of these, drop it.
NON_PROMPT_PREFIXES = (
    "<command-name", "<command-message", "<command-args", "<command-stdout",
    "<local-command", "<bash-", "<system-reminder", "<user-memory-input",
    "<task-notification", "Caveat:", "[Request interrupted",
)

# Heuristic signals that a "prompt" is really pasted code / logs / a task dump,
# which would pollute the prose-quality stats. Used to separate prose from pastes.
PASTE_SIGNALS = re.compile(
    r"className|=>|\bfunction \b|\breturn \b|\bconst \b|\bimport \b|\{\"|\.tsx"
    r"|error TS[0-9]|taskNotification|statusCompleted|stdout|https?://|<tool_use|tool_result",
    re.IGNORECASE,
)

# Workflow verbs worth mining. Repeated hits are strong candidates for a custom
# slash command or subagent. Grouped so synonyms collapse to one workflow.
WORKFLOW_TERMS = {
    "merge": r"\bmerge",
    "push": r"\bpush",
    "commit": r"\bcommit",
    "deploy": r"\bdeploy|\brailway|\bvercel|\bfly deploy",
    "test": r"\btest\b|\bvitest|\bjest|\bpytest",
    "typecheck": r"\btypecheck|\btype check|\btsc\b",
    "lint": r"\blint\b|\beslint|\bruff\b",
    "build": r"\bbuild\b",
    "eval": r"\beval\b|\bevals\b|\bgolden\b|\bscoreboard\b|\bbenchmark\b",
    "audit": r"\baudit\b",
    "review": r"\breview\b|\bcode review",
    "rerun": r"\bre-?run\b|\bregen|\breprocess",
    "revert": r"\brevert\b|\bundo\b|\broll ?back",
    "refactor": r"\brefactor",
    "migrate": r"\bmigrat",
    "fix": r"\bfix\b|\bbug\b|\bbroken\b",
    "seed": r"\bseed\b",
    "screenshot": r"\bscreenshot|\bsnapshot\b",
}


def collect_user_prompts(files):
    """Return (prompts, slash_cmd_counter). Each prompt is {t, c, sidechain, cwd}."""
    prompts = []
    slash_cmds = Counter()
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    # Cheap pre-filter: skip lines that can't be a user turn.
                    if '"type":"user"' not in line and '"type": "user"' not in line:
                        continue
                    try:
                        obj = json.loads(line)
                    except (ValueError, json.JSONDecodeError):
                        continue
                    if obj.get("type") != "user":
                        continue
                    msg = obj.get("message") or {}
                    content = msg.get("content")
                    # Tool results arrive as list content; typed prompts as a string.
                    if not isinstance(content, str):
                        continue
                    stripped = content.lstrip()
                    # Tally slash-command usage before discarding those messages.
                    m = re.match(r"<command-name>\s*(/[^<\s]+)", stripped)
                    if m:
                        slash_cmds[m.group(1)] += 1
                    if stripped.startswith(NON_PROMPT_PREFIXES):
                        continue
                    if not stripped:
                        continue
                    prompts.append({
                        "t": obj.get("timestamp", ""),
                        "c": content,
                        "sidechain": bool(obj.get("isSidechain")),
                        "cwd": obj.get("cwd", ""),
                    })
        except (OSError, IOError):
            continue
    return prompts, slash_cmds


def bucket(n):
    if n <= 15:
        return "tiny (<=15, one-word/nudge)"
    if n <= 40:
        return "very short (16-40)"
    if n <= 100:
        return "short (41-100)"
    if n <= 300:
        return "medium (101-300)"
    if n <= 800:
        return "detailed (301-800)"
    return "very detailed (800+)"


# High-precision credential shapes. Read-only detection; matches are masked
# before they ever leave this process. This is a safety feature, not storage.
SECRET_PATTERNS = [
    ("Anthropic API key", re.compile(r"sk-ant-api\d{2}-[A-Za-z0-9_\-]{8}")),
    ("OpenAI API key", re.compile(r"sk-(?:proj-)?(?!ant)[A-Za-z0-9]{20,}")),
    ("AWS access key ID", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("DB URL with password", re.compile(
        r"(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?)://[A-Za-z0-9_.\-]+:[^@\s\"']+@")),
    ("GitHub token", re.compile(r"(?:ghp_|gho_|ghu_|ghs_|ghr_|github_pat_)[A-Za-z0-9_]{20,}")),
    ("Google API key", re.compile(r"AIza[0-9A-Za-z_\-]{20,}")),
    ("Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}")),
    ("Private key block", re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----")),
]

RETRY_SET = {"try", "try again", "try now", "retry", "again", "run it again",
             "go again", "once more", "and again", "now"}


def _mask(s):
    s = s.strip()
    keep = min(12, max(4, len(s) // 3))
    return s[:keep] + "…[redacted]"


def scan_secrets(prompts):
    """Flag credential-shaped strings pasted into prompts. Masked, read-only."""
    summary, samples, hit_prompts = {}, {}, 0
    for p in prompts:
        c = p["c"]
        prompt_hit = False
        for label, rgx in SECRET_PATTERNS:
            for m in rgx.finditer(c):
                summary[label] = summary.get(label, 0) + 1
                samples.setdefault(label, set()).add(_mask(m.group(0)))
                prompt_hit = True
        if prompt_hit:
            hit_prompts += 1
    return {
        "found": bool(summary),
        "by_type": summary,
        "masked_samples": {k: sorted(v)[:3] for k, v in samples.items()},
        "prompts_containing_secrets": hit_prompts,
    }


def detect_anti_patterns(prompts, prose):
    """Named failure modes with real counts. Memorable beats abstract."""
    n = len(prompts) or 1

    def pct(x):
        return round(x / n * 100, 1)

    trailing = sum(1 for p in prompts if p["c"].rstrip().endswith("?"))

    retry = 0
    for p in prose:
        s = p["c"].strip().lower().rstrip(".!")
        if s in RETRY_SET or re.match(r"^still (not working|broken|failing|the same|wrong)", s):
            retry += 1

    vague = 0
    for p in prose:
        c = p["c"].strip()
        if len(c) < 60 and "@" not in c and re.match(
                r"(?i)^(fix|do|change|redo|sort|update|make|move|remove|add)\s+(it|this|that|them)\b", c):
            vague += 1

    bundle = 0
    for p in prompts:
        c = p["c"]
        # Real multi-ask signals: two questions, a numbered list, or "also" + a question.
        # Bare "then" is excluded because "do X then Y" is normal single-intent prose.
        if len(c) > 150 and (c.count("?") >= 2 or re.search(r"\b1\..*\b2\.", c, re.S)
                             or (re.search(r"\balso\b", c, re.I) and "?" in c)):
            bundle += 1

    dump = 0
    for p in prompts:
        c = p["c"]
        if len(c) > 400 and PASTE_SIGNALS.search(c) and len(c.strip().split("\n", 1)[0].split()) < 12:
            dump += 1

    return [
        {"name": "The Trailing Question", "count": trailing, "pct": pct(trailing),
         "note": "decided instructions ending in '?' make the model deliberate instead of act"},
        {"name": "The Blind Retry", "count": retry, "pct": pct(retry),
         "note": "'try again' with no new info re-runs the same thing; say what changed"},
        {"name": "The Vague-It", "count": vague, "pct": pct(vague),
         "note": "'fix it' with no anchor forces a guess; name the target and symptom"},
        {"name": "The Mega-Bundle", "count": bundle, "pct": pct(bundle),
         "note": "several missions in one message; the middle one silently gets dropped"},
        {"name": "The Silent Paste-Dump", "count": dump, "pct": pct(dump),
         "note": "a big paste with almost no framing; say what you want done with it"},
    ]


def compute_score(out):
    """Deterministic 0-100 prompt score with a transparent breakdown."""
    d = out["length"]["pct_detailed_ge300"]
    fm = out["file_at_mentions"]
    q = out["question_vs_instruction"]["pct_ending_in_question"]
    fr = out["friction_signals"]
    prose_n = out["totals"]["prose_prompts"] or 1
    slash = out["slash_command_usage"]
    setup = out["custom_setup_present"]

    direction = 30 if d >= 20 else 20 if d >= 12 else 10 if d >= 5 else 0
    spec = 20 if fm >= 40 else 10 if fm >= 10 else 0
    dec = 20 if q <= 15 else 10 if q <= 30 else 0
    rework = fr.get("still", 0) + fr.get("again", 0) + fr.get("that's wrong", 0)
    rr = rework / prose_n * 100
    eff = 15 if rr < 8 else 10 if rr < 15 else 5
    used = any(k not in ("/model", "/clear", "/compact", "/help", "/init") for k in slash)
    lev = 15 if used else (5 if (setup.get("user_commands_dir") or setup.get("user_agents_dir")) else 0)

    total = direction + spec + dec + eff + lev
    band = ("Expert" if total >= 85 else "Advanced" if total >= 70 else
            "Proficient" if total >= 50 else "Developing" if total >= 30 else "Beginner")
    return {
        "score": total, "out_of": 100, "band": band,
        "components": [
            {"name": "Direction & structure", "points": direction, "max": 30,
             "note": f"{d}% of prompts are detailed briefs (300+ chars)"},
            {"name": "Specificity & anchoring", "points": spec, "max": 20,
             "note": f"{fm} file @-mentions"},
            {"name": "Decisiveness", "points": dec, "max": 20,
             "note": f"{q}% of prompts end in a question mark"},
            {"name": "Efficiency (low rework)", "points": eff, "max": 15,
             "note": f"~{round(rr)}% rework rate"},
            {"name": "Leverage (commands/agents)", "points": lev, "max": 15,
             "note": "custom commands/subagents in active use" if used else "leverage layer thin or unused"},
        ],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--project", default=None,
                    help="substring to match a single project directory")
    ap.add_argument("--sample", type=int, default=30,
                    help="how many prose prompts to surface for coaching")
    args = ap.parse_args()

    if not os.path.isdir(args.root):
        print(json.dumps({"error": f"No Claude Code history found at {args.root}. "
                          "Is this a Claude Code machine?"}))
        return

    pattern = os.path.join(args.root, "*", "**", "*.jsonl")
    files = glob.glob(pattern, recursive=True)
    if args.project:
        files = [f for f in files if args.project.lower() in f.lower()]
    if not files:
        print(json.dumps({"error": "No transcript files matched.",
                          "root": args.root, "project": args.project}))
        return

    all_prompts, slash_cmds = collect_user_prompts(files)
    prompts = [p for p in all_prompts if not p["sidechain"]]

    if not prompts:
        print(json.dumps({"error": "Found transcripts but no human-typed prompts.",
                          "files_scanned": len(files)}))
        return

    lengths = [len(p["c"]) for p in prompts]
    lengths_sorted = sorted(lengths)
    n = len(prompts)
    median = lengths_sorted[n // 2]

    buckets = Counter(bucket(x) for x in lengths)

    ends_q = sum(1 for p in prompts if p["c"].rstrip().endswith("?"))

    # Separate genuine prose from pasted code/logs so quality stats aren't polluted.
    prose = [p for p in prompts if not PASTE_SIGNALS.search(p["c"])]
    prose_short = [p for p in prose if len(p["c"]) <= 40]
    prose_mid = [p for p in prose if 60 <= len(p["c"]) <= 550]

    # Top short prompts (mostly approvals vs nudges), very diagnostic of workflow.
    short_counter = Counter(p["c"].strip() for p in prose_short)

    # Workflow vocabulary frequency on short/medium prompts (avoid paste pollution).
    mineable = [p["c"] for p in prose if len(p["c"]) < 500]
    workflow_hits = {}
    for label, rgx in WORKFLOW_TERMS.items():
        r = re.compile(rgx, re.IGNORECASE)
        workflow_hits[label] = sum(1 for c in mineable if r.search(c))
    workflow_hits = dict(sorted(workflow_hits.items(), key=lambda kv: -kv[1]))

    # Friction signals (rework / correction) on prose only.
    friction_terms = {
        "still": r"\bstill\b", "again": r"\bagain\b", "not working": r"not work",
        "revert/undo": r"\brevert\b|\bundo\b", "why": r"\bwhy\b",
        "no,/nope": r"^(no,|no\.|nope)", "instead": r"\binstead\b",
        "actually": r"\bactually\b", "that's wrong": r"wrong|incorrect|not right",
    }
    friction = {}
    for label, rgx in friction_terms.items():
        r = re.compile(rgx, re.IGNORECASE)
        friction[label] = sum(1 for p in prose if r.search(p["c"]))

    # File @-mentions (a good habit worth measuring).
    at_mentions = sum(1 for p in prompts if re.search(r"@[\"']?[~/]", p["c"]))

    # Curated prose sample for the model to coach on (varied lengths).
    sample = [p["c"].replace("\n", " ⏎ ")[:400] for p in prose_mid]
    # Even spread across the sample rather than the first N.
    if len(sample) > args.sample and args.sample > 0:
        step = len(sample) / args.sample
        sample = [sample[int(i * step)] for i in range(args.sample)]

    # Distinct active days and project spread.
    days = {p["t"][:10] for p in prompts if p["t"]}
    projects = Counter(os.path.basename(os.path.dirname(f)) for f in files)

    out = {
        "totals": {
            "typed_prompts": n,
            "prose_prompts": len(prose),
            "likely_pastes": n - len(prose),
            "files_scanned": len(files),
            "active_days": len(days),
            "date_range": [min(days) if days else "", max(days) if days else ""],
        },
        "length": {
            "mean_chars": round(sum(lengths) / n),
            "median_chars": median,
            "buckets": dict(buckets),
            "pct_tiny_le40": round(sum(1 for x in lengths if x <= 40) / n * 100),
            "pct_detailed_ge300": round(sum(1 for x in lengths if x >= 300) / n * 100),
        },
        "question_vs_instruction": {
            "prompts_ending_in_question": ends_q,
            "pct_ending_in_question": round(ends_q / n * 100),
        },
        "top_short_prompts": short_counter.most_common(30),
        "workflow_vocabulary": workflow_hits,
        "friction_signals": friction,
        "file_at_mentions": at_mentions,
        "slash_command_usage": dict(slash_cmds.most_common(20)),
        "custom_setup_present": {
            "user_commands_dir": os.path.isdir(os.path.expanduser("~/.claude/commands")),
            "user_agents_dir": os.path.isdir(os.path.expanduser("~/.claude/agents")),
            "user_skills_dir": os.path.isdir(os.path.expanduser("~/.claude/skills")),
        },
        "projects_by_session_count": dict(projects.most_common(10)),
        "prose_sample": sample,
    }
    out["anti_patterns"] = detect_anti_patterns(prompts, prose)
    out["secret_scan"] = scan_secrets(all_prompts)
    out["prompt_score"] = compute_score(out)
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
