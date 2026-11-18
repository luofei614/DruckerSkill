# 协作分发参考 · 平台矩阵 + 检测 + 护栏 + 适配器接口

> 本文件是 `ddd-customer-insight` 「协作分发」阶段（SKILL.md ⑧）的细节层。
> **SKILL.md 只写通用流程，所有「哪个工具叫什么、怎么推」都在这里。** 新增平台 = 在这里加一行 + 在 `assets/adapters/` 加一个同名文件，SKILL.md 一字不改。

## 一、交付物类型（均为「在线可协作」，非 .docx 文件）

| 分析产物 | 推送形态 | 说明 |
|---|---|---|
| 顾客分析画布（11 格） | **Base 类**（多维表格 / 多维表 / 在线表格） | 每格一行：格号 / 列 / 标题 / 结论 / 原话溯源 / 置信度 / 状态；团队可协作打勾「状态」 |
| 顾客洞察报告（叙事） | **在线协作文档**（飞书文档 / 钉钉文档 / 企微文档） | 在线可评论、@人；以叙事性洞察为主，可按适配器能力以图片嵌入或链接 |

## 二、平台矩阵（唯一写平台名的地方）

| 平台 key | 中文 | Base 类产品 | 在线文档产品 | 推送方式（本环境） | 状态 |
|---|---|---|---|---|---|
| `feishu` | 飞书 | 多维表格 | 飞书文档 | `lark-cli base` + `lark-cli docs` | 可推（需先 `lark-cli auth login` 连接） |
| `dingtalk` | 钉钉 | 多维表 / 智能表 | 钉钉文档 | `dws aitable` + `dws doc`（dws connector 已连接可直推） | 可推：`base create`→`table create`→`record create` 建画布；`doc create --content-file` 建报告（adapter 脚本仍为占位，手动 dws 命令即可） |
| `wecom` | 企业微信 | 在线表格 / 微盘 | 企业微信文档 | wecom connector（本环境待接入） | 检测可达；推送需接入 connector |

> 适配器文件：`assets/adapters/{feishu,dingtalk,wecom}.py`，统一接口见第四节。
> 飞书已实装骨架；钉钉/企微先占位，连上 connector 后补全 `push_*` 即可，SKILL.md 不变。

## 三、检测机制（活体探测，不靠会话快照）

1. SKILL.md ⑧ 运行前，从当前 `<connector-status>` 构造 `WORKBUDDY_CONNECTOR_STATUS` 环境变量（JSON：`{"feishu":"connected","dingtalk":"disconnected","wecom":"disconnected"}`）。
2. 对每个平台调 `adapters/<平台>.detect(status_map)` 做活体确认，返回三态：
   - `available`：已连接且本环境可推送 → 候选。
   - `installed_not_auth`：工具已知但未授权/未连接 → 提示用户去连接。
   - `no_adapter`：本环境无推送工具 → 降级提示。
3. 飞书 `detect` 额外跑 `lark-cli auth status` 做实活体校验；钉钉/企微 `detect` 以 connector 状态为准（本环境无 CLI）。

## 四、护栏（贯穿始终）

- **默认个人空间**：`push_*(target="personal")` 默认落到用户个人空间，不惊动团队。
- **团队空间需一次性确认**：若用户选团队/共享空间，必须显式确认后才传 folder/space 参数推送。
- **多工具询问**：候选 ≥2 时，用 AskUserQuestion 让用户选一个（提供「全部」选项）；候选 1 个直接推；0 个保留本地并提示。
- **幂等**：以 `meta.title + 日期` 作为批次键去重，已存在则更新而非新建（见各 adapter 的 upsert 路径）。
- **红线不变**：原话溯源、置信度、假设标签原样带走；推送层只搬运不改写、不重分析、不替企业下结论。

## 五、适配器统一接口

每个 `assets/adapters/<平台>.py` 必须导出：

