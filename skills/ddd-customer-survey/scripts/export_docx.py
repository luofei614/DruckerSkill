#!/usr/bin/env python3
"""ddd-customer-survey · 问题清单整合表 → 双 Word(.docx) 导出。

把 `assets/question_inventory_template.md` 的整合表拆成两份真实 .docx：
- 纯净版（M1–M7，仅 模块/题号/题干/题型/是否必答/分支条件，零 KP/方法论，可直发顾客或导入平台）
- [内部]标注版（M0–M7，追加 对应KP/画布字段映射/设计意图·防引导备注，供内部自检与下游 C2–C6）

复用 knowledge-insight 的 md→docx 引擎（标题/表格/列表/加粗/`code`/引用）。
纯净版在转换前再做一次字符串扫描，剥离任何 `kp-` / 德鲁克 / 方法论 残留（双重净水）。

用法:
  python scripts/export_docx.py --file <整合表.md> \
      --out-pure <纯净版.docx> --out-internal <[内部]标注版.docx>
"""
import argparse
import json
import re
from docx import Document
from docx.shared import Pt

BODY_FONT = "宋体"
BODY_SIZE = 11

# 标记标题（块分隔），块内容 = 该标题之后、下一个 `## ` 之前
PURE_MARKER = "## 纯净版"
INTERNAL_MARKER = "## [内部]标注版"

# 纯净版防御性净水：剥离任何理论/方法论痕迹
_PURE_FORBIDDEN = [
    (re.compile(r"kp-[A-Za-z0-9\-]+"), ""),
    (re.compile(r"德鲁克"), ""),
    (re.compile(r"方法论"), ""),
    (re.compile(r"\[内部\]"), ""),
]


def parse_inline(p, text):
    parts = re.split(r"(\*\*.*?\*\*|`.*?`)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            r = p.add_run(part[2:-2])
            r.bold = True
        elif part.startswith("`") and part.endswith("`"):
            r = p.add_run(part[1:-1])
            r.font.name = "Consolas"
        else:
            p.add_run(part)


def extract_block(md_text, marker):
    """返回 marker 行之后、下一个 `## ` 标题之前的内容（含 marker 自身作为标题）。"""
    lines = md_text.split("\n")
    start = None
    for i, line in enumerate(lines):
        if line.strip() == marker or line.strip().startswith(marker):
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^##\s+", lines[j]):
            end = j
            break
    return "\n".join(lines[start:end])


def md_to_docx(md_text, doc):
    lines = md_text.split("\n")
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(cells)
                i += 1
            if rows:
                header = rows[0]
                table = doc.add_table(rows=1, cols=len(header))
                table.style = "Table Grid"
                hdr_cells = table.rows[0].cells
                for j, h in enumerate(header):
                    hdr_cells[j].text = ""
                    parse_inline(hdr_cells[j].paragraphs[0], h)
                    for rn in hdr_cells[j].paragraphs[0].runs:
                        rn.bold = True
                for r in rows[2:]:
                    cells = table.add_row().cells
                    for j, c in enumerate(r):
                        cells[j].text = ""
                        parse_inline(cells[j].paragraphs[0], c)
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            h = doc.add_heading(level=level)
            parse_inline(h, m.group(2))
            i += 1
            continue
        if line.startswith(">"):
            quote = line.lstrip("> ").strip()
            while i + 1 < n and lines[i + 1].startswith(">"):
                i += 1
                quote += "\n" + lines[i].lstrip("> ").strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Pt(18)
            r = p.add_run(quote)
            r.italic = True
            i += 1
            continue
        m = re.match(r"^[\s]*[-*]\s+(.*)$", line)
        if m:
            p = doc.add_paragraph(style="List Bullet")
            parse_inline(p, m.group(1))
            i += 1
            continue
        m = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if m:
            p = doc.add_paragraph(style="List Number")
            parse_inline(p, m.group(1))
            i += 1
            continue
        if not stripped:
            i += 1
            continue
        p = doc.add_paragraph()
        parse_inline(p, line)
        i += 1


def purify(text):
    for pat, repl in _PURE_FORBIDDEN:
        text = pat.sub(repl, text)
    return text


def export_block(block_md, out_path, do_purify=False):
    if do_purify:
        block_md = purify(block_md)
    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(BODY_SIZE)
    md_to_docx(block_md, doc)
    doc.save(out_path)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="问题清单整合表 markdown 路径")
    ap.add_argument("--out-pure", default="问题清单整合表_纯净版.docx", help="纯净版 .docx 输出")
    ap.add_argument("--out-internal", default="问题清单整合表_内部标注版.docx", help="[内部]标注版 .docx 输出")
    args = ap.parse_args()

    with open(args.file, encoding="utf-8") as f:
        text = f.read()

    pure_block = extract_block(text, PURE_MARKER)
    internal_block = extract_block(text, INTERNAL_MARKER)
    if pure_block is None or internal_block is None:
        raise SystemExit(f"[export_docx] 未找到标记：纯净版={pure_block is not None} 标注版={internal_block is not None}")

    export_block(pure_block, args.out_pure, do_purify=True)
    export_block(internal_block, args.out_internal, do_purify=False)
    print(json.dumps({
        "out_pure": args.out_pure,
        "out_internal": args.out_internal,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
