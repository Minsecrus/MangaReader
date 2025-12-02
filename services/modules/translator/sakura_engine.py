# services/modules/translator/sakura_engine.py
import os
import threading
import shutil
import sys
import json
import contextlib
from .base import BaseTranslator
from huggingface_hub import hf_hub_download
from ..utils import log_message

import tqdm

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None


# 直接 Monkey Patch tqdm.tqdm 类的方法
# 这样无论 huggingface_hub 如何引用 tqdm，都会使用我们修改后的方法
_original_init = tqdm.tqdm.__init__
_original_update = tqdm.tqdm.update


def _patched_init(self, *args, **kwargs):
    # 1. 强制开启进度条
    kwargs["disable"] = False
    # 2. 将原始的视觉进度条重定向到空设备 (devnull)
    # 这样控制台就不会出现 ████▌ 这种字符，避免干扰 JSON 解析
    kwargs["file"] = open(os.devnull, "w")

    _original_init(self, *args, **kwargs)

    # 初始化自定义状态
    self.last_percent = -1


def _patched_update(self, n=1):
    # 调用原始 update 更新内部计数器
    _original_update(self, n)

    # 计算百分比并输出 JSON
    if self.total and self.total > 0:
        percent = (self.n / self.total) * 100

        # 过滤频率：每 0.5% 发送一次
        if int(percent * 2) > getattr(self, "last_percent", -1):
            self.last_percent = int(percent * 2)

            msg = {
                "type": "download_progress",
                "percent": round(percent, 1),
                "filename": self.desc or "model",
            }
            # 3. 显式写入 stdout 并 flush，确保 Electron 能立即收到
            sys.stdout.write(json.dumps(msg) + "\n")
            sys.stdout.flush()


@contextlib.contextmanager
def patch_tqdm():
    """
    上下文管理器：在代码块执行期间，替换 tqdm 的行为
    """
    # 替换方法
    tqdm.tqdm.__init__ = _patched_init
    tqdm.tqdm.update = _patched_update

    try:
        yield
    finally:
        # 还原方法，避免影响其他模块
        tqdm.tqdm.__init__ = _original_init
        tqdm.tqdm.update = _original_update


class SakuraEngine(BaseTranslator):
    def __init__(self, model_root_dir):
        path = os.path.join(model_root_dir, "sakura")
        super().__init__(path)

        self.repo_id = "shing3232/Sakura-1.5B-Qwen2.5-v1.0-GGUF-IMX"
        self.filename = "sakura-1.5b-qwen2.5-v1.0-Q5KS.gguf"

        # 为了更准确的判断，我们这里还是用 .gguf 结尾的文件路径
        self.model_file_path = os.path.join(self.model_dir, self.filename)

        self.llm = None
        self.lock = threading.Lock()

    def check_model_exists(self):
        # 检查物理文件是否存在
        # 注意：使用 hf_hub_download 后，实际文件可能是一个 symlink 指向 .cache
        # 但 os.path.exists 会自动追踪 symlink，所以逻辑是通用的
        path = self.model_file_path
        exists = os.path.exists(path)
        log_message(f"🔍 [Check] Path: {path}")
        log_message(f"🔍 [Check] Exists: {exists}")
        return exists

    def delete_model(self):
        # 1. 释放内存
        if self.llm:
            log_message("🔄 Unloading model...")
            try:
                del self.llm
                self.llm = None
                self.is_ready = False
            except:
                pass

        deleted = False

        # 2. 删除主文件 (如果是 symlink 会删掉 symlink，如果是实体文件删实体)
        if os.path.exists(self.model_file_path):
            try:
                os.remove(self.model_file_path)
                log_message(f"🗑️ Deleted model link/file: {self.filename}")
                deleted = True
            except Exception as e:
                log_message(f"❌ Failed to delete model file: {e}")

        # 3. ✅ 关键：清理 .cache 缓存
        # HuggingFace 的默认缓存结构通常在 models/translation/sakura/.cache
        # 我们把它整个干掉，这样才是真的“卸载”
        cache_dir = os.path.join(self.model_dir, ".cache")
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                log_message("🧹 Cleaned up HuggingFace cache directory.")
                deleted = True
            except Exception as e:
                log_message(f"⚠️ Failed to clean cache: {e}")

        return deleted

    def download_model(self, progress_callback=None):
        log_message(f"⬇️ Downloading SakuraLLM via HuggingFace Hub...")
        log_message(f"   Repo: {self.repo_id}")

        try:
            # ✅ 使用上下文管理器，只在下载期间开启“间谍模式”
            with patch_tqdm():
                file_path = hf_hub_download(
                    repo_id=self.repo_id,
                    filename=self.filename,
                    local_dir=self.model_dir,
                    # 不再需要 local_dir_use_symlinks=False，
                    # 现在的版本默认行为很智能，保留缓存机制更好
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
                return output["choices"][0]["text"].strip()
            except Exception as e:
                log_message(f"Sakura output error: {e}")
                return text
