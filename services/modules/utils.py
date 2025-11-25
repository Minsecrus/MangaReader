# services/modules/utils.py
import sys
import json


def log_message(message):
    """输出日志到 stderr (Electron console 会显示)"""
    print(f"[Backend Service] {message}", file=sys.stderr, flush=True)


def send_response(response):
    """发送 JSON 响应到 stdout (Electron 通过 stdio 接收)"""
    print(json.dumps(response, ensure_ascii=False), flush=True)
