import subprocess
import json
import sys
import os
import time

def test_backend():
    # 1. 确定后端路径
    backend_path = os.path.abspath("dist/backend/backend.exe")
    if not os.path.exists(backend_path):
        print(f"Error: Backend not found at {backend_path}")
        return

    print(f"Starting backend: {backend_path}")
    
    # 2. 启动进程
    # 注意：必须传入 --model-dir，否则后端会报错退出
    model_dir = os.path.abspath("models/ocr")
    process = subprocess.Popen(
        [backend_path, "--model-dir", model_dir],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        bufsize=1  # Line buffered
    )

    # 3. 读取初始化消息
    print("--- Initialization Logs ---")
    while True:
        line = process.stdout.readline()
        if not line:
            break
        try:
            data = json.loads(line)
            print(f"Received: {line.strip()}")
            if data.get("status") == "ready":
                print("Backend is READY!")
                break
        except json.JSONDecodeError:
            print(f"Raw Output: {line.strip()}")

    # 4. 发送分词测试命令
    test_text = "日本語のテストです。"
    print(f"\n--- Sending Tokenize Request: '{test_text}' ---")
    
    req = {
        "id": "test-1",
        "command": "tokenize",
        "text": test_text
    }
    
    process.stdin.write(json.dumps(req) + "\n")
    process.stdin.flush()

    # 5. 读取响应
    while True:
        line = process.stdout.readline()
        if not line:
            break
        try:
            data = json.loads(line)
            # 过滤掉非响应消息 (如日志)
            if data.get("id") == "test-1":
                print("\n--- Tokenize Result ---")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                # 检查是否乱码
                tokens = data.get("tokens", [])
                if tokens and all(t["word"] == "?" for t in tokens):
                     print("\n[FAIL] Tokens appear to be garbled (????)")
                else:
                     print("\n[PASS] Tokens look valid.")
                break
            else:
                print(f"Ignored: {line.strip()}")
        except json.JSONDecodeError:
            print(f"Raw: {line.strip()}")

    # 6. 清理
    process.terminate()

if __name__ == "__main__":
    test_backend()
