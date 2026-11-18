#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DruckerWiki 检索脚本（ddd-knowledge-qa 配套）
=============================================
从 ~/DruckerWiki 知识库召回与用户问题最相关的德鲁克知识点（KP）与跨书概念页。

检索策略（多路召回 + 加权排序）：
  1. 概念精确召回（Layer A）：从知识库真实概念词表做正向最大匹配，
     命中 title/aliases/tags 给高权重；标题子串命中给强信号。
  2. 语义模糊召回（Layer B）：对多字段做 2-gram 重叠打分（中文相邻二字）。
  3. 书名/章号定向：识别《管理的实践》第6章 这类限定，收窄候选集。
  4. 同义词扩展：客户→顾客、成效→成果 等，提升中文召回。

仅依赖 Python 标准库，兼容 3.9+。

用法：
  python3 retrieve.py "顾客是谁" [--top 6] [--json]
  python3 retrieve.py "解释《管理的实践》第6章" --top 8
  python3 retrieve.py "知识是易腐商品" --json
"""
import os
import re
import sys
import json
import argparse

WIKI_ROOT = os.path.expanduser("~/DruckerWiki")

BOOK_KP = {
    "为成果而管理": "为成果而管理/kp",
    "管理的实践": "管理的实践/kp",
    "卓有成效的管理者": "卓有成效的管理者/kp",
    "创新与企业家精神": "创新与企业家精神/kp",
}
CONCEPTS_DIR = "concepts"

# 确定性同义词（双向入词表 + 查询替换）
SYNONYMS = {
    "客户": "顾客", "顾客": "客户",
    "成效": "成果", "效果": "成果",
    "知识员工": "知识工作者", "知识型员工": "知识工作者",
    "MBO": "目标管理", "目标管理": "MBO",
    "创新源": "创新机会", "创新来源": "创新机会",
    "事业理论": "事业是什么", "我们的事业": "事业是什么",
    "外面": "外部",
}

# 中文停用单字（用于过滤噪声 2-gram）
STOP = set("的是在与对和为被把从及或且该等其也都很更最一这个那个如何怎样什么怎么为什么德鲁克解释讲分析看关于用基于以于把当把把把将应可要能没".replace("把", ""))

CJK = r"[\u4e00-\u9fff]"


# --------------------------------------------------------------------------
# frontmatter 解析（兼容 inline list 与 block list，不依赖第三方 yaml）
# --------------------------------------------------------------------------
def parse_frontmatter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}, text
    fm_text = m.group(1)
    body = text[m.end():]
    data = {}
    lines = fm_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        mm = re.match(r"^([A-Za-z_]+):\s*(.*)$", line)
        if not mm:
            i += 1
            continue
        key = mm.group(1)
        val = mm.group(2).strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            if inner == "":
                data[key] = []
            else:
                items = [x.strip().strip('"').strip("'") for x in inner.split(",")]
                data[key] = [x for x in items if x]
            i += 1
        elif val == "":
            items = []
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if re.match(r"^\s*-\s+", nxt):
                    item = re.sub(r"^\s*-\s+", "", nxt).strip().strip('"').strip("'")
                    if item:
                        items.append(item)
                    j += 1
                elif nxt.strip() == "":
                    j += 1
                else:
                    break
            data[key] = items if items else ""
            i = j
        else:
            data[key] = val.strip().strip('"').strip("'")
            i += 1
    return data, body


def extract_section(body, header):
    pattern = re.compile(r"^##\s+" + re.escape(header) + r"\s*$", re.MULTILINE)
    m = pattern.search(body)
    if not m:
        return ""
    start = m.end()
    nm = re.search(r"^##\s+", body[start:])
    end = start + nm.start() if nm else len(body)
    return body[start:end].strip()


# --------------------------------------------------------------------------
# 文档构建
# --------------------------------------------------------------------------
def build_kp_doc(path, book):
    text = open(path, encoding="utf-8").read()
    fm, body = parse_frontmatter(text)
    title = fm.get("title", "") or os.path.splitext(os.path.basename(path))[0]
    aliases = fm.get("aliases", []) or []
    tags = fm.get("tags", []) or []
    chapter = fm.get("chapter", "") or ""
    summary = fm.get("summary", "") or ""
    symptoms = fm.get("symptoms", []) or []
    scenarios = fm.get("scenarios", []) or []
    frameworks = fm.get("frameworks", []) or []
    coverage = fm.get("coverage", "") or ""
    source_book = fm.get("source_book", book) or book
    high = "\n".join(
        extract_section(body, h)
        for h in ["检索导言", "核心定义", "关键论点", "原话观点", "检索骨架"]
    )
    return {
        "path": os.path.relpath(path, WIKI_ROOT),
        "type": "kp", "id": fm.get("id", ""), "title": title,
        "aliases": aliases, "tags": tags, "chapter": chapter,
        "summary": summary, "symptoms": symptoms, "scenarios": scenarios,
        "frameworks": frameworks, "coverage": coverage,
        "source_book": source_book, "book": book,
        "body": body, "high": high,
    }


def build_concept_doc(path):
    text = open(path, encoding="utf-8").read()
    fm, body = parse_frontmatter(text)
    m = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    raw_title = m.group(1) if m else os.path.splitext(os.path.basename(path))[0]
    title = fm.get("title", "") or re.split(r"[\(（]", raw_title)[0].strip()
    summary = extract_section(body, "摘要")
    high = summary + "\n" + extract_section(body, "跨书全景") + "\n" + extract_section(body, "整合对比")
    return {
        "path": os.path.relpath(path, WIKI_ROOT),
        "type": "concept", "id": "", "title": title,
        "aliases": [], "tags": [], "chapter": "",
        "summary": summary, "symptoms": [], "scenarios": [],
        "frameworks": [], "coverage": "🟢",
        "source_book": "跨书概念", "book": "",
        "body": body, "high": high,
    }


def build_docs():
    docs = []
    for book, rel in BOOK_KP.items():
        d = os.path.join(WIKI_ROOT, rel)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md"):
                continue
            docs.append(build_kp_doc(os.path.join(d, fn), book))
    cd = os.path.join(WIKI_ROOT, CONCEPTS_DIR)
    if os.path.isdir(cd):
        for fn in sorted(os.listdir(cd)):
            if not fn.endswith(".md"):
                continue
            docs.append(build_concept_doc(os.path.join(cd, fn)))
    return docs


def build_vocab(docs):
    vocab = set()
    for d in docs:
        vocab.add(d["title"])
        vocab.update(d["aliases"])
        vocab.update(d["tags"])
    for k, v in SYNONYMS.items():
        vocab.add(k)
        vocab.add(v)
    return vocab


# --------------------------------------------------------------------------
# 分词 / 匹配
# --------------------------------------------------------------------------
def bigrams(s):
    res = set()
    for w in re.findall(r"[A-Za-z0-9]+", s):
        res.add(w.lower())
    cjk = "".join(re.findall(CJK, s))
    if len(cjk) == 1:
        if cjk not in STOP:
            res.add(cjk)
    for i in range(len(cjk) - 1):
        bg = cjk[i:i + 2]
        if any(ch in STOP for ch in bg):
            continue
        res.add(bg)
    return res


def max_match(query, vocab):
    terms = []
    i = 0
    n = len(query)
    while i < n:
        matched = None
        for L in range(min(8, n - i), 0, -1):
            cand = query[i:i + L]
            if cand in vocab:
                matched = cand
                break
        if matched:
            terms.append(matched)
            i += len(matched)
        else:
            i += 1
    return terms


def detect_scope(query):
    scope_book = None
    scope_chap = None
    for name in BOOK_KP:
        if name in query or ("《" + name + "》") in query:
            scope_book = name
            break
    if not scope_book:
        for short, full in [("为成果", "为成果而管理"),
                            ("卓有成效", "卓有成效的管理者"),
                            ("创新", "创新与企业家精神")]:
            if short in query:
                scope_book = full
                break
    m = re.search(r"第?\s*([0-9]+)\s*章", query)
    if m:
        scope_chap = int(m.group(1))
    return scope_book, scope_chap


# --------------------------------------------------------------------------
# 打分
# --------------------------------------------------------------------------
def score_doc(doc, query, terms, qgrams):
    score = 0
    matched = []
    doc_terms = set(doc["aliases"]) | set(doc["tags"]) | {doc["title"]}
    for t in terms:
        if t in doc_terms:
            score += 6
            matched.append("概念:" + t)
        elif t and (t in doc["summary"] or t in doc["chapter"]):
            score += 1
            matched.append("摘要/章:" + t)
    if len(doc["title"]) >= 4 and doc["title"] in query:
        score += 20
        matched.append("标题命中")
    fields = {
        "title": (doc["title"], 6),
        "aliases": (" ".join(doc["aliases"]), 5),
        "tags": (" ".join(doc["tags"]), 4),
        "frameworks": (" ".join(doc["frameworks"]), 4),
        "symptoms": (" ".join(doc["symptoms"]), 3),
        "chapter": (doc["chapter"], 3),
        "summary": (doc["summary"], 2),
        "high": (doc["high"][:300], 1),
    }
    for _fname, (ftext, w) in fields.items():
        fg = bigrams(ftext)
        ov = len(qgrams & fg)
        if ov:
            score += ov * w
    return score, matched


def kp_key(path):
    """从路径提取 KP 章-序，用于定向章时按书序排序。"""
    m = re.search(r"kp-[gei]?(\d+)-(\d+)", path)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return (999, 999)


def main():
    ap = argparse.ArgumentParser(description="DruckerWiki 检索")
    ap.add_argument("query", help="用户自然语言问题")
    ap.add_argument("--top", type=int, default=6, help="返回条数")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    args = ap.parse_args()

    if not os.path.isdir(WIKI_ROOT):
        sys.stderr.write("ERROR: DruckerWiki 未找到: %s\n" % WIKI_ROOT)
        sys.exit(2)

    docs = build_docs()
    vocab = build_vocab(docs)
    scope_book, scope_chap = detect_scope(args.query)

    # 同义词扩展（保留原词 + 追加同义词，避免替换导致原词 2-gram 丢失）
    q = args.query
    extra = []
    for k, v in SYNONYMS.items():
        if k in q and v not in q:
            extra.append(v)
        if v in q and k not in q:
            extra.append(k)
    if extra:
        q = q + " " + " ".join(extra)

    terms = max_match(q, vocab)
    qgrams = bigrams(q)

    results = []
    for d in docs:
        if scope_book and d["source_book"] != scope_book:
            continue
        if scope_chap is not None and d["type"] == "kp":
            m = re.search(r"第(\d+)章", d["chapter"])
            if not m or int(m.group(1)) != scope_chap:
                continue
        sc, mt = score_doc(d, q, terms, qgrams)
        if sc > 0:
            results.append((sc, d, mt))

    if scope_chap is not None:
        # 定向某章：按书序（章-序）呈现，score 仅作过滤
        results.sort(key=lambda x: (kp_key(x[1]["path"]), -x[0]))
    else:
        results.sort(key=lambda x: -x[0])
    results = results[: args.top]

    if args.json:
        out = []
        for sc, d, mt in results:
            out.append({
                "path": d["path"],
                "title": d["title"],
                "source_book": d["source_book"],
                "chapter": d["chapter"],
                "coverage": d["coverage"],
                "summary": d["summary"][:200],
                "matched": mt,
                "score": sc,
                "snippet": re.sub(r"\s+", " ", d["high"])[:160],
            })
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        if not results:
            print("（未检索到相关知识点，建议换用德鲁克原书术语，或检查 ~/DruckerWiki 路径）")
            return
        for sc, d, mt in results:
            print("📄 %s  [%s·%s]  coverage=%s" % (d["title"], d["source_book"], d["chapter"], d["coverage"]))
            print("   路径: %s" % d["path"])
            print("   摘要: %s" % d["summary"][:80])
            print("   命中: %s" % ", ".join(mt))
            print("   评分: %s" % sc)
            print("   片段: %s" % re.sub(r"\s+", " ", d["high"])[:120])
            print()


if __name__ == "__main__":
    main()
