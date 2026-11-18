---
name: ddd-knowledge-insight
description: 把德鲁克知识分析调研结果（A/B/C三问原话、知识画布填充、诊断schema）按德鲁克框架升维为知识洞察——资源vs知识甄别、动词+名词独特知识提炼、四维度诊断(对/值/深/新)、五维交汇事业新机会，并输出知识分析画布与洞察报告（HTML，含原话溯源+置信度）、[内部]方法论说明（Markdown + Word(.docx) 双交付）及机器可读 delivery_bundle.json（画布三源×结论 + 报告 A/B/C 三节，与 HTML 同源，供 ddd-opportunity-synthesis 消费）。对应德鲁克知识点：知识即企业、独特知识、知识分析三问、资源vs知识、知识现实五原则、知识是易腐商品、知识诊断四维度、知识的表达、知识与市场双向反馈。用于：分析知识分析结果、生成知识画布、德鲁克知识洞察、知识诊断前置、独特知识提炼、我们公司的独特知识是什么、知识短板盘点。**不**做知识探询设计（那是 ddd-knowledge-survey）、不实际执行访谈/转写、不替代知识管理咨询、不替企业下结论。
agent_created: true
---

# Drucker Knowledge Insight Analyzer（德鲁克知识洞察分析器）

> 形态对齐 `ddd-customer-insight`（顾客侧分析器）。德鲁克 KB 关键 KP 摘要已**预编译**进 `references/drucker_kb_precompiled.md`（离线可用、更快，无需实时检索 `~/DruckerWiki`）。本 skill 是 `ddd-knowledge-survey`（知识探询设计）的下游「分析」环节，产出可直接喂给 `ddd-knowledge-manual`（知识手册维护）。

## 能力边界（4 问）

- **承接的重复任务**：把知识分析调研结果（A/B/C 三问原话、已填知识画布）按德鲁克框架升维为「资源vs知识甄别 → 动词+名词独特知识 → 四维度诊断 → 五维交汇机会」。
- **产出**：知识分析画布（HTML）+ 洞察报告（HTML）+ [内部]方法论说明（Markdown 源 + Word(.docx) 交付）+ **机器可读 delivery_bundle.json**（画布三源×结论 + 报告 A/B/C 三节，与 HTML 同源），均含原话溯源与置信度；HTML 可打印/导出 PDF，[内部]方法论说明用 `scripts/export_docx.py` 真实转换为 Word（禁止仅改后缀），delivery_bundle.json 由 `assets/build_bundle.py` 结构化导出供下游 synthesis 消费。
- **不路由的近邻（exclusions）**：
  1. 不做知识探询设计（那是 `ddd-knowledge-survey`）；
  2. 不实际执行访谈 / ASR 转写（探询执行是人工环节）；
  3. 不替代知识管理咨询 / 战略咨询；
  4. 不替企业下结论——AI 只做「提取、组织、升维」，洞察与决策交人；
  5. 不做知识手册的版本管理/半年提醒（那是 `ddd-knowledge-manual`）。
- **细节在 SKILL.md 之外**：分析 playbook、画布 schema、输出风险、输入参数见 `references/`。

## 何时使用（When to use）

- 用户已完成知识探询（A/B/C 三问），手上有原话 / 已填知识画布 / 诊断 schema，问「这些结果怎么分析」「帮我生成知识画布」「提炼我们的独特知识」「用德鲁克看我们的知识资产」。
- 输入已结构化的 `ddd-knowledge-survey` 产物（`knowledge_canvas_frame.md` 填充版 / `diagnosis_schema.md`）最佳；原始 A/B/C 原话也可，本技能先做轻量映射（见 `analysis_playbook.md` ①）。

## 总流程（7 步）

```
① 立场校准(成果锚定) → ② 三源重建(跟别人比/跟自己比/问优秀顾客)
→ ③ 资源vs知识甄别 → ④ 动词+名词提炼 → ⑤ 四维度诊断(对/值/深/新)
→ ⑥ 五维交汇(轻量草稿) → ⑦ HTML画布+报告组装
```

详细每一步的操作、KP 映射、五原则校验模板见 `references/analysis_playbook.md`；画布字段定义见 `references/canvas_schema.md`。

### ① 立场校准
回填「知识分析要服务的成果/行动」（kp-07-01 知识即企业 → 知识是差异化根源；锚定到 kp-01-01 成果在外部）。明确本次分析是「盘点独特知识」「诊断知识健康度」还是「找事业新机会」。

