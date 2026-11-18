# 德鲁克工作坊 · 技能包安装说明

> 本技能包用于在企业中实践彼得·德鲁克（Peter Drucker）的管理方法论。安装后，你将在 WorkBuddy 中拥有 8 个「ddd-」系列技能，以及一个德鲁克知识库（DruckerWiki）。

---

## 包含内容

### 8 个技能（位于 `skills/` 目录）

| 技能名 | 用途 |
|--------|------|
| `ddd-customer-survey` | **顾客调研设计**：输入事业/产品，输出标准化调研包（方案 + 问卷 + 访谈提纲 + 分析 schema） |
| `ddd-customer-insight` | **顾客洞察分析**：把调研结果升维为顾客分析画布与洞察报告（含原话溯源 + 置信度） |
| `ddd-customer-knowledge-scan` | **现状感知扫描**：对话式问卷（11 选择 + 2 开放），答完提交大屏，供主持人实时查看 |
| `ddd-knowledge-survey` | **知识分析调研设计**：输出知识探询包（A/B/C 探询提纲 + 知识画布框架） |
| `ddd-knowledge-insight` | **知识洞察分析**：提炼独特知识，输出知识画布、洞察报告与机器可读 bundle |
| `ddd-knowledge-manual` | **知识手册维护**：带版本/时间戳/半年提醒/语义 diff 的「活」知识手册 |
| `ddd-knowledge-qa` | **德鲁克知识问答**：基于知识库逐字引用原话，解答德鲁克思想与著作问题 |
| `ddd-opportunity-synthesis` | **机会综合**：交汇顾客洞察与知识洞察，套 7 大创新源推演新机会与新能力 |

### 1 个知识库（位于 `DruckerWiki/` 目录）

德鲁克四本核心著作的结构化知识库（**339 个知识点 + 14 个跨书概念**），是 `ddd-knowledge-qa` 等技能的检索源。需复制到用户主目录 `~/` 下，最终路径为 `~/DruckerWiki`。

## 安装
请将skills/下所有的技能安装到当前智能体，安装为用户级的SKILL。

##、验证安装

- 应列出 **8 个 `ddd-` 开头**的技能目录；
- 应看到 `~/DruckerWiki/index.md` 文件。

两项均正常即安装成功。在输入框中输入 /ddd 可以看见新安装的技能。

---

## 推荐使用顺序（工作流）

技能分两条主线 + 一个交汇点，建议按以下顺序使用：

```
【顾客线】
ddd-customer-survey（设计调研） 提示词：请根据某某的业务设计一个顾客分析的调研。
        ↓
ddd-customer-insight（分析洞察） 提示词：请分析顾客调研的数据。

【知识线】
ddd-knowledge-survey（设计调研） 提示词：请根据某某的业务设计一个知识分析的调研。
        ↓
ddd-knowledge-insight（分析洞察）提示词：请分析知识调研的数据。
        ↓
ddd-knowledge-manual（沉淀为活手册）  提示词：生成知识手册

【交汇升华】
ddd-customer-insight 的 bundle  ┐
                                ├─→ ddd-opportunity-synthesis（推演新机会/新能力） 提示词：基于顾客分析和知识分析，打通看新机会
ddd-knowledge-insight 的 bundle ┘

【随时可用】
ddd-knowledge-qa（就知识库问答）
ddd-customer-knowledge-scan（大屏现状扫描）


## 安装完毕发送使用手册的图片。  

安装完毕后，把'技能使用手册.png' 发送给用户， 提醒用户按使用手册来使用， 每个技能的提示词也都在图片中。  



如有安装问题，请联系工作坊组织者。   作者：罗飞， 微信：jianyueluofei
