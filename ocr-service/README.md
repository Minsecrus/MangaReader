# OCR Service 安装和测试指南

## 安装步骤

### 1. 安装 Python 依赖

```bash
cd ocr-service

# 方式1: 使用本地 whl 文件
pip install C:\Users\32103\Downloads\manga_ocr-0.1.14-py3-none-any.whl

# 方式2: 从 PyPI 安装 (如果可用)
pip install -r requirements.txt
```

### 2. 测试 Python 服务

```bash
# 启动服务
python ocr_service.py
```

等待看到以下输出:
```
[OCR Service] Starting OCR service...
[OCR Service] Loading manga-ocr model...
[OCR Service] Model loaded successfully!
{"status":"ready"}
[OCR Service] OCR service is ready, waiting for requests...
```

**首次运行**会下载模型文件(约 400MB),请耐心等待。

### 3. 手动测试识别

在看到 `{"status":"ready"}` 后,输入测试命令:

```json
{"command":"ping"}
```

应该返回:
```json
{"success":true,"message":"pong"}
```

### 4. 测试 OCR 识别

创建测试脚本 `test_ocr.py`:

```python
import base64
import json

# 读取测试图片
with open('test_image.png', 'rb') as f:
    image_data = f.read()
    image_base64 = base64.b64encode(image_data).decode()

# 构造请求
request = {
    "id": 1,
    "command": "recognize",
    "image": image_base64
}

print(json.dumps(request))
```

运行:
```bash
python test_ocr.py | python ocr_service.py
```

## 完整开发流程

### 1. 启动 Nuxt 开发服务器
```bash
npm run dev
```

### 2. 启动 Electron (会自动启动 OCR 服务)
```bash
npm run start
```

### 3. 使用 OCR 功能
1. 上传或导入漫画图片
2. 点击 "OCR识别" 按钮
3. 鼠标变为十字,拖动框选识别区域
4. 松开鼠标,等待识别完成
5. 识别结果会显示在"原文"区域

## 常见问题

### 1. `ImportError: DLL load failed while importing fugashi`
- 原因: Python 来自 Microsoft Store
- 解决: 从 [python.org](https://www.python.org/downloads/) 重新安装 Python

### 2. 首次识别很慢
- 原因: 需要下载模型文件(约 400MB)
- 解决: 耐心等待,下载完成后会自动缓存

### 3. OCR 服务启动失败
- 检查 Python 版本: `python --version` (需要 3.6+)
- 检查依赖安装: `pip list | grep manga-ocr`
- 查看错误日志: Electron 控制台会显示详细错误

### 4. 识别结果不准确
- manga-ocr 专门针对日文漫画优化
- 对于长文本,可以尝试分段识别
- 确保选中区域包含清晰的文字

## 性能优化建议

1. **首次启动**: OCR 服务启动需要加载模型,约 5-10 秒
2. **识别速度**: 每次识别约 1-3 秒(取决于图片大小)
3. **内存占用**: 模型加载后约占用 500MB-1GB 内存

## 下一步: 打包

打包步骤参考 `docs/packaging.md` (待创建)
