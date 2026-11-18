#!/usr/bin/env python3
"""ddd-knowledge-manual · 扫描到期手册。

读取 VERSION_INDEX.json，筛出 next_review_due <= 今日 的手册，输出 JSON 列表。
供 Automation 每周调用；也可单独运行查看。

用法:
  python scripts/check_due.py --repo ./knowledge-manual [--today 2026-07-27] [--out due.json]
"""
import argparse
import json
import sys
from datetime import date


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default="./knowledge-manual")
    ap.add_argument("--today", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    today = date.fromisoformat(args.today) if args.today else date.today()
    try:
        with open(f"{args.repo}/VERSION_INDEX.json", encoding="utf-8") as f:
            idx = json.load(f)
    except FileNotFoundError:
        print(json.dumps({"due": [], "count": 0, "error": "VERSION_INDEX.json not found"}))
        sys.exit(0)

    due = []
    for m in idx.get("manuals", []):
        nd = m.get("next_review_due")
        if not nd:
            continue
        try:
            d = date.fromisoformat(nd)
        except ValueError:
            continue
        if d <= today:
            due.append({
                "topic": m["topic"],
                "title": m.get("title"),
                "version": m.get("version"),
                "owner": m.get("owner"),
                "next_review_due": nd,
                "overdue_days": (today - d).days,
                "sync_status": m.get("sync_status", {}),
            })

    result = {"due": due, "count": len(due), "checked_on": today.isoformat()}
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        print(out)

    if due:
        print(f"[提醒] {len(due)} 份手册已到回顾周期：", file=sys.stderr)
        for d in due:
            print(f"  - {d['title']} v{d['version']} 逾期 {d['overdue_days']} 天 (应 {d['next_review_due']})", file=sys.stderr)


if __name__ == "__main__":
    main()
