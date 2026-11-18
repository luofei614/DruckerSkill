"""wecom.py — 企业微信适配器（在线表格/微盘 + 企业微信文档）。

当前环境未内置企微 CLI / connector 工具。detect 依据会话 connector 状态判定；
push_* 在缺工具时优雅返回不可用，待接入 wecom connector 后补全即可（SKILL.md 不变）。

接入 TODO（连上 connector 后）：
  push_base -> 调 wecom connector 创建「在线表格/微盘」，写入 11 行（格号/列/标题/结论/原话溯源/置信度/状态）
  push_doc  -> 调 wecom connector 创建「企业微信文档」并写入报告 markdown
"""
from __future__ import annotations

from typing import Dict

from _common import PushResult

PLATFORM = "wecom"
DISPLAY = "企业微信"


def detect(status_map: Dict[str, str]) -> str:
    st = status_map.get(PLATFORM, "disconnected")
    return "available" if st == "connected" else "installed_not_auth"


def push_base(bundle, target: str = "personal") -> PushResult:
    return PushResult(
        PLATFORM, "base", False,
        error="本环境未接入企业微信推送适配器。请连接 wecom connector 后启用；矩阵见 references/collab_delivery.md。",
    )


def push_doc(bundle, target: str = "personal") -> PushResult:
    return PushResult(
        PLATFORM, "doc", False,
        error="本环境未接入企业微信推送适配器。请连接 wecom connector 后启用。",
    )
