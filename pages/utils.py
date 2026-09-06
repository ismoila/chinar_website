# utils.py
import logging
import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)

CBU_URL = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/USD/"
CACHE_KEY = "usd_uzs_rate"
FALLBACK_KEY = "usd_uzs_rate_fallback"
CACHE_TTL = 3600  # 1 soat


def get_usd_to_uzs_rate():
    """CBU dan USD/UZS kursini qaytaradi (keshlangan holda)."""
    rate = cache.get(CACHE_KEY)
    if rate:
        return rate

    try:
        response = requests.get(CBU_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        rate = float(data[0]["Rate"])

        cache.set(CACHE_KEY, rate, CACHE_TTL)
        cache.set(FALLBACK_KEY, rate, None)
        return rate

    except Exception as e:
        logger.error(f"CBU kursini olishda xato: {e}")
        fallback = cache.get(FALLBACK_KEY)
        return fallback if fallback else 12500