# services/modules/translator/sakura_engine.py
import os
import threading
from .base import BaseTranslator
from huggingface_hub import hf_hub_download
from ..utils import log_message
import shutil

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None


class SakuraEngine(BaseTranslator):
    def __init__(self, model_root_dir):
        path = os.path.join(model_root_dir, "sakura")
        super().__init__(path)

        # ✅ 仓库 ID: 社区量化版仓库
        self.repo_id = "shing3232/Sakura-1.5B-Qwen2.5-v1.0-GGUF-IMX"

        # ✅ 文件名: 修正为真实存在的 Q5KS 版本 (1.26 GB)
        self.filename = "sakura-1.5b-qwen2.5-v1.0-Q5KS.gguf"
        self.model_file_path = os.path.join(self.model_dir, self.filename)

        self.llm = None
        self.lock = threading.Lock()

    def check_model_exists(self):
        path = self.model_file_path
        exists = os.path.exists(path)

        log_message(f"🔍 [Check] Path: {path}")
        log_message(f"🔍 [Check] Exists: {exists}")

        return exists

    def delete_model(self):
        # 1. 尝试释放内存
        if self.llm:
            log_message("🔄 Unloading model from memory...")
            try:
                del self.llm
                self.llm = None
                self.is_ready = False
            except:
                pass

        # 2. 删除 .gguf 主模型文件
        deleted_main = False
        if os.path.exists(self.model_file_path):
            try:
                os.remove(self.model_file_path)
                log_message(f"🗑️ Deleted main file: {self.filename}")
                deleted_main = True
            except Exception as e:
                log_message(f"❌ Failed to delete main file: {e}")

        # 3. 彻底清理 .cache 文件夹 (元数据残留)
        # self.model_dir 就是 .../models/translation/sakura
        cache_dir = os.path.join(self.model_dir, ".cache")
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)  # 递归删除文件夹
                log_message("🧹 Cleaned up HuggingFace cache directory.")
            except Exception as e:
                log_message(f"⚠️ Failed to clean cache: {e}")

        return deleted_main

    def download_model(self, progress_callback=None):
        log_message(f"⬇️ Downloading SakuraLLM to: {self.model_dir}")
        log_message(f"   File: {self.filename}")
        try:
            hf_hub_download(
                repo_id=self.repo_id,
                filename=self.filename,
                local_dir=self.model_dir,
                token=False,
            )
            log_message("✅ SakuraLLM download complete.")
            return True
        except Exception as e:
            log_message(f"❌ Download failed: {e}")
            raise e

    def initialize(self):
        if Llama is None:
            log_message("❌ Error: llama-cpp-python not installed.")
            self.is_ready = False
            return

        model_path = self.model_file_path

        if not os.path.exists(model_path):
            log_message(f"⚠️ Initialize failed. Model not found at: {model_path}")
            self.is_ready = False
            return

        try:
            log_message(f"🚀 Loading SakuraLLM (CPU Mode) from: {model_path}")

            self.llm = Llama(
                model_path=model_path, n_ctx=1024, n_threads=4, verbose=False
            )

            self.is_ready = True
            log_message("✅ SakuraLLM Engine loaded.")
        except Exception as e:
            log_message(f"❌ Failed to load Sakura: {e}")
            self.is_ready = False

    def translate(self, text):
        if not self.is_ready or not self.llm:
            raise Exception("Sakura Engine not ready")

        with self.lock:
            # Prompt 格式保持不变
            system_prompt = "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。"

            prompt = (
                f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
                f"<|im_start|>user\n将下面的日文文本翻译成中文：{text}<|im_end|>\n"
                f"<|im_start|>assistant\n"
            )

            output = self.llm(
                prompt,
                max_tokens=512,
                stop=["<|im_end|>", "\n\n"],
                echo=False,
                temperature=0.1,
            )

            try:
                translation = output["choices"][0]["text"].strip()
                return translation
            except Exception as e:
                log_message(f"Sakura output error: {e}")
                return text
