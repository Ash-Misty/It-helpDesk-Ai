from typing import Tuple, Optional


class ModelLoader:
    _instance: Optional["ModelLoader"] = None
    _model = None
    _tokenizer = None
    _loaded = False
    _load_error = None
    _model_name = "Qwen/Qwen2.5-1.5B-Instruct"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self) -> Tuple[None, None]:
        if self._loaded:
            return self._model, self._tokenizer

        if self._load_error is not None:
            return None, None

        self._loaded = True
        return None, None

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    @property
    def load_error(self) -> Optional[str]:
        return self._load_error

    @property
    def current_model_name(self) -> str:
        return self._model_name

    @property
    def using_fallback(self) -> bool:
        return False


model_loader = ModelLoader()
