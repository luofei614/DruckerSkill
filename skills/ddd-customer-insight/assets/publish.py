#!/usr/bin/env python3
"""publish.py — 协作分发编排（被 SKILL.md ⑧ 调用）。

读取 delivery_bundle.json，探测已连接协作工具，路由并推送：
  画布(11格) -> 该平台 Base 类（多维表格/多维表/在线表格）
  报告(叙事) -> 该平台在线协作文档（飞书文档/钉钉文档/企微文档）

多工具时由上层用 AskUserQuestion 选定后传 --platform；本脚本只负责执行。
默认推个人空间；团队空间需上层确认后另传参数。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 把 assets 目录与 adapters 目录加入 import 路径
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE / "adapters"))

from _common import PLATFORMS, detect_status_map, load_adapter  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="协作分发编排")
    ap.add_argument("--bundle", required=True, help="delivery_bundle.json 路径")
    ap.add_argument("--platform", choices=PLATFORMS + ["all"], default="all")
    ap.add_argument("--adapters-dir", default=str(_HERE / "adapters"))
    args = ap.parse_args()

    from build_bundle import DeliveryBundle  # noqa: E402

    bundle = DeliveryBundle.from_json(args.bundle)
    status_map = detect_status_map()
    adapters_dir = Path(args.adapters_dir)

    # 1) 探测候选
    candidates = []
    for p in PLATFORMS:
        mod = load_adapter(p, adapters_dir)
        if not mod:
            print(f"[publish] {p}: 无适配器文件，跳过")
            continue
        state = mod.detect(status_map)
        print(f"[publish] {mod.DISPLAY}({p}): {state}")
        if state == "available":
            candidates.append(p)

    if not candidates:
        print("[publish] 未检测到已连接且可推送的协作工具；保留本地 HTML/PDF。")
        print("[publish] 提示：连接飞书/钉钉/企微后重跑，或用 /publish 补推。")
        return

    # 2) 路由
    if args.platform == "all":
        targets = candidates
    else:
        if args.platform not in candidates:
            print(f"[publish] 指定平台 {args.platform} 不在可用候选 {candidates} 中，跳过。")
            return
        targets = [args.platform]

    # 3) 推送
    results = []
    for p in targets:
        mod = load_adapter(p, adapters_dir)
        rb = mod.push_base(bundle)
        rd = mod.push_doc(bundle)
        results.append(rb.to_dict())
        results.append(rd.to_dict())
        print(f"[publish] {mod.DISPLAY}: base.ok={rb.ok} doc.ok={rd.ok}")

    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
