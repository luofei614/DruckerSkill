#!/usr/bin/env python3
"""ddd-knowledge-manual · 打时间戳 + 版本登记。

把手册 markdown 写入/更新 frontmatter（created_at/updated_at/next_review_due/version/owner/
sync_status），并追加到 VERSION_INDEX.json + CHANGELOG.md。本地 markdown 为唯一可信源。

用法:
  python scripts/stamp_version.py --file knowledge-manual/manuals/王德峰视频课业务知识手册_v1.md --repo knowledge-manual \
      --owner "团队" --title "XX知识手册" --topic "XX业务" --perishability high
# 文件名用中文业务名+_v{n}；topic 为内部稳定 id（建议中文）。脚本记录 manuals/<basename> 真实路径。
"""
import argparse
import json
import os
import re
import sys
from datetime import date, timedelta

INDEX_NAME = "VERSION_INDEX.json"
CHANGELOG = "CHANGELOG.md"


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, 0
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}, 0
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, m.end()


def update_frontmatter(text, updates):
    fm, end = parse_frontmatter(text)
    fm.update(updates)
    lines = [f"{k}: {v}" for k, v in fm.items()]
    new_fm = "---\n" + "\n".join(lines) + "\n---\n"
    body = text[end:] if end else text
    return new_fm + body


def load_index(repo):
    path = os.path.join(repo, INDEX_NAME)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"manuals": []}


def save_index(repo, idx):
    with open(os.path.join(repo, INDEX_NAME), "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--repo", default="./knowledge-manual")
    ap.add_argument("--owner", default="")
    ap.add_argument("--title", default="")
    ap.add_argument("--topic", default="")
    ap.add_argument("--source-run", default="")
    ap.add_argument("--outcome-anchor", default="")
    ap.add_argument("--perishability", default="med", choices=["high", "med", "low"])
    ap.add_argument("--threshold", type=int, default=182)
    ap.add_argument("--high-threshold", type=int, default=90)
    ap.add_argument("--today", default=None)
    args = ap.parse_args()

    today = date.fromisoformat(args.today) if args.today else date.today()
    threshold = args.high_threshold if args.perishability == "high" else args.threshold
    due = today + timedelta(days=threshold)

    with open(args.file, encoding="utf-8") as f:
        text = f.read()
    fm, _ = parse_frontmatter(text)

    title = args.title or fm.get("title") or ""
    if not title:
        print("ERROR: 无法确定标题，请用 --title 或 frontmatter 的 title。", file=sys.stderr)
        sys.exit(1)
    topic = args.topic or fm.get("topic") or re.sub(
        r"[^a-z0-9\u4e00-\u9fff]+", "-", title.lower()
    ).strip("-")
    owner = args.owner or fm.get("owner") or ""

    idx = load_index(args.repo)
    existing = next((m for m in idx["manuals"] if m["topic"] == topic), None)
    if existing:
        version = existing["version"] + 1
        created_at = existing["created_at"]
    else:
        version = 1
        created_at = today.isoformat()

    updated_at = today.isoformat()
    next_due = due.isoformat()

    updates = {
        "title": title,
        "topic": topic,
        "version": version,
        "created_at": created_at,
        "updated_at": updated_at,
        "next_review_due": next_due,
        "owner": owner,
        "perishability": args.perishability,
    }
    if args.source_run:
        updates["source_run"] = args.source_run
    if args.outcome_anchor:
        updates["outcome_anchor"] = args.outcome_anchor

    with open(args.file, "w", encoding="utf-8") as f:
        f.write(update_frontmatter(text, updates))

    entry = {
        "topic": topic,
        "title": title,
        "version": version,
        "created_at": created_at,
        "updated_at": updated_at,
        "next_review_due": next_due,
        "owner": owner,
        "perishability": args.perishability,
        "file": f"manuals/{os.path.basename(args.file)}",
        "sync_status": {"feishu": "pending", "dingtalk": "pending", "wecom": "pending"},
    }
    if args.source_run:
        entry["source_run"] = args.source_run
    if args.outcome_anchor:
        entry["outcome_anchor"] = args.outcome_anchor

    if existing:
        idx["manuals"][idx["manuals"].index(existing)] = entry
    else:
        idx["manuals"].append(entry)
    save_index(args.repo, idx)

    clog = os.path.join(args.repo, CHANGELOG)
    line = f"- v{version} ({updated_at}): {'初始化手册' if version == 1 else '更新手册'}，next_review_due={next_due}。\n"
    if not os.path.exists(clog):
        with open(clog, "w", encoding="utf-8") as f:
            f.write("# 知识手册更新日志\n\n" + line)
    else:
        with open(clog, "a", encoding="utf-8") as f:
            f.write(line)

    print(json.dumps(
        {"topic": topic, "version": version, "next_review_due": next_due, "file": entry["file"]},
        ensure_ascii=False,
    ))


if __name__ == "__main__":
    main()