### ② 三源重建
把原话按 **跟别人比(A) / 跟自己比(B) / 问优秀顾客(C)** 三列归位（kp-07-04）。A 类再分双向：干得好别人干不了 / 干不好别人干得了（后者 = 知识短板，对称顾客侧的「非顾客」）。

### ③ 资源 vs 知识甄别
逐条标 **R(资源) / K(知识)**。渠道、厂房、资金、政策红利等可购买/可替代优势属「资源」，不计入知识（kp-07-02 信息≠知识；kp-07-03 独特知识）。拦截把资源误述为知识。

### ④ 动词+名词提炼
把 K 类候选抽象成「在 XX 领域，能做好 XX 事」（kp-07-08 知识的表达·具体而非笼统）。拦截「我们质量好」「我们服务优」等形容词伪知识；要求可观测、可验证。

### ⑤ 四维度诊断
对每条独特知识诊断四维度（kp-07-07 知识诊断四维度）：
- **对（正确）**：它指向领先吗？有顾客证据吗？
- **值（回报）**：收入真来自这吗？还是来自渠道/资源？
- **深（融入）**：系统化嵌入交付了吗？还是只在几个人脑子里？
- **新（改进）**：有过时风险吗？还有哪些场景在浪费这条知识？
每维度配「魔鬼代言人」3 条尖锐质疑。

### ⑥ 五维交汇（轻量草稿）
用 **顾客三问（来自 customer-insight 或 D1）× 独特知识 × 企业渴望 × 外界变化&未满足需求** 交汇，产出**事业新机会假设卡**（标「草稿·假设·待验证」，kp-07-09 知识与市场双向反馈）。本步仅草稿，不展开完整 C9 知识库。

### ⑦ HTML 画布 + 报告组装
用 `assets/knowledge_canvas_template.html` 与 `assets/insight_report_template.html` 填充。画布每格挂原话+置信度；报告含动词+名词独特知识清单、四维度诊断表、五维交汇假设卡。

**同时**用 `assets/build_bundle.py` 把 画布(三源×结论) + 报告(A/B/C 三节) 结构化为 `delivery_bundle.json`（与 HTML 同源，绝不回扫 HTML），供 `ddd-opportunity-synthesis` 双向反馈消费（知识结论→错失/低估的市场机会；市场结论→待补的新知识/能力）。

**另产 [内部]方法论说明**（单独成文档，标注 `[内部]`，不进入客户交付物）：把分析框架、数据诚信边界（C 类实录/模拟区分）、资源vs知识甄别要点、AI 角色边界、与下游衔接写清；随后用 `python scripts/export_docx.py --file <方法论.md>` 生成同名 `.docx` 交付，与 markdown 源保持同步。

## 输出契约（Output Contract）

- **知识分析画布（HTML）**：三源列（跟别人比 / 跟自己比 / 问优秀顾客）× 结论行，每格四字段——结论 / 原话支撑 / 置信度 / 状态。字段定义见 `references/canvas_schema.md`。
- **洞察报告（HTML）**：动词+名词独特知识清单 + 四维度诊断表（对/值/深/新 + 魔鬼代言人）+ 五维交汇事业新机会假设卡。
- **[内部]方法论说明（Markdown 源 + Word(.docx)）**：框架来源、数据诚信边界、资源vs知识关键点、AI 角色边界、与下游衔接。**必出 Word 交付物**（`scripts/export_docx.py` 真实转换），不进入客户产物。
- **delivery_bundle.json（机器可读中间表示）**：`meta` + `canvas[三源列×结论四字段]` + `report[A 动词+名词独特知识清单 / B 四维度诊断 / C 五维交汇事业新机会假设卡]`；schema 见 `assets/delivery_bundle_schema.json`，生成/校验见 `assets/build_bundle.py`（与 `ddd-customer-insight` 同构）。
- **交付格式**：画布/报告默认生成 **HTML**（打印友好、可导出 PDF）；[内部]方法论说明同时交付 **Word(.docx)**。
- **输出风险画像**见 `references/output-risk-profile.md`（分析产物最常犯的 6 类错误与 reviewer 检查项）。

## 德鲁克红线（9 条，不可违背）

