"""_common.py — 协作分发层公共定义。

平台特有关系放在各 adapter；本文件只放跨平台通用件（平台清单、结果对象、探测辅助、动态加载）。
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


# 平台标识（与 references/collab_delivery.md 的矩阵 key 一致）
PLATFORMS = ["feishu", "dingtalk", "wecom"]


@dataclass
class PushResult:
    """统一的推送返回对象，供 SKILL.md ⑧ 统一展示。"""

    platform: str
    kind: str            # "base" | "doc"
    ok: bool
    url: Optional[str] = None
    error: Optional[str] = None
    note: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "platform": self.platform,
            "kind": self.kind,
            "ok": self.ok,
            "url": self.url,
            "error": self.error,
            "note": self.note,
        }


def detect_status_map() -> Dict[str, str]:
    """从环境变量读取会话级 connector 状态（由 SKILL.md ⑧ 在运行前注入）。

    值：connected / disconnected。缺省全 disconnected。
    """
    raw = os.environ.get("WORKBUDDY_CONNECTOR_STATUS", "")
    m = {p: "disconnected" for p in PLATFORMS}
    if raw:
        try:
            data = json.loads(raw)
            for p in PLATFORMS:
                if data.get(p) in ("connected", "disconnected"):
                    m[p] = data[p]
        except Exception:
            pass
    return m


def run(cmd: List[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def load_adapter(platform: str, adapters_dir: Path):
    """按平台名从文件动态加载 adapter 模块（不依赖包名，避免 import 路径问题）。"""
    fp = adapters_dir / f"{platform}.py"
    if not fp.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"adapters_{platform}", fp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
