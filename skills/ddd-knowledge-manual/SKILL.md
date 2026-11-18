---
name: ddd-knowledge-manual
description: 把德鲁克「知识是易腐商品，需每半年更新」的理念工程化为可维护的知识手册——知识手册生成与版本管理（自动时间戳+版本记录）、半年更新提醒（飞书/钉钉/企微多平台，多可用时由用户选发）、新旧版本语义 diff（增/删/改可追溯）、德鲁克编写框架（动词+名词/资源vs知识/四维度/易腐意识）。本地 markdown 为源，平台文档为同步视图。用于：维护知识手册、知识库版本管理、知识手册更新提醒、知识手册新旧对比、独特知识沉淀与保鲜、事业知识资产盘点。**不**做知识探询设计（ddd-knowledge-survey）、不替代 insight 做知识提炼/诊断（ddd-knowledge-insight）、不自动改写手册内容、不替企业下结论。
agent_created: true
---

# Drucker Knowledge Manual Maintainer（德鲁克知识手册维护器）

> 是 C9「知识库沉淀与保鲜」的落地版。把 `ddd-knowledge-insight` 提炼的独特知识沉淀为**会自己提醒、会自己对比版本**的活手册。德鲁克 KB 关键 KP 已预编译（见 `references/drucker_kb_precompiled.md`，离线可用）。

## 核心设计原则

- **本地为主 + 平台同步**：`./knowledge-manual/` 下的 markdown 是**唯一可信源**，跑版本/时间戳/语义 diff；飞书/钉钉/企微文档只接收渲染副本（视图）。原因：平台文档 WebFetch 会截断、连接器常断、语义 diff 无法可靠回读。
- **半年 = 182 天**（约等于 6 个日历月，避开 2 月/闰年歧义）。每次更新把 `updated_at` 重写为当天，`next_review_due` 重置——即「重置时钟」。
- **易腐分级**：每条知识标 `perishability`（高/中/低）；高易腐条目审查周期可短至 **90 天**，半年为默认下限——真正贴合 kp-07-06 的动态含义。
- **只提醒、不自动改写**（human-in-the-loop 红线）：提醒通知人审，更新动作仍由人执行。

## 能力边界（4 问）

- **承接的重复任务**：把企业核心知识资产固化为带版本/时间戳的手册，并维护其「提醒→审查→diff→新版」生命周期。
- **产出**：带 frontmatter 时间戳的手册 markdown + `VERSION_INDEX.json`（版本总账）+ `CHANGELOG.md`（更新日志）+ **Word(.docx) 交付物**（必选，python-docx 真实转换，禁止仅改后缀）+ 三平台渲染副本（可选同步）+ HTML diff 报告。
- **不路由的近邻（exclusions）**：
  1. 不做知识探询设计（那是 `ddd-knowledge-survey`）；
  2. 不替代 `ddd-knowledge-insight` 做知识提炼/诊断——本技能消费其产出；
  3. 不自动改写手册内容——只生成模板/提醒/对比，更新由人审；
  4. 不替企业下结论/写业务内容——AI 只做结构、版本、对比、提醒。
- **细节在 SKILL.md 之外**：编写框架、易腐 KP、提醒规格、平台同步见 `references/`。

## 何时使用（When to use）

- 「帮我们建/维护知识手册」「知识库怎么版本管理」「到半年了该提醒更新知识手册了」「对比一下新旧两版知识手册」「把 insight 产出的独特知识沉淀成手册」。
- 输入：`ddd-knowledge-insight` 的动词+名词独特知识清单最佳；也可从零按 `assets/manual_template.md` 起草。

## 总流程（生命周期）

```
① 起草/生成手册(用 manual_template) → ② stamp_version 打时间戳+登记版本 → ②b export_docx 生成 Word 交付物
→ 〔循环〕③ 每周自动化 check_due 扫描 → ④ 到期 notify 多平台提醒(用户选发)
→ ⑤ 人审并更新手册 → ⑥ diff_manual 新旧语义对比(增/删/改) → ⑦ stamp 新版(重置时钟)
→ ⑧ platform_sync 推渲染副本(断则记 pending)
```

