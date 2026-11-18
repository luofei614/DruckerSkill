#!/usr/bin/env python3
"""ddd-knowledge-manual · 新旧版本语义 diff。

按条目编号(kid, 形如 [K001] 或 K001) 匹配，分类 新增/删除/修改/未变。
无编号条目时降级为 difflib 行级对比。输出 HTML 或 markdown 报告。

用法:
  python scripts/diff_manual.py manuals/foo-v1.md manuals/foo-v2.md \
      --format html --out diff_report.html --title "XX知识手册"
"""
import argparse
import difflib
import json
import re
import sys
from datetime import date

# 条目编号约定为 K001（可带方括号）。排除纯数字小节标题（如 "## 1. 独特知识清单"）。
KID_RE = re.compile(r"^##\s*(?:\[(K\d+)\]|(K\d+))\s*(.*)$")


def parse_entries(text):
    entries, cur, buf = {}, None, []
    for line in text.splitlines():
        m = KID_RE.match(line)
        if m:
            if cur:
                entries[cur[0]] = "\n".join(buf).strip()
            kid = m.group(1) or m.group(2)
            cur = (kid, m.group(3).strip())
            buf = []
        elif cur:
            buf.append(line)
    if cur:
        entries[cur[0]] = "\n".join(buf).strip()
    return entries


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_html(args, added, deleted, modified, unchanged, e_old, e_new):
    def item(k, kind, old="", new=""):
        if kind == "mod":
            body = f'<div class="old">{escape(old)}</div><div class="new">{escape(new)}</div>'
        else:
            body = f'<div>{escape(new or old)}</div>'
        return f'<div class="item {kind}"><span class="kid">[{k}]</span>{body}</div>'

    added_s = "".join(item(k, "add", new=e_new[k]) for k in added) or "<p>无</p>"
    del_s = "".join(item(k, "del", old=e_old[k]) for k in deleted) or "<p>无</p>"
    mod_s = "".join(item(k, "mod", old=e_old[k], new=e_new[k]) for k in modified) or "<p>无</p>"
    unc_s = "".join(item(k, "same", new=e_new[k]) for k in unchanged) or "<p>无</p>"
    return f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<title>知识手册版本对比</title><style>
:root{{--add:#1b873f;--del:#c0392b;--mod:#b26a00;--same:#6b7785;}}
body{{font-family:-apple-system,"PingFang SC",sans-serif;color:#1f2933;margin:0;padding:28px;}}
.item{{border:1px solid #d9e2ec;border-radius:8px;padding:8px 12px;margin-bottom:8px;background:#f5f7fa;}}
.item.add{{border-left:5px solid var(--add);}} .item.del{{border-left:5px solid var(--del);}}
.item.mod{{border-left:5px solid var(--mod);}} .kid{{font-family:monospace;color:#6b7785;}}
.old{{color:var(--del);text-decoration:line-through;}} .new{{color:var(--add);}}
.pill{{padding:3px 10px;border-radius:16px;color:#fff;margin-right:8px;}}
.pill.add{{background:var(--add);}} .pill.del{{background:var(--del);}} .pill.mod{{background:var(--mod);}} .pill.same{{background:var(--same);}}
</style></head><body>
<h1>知识手册版本对比报告</h1><p>{escape(args.title)}</p>
<p><span class="pill add">新增 {len(added)}</span><span class="pill del">删除 {len(deleted)}</span>
<span class="pill mod">修改 {len(modified)}</span><span class="pill same">未变 {len(unchanged)}</span></p>
<h2>新增</h2>{added_s}<h2>删除</h2>{del_s}<h2>修改</h2>{mod_s}<h2>未变</h2>{unc_s}
</body></html>"""


def render_md(added, deleted, modified, unchanged, e_old, e_new):
    lines = ["# 知识手册版本对比", "",
             f"新增 {len(added)} / 删除 {len(deleted)} / 修改 {len(modified)} / 未变 {len(unchanged)}", ""]
    lines += ["## 新增"] + [f"- [{k}] {e_new[k]}" for k in added]
    lines += ["## 删除"] + [f"- [{k}] {e_old[k]}" for k in deleted]
    lines += ["## 修改"] + [f"- [{k}] 旧：{e_old[k]} → 新：{e_new[k]}" for k in modified]
    lines += ["## 未变"] + [f"- [{k}] {e_new[k]}" for k in unchanged]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("old")
    ap.add_argument("new")
    ap.add_argument("--format", default="html", choices=["html", "md"])
    ap.add_argument("--out", default="diff_report.html")
    ap.add_argument("--title", default="知识手册")
    args = ap.parse_args()

    with open(args.old, encoding="utf-8") as f:
        old = f.read()
    with open(args.new, encoding="utf-8") as f:
        new = f.read()

    e_old, e_new = parse_entries(old), parse_entries(new)

    if not e_old and not e_new:
        diff = list(difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm=""))
        print("未检测到编号条目，已降级为行级对比。", file=sys.stderr)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write("<html><body><h1>行级对比</h1><pre>" + escape("\n".join(diff)) + "</pre></body></html>")
        print(json.dumps({"counts": {"added": 0, "deleted": 0, "modified": 0, "unchanged": 0}}, ensure_ascii=False))
        return

    old_k, new_k = set(e_old), set(e_new)
    added = sorted(new_k - old_k)
    deleted = sorted(old_k - new_k)
    common = sorted(old_k & new_k)
    modified = [k for k in common if norm(e_old[k]) != norm(e_new[k])]
    unchanged = [k for k in common if norm(e_old[k]) == norm(e_new[k])]

    if args.format == "html":
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(render_html(args, added, deleted, modified, unchanged, e_old, e_new))
    else:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(render_md(added, deleted, modified, unchanged, e_old, e_new))

    print(json.dumps({
        "added": added, "deleted": deleted, "modified": modified, "unchanged": unchanged,
        "counts": {"added": len(added), "deleted": len(deleted), "modified": len(modified), "unchanged": len(unchanged)},
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
