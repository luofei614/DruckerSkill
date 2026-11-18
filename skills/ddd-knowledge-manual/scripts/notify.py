#!/usr/bin/env python3
"""ddd-knowledge-manual · 多平台提醒渲染。

读取 check_due.py 输出的到期列表，渲染指定平台的提醒卡片/消息。
实际发送由运行时连接器（飞书/钉钉/企微）完成；本脚本只生成 payload。

用法:
  python scripts/notify.py --due-file due.json --platform feishu [--assets ../assets] [--review-url https://...]
"""
import argparse
import json
import os
import sys

TEMPLATES = {
    "feishu": "reminder_card_feishu.json",
    "dingtalk": "reminder_card_dingtalk.md",
    "wecom": "reminder_card_wecom.md",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--due-file", required=True)
    ap.add_argument("--platform", required=True, choices=list(TEMPLATES))
    ap.add_argument("--assets", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets"))
    ap.add_argument("--review-url", default="")
    args = ap.parse_args()

    with open(args.due_file, encoding="utf-8") as f:
        due = json.load(f).get("due", [])

    tpl_path = os.path.join(args.assets, TEMPLATES[args.platform])
    if not os.path.exists(tpl_path):
        print(f"ERROR: 模板不存在 {tpl_path}", file=sys.stderr)
        sys.exit(1)
    with open(tpl_path, encoding="utf-8") as f:
        tpl = f.read()

    for d in due:
        sub = {
            "{{title}}": d.get("title", ""),
            "{{owner}}": d.get("owner", ""),
            "{{due_date}}": d.get("next_review_due", ""),
            "{{overdue_days}}": str(d.get("overdue_days", 0)),
            "{{version}}": str(d.get("version", "")),
            "{{repo}}": "",
            "{{review_url}}": args.review_url,
        }
        rendered = tpl
        for k, v in sub.items():
            rendered = rendered.replace(k, v)

        if args.platform == "feishu":
            try:
                payload = json.loads(rendered)
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            except json.JSONDecodeError as e:
                print("ERROR: 飞书卡片 JSON 渲染失败：", e, file=sys.stderr)
                print(rendered)
        else:
            print(rendered)


if __name__ == "__main__":
    main()
