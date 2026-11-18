# 检索算法说明（ddd-knowledge-qa）

> 配套 `scripts/retrieve.py`（仅用 Python 标准库，兼容 3.9+）。本文档说明多路召回策略、打分权重、同义词、定向逻辑与输出格式，便于维护与调参。

## 1. 扫描范围
- 四书 `kp/` 目录：`为成果而管理/kp`、`管理的实践/kp`、`卓有成效的管理者/kp`、`创新与企业家精神/kp`（共 339 个 KP）。
- `concepts/` 跨书概念合订页（14 个，无 YAML frontmatter，首行 `# 标题`）。

## 2. 文档字段提取
每个 KP 解析 YAML frontmatter（兼容 inline list 与 block list），取可检索字段：
`title / aliases / tags / chapter / summary / symptoms / scenarios / frameworks / source_book / coverage`。
正文取高信息密度段作 `high` 文本（检索导言 + 核心定义 + 关键论点 + 原话观点 + 检索骨架，截断前 300 字）。

概念页：`title` 取自首行 `#`；`high` = 摘要 + 跨书全景 + 整合对比。

## 3. 多路召回与打分（两层次）
### Layer A — 概念精确召回（高权重）
- **词表（vocabulary）**：所有 KP 的 title / aliases / tags + 概念页标题 + 同义词双向，构建真实概念词表。
- **正向最大匹配**：对查询做 1–8 字正向最大匹配，提取词表中的概念词 `terms`。
- 对每个文档：
  - `term ∈ {aliases ∪ tags ∪ title}` → **+6**
  - `term ∈ summary 或 chapter` → **+1**
  - `title（≥4字）完整出现在查询中` → **+20**（强信号，覆盖长正文 KP 的累积分）

### Layer B — 语义模糊召回（2-gram 重叠）
- 对查询与字段分别生成 2-gram（中文相邻二字；英文按词；过滤含停用单字的 2-gram）。
- 字段权重：`title 6 / aliases 5 / tags 4 / frameworks 4 / symptoms 3 / chapter 3 / summary 2 / high 1`。
- `score_B += len(query_2gram ∩ field_2gram) × weight`。

### 总分
`total = score_A（精确） + score_B（重叠）`。Layer A 主导召回精度，Layer B 兜底语义相近。

## 4. 同义词扩展（保留原词，非替换）
`SYNONYMS = {客户↔顾客, 成效↔成果, 知识员工↔知识工作者, MBO↔目标管理, 创新源↔创新机会, 事业理论↔事业是什么, …}`
处理：若查询含 `k` 且缺 `v`，追加 `v` 到查询串（反之亦然）。**保留原词**，避免替换导致原词 2-gram 丢失、误召回。

## 5. 书名 / 章号定向
- **书名**：识别《管理的实践》/ 管理的实践 / 为成果 / 卓有成效 / 创新 等，限定 `source_book`。
- **章号**：正则 `第?(\d+)章`，限定 `chapter` 含该章号。
- 定向章时，候选集为该章全部 KP，**按书序（章-序，取自文件名）排序**，score 仅作过滤——契合「解释第X章」需按论述顺序呈现。

## 6. 输出格式
- 默认人类可读：逐条显示 标题 / [书名·章] / coverage / 路径 / 摘要 / 命中字段 / 评分 / 片段。
- `--json`：输出数组，每项含 `path, title, source_book, chapter, coverage, summary, matched, score, snippet`，供程序消费。

## 7. 调用示例
```bash
python3 scripts/retrieve.py "顾客是谁" --top 4
python3 scripts/retrieve.py "解释《管理的实践》第6章" --top 6
python3 scripts/retrieve.py "知识是易腐商品" --json
python3 scripts/retrieve.py "德鲁克的七种创新来源" --top 5
```

## 8. 调参提示
- 召回偏窄 → 调高 Layer B 字段权重或扩充 `SYNONYMS`。
- 长正文 KP 压过概念页 → 提高 title 子串命中权重（当前 +20）或缩短 `high` 截断长度。
- 误召回 → 检查 `STOP` 停用字、扩充 vocabulary（aliases 往往比 title 更短更易命中）。
