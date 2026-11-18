"""feishu.py — 飞书适配器（多维表格 + 飞书文档）。

依赖：本环境已安装 `lark-cli`（路径见 LARK）。
推送源：DeliveryBundle（assets/build_bundle.py）。
flag 已对照 lark-cli 内置 skill（lark-base / lark-doc）校订：
  - base +base-create --name --table-name --fields '<json>'
  - base +record-batch-create --base-token --table-id --json '{"create_records":[...]}'
  - docs +create --title --doc-format markdown --content '<md>'
设环境变量 DRY_RUN=1 可「只校验命令格式、不实际创建」（短路返回 ok）。
"""
from __future__ import annotations

import json
import os
import subprocess
from typing import Dict, Any, List, Optional

from _common import PushResult, run

PLATFORM = "feishu"
DISPLAY = "飞书"
LARK = os.environ.get(
    "LARK_CLI",
    "/Users/luofei/.workbuddy/binaries/node/cli-connector-packages/bin/lark-cli",
)
DRY = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")

# 多维表格字段（与 Cell.to_row 的键一一对应，均为 text）
FIELD_DEFS = [
    {"name": "格号", "type": "text"},
    {"name": "列", "type": "text"},
    {"name": "标题", "type": "text"},
    {"name": "结论", "type": "text"},
    {"name": "原话溯源", "type": "text"},
    {"name": "置信度", "type": "text"},
    {"name": "状态", "type": "text"},
]
TABLE_NAME = "画布"


def _lark(args: List[str], **kw) -> subprocess.CompletedProcess:
    if DRY:
        args = args + ["--dry-run"]
    return run([LARK, *args], **kw)


def detect(status_map: Dict[str, str]) -> str:
    """活体探测：飞书以 `lark-cli auth status` 为准。"""
    try:
        r = _lark(["auth", "status"], timeout=20)
    except Exception:
        return "installed_not_auth"
    out = (r.stdout + r.stderr).lower()
    if r.returncode == 0 and "not logged" not in out and "error" not in out:
        return "available"
    return "installed_not_auth"


def push_base(bundle, target: str = "personal") -> PushResult:
    """画布(11格) → 飞书多维表格（默认个人空间）。"""
    name = bundle.meta.get("title", "顾客分析画布") + " · 画布"
    r = _lark([
        "base", "+base-create",
        "--name", name,
        "--table-name", TABLE_NAME,
        "--fields", json.dumps(FIELD_DEFS, ensure_ascii=False),
    ])
    if r.returncode != 0:
        return PushResult(PLATFORM, "base", False, error=(r.stderr or r.stdout).strip())
    if DRY:
        return PushResult(PLATFORM, "base", True, note="[dry-run] 命令格式校验通过（未实际创建）")

    token = _parse(r.stdout, ("base_token", "app_token", "baseToken", "token"))
    if not token:
        return PushResult(PLATFORM, "base", False, error="无法解析 base_token：" + r.stdout[:200])

    records = [c.to_row() for c in bundle.canvas]
    payload = json.dumps({"create_records": records}, ensure_ascii=False)
    r2 = _lark([
        "base", "+record-batch-create",
        "--base-token", token,
        "--table-id", TABLE_NAME,
        "--json", payload,
    ])
    if r2.returncode != 0:
        return PushResult(
            PLATFORM, "base", False,
            error=(r2.stderr or r2.stdout).strip(),
            note=f"Base 已建 token={token}",
        )
    url = f"https://feishu.cn/base/{token}"
    return PushResult(
        PLATFORM, "base", True, url=url,
        note="已创建在个人空间（默认）；可分享协作打勾「状态」",
    )


def push_doc(bundle, target: str = "personal") -> PushResult:
    """报告(叙事) → 飞书文档（在线协作文档，非 .docx 文件）。"""
    name = bundle.meta.get("title", "顾客洞察报告") + " · 报告"
    md = _render_report_md(bundle)
    r = _lark([
        "docs", "+create",
        "--title", name,
        "--doc-format", "markdown",
        "--content", md,
    ])
    if r.returncode != 0:
        return PushResult(PLATFORM, "doc", False, error=(r.stderr or r.stdout).strip())
    if DRY:
        return PushResult(PLATFORM, "doc", True, note="[dry-run] 命令格式校验通过（未实际创建）")

    doc_id = _parse(r.stdout, ("document_id", "doc_id", "docId", "doc_token", "token"))
    if not doc_id:
        return PushResult(PLATFORM, "doc", False, error="无法解析 doc id：" + r.stdout[:200])
    url = f"https://feishu.cn/docx/{doc_id}"
    return PushResult(
        PLATFORM, "doc", True, url=url,
        note="在线协作文档（非 .docx 文件）",
    )


def _parse(out: str, keys: tuple) -> Optional[str]:
    try:
        d = json.loads(out)
    except Exception:
        toks = out.strip().split()
        return toks[-1] if toks else ""
    data = d.get("data", d)
    if isinstance(data, dict):
        for k in keys:
            if data.get(k):
                return str(data[k])
    for k in keys:
        if d.get(k):
            return str(d.get(k))
    return ""


def _render_report_md(bundle) -> str:
    lines = [f"# {bundle.meta.get('title', '顾客洞察报告')}", ""]
    for sec in bundle.report:
        lines.append(f"## {sec.title}")
        for b in sec.blocks:
            if b.type == "h3":
                lines.append(f"### {b.text}")
            elif b.type == "quote":
                lines.append(f"> {b.text}")
            elif b.type == "list":
                lines.append(f"- {b.text}")
            else:
                lines.append(b.text)
        lines.append("")
    return "\n".join(lines)