### ① 起草 / 生成
用 `assets/manual_template.md`（带 kid 锚点骨架）起草；或消费 `ddd-knowledge-insight` 产出。

### ② 打时间戳 + 登记版本
**文件命名（强制）**：手册 markdown / docx 文件名用**中文业务名 + `_v{n}`** 后缀，例如 `王德峰视频课业务知识手册_v1.md`；`topic` 为内部稳定 id（建议中文业务名，如 `王德峰视频课业务`，与文件名解耦，跨版本不变）。
`python scripts/stamp_version.py --file <手册.md> --repo ./knowledge-manual --owner <人> [--perishability high] [--topic <中文id>]`
→ 写入/更新 frontmatter（`created_at/updated_at/next_review_due/version/owner/sync_status`），追加 `VERSION_INDEX.json`（**记录真实文件路径，不再用 topic 拼文件名**），首版写 `CHANGELOG.md`。

### ②b 生成 Word 交付物
`python scripts/export_docx.py --file <手册.md> --out <手册.docx>` → 把本地 markdown **真实转换**为 .docx（剥离 frontmatter、渲染标题/引用/表格/列表/加粗），与 md **同名同目录**；对客户/打印/归档场景为必选交付物（禁止仅改后缀）。

### ③ 每周扫描（自动化触发）
`python scripts/check_due.py --repo ./knowledge-manual` → 输出到期手册列表（today ≥ next_review_due）。由 Automation（`assets/automation_template.json`）每周调用。

### ④ 多平台提醒（用户选发）
`python scripts/notify.py --due-file due.json --platform <feishu|dingtalk|wecom>` → 渲染对应平台提醒卡片/消息。
**路由规则**（SKILL.md 不写死平台名，运行时按连接器状态）：
- 0 个平台连 → 仅对话内告警；
- 1 个连 → 直发；
- ≥2 个连 → **用 AskUserQuestion 让用户选发哪个**（提供「全部」）。
模板见 `assets/reminder_card_{feishu.json,dingtalk.md,wecom.md}`。

### ⑤ 人审并更新
人基于提醒审查内容、增补/修订条目（保持 kid 稳定）。

### ⑥ 新旧语义对比
`python scripts/diff_manual.py <旧版.md> <新版.md> --format html --out diff_report.html`
→ 按 kid 分类 **新增 / 删除 / 修改 / 未变**；无 kid 降级 `difflib` 行级；结果写入 `CHANGELOG.md` + 生成 HTML 报告（`assets/diff_report_template.html`）。

### ⑦ 新版（重置时钟）
再次 `stamp_version.py` → version+1，`updated_at`=今天，`next_review_due` 重置。

### ⑧ 平台同步
`references/platform_sync.md` 定义三平台导出；向已连平台推渲染副本，断开记 `pending` 连上补推。

## 输出契约（Output Contract）

- **手册 markdown**（源）：带 frontmatter + kid 锚点条目 + 六段骨架（见 `assets/manual_template.md`）。**文件名须为中文业务名 + `_v{n}`**（如 `王德峰视频课业务知识手册_v1.md`），不用英文/pinyin slug。
- **VERSION_INDEX.json**：机器可读版本总账。
- **CHANGELOG.md**：人读更新日志（每次 diff 摘要）。
- **Word(.docx) 交付物**（必选）：与手册 markdown 同名同目录，用 `scripts/export_docx.py` 真实转换（禁止仅改后缀）；面向客户/打印/归档场景。
- **三平台渲染副本**（可选）：飞书/钉钉/企微文档视图。
- **HTML diff 报告**：增/删/改可视化。
- **纯净度**：手册正文面向企业、零内部理论标记；`[内部]` 说明另存。

