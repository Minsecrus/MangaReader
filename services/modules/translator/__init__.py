# services/modules/translator/__init__.py
from .sakura_engine import SakuraEngine


def get_translator_engine(engine_name, model_root_dir):
    # 现在我们只支持 sakura
    if engine_name == "sakura":
        return SakuraEngine(model_root_dir)
    else:
        raise ValueError(f"Unknown engine: {engine_name}")
