# services/backend_service.py
import sys
import json
import argparse
import io

# 解决 Windows 下编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)

# 引入我们写好的模块
from modules.utils import log_message, send_response
from modules.ocr_engine import OCREngine
from modules.tokenizer import JapaneseTokenizer


def main():
    log_message("Starting Backend Service...")

    # 1. 解析参数
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str, help="Path to OCR model")
    args, _ = parser.parse_known_args()

    # 2. 初始化各模块
    # 注意：如果模块加载很慢，这会阻塞启动。目前逻辑是启动时加载。
    # 如果未来想秒开，可以把初始化放在第一次调用时 (Lazy Load)。
    ocr_engine = OCREngine(model_dir=args.model_dir)
    tokenizer = JapaneseTokenizer()

    # 3. 告诉 Electron 我们准备好了
    send_response({"status": "ready"})
    log_message("Waiting for commands...")

    # 4. 消息循环
    for line in sys.stdin:
        try:
            line = line.strip()
            if not line:
                continue

            request = json.loads(line)
            req_id = request.get("id")
            command = request.get("command")

            # === 路由分发 ===

            # -> OCR 任务
            if command == "recognize":
                try:
                    text = ocr_engine.recognize(request.get("image", ""))
                    send_response({"id": req_id, "success": True, "text": text})
                except Exception as e:
                    send_response({"id": req_id, "success": False, "error": str(e)})

            # -> 分词任务
            elif command == "tokenize":
                try:
                    tokens = tokenizer.tokenize(request.get("text", ""))
                    send_response({"id": req_id, "success": True, "tokens": tokens})
                except Exception as e:
                    send_response({"id": req_id, "success": False, "error": str(e)})

            # -> 未来：翻译任务
            # elif command == "translate":
            #     result = translator.translate(...)
            #     send_response(...)

            elif command == "ping":
                send_response({"success": True, "message": "pong"})

            elif command == "exit":
                sys.exit(0)

        except json.JSONDecodeError:
            log_message("Received invalid JSON")
        except Exception as e:
            log_message(f"Critical Loop Error: {e}")


if __name__ == "__main__":
    main()