## 德鲁克红线（8 条，不可违背）

1. **易腐必提示**：手册/报告须显式提示半年回顾 + 每条 perishability — kp-07-06。
2. **时钟可重置**：每次更新必须重写 `updated_at` 并重置 `next_review_due`，否则提醒失效。
3. **只提醒不自动改**：提醒通知人审，绝不自动改写手册 — human-in-the-loop。
4. **本地为主**：版本/diff 只跑在本地 markdown；平台文档为视图，不回读为主 — 可靠性。
5. **kid 稳定锚点**：条目 id 跨版本不变，否则语义 diff 退化为行级。
6. **资源 vs 知识 / 动词+名词**：手册编写遵守 insight 的提炼规范（引用框架见 `references/writing_guide.md`）— kp-07-02/07-03/07-08。
7. **成果锚定**：手册元信息含 `outcome_anchor`（服务什么成果）— kp-07-01。
8. **客户产物纯净度**：手册零 `[kp-xx]` / 德鲁克理论名 / 分析术语（内部说明另成文档）。

## 门禁（生产级）

- **触发自检**：description 覆盖目标说法且不过宽（误触发别的技能）。
- **时间戳自检**：每次生成/更新后 frontmatter 是否有 `created_at/updated_at/next_review_due`？`VERSION_INDEX.json` 是否登记？
- **Word 交付物自检**：每次生成/更新后是否用 `export_docx.py` 生成了与 md 同名的 `.docx`（真实转换，非仅改后缀）？
- **文件名中文自检**：手册文件名须为中文业务名 + `_v{n}`（如 `王德峰视频课业务知识手册_v1.md`），不得为英文/pinyin slug（如 `wangdefeng-video-course-v1.md`）；`VERSION_INDEX.json` 的 `file` 须与实际文件路径一致。
- **kid 自检**：条目是否带稳定 kid？diff 前检查。
- **纯净度自检**：手册正文扫描，命中 `kp-` / `德鲁克` / `方法论` 即返工。
- **资源边界自检**：SKILL.md 只承载路由/骨架/契约/红线；细节在 `references/` 与 `assets/` 与 `scripts/`。
- **人工复核标注**：diff 报告/提醒均标「需人工复核」，不伪造证据。

## 参考文件索引

- `references/writing_guide.md` — 德鲁克编写框架（六段骨架 + kid 锚点 + 动词+名词/资源vs知识/四维度）
- `references/drucker_kb_precompiled.md` — 预编译 KP（kp-07-06 易腐为主 + 关联）
- `references/reminder_spec.md` — 三平台提醒规格 + 路由规则 + Automation 模板说明
- `references/platform_sync.md` — 三平台（飞书/钉钉/企微）知识库文档同步
- `assets/manual_template.md` — 带 kid 锚点的手册骨架
- `assets/reminder_card_feishu.json` / `reminder_card_dingtalk.md` / `reminder_card_wecom.md` — 三平台提醒模板
- `assets/manual_export_feishu.md` / `manual_export_dingtalk.md` / `manual_export_wecom.md` — 三平台导出模板
- `assets/diff_report_template.html` — 新旧对比 HTML 报告模板
- `assets/automation_template.json` — 每周扫描 Automation 模板
- `scripts/stamp_version.py` — 打时间戳 + 版本登记
- `scripts/export_docx.py` — 手册 markdown → Word(.docx) 导出
- `scripts/check_due.py` — 扫描到期手册
- `scripts/diff_manual.py` — 新旧语义 diff
- `scripts/notify.py` — 多平台提醒渲染

## 上下游衔接

- **上游**：`ddd-knowledge-insight` 的动词+名词独特知识清单 + 四维度诊断 → 直接初始化手册 v1。
- **上游**：`ddd-knowledge-survey` 的探询设计 → insight → 本技能，形成「设计→分析→维护」完整闭环。
- **跨坊**：手册「知识短板」可反向喂回 survey/insight 做下一轮探询。
