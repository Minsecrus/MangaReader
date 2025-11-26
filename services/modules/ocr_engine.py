# services/modules/ocr_engine.py
import os
import base64
from io import BytesIO
from PIL import Image
from manga_ocr import MangaOcr
from huggingface_hub import snapshot_download
from .utils import log_message


class OCREngine:
    def __init__(self, model_dir=None):
        self.mocr = None
        # 如果没有传入路径，抛出错误，因为我们现在的策略是必须指定路径
        if not model_dir:
            raise ValueError("Model directory is required for cleaner deployment.")

        self.model_dir = model_dir
        self._load_model()

    def _check_integrity(self):
        """检查本地模型文件是否完整"""
        if not os.path.exists(self.model_dir):
            return False

        # 关键文件列表
        required_files = [
            "config.json",
            "preprocessor_config.json",
            "tokenizer_config.json",
            "vocab.txt",
        ]

        # 1. 检查小文件
        for f in required_files:
            if not os.path.exists(os.path.join(self.model_dir, f)):
                log_message(f"Missing file: {f}")
                return False

        # 2. 检查大权重文件 (safetensors 是新标准，bin 是旧标准，兼容一下)
        has_safetensors = os.path.exists(
            os.path.join(self.model_dir, "model.safetensors")
        )
        has_bin = os.path.exists(os.path.join(self.model_dir, "pytorch_model.bin"))

        if not (has_safetensors or has_bin):
            log_message(
                "Missing model weights (model.safetensors or pytorch_model.bin)"
            )
            return False

        return True

    def _load_model(self):
        # 1. 检查本地是否存在且完整
        if self._check_integrity():
            log_message(f"✅ Found valid model at: {self.model_dir}")
        else:
            # 2. 本地不完整，执行定向下载
            log_message(
                f"⬇️ Model missing or incomplete. Downloading to {self.model_dir}..."
            )
            log_message("⏳ This may take a while (approx 400MB)...")

            try:
                # 使用 snapshot_download 直接下载到指定文件夹
                # 这会避免使用系统缓存，直接把文件放进 App 的 models/ocr 目录
                snapshot_download(
                    repo_id="kha-white/manga-ocr-base",
                    local_dir=self.model_dir,
                    local_dir_use_symlinks=False,  # 关键：不使用软链接，确保是真实文件
                )
                log_message("✅ Download complete!")
            except Exception as e:
                log_message(f"❌ Download failed: {e}")
                raise e

        # 3. 加载模型 (此时文件一定在本地了)
        log_message("🚀 Loading OCR Engine from local storage...")
        try:
            # 强制指定 path，MangaOcr 就会直接读文件，不再联网也不读缓存
            self.mocr = MangaOcr(pretrained_model_name_or_path=self.model_dir)
            log_message("✅ OCR Engine initialized successfully.")
        except Exception as e:
            log_message(f"❌ Failed to load model: {e}")
            raise e

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
