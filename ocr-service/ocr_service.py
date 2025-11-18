#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manga OCR Service
接收来自 Electron 主进程的图片数据，使用 manga-ocr 进行识别，返回识别结果
"""

import sys
import json
import base64
from io import BytesIO
from PIL import Image
from manga_ocr import MangaOcr


def log_message(message):
    """输出日志到 stderr，避免干扰 stdout 的 JSON 通信"""
    print(f"[OCR Service] {message}", file=sys.stderr, flush=True)


def send_response(response):
    """发送 JSON 响应到 stdout"""
    print(json.dumps(response, ensure_ascii=False), flush=True)


def main():
    # 确保使用 UTF-8 编码
    import io
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    
    log_message("Starting OCR service...")

    try:
        # 初始化 MangaOCR
        # 首次运行会下载模型（约 400MB），可能需要几分钟
        log_message("Loading manga-ocr model...")
        mocr = MangaOcr()
        log_message("Model loaded successfully!")

        # 发送就绪信号
        send_response({"status": "ready"})

    except Exception as e:
        log_message(f"Failed to initialize OCR: {str(e)}")
        send_response({"status": "error", "message": str(e)})
        sys.exit(1)

    # 主循环：持续监听 stdin
    log_message("OCR service is ready, waiting for requests...")

    for line in sys.stdin:
        try:
            line = line.strip()
            if not line:
                continue

            request = json.loads(line)
            command = request.get("command")

            if command == "recognize":
                # OCR 识别命令
                request_id = request.get("id")
                log_message(f"Received OCR request (id: {request_id})")

                # 解码 base64 图片
                image_base64 = request.get("image", "")
                if not image_base64:
                    send_response({
                        "id": request_id,
                        "success": False, 
                        "error": "No image data provided"
                    })
                    continue

                # 移除 data:image/png;base64, 前缀（如果有）
                if "," in image_base64:
                    image_base64 = image_base64.split(",", 1)[1]

                image_data = base64.b64decode(image_base64)
                img = Image.open(BytesIO(image_data))

                log_message(f"Image size: {img.size}")

                # 执行 OCR 识别
                log_message("Running OCR recognition...")
                text = mocr(img)
                log_message(f"Recognition result: {text}")

                # 返回结果 (必须包含 id)
                send_response({
                    "id": request_id,
                    "success": True, 
                    "text": text
                })

            elif command == "ping":
                # 健康检查
                send_response({"success": True, "message": "pong"})

            elif command == "exit":
                # 退出命令
                log_message("Received exit command")
                send_response({"success": True, "message": "exiting"})
                sys.exit(0)

            else:
                send_response(
                    {"success": False, "error": f"Unknown command: {command}"}
                )

        except json.JSONDecodeError as e:
            log_message(f"JSON decode error: {str(e)}")
            send_response({"success": False, "error": f"Invalid JSON: {str(e)}"})

        except Exception as e:
            log_message(f"Error processing request: {str(e)}")
            send_response({"success": False, "error": str(e)})


if __name__ == "__main__":
    main()
