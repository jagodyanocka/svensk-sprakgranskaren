import json
from enum import Enum
from pathlib import Path

TRANSLATIONS_DIR = Path(__file__).parent.parent / "translations"


class Translator:
    def __init__(self, language: str):
        self.language = language
        self.translations = self._load_translations()

    def _load_translations(self) -> dict[str, str]:
        path = TRANSLATIONS_DIR / f"{self.language}.json"

        with path.open(encoding="utf-8") as file:
            return json.load(file)

    def get(self, key: str) -> str:
        return self.translations[key]

class Language(str, Enum):
    Polish= "pl"
    Swedish = "sv"
    English = "en"