```python
PLATFORM: str            # "feishu" / "dingtalk" / "wecom"
DISPLAY: str             # "飞书" / "钉钉" / "企业微信"
detect(status_map) -> str          # "available" / "installed_not_auth" / "no_adapter"
push_base(bundle, target="personal") -> PushResult
push_doc(bundle, target="personal") -> PushResult
```

`PushResult` 定义于 `assets/adapters/_common.py`：`{platform, kind, ok, url?, error?, note?}`。

## 六、数据源

推送源是 `delivery_bundle.json`（标准中间表示），由 `assets/build_bundle.py` 在步骤 ⑦ 生成（与 HTML 同源，绝不回扫 HTML；仅含画布 11 格 + 报告叙事）。schema 见 `assets/delivery_bundle_schema.json`。

## 七、运行入口

编排脚本 `assets/publish.py`（被 SKILL.md ⑧ 调用）：

```bash
python assets/publish.py --bundle delivery_bundle.json --platform all
# 多工具时由上层用 AskUserQuestion 选定后传 --platform feishu|dingtalk|wecom
```

## 八、钉钉推送·表单视图硬要求（避坑必读）

> 适用范围：本工作流把**问卷/调研内容**推送到钉钉时（问卷设计是 `ddd-customer-survey` 的产物，但同一 customer-research 工作流里常一起推）。**本技能自身产出的画布(11格)/报告不需要表单视图**——画布是给团队标注状态的 Base，报告是在线文档，二者都不是「让被调研者填写」的表单，不要误建。
>
> 完整实战细节见 `ddd-customer-survey` 的 `references/platform_export.md` 第 D 节（「钉钉沉淀实战要点」）。

### 8.1 坑（为什么用户会说「没建表单视图」）

只建了「**题目设计表**」（一行=一题，字段：模块/题号/题干/题型/是否必答/分支条件/对应KP）就当收答卷用了——这表是给内部管理的，**无法让被调研者直接填写**。用户要的是能发链接收集回答的**表单视图**，光有设计表满足不了。

### 8.2 硬要求（三件套，缺一不可）

推送问卷到钉钉时，必须建齐：

1. **题目设计表**（可选/内部用）：一行=一题，供团队跟踪进度。
2. **答卷回收表**（★表单底座）：**一个字段 = 一道题，一行 = 一份答卷**；另加「称呼/联系方式」等少量元字段。表单视图建在这张表上。
3. **表单视图**：在答卷回收表上执行
   ```bash
   dws aitable form create --base-id <BASE> --table-id <答卷表ID> \
       --name "顺旺产品经销商合作情况调研" \
       --description "合作中答第1-15题及第20题；暂未合作请答第1-3题及第16-19题。"
   ```
   返回 `viewId`，拼接分享链接：
   `https://docs.dingtalk.com/i/nodes/{baseId}?iframeQuery=sheetId%3D{tableId}%26viewId%3D{viewId}`

### 8.3 字段类型映射

- 开放题 → `text`
- 路由/筛选题（如「合作关系：合作中/未合作/曾合作」）→ `singleSelect`，选项即分支路径
- 排序题 → 钉钉无排序题型，用 `text` 让填写者手写顺序
- 表单**描述**里写清分支作答指引（如「合作中答 1–15 题，未合作答 16–19 题」），把防引导红线保留在问卷侧

### 8.4 建表工程约束（来自实战）

- `dws aitable table create` 单次最多带 **15 个字段**，超出用 `field create` 逐个追加。
- 批量 `create_fields` 易报 **TIMEOUT_ERROR**，改为**逐字段 + 重试（≤3 次）**更稳；重试后必须 `table list` 校验字段总数与重复。
- 网络超时后服务端可能已建成，**重试前先 `table list` 查重**，避免产生「xx 1」重复表。
- 删除为高风险操作：空表/重复表用 `dws aitable table delete --yes` 清，删除前先 `record query` 确认无数据。

### 8.5 对外收集需用户手动开

表单视图建好后，Agent **无法代开**公开填写权限。须在钉钉客户端打开表单 → 点「分享」→ 开启「公开收集」，用户确认身份后才可外发链接。交付时务必提示这一步。
