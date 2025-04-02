from typing import Dict
from dataclasses import dataclass
import json
import os
from pathlib import Path

@dataclass
class Language:
    code: str
    name: str
    rtl: bool = False

SUPPORTED_LANGUAGES = {
    "en": Language("en", "English"),
    "fa": Language("fa", "فارسی", rtl=True),
}

class Translations:
    """Manage translations for different languages"""
    
    def __init__(self):
        self.translations: Dict[str, Dict[str, str]] = {
            "en": {
                "welcome": "Welcome to the Chain Store Bot!",
                "select_language": "Please select your language:",
                "language_selected": "Language set to English",
                # ... other English translations ...
            },
            "fa": {
                "welcome": "به ربات فروشگاه زنجیره‌ای خوش آمدید!",
                "select_language": "لطفاً زبان خود را انتخاب کنید:",
                "language_selected": "زبان به فارسی تغییر کرد",
                # ... other Persian translations ...
            }
        }
        
    def load_translations(self):
        """Load translations from JSON files"""
        try:
            translations_dir = Path(__file__).parent.parent.parent / "translations"
            if not translations_dir.exists():
                translations_dir.mkdir(parents=True)
                
            for lang_code in SUPPORTED_LANGUAGES:
                file_path = translations_dir / f"{lang_code}.json"
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.translations[lang_code].update(json.load(f))
                        
        except Exception as e:
            # If loading fails, we'll use the default translations
            print(f"Warning: Failed to load translations: {e}")
            pass  # Keep using default translations
    
    def get_text(self, key: str, lang_code: str = "en") -> str:
        """Get translated text for given key and language"""
        if lang_code not in self.translations:
            lang_code = "en"
        return self.translations[lang_code].get(key, self.translations["en"].get(key, key))

    def add_translation(self, lang_code: str, key: str, text: str):
        """Add new translation"""
        if lang_code not in self.translations:
            self.translations[lang_code] = {}
        self.translations[lang_code][key] = text

# Create global translator instance
translator = Translations()
translator.load_translations()  # Load translations immediately

def _(key: str, lang_code: str = "en") -> str:
    """Shorthand function for getting translations"""
    return translator.get_text(key, lang_code)
