---
name: ddd-customer-insight
description: 把德鲁克顾客调研的原始结果（访谈原话/整合表）按德鲁克框架逐层榨出洞察——顾客现实画像、非顾客机会、价值锚点、看懂顾客两问、竞争空白，并输出填充好的顾客分析画布与洞察报告（HTML，含原话溯源+置信度）。对应德鲁克知识点：市场营销八大现实、顾客三问、非顾客、顾客心中的价值、JTBD最终用途、看懂顾客、决策链/渠道即顾客。用于：分析顾客调研结果、生成顾客画布、德鲁克洞察分析、调研结果怎么看、用德鲁克看这些访谈。**不**做录音转写、不重新设计问卷、不做知识诊断/独特知识提炼（留待知识坊）、不替企业下结论。
agent_created: true
---

# Drucker Customer Insight（德鲁克顾客洞察分析器）

> 形态对齐 `ddd-customer-survey`。德鲁克 KB 关键 KP 摘要已**预编译**进 `references/drucker_kb_precompiled.md`（离线可用、更快，无需实时检索 `~/DruckerWiki`）。

## 能力边界（4 问）

- **承接的重复任务**：把调研结果（原话/整合表）按德鲁克框架升维为「顾客现实 → 非顾客机会 → 价值锚点 → 看懂顾客 → 竞争空白 → 画布」。
- **产出**：顾客分析画布（HTML）+ 洞察报告（HTML），均含原话溯源与置信度；可打印/导出 PDF；检测到已连接协作工具（飞书/钉钉/企微）时，可按 `references/collab_delivery.md` 将画布推为多维表格、报告推为在线协作文档（均为「在线可协作」类，非 .docx 文件）。
- **不路由的近邻（exclusions）**：
  1. 不做 ASR 录音转写（那是 C2 环节）；
  2. 不重新设计问卷/访谈提纲（那是 `ddd-customer-survey`）；
  3. **不做知识诊断 / 独特知识提炼（知识坊侧，留待思路③，本技能不含知识分析画布）**；
  4. 不替企业下结论——AI 只做「提取、组织、升维」，洞察与决策交人。
- **细节在 SKILL.md 之外**：分析 playbook、画布 schema、输出风险、输入参数见 `references/`。

## 何时使用（When to use）

- 用户调研已完成，手上有访谈原话 / 收集表 / 整合表，问「这些结果怎么分析」「帮我生成顾客画布」「用德鲁克看这些访谈」。
- 输入已结构化的 `ddd-customer-survey` 分析 schema（题→画布字段+原话溯源）最佳；原始原话也可，本技能先做轻量映射（见 `analysis_playbook.md` ①）。

## 总流程（7 步）

```
① 立场校准(八大现实对照) → ② 三问重建 → ③ 非顾客归因 → ④ 价值分层
→ ⑤ 看懂顾客两问 → ⑥ 竞争聚合 → ⑦ 画布+报告组装(HTML) → ⑧ 协作分发(可选·自动)
```

详细每一步的操作、KP 映射、认知偏差模板见 `references/analysis_playbook.md`；画布字段定义见 `references/canvas_schema.md`。

### ① 立场校准
拉出企业预填「我们以为」，与原话逐条对照，输出**认知偏差清单**（八大现实）。重点查：内部假设是否被外部现实打脸。

### ② 三问重建
从原话抽「谁 / 买什么 / 价值」，定位画像与决策链（谁决定、谁影响、渠道即顾客）。

### ③ 非顾客归因
非顾客原话归入三类（从未接触 / 接触未成交 / 曾流失），提炼各类型流失原因 Top。

### ④ 价值分层
穿透「表层产品 → 中层方案 → 深层情感 + 最终用途」，分「购前看重 vs 购后看重」标错位。

### ⑤ 看懂顾客两问
扫描「从制造商逻辑看不合理」的行为 → 推其背后的现实处境 → 标原话。AI 仅当「磨刀石」，草稿交人辩论。

### ⑥ 竞争聚合
按「满足感」而非「产品线」聚合，抽三类竞争（直接/间接/非竞争对手），标「②③交界处」战略空白。

### ⑦ 画布 + 报告组装（HTML）
用 `assets/customer_canvas_template.html` 与 `assets/insight_report_template.html` 填充产出。每格挂原话+置信度；**同时**用 `assets/build_bundle.py` 把 画布(11格)+报告(叙事) 结构化为 `delivery_bundle.json`（与 HTML 同源，绝不回扫 HTML），供 ⑧ 推送使用。

### ⑧ 协作分发（可选 · 自动）

> 细节见 `references/collab_delivery.md`（平台矩阵 + 检测 + 护栏 + 适配器接口）。本步骤只写通用流程，**不写死任何平台名**。

- **触发**：默认开启；若用户明确说「不要推送 / 本地即可」则跳过。
- **A. 构造 status_map**：从当前 `<connector-status>` 取 `feishu` / `dingtalk` / `wecom` 的 connected 状态，注入环境变量 `WORKBUDDY_CONNECTOR_STATUS`（JSON）。
- **B. 候选探测**：对每个 connected 平台，调 `assets/adapters/<平台>.detect(status_map)` 做活体确认，得 `available` 者入候选。
- **C. 路由**：
  - 候选为空 → 仅保留本地 HTML/PDF，提示「未检测到已连接协作工具，可连接后重跑或用 /publish 补推」。
  - 候选 1 个 → 直接推送该平台。
  - 候选 ≥2 个 → 用 **AskUserQuestion** 让用户选一个（提供「全部」选项）。
