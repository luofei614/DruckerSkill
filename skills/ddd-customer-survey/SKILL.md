---
name: ddd-customer-survey
description: 把彼得·德鲁克的顾客分析方法论（企业目的在外部、顾客三问、非顾客、顾客心中的价值、独特知识）固化为可复用的「顾客调研设计」能力——输入事业/产品+调研目的，输出标准化调研包（调研方案+问卷+访谈提纲+分析schema+问题清单整合表），每处设计决策可追溯到德鲁克知识点(KP)。含非顾客分支、防引导红线、客户产物纯净度分离，并检测飞书/钉钉/企微/问卷星把问卷沉淀到平台。用于：设计顾客调研、设计问卷、德鲁克顾客分析、调研方案、非顾客调研、上线前需求探询。**不**做问卷数据采集与统计分析、不替企业下结论、不实际拨打访谈、不替代营销咨询。并产出跨模块「问题清单整合表」（纯净版+[内部]标注版双 .docx）。
agent_created: true
---

# Drucker Customer Survey Designer（德鲁克顾客调研设计）

> 本技能按德鲁克方法论重设计：强化能力边界、输出契约、输出风险画像与门禁自检。原 7 模块德鲁克红线设计予以保留。

## 能力边界（4 问）

- **承接的重复任务**：把德鲁克顾客分析方法论固化为「输入事业/产品 + 调研目的 → 输出标准化调研设计包」的可复用能力。
- **产出**：调研方案（内部）+ 问卷模板 + 访谈提纲 + 分析 schema + **问题清单整合表（纯净版 .docx / [内部]标注版 .docx）**；客户产物纯净、内部文档物理分离。
- **不路由的近邻（exclusions）**：
  1. 不做问卷数据采集与统计分析（那是下游 C4 聚类环节）；
  2. 不替企业/顾客下结论——AI 只做「提取与组织」，结论交人工（红线）；
  3. 不实际拨打/执行访谈，只产出提纲；
  4. 不做纯问卷工具排版（问卷星等仅导出可导入格式）；
  5. 不覆盖知识分析坊（M7 D1 仅采集交接）；
  6. 不替代营销战略咨询。
- **细节在 SKILL.md 之外**：完整输入参数、分群规则、题库、KP 预编译、方法矩阵、平台沉淀见 `references/`。

## 何时使用（When to use）

- 用户要为某产品/事业设计顾客调研或问卷（上线前需求探询 / 上线后 NPS / 非顾客增长挖掘 / 知识发现）。
- 用户提到「德鲁克顾客分析」「顾客三问」「非顾客」「调研方案」「问卷设计」。
- 需要把问卷沉淀到飞书多维表格 / 钉钉 AI 表格 / 企业微信 AI 表格 / 问卷星。

## 总流程（7 步）

```
① 输入校验 → ② 检索德鲁克 KB（预编译）→ ③ 分群矩阵 → ④ 7 模块生成 → ⑤ 防引导校验 → ⑥ 分析 schema → ⑦ 组装输出 + 平台沉淀
```

详细参数与分支见 `references/intent-boundary.md`（输入参数）、`references/question_bank.md`（题库/防引导）、`references/method_selection.md`（方法）、`references/platform_export.md`（沉淀）。

### ① 输入校验
必填：`business_context` / `research_purpose` / `channels` / `sample_plan`。缺失先追问（≤5 项，按优先级）。完整参数表见 `references/intent-boundary.md`。

### ② 检索德鲁克 KB（预编译）
默认离线读 `references/drucker_kb_precompiled.md`（关键 KP 摘要 + 提问话术）。仅当用户明确要求原文且本机存在 `~/DruckerWiki` 时，才读 `index.md` 取对应 KP 全文。

### ③ 分群矩阵
按 `references/question_bank.md` 规则生成顾客 / 非顾客 / 复购分群与配额，**非顾客组默认必含**（kp-06-07）。

### ④ 7 模块生成
M0 成果锚定 · M1 画像 · M2 认知触达 · M3 购买决策 · M4 价值满足感 · M5 非顾客 · M6 竞争替代 · M7 独特知识 D1。题库与题型规则见 `question_bank.md`；方法选择见 `method_selection.md`。

### ⑤ 防引导校验
套用 `question_bank.md` 的「防引导校验清单」，改写诱导性 / 封闭暗示题。核心：开放式优先、排序后置。

### ⑥ 分析 schema
按 `assets/analysis_schema.md` 把每题映射到画布字段，预留「原话溯源」占位，供下游 C2/C3/C4/C6 使用。

