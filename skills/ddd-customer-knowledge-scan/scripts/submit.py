#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""企业顾客与知识现状感知扫描 - 答案提交脚本（零第三方依赖，仅用标准库）

用法：
    python3 submit.py '<answers_json>'
    python3 submit.py --file /path/to/answers.json
    python3 submit.py --retry            # 重发本地暂存的未成功答卷

answers_json 结构（由 Skill 组装）：
{
  "choices": {"R1":"部分符合", ..., "K4":"部分清楚"},
  "open": {"Q1":"...", "Q2":"..."}
}
token 由本脚本自动附加，Skill 无需处理；后端已不再要求 session 字段。
提交失败时自动把答卷暂存到 ~/.customer_knowledge_scan_pending/，可用 --retry 重发。
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

# ==== 固定配置（部署后由维护者更新，参与者无需改动）====
API_URL = "https://backend.appmiaoda.com/projects/supabase340058401981640704/functions/v1/api-answers"
TOKEN = "gfqz-scan-2026"
# =====================================================

PENDING_DIR = os.path.expanduser("~/.customer_knowledge_scan_pending")

REQUIRED_CHOICES = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8", "K1", "K2", "K4"]
VALID_OPTIONS = {
    "R1": ["符合", "部分符合", "完全符合"],
    "R2": ["不清楚", "部分清楚", "完全清楚"],
    "R3": ["不清楚", "部分清楚", "很清楚"],
    "R4": ["不符合", "部分符合", "完全符合"],
    "R5": ["没意识到", "部分意识到", "完全意识到"],
    "R6": ["不重视", "偶尔重视", "十分重视"],
    "R7": ["不清楚", "部分清楚", "很清楚"],
    "R8": ["没有做到", "偶尔做到", "做得很好"],
    "K1": ["没意识到", "部分意识到", "完全意识到"],
    "K2": ["没更新", "偶尔更新", "持续更新"],
    "K4": ["不清楚", "部分清楚", "很清楚"],
}


def validate(payload):
    errs = []
    choices = payload.get("choices") or {}
    for qid in REQUIRED_CHOICES:
        v = choices.get(qid)
        if not v:
            errs.append("缺少选择题 %s 的答案" % qid)
        elif v not in VALID_OPTIONS[qid]:
            errs.append("%s 的答案「%s」不在合法选项 %s 中" % (qid, v, "/".join(VALID_OPTIONS[qid])))
    open_a = payload.get("open") or {}
    for qid in ["Q1", "Q2"]:
        if not (open_a.get(qid) or "").strip():
            errs.append("缺少开放题 %s 的回答" % qid)
    return errs


def post(payload, timeout=15, retries=3):
    body = dict(payload)
    body["token"] = TOKEN
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(
                API_URL, data=data,
                headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                text = resp.read().decode("utf-8", "replace")
                try:
                    j = json.loads(text)
                except ValueError:
                    j = {"raw": text[:500]}
                if resp.status in (200, 201) and j.get("success") is not False:
                    return True, j
                last_err = "HTTP %s: %s" % (resp.status, text[:300])
        except urllib.error.HTTPError as e:
            last_err = "HTTP %s: %s" % (e.code, e.read().decode("utf-8", "replace")[:300])
            if e.code in (400, 401, 403):  # 客户端错误不重试
                break
        except Exception as e:
            last_err = "%s: %s" % (type(e).__name__, e)
        if attempt < retries:
            time.sleep(2 * attempt)
    return False, {"error": last_err}


def save_pending(payload):
    os.makedirs(PENDING_DIR, exist_ok=True)
    fn = os.path.join(PENDING_DIR, "answers_%d.json" % int(time.time()))
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    return fn


def retry_pending():
    if not os.path.isdir(PENDING_DIR):
        print(json.dumps({"success": True, "message": "没有待重发的答卷"}, ensure_ascii=False))
        return 0
    files = sorted(f for f in os.listdir(PENDING_DIR) if f.endswith(".json"))
    if not files:
        print(json.dumps({"success": True, "message": "没有待重发的答卷"}, ensure_ascii=False))
        return 0
    ok_n, fail_n = 0, 0
    for fn in files:
        path = os.path.join(PENDING_DIR, fn)
        with open(path, encoding="utf-8") as f:
            payload = json.load(f)
        ok, resp = post(payload)
        if ok:
            os.remove(path)
            ok_n += 1
        else:
            fail_n += 1
    print(json.dumps({"success": fail_n == 0, "resent": ok_n, "still_pending": fail_n},
                     ensure_ascii=False))
    return 0 if fail_n == 0 else 1


def main():
    if "__MIAODA_API_URL__" in API_URL:
        print(json.dumps({"success": False,
                          "error": "API_URL 尚未配置，请联系 Skill 维护者"}, ensure_ascii=False))
        return 2
    args = sys.argv[1:]
    if args and args[0] == "--retry":
        return retry_pending()
    if args and args[0] == "--file":
        with open(args[1], encoding="utf-8") as f:
            payload = json.load(f)
    elif args:
        payload = json.loads(args[0])
    else:
        payload = json.load(sys.stdin)

    errs = validate(payload)
    if errs:
        print(json.dumps({"success": False, "error": "校验失败", "details": errs},
                         ensure_ascii=False))
        return 1

    ok, resp = post(payload)
    if ok:
        print(json.dumps({"success": True, "server": resp}, ensure_ascii=False))
        return 0
    else:
        fn = save_pending(payload)
        print(json.dumps({"success": False, "error": resp.get("error", "未知错误"),
                          "pending_file": fn,
                          "hint": "答卷已暂存，网络恢复后运行 submit.py --retry 重发"},
                         ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
