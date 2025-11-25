# services/modules/tokenizer.py
from sudachipy import dictionary, SplitMode
from .utils import log_message


class JapaneseTokenizer:
    # 静态配置：词性映射
    POS_MAPPING = {
        "名詞": "noun",
        "代名詞": "noun",
        "動詞": "verb",
        "形容詞": "adjective",
        "形状詞": "adjective",
        "副詞": "adverb",
        "助詞": "particle",
        "助動詞": "particle",
        "感動詞": "other",
        "接頭辞": "other",
        "接尾辞": "other",
        "記号": "other",
    }

    def __init__(self):
        self.tokenizer = None
        self.mode = SplitMode.C
        try:
            log_message("Initializing Sudachi Tokenizer...")
            self.tokenizer = dictionary.Dictionary(dict="core").create()
            log_message("✅ Tokenizer Initialized.")
        except Exception as e:
            log_message(f"❌ Tokenizer Init Failed: {e}")
            self.tokenizer = None
            self.init_error = str(e)

    def tokenize(self, text):
        if not self.tokenizer:
            raise Exception(
                f"Tokenizer not ready: {getattr(self, 'init_error', 'Unknown Error')}"
            )

        results = self.tokenizer.tokenize(text, self.mode)
        tokens = []

        for t in results:
            pos_list = t.part_of_speech()
            main_pos = pos_list[0]
            frontend_type = self.POS_MAPPING.get(main_pos, "other")
            tokens.append(
                {
                    "word": t.surface(),
                    "type": frontend_type,
                    # 未来可以在这里加: "reading": t.reading_form(), "dictionary_form": t.dictionary_form()
                }
            )

        return tokens
