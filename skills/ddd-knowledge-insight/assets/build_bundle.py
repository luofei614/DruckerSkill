#!/usr/bin/env python3
"""build_bundle.py — 知识洞察交付物 标准中间表示（delivery bundle）。

本模块是「协作分发层」的数据源：知识洞察分析在生成 HTML 的同一刻，
调用本模块把 知识画布(三源列×结论) + 报告(A/B/C 三节) 结构化为 delivery_bundle.json，
供 ddd-opportunity-synthesis 做「知识与市场双向反馈」消费，绝不回扫 HTML。

与 ddd-customer-insight 的 build_bundle.py 同构（CLI: demo / validate），便于 synthesis 统一调用。
仅用标准库，跨 runtime 可用。
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Any, List


# ---- 与 references/canvas_schema.md 对齐的常量（知识画布 = 三源列）----
CANVAS_COLUMNS = ["跟别人比", "跟自己比", "问优秀顾客"]
CONFIDENCE_LEVELS = ["高", "中", "低"]
STATUS_LEVELS = ["已验证", "假设·待验证", "证据不足·建议补访"]


@dataclass
class Quote:
    text: str
    src: str  # 出处，如 "行N·列X" 或 "S3·A-2·00:42"

    @classmethod
    def make(cls, text: str, src: str) -> "Quote":
        return cls(text=text, src=src)


@dataclass
class Cell:
    cell_id: str            # "1.1"
    col: str                # "跟别人比"
    title: str              # "干得好别人干不了（独特知识候选）"
    conclusion: str
    quotes: List[Quote] = field(default_factory=list)
    confidence: str = "中"
    status: str = "假设·待验证"

    def to_row(self) -> Dict[str, Any]:
        return {
            "格号": self.cell_id,
            "列": self.col,
            "标题": self.title,
            "结论": self.conclusion,
            "原话溯源": " | ".join(f"「{q.text}」({q.src})" for q in self.quotes) or "（无原话）",
            "置信度": self.confidence,
            "状态": self.status,
        }


@dataclass
class Block:
    type: str   # h2 | h3 | p | quote | list
    text: str

    @classmethod
    def h2(cls, t: str) -> "Block":
        return cls("h2", t)

    @classmethod
    def h3(cls, t: str) -> "Block":
        return cls("h3", t)

    @classmethod
    def p(cls, t: str) -> "Block":
        return cls("p", t)

    @classmethod
    def quote(cls, t: str) -> "Block":
        return cls("quote", t)

    @classmethod
    def item(cls, t: str) -> "Block":
        return cls("list", t)


@dataclass
class Section:
    title: str
    blocks: List[Block] = field(default_factory=list)


@dataclass
class DeliveryBundle:
    meta: Dict[str, Any] = field(default_factory=dict)
    canvas: List[Cell] = field(default_factory=list)
    report: List[Section] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "meta": self.meta,
            "canvas": [asdict(c) for c in self.canvas],
            "report": [
                {"title": s.title, "blocks": [asdict(b) for b in s.blocks]}
                for s in self.report
            ],
        }

    def to_json(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "DeliveryBundle":
        return cls(
            meta=d.get("meta", {}),
            canvas=[Cell(**_clean_cell(c)) for c in d.get("canvas", [])],
            report=[
                Section(
                    title=s.get("title", ""),
                    blocks=[Block(**b) for b in s.get("blocks", [])],
                )
                for s in d.get("report", [])
            ],
        )

    @classmethod
    def from_json(cls, path: str | Path) -> "DeliveryBundle":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def _clean_cell(c: Dict[str, Any]) -> Dict[str, Any]:
    quotes: List[Quote] = []
    for q in c.get("quotes", []):
        if isinstance(q, dict):
            quotes.append(Quote(text=q.get("text", ""), src=q.get("src", "")))
        else:
            quotes.append(Quote(text=str(q), src=""))
    return {
        "cell_id": c.get("cell_id", ""),
        "col": c.get("col", ""),
        "title": c.get("title", ""),
        "conclusion": c.get("conclusion", ""),
        "quotes": quotes,
        "confidence": c.get("confidence", "中"),
        "status": c.get("status", "假设·待验证"),
    }


# ---------- CLI ----------
def _demo_bundle() -> DeliveryBundle:
    """示例 bundle（仅用于联调/演示，非真实调研数据，避免伪造原话）。"""
    cells = [
        Cell("1.1", "跟别人比", "干得好别人干不了（独特知识候选）",
              "（示例）在「用大白话讲清玄学概念」领域，能做好「让零基础学员一次听懂」的事。",
              [Quote.make("（示例原话，非真实数据）", "示例·A-1")], "中", "假设·待验证"),
        Cell("1.2", "跟别人比", "干不好别人能干成（知识短板）",
              "（示例）在「学员社群持续活跃运营」上弱于头部同行。",
              [Quote.make("（示例原话，非真实数据）", "示例·A-2")], "中", "假设·待验证"),
        Cell("3.1", "问优秀顾客", "别人做不到的事（顾客视角独特价值）",
              "（示例）学员说「只有你们把道家智慧和现代压力管理连起来了」。",
              [Quote.make("（示例原话，非真实数据）", "示例·C-1")], "中", "假设·待验证"),
    ]
    report = [
        Section("A. 动词+名词独特知识清单", [
            Block.p("（示例）K001 在「玄学概念大白话化」领域，能做好「零基础一次听懂」的事。"),
        ]),
        Section("B. 四维度诊断", [
            Block.p("（示例）对：指向领先，有学员证据；值：收入部分来自此差异化；深：主要在创始人个人；新：有过时风险，需系统化。"),
        ]),
        Section("C. 五维交汇·事业新机会假设卡", [
            Block.p("（示例）卡1 | 顾客三问：都市白领想缓解焦虑 | 独特知识：大白话讲玄学 | 企业渴望：规模化 | 外界变化：国潮养生兴起 | 未满足需求：可信不玄乎的内容 | 机会假设：推出「不玄乎的东方身心课」 | 状态：草稿·假设·待验证"),
        ]),
    ]
    return DeliveryBundle(
        meta={
            "title": "示例·知识洞察交付包",
            "business": "示例事业",
            "generated_at": "DEMO",
            "consumer_hint": "画布 col 为三源列；报告 C 节『顾客三问』列消费自 ddd-customer-insight delivery_bundle.json",
        },
        canvas=cells,
        report=report,
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description="build delivery bundle (知识洞察交付中间表示)")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("demo").add_argument("--out", default="delivery_bundle.json")
    v = sub.add_parser("validate")
    v.add_argument("file")
    args = ap.parse_args(argv)

    if args.cmd == "demo":
        _demo_bundle().to_json(args.out)
        print(f"[build_bundle] demo bundle -> {args.out}")
    elif args.cmd == "validate":
        b = DeliveryBundle.from_json(args.file)
        print(f"[build_bundle] OK: canvas={len(b.canvas)} cells, "
              f"report={len(b.report)} sections")
    else:
        ap.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
