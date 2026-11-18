# 能力边界详解（Intent & Boundary）

> SKILL.md 能力边界 4 问的展开 + 完整输入参数表 + 近邻 exclusion + 平台检测说明。

## 一、输入参数表（Input Parameters）

| 参数 | 必填 | 说明 | 缺失处理 |
|---|---|---|---|
| `business_context` | 是 | 事业/业务背景（如「卞家庄视频课业务」） | 追问 |
| `research_purpose` | 是 | 本次分析目的（盘点/诊断/找机会） | 追问 |
| `src_a` | 否* | 跟别人比 原话/画布（A1/A2） | 缺则标 insufficient |
| `src_b` | 否* | 跟自己比 原话/画布（成败） | 缺则标 insufficient |
| `src_c` | 否* | 问优秀顾客 原话/画布 | 可对接 D1 |
| `filled_canvas` | 否 | 已填知识画布（`knowledge_canvas_frame.md` 填充版） | 无则走原始原话映射 |
| `diagnosis_schema` | 否 | 上游诊断 schema 空框填充版 | 无则本技能自建 |
| `outcome_anchor` | 否 | 知识分析服务的成果/行动 | ① 立场校准补 |
| `known_resources` | 否 | 已知资源清单（辅助 R/K 甄别） | 可选 |

> *三源至少提供一类才可分析；全缺则拒绝并引导先用 `ddd-knowledge-survey` 设计探询。

## 二、近邻 exclusion（不路由）

| 技能 | 关系 | 本技能不做 |
|---|---|---|
| `ddd-knowledge-survey` | 上游·设计 | 不设计探询提纲 |
| `ddd-customer-survey` / `ddd-customer-insight` | 跨坊 | 不做顾客调研/顾客画布（C 类可共用 D1） |
| `ddd-knowledge-manual` | 下游·维护 | 不做版本管理/半年提醒/diff |
| ASR 转写 / 访谈执行 | 采集 | 不实际执行访谈 |
| 知识管理咨询 / 战略咨询 | 替代 | 不替代 |

## 三、平台检测说明
- 本技能默认产出 **HTML 本地文件**（打印友好、可导出 PDF）。
- 若需推送在线协作（飞书/钉钉/企微文档），移交 `ddd-knowledge-manual` 的同步逻辑，或后续版本扩展；本技能自身不写死平台名。

## 四、输出形态
- 知识分析画布（HTML）
- 洞察报告（HTML）
- 两份可独立打印/导出 PDF；内部方法论说明不进客户产物。
