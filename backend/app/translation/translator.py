"""Translation service with multi-engine resilience."""
from __future__ import annotations

import logging
import html
from abc import ABC, abstractmethod
from functools import lru_cache
import requests

from ..config import config

logger = logging.getLogger("anuvad.translation")


class BaseTranslator(ABC):
    """Abstract base class for translation engines."""

    @abstractmethod
    def translate(self, text: str, src: str = "auto", dest: str = "es") -> str | None:
        """Translate text from source to destination language."""
        pass


class GoogleWebTranslator(BaseTranslator):
    """Translates via Google Translate web service using official Chrome client and persistent connection."""

    def __init__(self):
        self.endpoint = "https://translate.googleapis.com/translate_a/single"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            )
        })

    def translate(self, text: str, src: str = "auto", dest: str = "es") -> str | None:
        if not text or not text.strip():
            return None

        # Try dict-chrome-ex first (fastest, unblocked), fallback to webapp
        for client in ("dict-chrome-ex", "webapp"):
            params = {
                "client": client,
                "sl": src if src != "auto" else "auto",
                "tl": dest,
                "dt": "t",
                "q": text.strip(),
            }

            try:
                response = self.session.get(
                    self.endpoint, params=params, timeout=2.5
                )
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0 and len(data[0]) > 0:
                        parts = [chunk[0] for chunk in data[0] if chunk and chunk[0]]
                        result = "".join(parts).strip()
                        if result:
                            return result
                elif response.status_code == 429:
                    logger.debug(f"Google Web Translate client='{client}' rate limited (429).")
            except Exception as e:
                logger.debug(f"Google Web Translate client='{client}' error: {e}")

        return None


class MyMemoryTranslator(BaseTranslator):
    """Translates via MyMemory public translation API."""

    def __init__(self):
        self.endpoint = "https://api.mymemory.translated.net/get"

    def translate(self, text: str, src: str = "auto", dest: str = "es") -> str | None:
        if not text or not text.strip():
            return None

        source_lang = "en" if src == "auto" else src
        lang_pair = f"{source_lang}|{dest}"
        params = {"q": text.strip(), "langpair": lang_pair}

        try:
            response = requests.get(self.endpoint, params=params, timeout=4)
            if response.status_code == 200:
                data = response.json()
                translated = data.get("responseData", {}).get("translatedText")
                if translated and translated.strip():
                    # Decode HTML entities if any
                    return html.unescape(translated.strip())
        except Exception as e:
            logger.debug(f"MyMemory translation request failed: {e}")

        return None


class GoogleCloudTranslator(BaseTranslator):
    """Translates via official Google Cloud Translation API using API key."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"

    def translate(self, text: str, src: str = "auto", dest: str = "es") -> str | None:
        if not text or not text.strip():
            return None

        payload = {
            "q": text.strip(),
            "target": dest,
            "format": "text",
        }
        if src != "auto":
            payload["source"] = src

        try:
            response = requests.post(self.endpoint, json=payload, timeout=4)
            if response.status_code == 200:
                data = response.json()
                translations = data.get("data", {}).get("translations", [])
                if translations:
                    return html.unescape(translations[0].get("translatedText", ""))
        except Exception as e:
            logger.error(f"Google Cloud Translation error: {e}")

        return None


class ResilientTranslator:
    """Composite translator that chains providers and caches results."""

    def __init__(self, engine: str = "auto", api_key: str | None = None):
        self.engine = engine
        self.api_key = api_key
        self.engines: list[BaseTranslator] = []
        self._setup_engines()
        self._cache: dict[tuple[str, str, str], str] = {}

    def _setup_engines(self) -> None:
        # If API key is provided, use official Google Cloud first
        if self.api_key:
            self.engines.append(GoogleCloudTranslator(self.api_key))

        if self.engine == "google":
            self.engines.append(GoogleWebTranslator())
            self.engines.append(MyMemoryTranslator())
        elif self.engine == "mymemory":
            self.engines.append(MyMemoryTranslator())
            self.engines.append(GoogleWebTranslator())
        else:  # "auto"
            self.engines.append(GoogleWebTranslator())
            self.engines.append(MyMemoryTranslator())

    def translate(self, text: str, src: str = "auto", dest: str = "es") -> str | None:
        """
        Translate text, trying available engines in priority order.
        Returns original text if src and dest are identical.
        """
        if not text or not text.strip():
            return None

        cleaned = text.strip()
        if src != "auto" and src.lower() == dest.lower():
            return cleaned

        cache_key = (cleaned, src.lower(), dest.lower())
        if cache_key in self._cache:
            return self._cache[cache_key]

        for engine in self.engines:
            result = engine.translate(cleaned, src=src, dest=dest)
            if result and result.strip():
                # Store in cache (limit cache size to 1000 entries)
                if len(self._cache) > 1000:
                    self._cache.clear()
                self._cache[cache_key] = result.strip()
                return result.strip()

        logger.debug(f"All translation engines failed for text: '{cleaned[:30]}...'")
        return None


_global_translator: ResilientTranslator | None = None


def get_translator() -> ResilientTranslator:
    """Get or create singleton ResilientTranslator instance."""
    global _global_translator
    if _global_translator is None:
        _global_translator = ResilientTranslator(
            engine=config.translation_engine,
            api_key=config.google_translate_api_key,
        )
    return _global_translator
