# {{title}} · 知识手册（企业微信/腾讯文档副本）

> 本副本由 `ddd-knowledge-manual` 从本地手册同步生成，仅供在线查阅。版本/对比以本地 markdown 为准。

## 元信息
- 版本：v{{version}} ｜ 创建：{{created_at}} ｜ 更新：{{updated_at}} ｜ 应回顾：{{next_review_due}}
- 负责人：{{owner}} ｜ 成果锚定：{{outcome_anchor}}

## 1. 独特知识清单
{{#each knowledge}}
- **[{{kid}}]** {{statement}}（{{rk}}，易腐：{{perishability}}）
{{/each}}

## 2. 资源 vs 知识甄别
{{#each rk_table}}
- {{kid}}：{{statement}} → {{rk}}
{{/each}}

## 3. 四维度成熟度
{{#each four_dim}}
- {{kid}}：对={{correct}}｜值={{value}}｜深={{depth}}｜新={{novel}}｜薄弱={{weak}}
{{/each}}

## 4. 知识短板
{{shortboard}}

## 5. 五维机会草稿
{{opportunity}}

## 6. 更新日志
{{changelog}}
