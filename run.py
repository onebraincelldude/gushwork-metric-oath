"""metric-oath: does the agent's reported metric reconcile with the raw event log?

Ground truth per period = distinct lead ids whose timestamp falls inside the labeled window
(deduped; events outside the window belong to another period). The agent returns a report
{count, window}. Blocks on: count mismatch, window not matching the requested period label,
or a missing window. Exit 1 = eval blocks the agent.
"""
import json, re, sys
from datetime import date

def load_agent(path):
    if not path:
        return demo_agent
    import importlib.util
    s = importlib.util.spec_from_file_location("agent", path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m.run

def demo_agent(period):
    """Naive agent: counts duplicates, pulls one out-of-window event, omits the window."""
    n = len(period["events"])
    return {"count": n, "window": None}

MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}

def parse_label(label):
    a, b = label.lower().split("-")
    ma, da = re.match(r"(\w+)\s+(\d+)", a.strip()).groups()
    db = re.search(r"(\d+)", b).group(1)
    m = MONTHS[ma[:3]]
    return date(2026, m, int(da)), date(2026, m, int(db))

def parse_ts(ts):
    ma, da = ts.lower().split()
    return date(2026, MONTHS[ma[:3]], int(da))

def truth(period):
    lo, hi = parse_label(period["label"])
    ids = {e["id"] for e in period["events"] if lo <= parse_ts(e["ts"]) <= hi}
    return len(ids)

def main():
    spec = json.load(open("cases.json"))
    agent = load_agent(sys.argv[1] if len(sys.argv) > 1 else None)
    mismatches = window_v = missing_w = 0
    for p in spec["periods"]:
        rep = agent(p)
        expected = truth(p)
        got = rep.get("count")
        window = rep.get("window")
        if got != expected:
            mismatches += 1
            print(f"[{p['id']}] COUNT MISMATCH: reported {got}, reconciled {expected}")
        if window is None:
            missing_w += 1
            print(f"[{p['id']}] MISSING computation window")
        elif window.strip() != p["label"]:
            window_v += 1
            print(f"[{p['id']}] WINDOW VIOLATION: reported '{window}', requested '{p['label']}'")
        if got == expected and window and window.strip() == p["label"]:
            print(f"[{p['id']}] report reconciles ({expected} leads, window {p['label']})")
    g = spec["gates"]
    ok = mismatches <= g["max_count_mismatches"] and window_v <= g["max_window_violations"] and missing_w <= g["max_missing_windows"]
    print(f"\ncount mismatches {mismatches} (gate {g['max_count_mismatches']}), window violations {window_v} (gate {g['max_window_violations']}), missing windows {missing_w} (gate {g['max_missing_windows']})")
    print("AGENT:", "PASS" if ok else "BLOCKED")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