- **D. 推送内容（均为「在线可协作」类，非 .docx 文件）**：
  - 画布(11格) → 该平台 **Base 类**（多维表格 / 多维表 / 在线表格）；
  - 报告(叙事) → 该平台 **在线协作文档**（飞书文档 / 钉钉文档 / 企微文档）。
  - **默认创建在个人空间**；若用户选团队/共享空间则需一次性确认。
  - ⚠️ **附带推送问卷内容到钉钉时，必须建「答卷回收表 + 表单视图」**（题目设计表无法让被调研者填写）。三件套与建表约束见 `references/collab_delivery.md` 第八节；对外公开收集需用户在钉钉客户端手动开启。
- **E. 幂等**：以 `meta.title + 日期` 去重，已存在则更新而非新建。
- **F. 返回链接**；本地 HTML/PDF 不变。运行入口：`python assets/publish.py --bundle delivery_bundle.json --platform all`。

## 输出契约（Output Contract）

- **顾客分析画布（HTML）**：三列（顾客是谁 / 买的是什么 / 认为的价值）× 多层格，每格四字段——结论 / 原话支撑 / 置信度 / 状态。字段定义见 `references/canvas_schema.md`。
- **洞察报告（HTML）**：看懂顾客两问草稿 + 非顾客机会清单 + 竞争②③空白 + 行动假设卡（叙事性洞察，AI 仅升维提取、不替企业下结论）。
- **交付格式**：默认生成 **HTML**（打印友好、可导出 PDF）；`references/collab_delivery.md` 定义「检测到已连接协作工具时」的自动推送——画布→该平台 Base 类（多维表格/多维表/在线表格），报告→该平台在线协作文档（飞书文档/钉钉文档/企微文档），**默认个人空间、多工具时询问用户**；推送源为 `delivery_bundle.json`，本地 HTML/PDF 不变。
- **输出风险画像**见 `references/output-risk-profile.md`（分析产物最常犯的 6 类错误与 reviewer 检查项）。

## 德鲁克红线（8 条，不可违背）

1. **原话至上**：每条结论附 ≥1 条顾客原话（场次/题号/时间戳），无原话标「证据不足·建议补访」— kp-06-03。
2. **假设不结论**：看懂顾客两问、非顾客机会、竞争空白一律标「草稿·假设·待验证」，绝不替企业拍板 — kp-01-01。
3. **非顾客必含**：三类非顾客归因不可省略，这是增长金矿 — kp-06-07。
4. **价值由顾客定义**：价值锚点须来自顾客原话，不得用企业自认价值 — kp-g06-03。
5. **购前购后错位必查**：价值分层必须分付款前/体验后并标错位 — kp-g06-03。
6. **看懂顾客仅草稿**：非理性行为→现实处境的推断标注为草稿，洞察归人 — kp-06-11。
7. **置信度必标**：每格结论打高/中/低置信度，低则高亮 — kp-06-03 证据卫生。
8. **客户产物纯净度**：HTML 画布/报告零 `[kp-xx]` / 德鲁克理论名 / 方法论注释（内部说明另成文档）。

## 门禁（生产级）

- **触发自检**：description 覆盖目标说法且不过宽；
- **原话溯源自检**：每结论是否 ≥1 原话？无原话是否标「证据不足」？
- **纯净度自检**：交付 HTML 字符串扫描，命中 `kp-` / `德鲁克` / `方法论` 即返工（内部说明不进客户产物）。
- **资源边界自检**：SKILL.md 只承载路由/骨架/契约/红线；细节均在 `references/` 与 `assets/`。
- **人工复核标注**：含结论性表述须标「需人工复核 / 假设·待验证」，不伪造证据。

## 参考文件索引

- `references/drucker_kb_precompiled.md` — 预编译 KP 摘要（分析视角）+ 提问/对照话术（离线底座）
- `references/analysis_playbook.md` — 7 步流水线 + KP 映射 + 认知偏差（八大现实）模板
- `references/canvas_schema.md` — 顾客画布字段定义 + 填写/原话挂载规则
- `references/output-risk-profile.md` — 分析产物输出风险画像 + reviewer 检查项
- `references/intent-boundary.md` — 完整输入参数 + 近邻 exclusion + 平台检测说明
- `references/collab_delivery.md` — 协作分发：平台矩阵(飞书/钉钉/企微) + 检测 + 护栏 + 适配器接口
- `assets/build_bundle.py` — 标准中间表示 `delivery_bundle.json` 生成/读取（画布 11 格 + 报告叙事）
- `assets/delivery_bundle_schema.json` — 中间表示 schema（画布 + 报告）
- `assets/adapters/{_common,feishu,dingtalk,wecom}.py` — 三平台推送适配器（统一接口，SKILL.md 零平台写死）
- `assets/publish.py` — 协作分发编排入口
- `assets/customer_canvas_template.html` — 顾客分析画布 HTML 模板（打印已优化：列允许跨页断开、卡片不截断，避免导出 PDF 首页空白）
- `assets/insight_report_template.html` — 洞察报告 HTML 模板

## 上游衔接

`ddd-customer-survey` 的 `analysis_schema.md`（题 → 画布字段 + 原话溯源）直接喂本技能的 `canvas_schema.md`，无缝消费；本技能产出亦可向下游 C9 知识库沉淀。