1. **三源必含**：跟别人比 / 跟自己比 / 问优秀顾客 默认全处理，不可省略任一类 — kp-07-04。
2. **资源 vs 知识甄别不可省**：渠道/厂房/资金等可购买优势不表达为知识 — kp-07-02 / kp-07-03。
3. **动词+名词规范校验**：独特知识须「在 XX 领域，能做好 XX 事」；拦截形容词伪知识 — kp-07-08。
4. **原话至上**：每条结论附 ≥1 条原话（来源/题号），无原话标「证据不足·建议补访」— kp-07-03 源头 / kp-07-04。
5. **易腐意识**：报告须提示建立半年回顾 / 知识更新机制 — kp-07-06。
6. **知识短板必标**：「别人干得了而我们干不了」= 反向缺口，对称非顾客，不可漏 — kp-07-04·A2。
7. **成果锚定**：开头强制回填知识分析服务的成果/行动 — kp-07-01 / kp-01-01。
8. **客户产物纯净度**：HTML 画布/报告零 `[kp-xx]` / 德鲁克理论名 / 方法论注释（内部说明另成文档）。
9. **AI 只升维不替结论**：五维交汇/诊断一律标「草稿·假设·待验证」，绝不替企业拍板 — kp-07-01 / kp-01-01。

## 门禁（生产级）

- **触发自检**：description 覆盖目标说法且不过宽；
- **原话溯源自检**：每结论是否 ≥1 原话？无原话是否标「证据不足」？
- **资源vs知识自检**：是否逐条标 R/K？有无把资源当知识？
- **纯净度自检**：交付 HTML 字符串扫描，命中 `kp-` / `德鲁克` / `方法论` 即返工（内部说明不进客户产物）。
- **Word 交付物自检**：[内部]方法论说明须生成 `.docx`（`scripts/export_docx.py` 真实转换，内容、标题层级与原 md 一致）；若缺失或仅改后缀即返工。
- **JSON 自检**：`python assets/build_bundle.py validate delivery_bundle.json` 通过；canvas 三源列齐全、report 含 A/B/C 三节。
- **资源边界自检**：SKILL.md 只承载路由/骨架/契约/红线；细节均在 `references/` 与 `assets/`。
- **人工复核标注**：含结论性表述须标「需人工复核 / 假设·待验证」，不伪造证据。

## 参考文件索引

- `references/drucker_kb_precompiled.md` — 预编译 KP 摘要（分析视角）+ 升维话术（离线底座）
- `references/analysis_playbook.md` — 7 步流水线 + KP 映射 + 五原则校验模板
- `references/canvas_schema.md` — 知识画布字段定义（三源×结论 + 四维度 + 五维）+ 填写/原话挂载规则
- `references/output-risk-profile.md` — 分析产物输出风险画像 + reviewer 检查项
- `references/intent-boundary.md` — 完整输入参数 + 近邻 exclusion + 平台检测说明
- `assets/knowledge_canvas_template.html` — 知识分析画布 HTML 模板（打印已优化：列允许跨页断开、卡片不截断，避免导出 PDF 首页空白）
- `assets/insight_report_template.html` — 洞察报告 HTML 模板
- `assets/build_bundle.py` — 标准中间表示 delivery_bundle.json 生成/校验（与 ddd-customer-insight 同构）
- `assets/delivery_bundle_schema.json` — 中间表示 schema（镜像 customer-insight）
- `scripts/export_docx.py` — markdown → Word(.docx) 真实转换（用于 [内部]方法论说明等 Word 交付物，python-docx）

## 上下游衔接

- **上游**：`ddd-knowledge-survey` 的 `knowledge_canvas_frame.md`（填充版）/ `diagnosis_schema.md` 直接喂本技能；A/B/C 三问原话亦可。
- **下游**：本技能产出的动词+名词独特知识清单 + 四维度诊断，可初始化为 `ddd-knowledge-manual` 的手册 v1，进入「版本管理 + 半年提醒 + diff」生命周期；**本技能产出的 `delivery_bundle.json` 是 `ddd-opportunity-synthesis`（机会综合）的消费输入之一**（与 `ddd-customer-insight` 的 bundle 做「知识与市场双向反馈」）。
- **跨坊**：C 类「问优秀顾客」原话可与 `ddd-customer-survey` 的 D1 / `ddd-customer-insight` 的顾客画布共用，支撑五维交汇的「顾客三问」维度。