### ⑦ 组装输出 + 平台沉淀
- 客户产物用 `assets` 模板生成并剥离所有 `[kp-xx]` / 德鲁克 / 方法论痕迹；内部文档加「[内部]」前缀分离。
- 新增「问题清单整合表」：用 `assets/question_inventory_template.md` 生成，经 `scripts/export_docx.py` 一次产出双 docx：
  · 纯净版（M1–M7，仅 模块/题号/题干/题型/是否必答/分支条件，零 KP/方法论，可直发顾客或导入平台）；
  · [内部]标注版（M0–M7，追加 对应KP/画布字段映射/设计意图·防引导备注，供内部自检与下游 C2–C6）。
- 默认生成真实 Word(.docx)；连接表格/问卷平台时按 `platform_export.md` 同步生成表单版。
- 平台沉淀为检查项：检测 connector 状态，询问后沉淀。

## 输出契约（Output Contract）

一次运行交付一个调研设计包，物理分离为两类：

- **客户产物（纯净）**：问卷 / 访谈提纲 / 焦点小组提纲 / **问题清单整合表（M1–M7 纯净版 .docx，可导入飞书/钉钉/企微多维表格，列对齐 `platform_export.md` 的 7 列模型前 6 列）**，零方法论痕迹，可直接发给被调研客户。
- **内部文档（[内部]）**：设计理念（德鲁克映射）+ 产物使用说明 + 分析 schema / 调研方案 / KP 索引 / **问题清单整合表（[内部]标注版 .docx，M0–M7，含 KP/画布映射/防引导备注）**。
- **交付格式**：默认真实 .docx；有表格/问卷平台则并发生成表单版。

> 客户产物最常犯的 6 类错误与 reviewer 检查项见 `references/output-risk-profile.md`。

## 德鲁克红线（9 条，不可违背）

1. 非顾客必含（M5 默认生成）— kp-06-07
2. 开放式优先、排序后置，禁诱导性封闭选项 — kp-06-02 / kp-06-03
3. 价值四问必嵌（用途/任务/满足感/价值定义）— kp-g06-03 / kp-06-04
4. 购买旅程全覆盖（知晓→购买→体验→用途）— kp-06-03
5. 决策链显性化（决策者≠使用者，渠道即顾客）— kp-06-05
6. 访谈类必提示录制留痕（对接转写技能）
7. 成果锚定：问卷开头强制回填「调研要服务的成果/行动」— kp-01-01
8. 客户产物纯净度：零 `[kp-xx]` / 德鲁克 / 方法论 / 防引导痕迹
9. 交付格式：默认真实 .docx，有平台则并发生成表单版
10. 问题清单整合表纯净版：M0 内部题不出现，且零 `[kp-xx]`/德鲁克/方法论/防引导痕迹（与红线 8 同标准）；[内部]标注版须保留 M0 与 KP/画布/防引导三列。

## 门禁（生产级）

- **触发自检**：description 覆盖目标用户说法且不过宽（误触发别的技能）。
- **纯净度自检**：客户产物交付前字符串扫描，命中 `kp-` / `德鲁克` / `方法论` / `画布` / `JTBD` 即返工。
- **资源边界自检**：SKILL.md 只承载路由/骨架/契约/红线；细节均在 `references/` 与 `assets/`，无装饰性空目录。
- **人工复核标注**：含结论性表述须标「需人工复核」，不伪造证据。

## 参考文件索引

- `references/intent-boundary.md` — 能力边界详解 + 完整输入参数表 + 平台检测补充
- `references/output-risk-profile.md` — 客户产物输出风险画像 + reviewer 检查项
- `references/drucker_kb_precompiled.md` — 预编译 KP 摘要 + 提问话术（理论底座）
- `references/question_bank.md` — 7 模块题库 + 防引导校验清单 + 分群矩阵规则
- `references/method_selection.md` — 调研方法选择矩阵
- `references/platform_export.md` — 平台检测与问卷沉淀指引
- `assets/survey_plan_template.md` / `questionnaire_template.md` / `interview_guide_template.md` / `analysis_schema.md` / `question_inventory_template.md`
- `scripts/export_docx.py` — 问题清单整合表 → 纯净版+[内部]标注版 双 .docx 真实转换（python-docx；运行须 `python-docx` 所属 venv，如 `~/.workbuddy/binaries/python/envs/default/bin/python`）

## 下游衔接

本 skill 是「设计」环节，输出可直接喂给采集/整理链路：C2 访谈转写 → C3 结构化 → C4 顾客现实聚类 → C6 画布自动填充。整合表的统一题号 `Mx-y` 作为 C2 访谈转写 → C4 聚类的稳定跨文件主键（与知识坊 D1 衔接、与 `ddd-opportunity-synthesis` 的机会×能力矩阵对齐）。
