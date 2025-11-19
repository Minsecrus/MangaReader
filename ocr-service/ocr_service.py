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

    try:
        # 获取脚本所在目录
        if getattr(sys, "frozen", False):
            # 如果打包成了单文件 exe (PyInstaller)
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))

        # 本地模型路径
        local_model_path = os.path.join(script_dir, "ocr-model")

        mocr = None

        # 1. 尝试加载本地模型
        if check_local_model_integrity(local_model_path):
            log_message(f"✅ Found valid local model at: {local_model_path}")
            log_message("Loading local model (Offline Mode)...")
            try:
                mocr = MangaOcr(pretrained_model_name_or_path=local_model_path)
            except Exception as e:
                log_message(f"⚠️ Failed to load local model despite files existing: {e}")
                log_message("Falling back to online mode...")
        else:
            log_message(f"❗ Local model not found or incomplete at: {local_model_path}")

        # 2. 如果本地加载失败或不存在，尝试在线加载
        if mocr is None:
            log_message("🌐 Connecting to HuggingFace (Online Mode)...")
            log_message(
                "NOTE: First run will download the model (400MB+). Please wait."
            )
            # 不传参，默认使用 kha-white/manga-ocr-base 并自动下载/缓存
            mocr = MangaOcr()

        log_message("✅ Model loaded successfully!")
        send_response({"status": "ready"})

    except Exception as e:
        log_message(f"❌ CRITICAL ERROR: {str(e)}")
        send_response({"status": "error", "message": str(e)})
        sys.exit(1)

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
