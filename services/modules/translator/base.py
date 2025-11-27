from abc import ABC, abstractmethod


class BaseTranslator(ABC):
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.is_ready = False

    @abstractmethod
    def initialize(self):
        """初始化/加载模型"""
        pass

    @abstractmethod
    def translate(self, text):
        """执行翻译"""
        pass

    @abstractmethod
    def download_model(self, progress_callback=None):
        """下载模型文件"""
        pass
