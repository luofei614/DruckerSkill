#!/usr/bin/env python3
"""build_bundle.py — 顾客洞察交付物 标准中间表示（delivery bundle）。

本模块是「协作分发层」的数据源：洞察分析在生成 HTML 的同一刻，
调用本模块把 画布(11格) + 报告(叙事) 结构化为 delivery_bundle.json，
再由 assets/adapters/<平台>.py 翻译成各协作工具的「在线可协作」产物
（多维表格 / 在线协作文档），绝不回扫 HTML。

仅用标准库，跨 runtime 可用。
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Any, List, Optional


# ---- 与 references/canvas_schema.md 对齐的常量 ----
CANVAS_COLUMNS = ["顾客是谁", "买的是什么", "认为的价值"]
CONFIDENCE_LEVELS = ["高", "中", "低"]
STATUS_LEVELS = ["已验证", "假设·待验证", "证据不足·建议补访"]


@dataclass
class Quote:
    text: str
    src: str  # 出处，如 "行N·列X" 或 "S3·M5-12·00:42"

    @classmethod
    def make(cls, text: str, src: str) -> "Quote":
        return cls(text=text, src=src)


@dataclass
class Cell:
    cell_id: str            # "1.1"
    col: str                # "顾客是谁"
    title: str              # "现实顾客画像"
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
    """示例 bundle（仅用于联调/演示，非真实调研数据，避免伪造顾客原话）。"""
    cells = [
        Cell("1.1", "顾客是谁", "现实顾客画像",
              "（示例）都市白领，经 B站/视频号长期关注后转化。",
              [Quote.make("（示例原话，非真实数据）", "示例·行12·列I")], "中", "假设·待验证"),
        Cell("2.3", "买的是什么", "深层情感+最终用途",
              "（示例）买的不是知识量，是精神安顿与焦虑缓解。",
              [Quote.make("（示例原话，非真实数据）", "示例·行45·列M")], "中", "假设·待验证"),
        Cell("3.1", "认为的价值", "购前价值锚点",
              "（示例）购前最看重信任与价格。", [], "低", "证据不足·建议补访"),
    ]
    return DeliveryBundle(
        meta={"title": "示例·顾客洞察交付包", "business": "示例事业", "generated_at": "DEMO"},
        canvas=cells,
        report=[Section("示例报告章节", [Block.p("（示例）这是一支叙事段落。")])],
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description="build delivery bundle (洞察交付中间表示)")
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
