#!/usr/bin/env python3
"""Agent usage signals of this repository from the agent tools' local session logs (for /weekly).

Usage:
  python3 tools/usage.py [--days 7 | --since YYYY-MM-DD] [--until YYYY-MM-DD] [--json]

Sources (read-only, this repository only):
  claude-code  $CLAUDE_CONFIG_DIR or ~/.claude → projects/<repo path slug>/**/*.jsonl
               tokens per model, cost and lines from the session's last `cost-state` record when present
  codex        $CODEX_HOME or ~/.codex → sessions/**/rollout-*.jsonl whose session cwd is this repository
               tokens from the last `token_count` event; no cost recorded
Copilot and Cursor keep no readable local logs: not counted.

Sessions are counted whole and assigned to the day they started. Supervision signals are counts of
human prompts, interrupts and rejected tool calls. Prompt text is never printed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import wf  # noqa: E402

COMMAND_RX = re.compile(r"<command-name>/?([\w:-]+)</command-name>")
CODEX_COMMAND_RX = re.compile(r"^/(?:prompts:)?([\w-]+)")
REJECTED = "tool use was rejected"
INTERRUPTED = "[Request interrupted by user"


def _ts(s: str | None) -> dt.datetime | None:
    if not s:
        return None
    try:
        t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return t.astimezone()  # naive timestamps are taken as local time


def _session(tool: str, sid: str) -> dict:
    return {"tool": tool, "id": sid, "start": None, "end": None, "step": None, "prompts": 0,
            "interrupts": 0, "rejected": 0, "models": {}, "cost": None, "lines": None}


def _seen(s: dict, t: dt.datetime | None) -> None:
    if t:
        s["start"] = min(s["start"] or t, t)
        s["end"] = max(s["end"] or t, t)


def _add(models: dict, model: str, **tok: int) -> None:
    m = models.setdefault(model, {"input": 0, "output": 0, "cache_write": 0, "cache_read": 0, "cost": None})
    for k, v in tok.items():
        m[k] += v or 0


# ---------------------------------------------------------------- claude code

def claude_dir() -> str:
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    return os.path.join(base, "projects", re.sub(r"[^A-Za-z0-9]", "-", wf.ROOT))


def _texts(content) -> list[str]:
    if isinstance(content, str):
        return [content]
    return [b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text"]


def _results(content) -> list[str]:
    out = []
    for b in content if isinstance(content, list) else []:
        if isinstance(b, dict) and b.get("type") == "tool_result":
            c = b.get("content")
            out.append(c if isinstance(c, str) else " ".join(_texts(c)))
    return out


def claude_sessions() -> list[dict]:
    sessions: dict[str, dict] = {}
    seen_msgs: set[str] = set()
    for f in sorted(glob.glob(os.path.join(claude_dir(), "**", "*.jsonl"), recursive=True)):
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                sid = d.get("sessionId")
                if not sid:
                    continue
                s = sessions.setdefault(sid, _session("claude-code", sid))
                kind = d.get("type")
                if kind == "cost-state":
                    s["cost"] = d.get("totalCostUSD")
                    s["lines"] = (d.get("totalLinesAdded", 0), d.get("totalLinesRemoved", 0))
                    s["cost_models"] = {k: {"input": v.get("inputTokens", 0), "output": v.get("outputTokens", 0),
                                            "cache_write": v.get("cacheCreationInputTokens", 0),
                                            "cache_read": v.get("cacheReadInputTokens", 0), "cost": v.get("costUSD")}
                                        for k, v in (d.get("modelUsage") or {}).items()}
                    if d.get("startTime"):
                        _seen(s, dt.datetime.fromtimestamp(d["startTime"] / 1000).astimezone())
                    continue
                if kind not in ("user", "assistant"):
                    continue
                _seen(s, _ts(d.get("timestamp")))
                msg = d.get("message") or {}
                if kind == "assistant":
                    key = f'{msg.get("id")}:{d.get("requestId")}'
                    model, u = msg.get("model"), msg.get("usage")
                    if key in seen_msgs or not u or not model or model.startswith("<"):
                        continue
                    seen_msgs.add(key)
                    _add(s["models"], model, input=u.get("input_tokens"), output=u.get("output_tokens"),
                         cache_write=u.get("cache_creation_input_tokens"), cache_read=u.get("cache_read_input_tokens"))
                    continue
                content = msg.get("content")
                s["rejected"] += sum(REJECTED in r for r in _results(content))
                if d.get("isMeta") or d.get("isSidechain") or d.get("userType", "external") != "external":
                    continue
                texts = [t.strip() for t in _texts(content)]
                if any(t.startswith(INTERRUPTED) for t in texts):
                    s["interrupts"] += 1
                    continue
                cmd = next((m.group(1) for t in texts if (m := COMMAND_RX.search(t))), None)
                if cmd:
                    s["step"] = s["step"] or cmd
                    s["prompts"] += 1
                elif any(t and not t.startswith("<") for t in texts):
                    s["prompts"] += 1
    for s in sessions.values():
        if s.get("cost_models"):
            s["models"] = s.pop("cost_models")
    return [s for s in sessions.values() if s["start"] and s["models"]]


# ---------------------------------------------------------------- codex

def codex_sessions() -> list[dict]:
    base = os.environ.get("CODEX_HOME") or os.path.expanduser("~/.codex")
    out = []
    for f in sorted(glob.glob(os.path.join(base, "sessions", "**", "rollout-*.jsonl"), recursive=True)):
        s, model, usage, ours = _session("codex", os.path.basename(f)), None, None, False
        with open(f, encoding="utf-8") as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                p, kind = d.get("payload") or {}, d.get("type")
                _seen(s, _ts(d.get("timestamp")))
                if kind == "session_meta":
                    s["id"] = p.get("id") or s["id"]
                    cwd = os.path.abspath(p.get("cwd") or "")
                    ours = cwd == wf.ROOT or cwd.startswith(wf.ROOT + os.sep)
                elif kind == "turn_context":
                    model = p.get("model") or model
                elif kind == "event_msg" and p.get("type") == "token_count":
                    usage = ((p.get("info") or {}).get("total_token_usage")) or usage
                elif kind == "event_msg" and p.get("type") == "user_message":
                    s["prompts"] += 1
                    m = CODEX_COMMAND_RX.match((p.get("message") or "").strip())
                    s["step"] = s["step"] or (m.group(1) if m else None)
                elif kind == "event_msg" and p.get("type") == "turn_aborted":
                    s["interrupts"] += 1
        if ours and usage and s["start"]:
            cached = usage.get("cached_input_tokens", 0)
            _add(s["models"], model or "codex", input=usage.get("input_tokens", 0) - cached,
                 output=usage.get("output_tokens", 0), cache_read=cached)
            out.append(s)
    return out


# ---------------------------------------------------------------- tiers

def tier_of(model: str) -> str | None:
    """Tier whose configured model is `model` (exact name first, then alias inside the name: haiku → claude-haiku-5-5)."""
    pairs = [(tier, wf.model_for(tool, tier).lower()) for tool in wf.enabled_tools() for tier in wf.TIERS]
    m = model.lower()
    return (next((t for t, a in pairs if a == m), None)
            or next((t for t, a in pairs if re.search(rf"(^|[-_ ]){re.escape(a)}($|[-_ ])", m)), None))


def expected_tier(step: str | None) -> str | None:
    if not step:
        return None
    return wf.workflow().get("commands", {}).get(step, {}).get("tier")


def main_model(s: dict) -> str:
    return max(s["models"], key=lambda m: s["models"][m]["output"])


# ---------------------------------------------------------------- output

def collect(since: dt.date, until: dt.date) -> list[dict]:
    rows = [s for s in claude_sessions() + codex_sessions() if since <= s["start"].date() <= until]
    for s in rows:
        s["main"] = main_model(s)
        s["tier"] = expected_tier(s["step"])
        s["main_tier"] = tier_of(s["main"])
        s["mismatch"] = bool(s["tier"] and s["main_tier"] and s["tier"] != s["main_tier"])
    return sorted(rows, key=lambda s: s["start"])


def _n(v: int) -> str:
    return f"{v / 1e6:.2f}M" if v >= 1e6 else f"{v / 1e3:.1f}k" if v >= 1e3 else str(v)


def _usd(v: float | None) -> str:
    return "—" if v is None else f"{v:.2f}"


def render(rows: list[dict], since: dt.date, until: dt.date) -> str:
    by_tool = {t: sum(s["tool"] == t for s in rows) for t in ("claude-code", "codex")}
    out = [f"# Agent usage — {since} → {until}", "",
           f"Sources: claude-code {by_tool['claude-code']} sessions, codex {by_tool['codex']} sessions "
           "(local logs of this repository). Copilot, Cursor: no local logs. Sessions counted whole, by start day.", ""]
    if not rows:
        return "\n".join(out + ["No sessions in the period."])
    out += ["| Start | Tool | Step | Step tier | Main model (tier) | Prompts | Interrupts | Rejected | Output tok | Cache read tok | Lines +/− | Cost USD |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in rows:
        out.append(f"| {s['start']:%m-%d %H:%M} | {s['tool']} | {s['step'] or '—'} | {s['tier'] or '—'} "
                   f"| {s['main']} ({s['main_tier'] or '?'}){' ✗' if s['mismatch'] else ''} | {s['prompts']} | {s['interrupts']} "
                   f"| {s['rejected']} | {_n(sum(m['output'] for m in s['models'].values()))} "
                   f"| {_n(sum(m['cache_read'] for m in s['models'].values()))} "
                   f"| {'+%d/−%d' % s['lines'] if s['lines'] else '—'} | {_usd(s['cost'])} |")
    models: dict[str, dict] = {}
    for s in rows:
        for name, m in s["models"].items():
            t = models.setdefault(name, {"sessions": 0, "input": 0, "output": 0, "cache_write": 0, "cache_read": 0, "cost": None})
            t["sessions"] += 1
            for k in ("input", "output", "cache_write", "cache_read"):
                t[k] += m[k]
            if m.get("cost") is not None:
                t["cost"] = (t["cost"] or 0) + m["cost"]
    out += ["", "| Model | Tier | Sessions | Input tok | Output tok | Cache write tok | Cache read tok | Cost USD |",
            "|---|---|---|---|---|---|---|---|"]
    for name, t in sorted(models.items(), key=lambda kv: -kv[1]["output"]):
        out.append(f"| {name} | {tier_of(name) or '?'} | {t['sessions']} | {_n(t['input'])} | {_n(t['output'])} "
                   f"| {_n(t['cache_write'])} | {_n(t['cache_read'])} | {_usd(t['cost'])} |")
    costs = [s["cost"] for s in rows if s["cost"] is not None]
    out += ["", f"Totals: {len(rows)} sessions · {sum(s['prompts'] for s in rows)} prompts · "
            f"{sum(s['interrupts'] for s in rows)} interrupts · {sum(s['rejected'] for s in rows)} rejected tool calls · "
            f"cost {_usd(sum(costs)) if costs else '—'} USD ({len(costs)}/{len(rows)} sessions with recorded cost) · "
            f"tier mismatches (✗): {sum(s['mismatch'] for s in rows)}"]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--since", type=dt.date.fromisoformat)
    ap.add_argument("--until", type=dt.date.fromisoformat, default=dt.date.today())
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    since = a.since or a.until - dt.timedelta(days=a.days)
    rows = collect(since, a.until)
    if a.json:
        print(json.dumps([{**s, "start": s["start"].isoformat(), "end": s["end"].isoformat()} for s in rows], indent=2))
    else:
        print(render(rows, since, a.until))


if __name__ == "__main__":
    main()
