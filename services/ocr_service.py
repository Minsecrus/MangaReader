#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manga OCR Service (Hybrid Mode)
自动检测：优先加载本地模型，如果本地没有，则在线下载/加载
"""

import sys
import json
import base64
import os
import argparse
from io import BytesIO
from PIL import Image
from manga_ocr import MangaOcr

# 增加 stdout 的缓冲设置，防止打印进度条时卡住
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)


def log_message(message):
    """输出日志到 stderr"""
    print(f"[OCR Service] {message}", file=sys.stderr, flush=True)


def send_response(response):
    """发送 JSON 响应到 stdout"""
    print(json.dumps(response, ensure_ascii=False), flush=True)


def check_local_model_integrity(model_path):
    """检查本地模型文件是否完整"""
    if not os.path.exists(model_path):
        return False

    # 检查必要的配置文件和词表
    required_files = [
        "config.json",
        "special_tokens_map.json",
        "tokenizer_config.json",
        "vocab.txt",  # 或者 spiece.model，视模型而定，manga-ocr通常是vocab.txt
    ]

    for f in required_files:
        if not os.path.exists(os.path.join(model_path, f)):
            log_message(f"Missing file: {f}")
            return False

    # 检查权重文件 (safetensors 或 bin 只要有一个就行)
    has_safetensors = os.path.exists(os.path.join(model_path, "model.safetensors"))
    has_bin = os.path.exists(os.path.join(model_path, "pytorch_model.bin"))

    if not (has_safetensors or has_bin):
        log_message("Missing model weights (model.safetensors or pytorch_model.bin)")
        return False

    return True


def main():
    log_message("Starting OCR service...")

    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str, help="Path to the OCR model directory")
    args, unknown = parser.parse_known_args()

    mocr = None
    local_model_path = args.model_dir  # 获取传入的路径

    # 1. 优先尝试加载传入的本地路径
    if local_model_path:
        log_message(f"Checking model at: {local_model_path}")

        if check_local_model_integrity(local_model_path):
            log_message("✅ Valid local model found. Loading offline mode...")
            try:
                mocr = MangaOcr(pretrained_model_name_or_path=local_model_path)
            except Exception as e:
                log_message(f"⚠️ Load failed: {e}")
        else:
            log_message(
                "❗ Local model not found or incomplete. (Will use online mode)"
            )
    else:
        log_message("⚠️ No model path provided.")

    # 2. 如果本地加载失败，走在线模式 (默认下载到 C盘 .cache)
    if mocr is None:
        log_message("🌐 Connecting to HuggingFace (Online Mode)...")
        # 可以在这里指定 cache_dir 也可以默认
        mocr = MangaOcr()

    log_message("✅ Model loaded successfully!")
    send_response({"status": "ready"})

    # --- 下面保持原有逻辑不变 ---
    log_message("Waiting for requests...")

    for line in sys.stdin:
        try:
            line = line.strip()
            if not line:
                continue

            request = json.loads(line)
            command = request.get("command")

            if command == "recognize":
                request_id = request.get("id")
                log_message(f"Processing request {request_id}")

                image_base64 = request.get("image", "")
                if "," in image_base64:
                    image_base64 = image_base64.split(",", 1)[1]

                image_data = base64.b64decode(image_base64)
                img = Image.open(BytesIO(image_data))

                text = mocr(img)
                log_message(f"Result: {text}")
                send_response({"id": request_id, "success": True, "text": text})

            elif command == "ping":
                send_response({"success": True, "message": "pong"})

            elif command == "exit":
                sys.exit(0)

        except Exception as e:
            # 捕获所有处理过程中的错误，防止进程退出
            error_msg = str(e)
            log_message(f"Error: {error_msg}")
            # 如果能解析出ID，尽量发回报错信息
            try:
                req_id = json.loads(line).get("id")
                if req_id is not None:
                    send_response({"id": req_id, "success": False, "error": error_msg})
            except:
                pass


if __name__ == "__main__":
    main()
