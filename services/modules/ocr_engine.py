# services/modules/ocr_engine.py
import os
import base64
from io import BytesIO
from PIL import Image
from manga_ocr import MangaOcr
from .utils import log_message


class OCREngine:
    def __init__(self, model_dir=None):
        self.mocr = None
        self._load_model(model_dir)

    def _check_integrity(self, model_path):
        """检查模型完整性"""
        required_files = ["config.json", "vocab.txt"]  # 简化检查，关键文件在就行
        for f in required_files:
            if not os.path.exists(os.path.join(model_path, f)):
                return False
        return os.path.exists(
            os.path.join(model_path, "model.safetensors")
        ) or os.path.exists(os.path.join(model_path, "pytorch_model.bin"))

    def _load_model(self, model_dir):
        # 1. 尝试本地加载
        if model_dir and os.path.exists(model_dir):
            log_message(f"Checking local OCR model at: {model_dir}")
            if self._check_integrity(model_dir):
                try:
                    self.mocr = MangaOcr(pretrained_model_name_or_path=model_dir)
                    log_message("✅ OCR Engine loaded (Offline Mode).")
                    return
                except Exception as e:
                    log_message(f"⚠️ Local load failed: {e}")
            else:
                log_message("❗ Local model incomplete. Switching to Online Mode.")

        # 2. 在线加载 (HuggingFace)
        log_message("🌐 Loading OCR model from HuggingFace...")
        self.mocr = MangaOcr()  # 默认下载
        log_message("✅ OCR Engine loaded (Online Mode).")

    def recognize(self, image_base64):
        """执行 OCR"""
        if not self.mocr:
            raise Exception("OCR Model not initialized")

        # 处理 Base64
        if "," in image_base64:
            image_base64 = image_base64.split(",", 1)[1]

        image_data = base64.b64decode(image_base64)
        img = Image.open(BytesIO(image_data))

        return self.mocr(img)
