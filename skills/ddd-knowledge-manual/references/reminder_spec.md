# 提醒规格（三平台 · 用户选发）

> 半年更新提醒的多平台实现。SKILL.md 不写死平台名，运行时按连接器状态路由。

## 一、触发链路

```
每周 Automation → check_due.py（扫 VERSION_INDEX.json 得到期列表）
       → notify.py --due-file due.json --platform <P> 渲染该平台提醒
       → 交付对应连接器发送（或对话内告警兜底）
```

## 二、路由规则（运行时）

| 已连平台数 | 行为 |
|---|---|
| 0 | 仅对话内告警（红色清单），不外部发送 |
| 1 | 直发该平台 |
| ≥2 | **用 AskUserQuestion 让用户选发哪个**（提供「全部」选项） |

> 「多可用时由用户选发」是已确认的设计：不自动广播，避免打扰；也不擅自替用户选平台。

## 三、三平台提醒形态与模板

| 平台 | 连接器 key | 形态 | 模板文件 |
|---|---|---|---|
| 飞书 | `feishu` | 交互卡片(JSON)，含手册名/owner/逾期天数/「去审查」链接 | `assets/reminder_card_feishu.json` |
| 钉钉 | `dingtalk` | ActionCard(markdown) | `assets/reminder_card_dingtalk.md` |
| 企微 | `wecom` | markdown / 模板卡片 | `assets/reminder_card_wecom.md` |

`notify.py` 做占位符替换：`{{title}} {{owner}} {{due_date}} {{overdue_days}} {{version}} {{repo}}`。
飞书模板为 JSON，替换后 `json.loads` 校验再输出，确保卡片合法。

## 四、Automation 模板

见 `assets/automation_template.json`。要点：
- `scheduleType: recurring`，`rrule: FREQ=WEEKLY;BYDAY=MO`（每周一）
- `prompt`：调用 `check_due.py` → 若有到期，按连接器状态路由 → 渲染并请用户选平台发送。
- 创建方式：用 `automation_update` 工具以该模板注册（用户可让我代注册）。

## 五、护栏（红线）
- **只通知、不自动改写**：提醒不含任何修改手册的动作。
- 提醒内容不含内部理论标记（纯净度）。
- 逾期天数基于 `next_review_due` 与系统当日日期计算。
- 若 `sync_status` 有 `pending`，提醒中一并提示「有未同步的平台副本」。
