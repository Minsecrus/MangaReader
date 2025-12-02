# services/backend_service.py
import sys
import json
import argparse
import io
import os

# 解决 Windows 下编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)

# 引入我们写好的模块
from modules.utils import log_message, send_response
from modules.ocr_engine import OCREngine
from modules.tokenizer import JapaneseTokenizer

# 引入 Sakura 工厂
from modules.translator import get_translator_engine


def main():
    log_message("Starting Backend Service...")

    # 发送状态 启动中
    send_response({"type": "init_status", "message": "正在启动后台服务..."})

    # 1. 解析参数
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str, help="Path to OCR model")
    args, _ = parser.parse_known_args()

    models_root = os.path.dirname(args.model_dir)
    translation_root = os.path.join(models_root, "translation")

    if not os.path.exists(translation_root):
        os.makedirs(translation_root, exist_ok=True)

    # 初始化OCR
    send_response(
        {
            "type": "init_status",
            "message": "正在加载 OCR 引擎 (首次运行可能需要下载模型)...",
        }
    )
    ocr_engine = OCREngine(model_dir=args.model_dir)

    # 初始化分词器
    send_response({"type": "init_status", "message": "正在加载日语分词组件..."})
    tokenizer = JapaneseTokenizer()

    # 初始化翻译模块
    send_response({"type": "init_status", "message": "正在配置翻译模块..."})
    log_message(f"Init Translator (Sakura) root: {translation_root}")
    # 强制指定使用 sakura
    translator = get_translator_engine("sakura", translation_root)
    # 尝试加载 (如果没下载，这里会失败，但在 translate 命令里会触发下载)
    translator.initialize()

    # 准备就绪
    send_response({"type": "init_status", "message": "资源加载完毕，即将进入..."})
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

            # --- Translate ---
            elif command == "translate":
                try:
                    text = request.get("text", "")

                    # 1. 检查是否已加载
                    if not translator.is_ready:
                        # 2. 检查物理文件是否存在
                        if translator.check_model_exists():
                            # 存在则加载
                            translator.initialize()
                        else:
                            raise Exception("MODEL_NOT_FOUND")

                    # 3. 执行翻译
                    result = translator.translate(text)
                    send_response(
                        {"id": req_id, "success": True, "translation": result}
                    )

                except Exception as e:
                    # 捕获错误 (包括上面的 MODEL_NOT_FOUND)
                    log_message(f"Translation Error: {e}")
                    send_response({"id": req_id, "success": False, "error": str(e)})

            # --- Model Management (New) ---

            # 1. 检查模型状态
            elif command == "check_model":
                exists = translator.check_model_exists()
                send_response({"id": req_id, "success": True, "exists": exists})

            # 2. 下载模型
            elif command == "download_model":
                try:
                    translator.download_model()
                    # 下载完顺便初始化一下，确保可用
                    translator.initialize()
                    send_response({"id": req_id, "success": True})
                except Exception as e:
                    send_response({"id": req_id, "success": False, "error": str(e)})

            # 3. 删除模型
            elif command == "delete_model":
                success = translator.delete_model()
                send_response({"id": req_id, "success": success})

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
