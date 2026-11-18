# 平台同步规格（三平台 · 本地主 + 视图）

> 知识手册的线上文档同步。本地 `./knowledge-manual/` markdown 为唯一可信源；飞书/钉钉/企微文档只收渲染副本。

## 一、原则
- **本地为主**：版本/diff/时间戳只在本地 markdown 跑；平台文档是「视图」，不回读为主。
- **推送即渲染**：把手册正文（含 kid 锚点）渲染为平台文档格式后推送。
- **断则记 pending**：连接器未连 → `VERSION_INDEX.json` 的 `sync_status.<平台>=pending`；连上后补推。
- **幂等**：以 `topic+version` 去重，已存在则更新而非新建。

## 二、三平台导出模板

| 平台 | 连接器 key | 文档载体 | 导出模板 |
|---|---|---|---|
| 飞书 | `feishu` | 飞书文档 / 多维表格 | `assets/manual_export_feishu.md` |
| 钉钉 | `dingtalk` | 钉钉文档 / AI 表格 | `assets/manual_export_dingtalk.md` |
| 企微 | `wecom` | 企业微信文档 / 腾讯文档 | `assets/manual_export_wecom.md` |

导出模板为参数化 markdown，套用手册 frontmatter + 六段正文即可生成平台副本。

## 三、同步触发
- **手动**：人审更新后，调用同步（或在 `stamp_version.py` 流程末尾提示）。
- **自动**：未来可由 Automation 在 `stamp_version` 后探测连接器并推送（当前为手动+提示）。
- 同步失败/断开 → 更新 `sync_status`，提示「待同步」。

## 四、回读注意（重要）
- 平台文档**不可**作为 diff 源：实测飞书文档 WebFetch 会截断，且连接器常断。
- 所有「新旧对比」必须基于本地 markdown 的两版文件；平台副本仅供人阅。

## 五、纯净度
- 平台副本同样零内部理论标记（与本地手册同源，模板已脱敏）。
