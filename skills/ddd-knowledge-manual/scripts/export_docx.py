#!/usr/bin/env python3
"""ddd-knowledge-manual · 手册 markdown → Word(.docx) 导出。

把知识手册 markdown（本地唯一可信源）真实转换为 .docx 交付物：
- 标题层级 (#~######) → Word 标题样式
- 引用块 (>)、表格 (|..|)、无序/有序列表、加粗 **x** / 行内 `code`
- 默认剥离 YAML frontmatter（机器用）；并把正文「见文件头 frontmatter」占位替换为真实时间戳
- 支持 ## [K001] 带 kid 的条目标题

用法:
  python scripts/export_docx.py --file manuals/foo-v1.md --out manuals/foo-v1.docx
"""
import argparse
import json
import re
from docx import Document
from docx.shared import Pt, RGBColor

BODY_FONT = "宋体"
BODY_SIZE = 11


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def strip_frontmatter(text):
    if text.startswith("---"):
        m = re.match(r"^---\s*\n.*?\n---\s*\n", text, re.DOTALL)
        if m:
            return text[m.end():]
    return text


def build_view(text):
    """去掉 frontmatter，并把正文里指向 frontmatter 的占位替换为真实值。"""
    fm = parse_frontmatter(text)
    body = strip_frontmatter(text)
    if "见文件头 frontmatter" in body:
        ver = fm.get("version", "")
        created = fm.get("created_at", "")
        due = fm.get("next_review_due", "")
        repl = f"v{ver} · 创建/更新 {created} · 下次回顾到期 {due}"
        body = body.replace("- 版本 / 时间戳：见文件头 frontmatter",
                             f"- 版本 / 时间戳：{repl}")
    return body


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


def md_to_docx(md_text, doc):
    lines = md_text.split("\n")
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        # 表格：当前行以 | 开头，且下一行是 |---| 分隔
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
        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            h = doc.add_heading(level=level)
            parse_inline(h, m.group(2))
            i += 1
            continue
        # 引用块
        if line.startswith(">"):
            quote = line.lstrip("> ").strip()
            while i + 1 < n and lines[i + 1].startswith(">"):
                i += 1
                quote += "\n" + lines[i].lstrip("> ").strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Pt(18)
            r = p.add_run(quote)
            r.italic = True
            r.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
            i += 1
            continue
        # 无序列表
        m = re.match(r"^[\s]*[-*]\s+(.*)$", line)
        if m:
            p = doc.add_paragraph(style="List Bullet")
            parse_inline(p, m.group(1))
            i += 1
            continue
        # 有序列表
        m = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if m:
            p = doc.add_paragraph(style="List Number")
            parse_inline(p, m.group(1))
            i += 1
            continue
        # 空行
        if not stripped:
            i += 1
            continue
        # 普通段落
        p = doc.add_paragraph()
        parse_inline(p, line)
        i += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="源手册 markdown 路径")
    ap.add_argument("--out", default=None, help="输出 .docx 路径（默认与 md 同名同目录，后缀 .docx）")
    args = ap.parse_args()
    out = args.out or re.sub(r"\.md$", ".docx", args.file)
    with open(args.file, encoding="utf-8") as f:
        text = f.read()
    body = build_view(text)
    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(BODY_SIZE)
    md_to_docx(body, doc)
    doc.save(out)
    print(json.dumps({"out": out}, ensure_ascii=False))


if __name__ == "__main__":
    main()
