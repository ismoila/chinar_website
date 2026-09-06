"""
Rasmlarni avtomatik kichraytirish — sayt tez ochilishi uchun.

Ishlatilishi (shablonda):

    {% load rasm %}
    <img src="{% thumb product.image 600 %}" ...>

Har bir rasmdan BIR MARTA kichik WebP nusxa yasaladi va
media/cache/<kenglik>/... ichiga saqlanadi. Keyingi safar tayyor nusxa beriladi.

ASL FAYLLARGA TEGILMAYDI — ular joyida qoladi.

Agar biror sabab bilan kichraytirib bo'lmasa (fayl yo'q, buzuq, Pillow xatosi) —
asl rasm URL'i qaytariladi, ya'ni sayt hech qachon buzilmaydi.
"""

import os
import logging

from django import template
from django.conf import settings

register = template.Library()
logger = logging.getLogger(__name__)

CACHE_DIR = "cache"      # media/cache/600/... , media/cache/1200/...
QUALITY = 82             # kichik nusxalar uchun
QUALITY_KATTA = 90       # 1000px va undan katta nusxalar uchun (to'qima naqshlari aniq chiqsin)


def _sifat(width):
    return QUALITY_KATTA if width >= 1000 else QUALITY

# Yaratishga urinib ko'rilgan, lekin xato bergan rasmlar —
# har bir so'rovda qayta urinmaslik uchun
_xato = set()


def _out_rel(rel_name, width):
    """media ichidagi kichik nusxa yo'li: cache/600/products/xxx.webp"""
    base, _ext = os.path.splitext(rel_name)
    return "{}/{}/{}.webp".format(CACHE_DIR, width, base).replace("\\", "/")


def make_thumb(image_field, width=600):
    """
    Kichraytirilgan nusxani yasaydi (agar hali yo'q bo'lsa) va
    uning media ichidagi nisbiy yo'lini qaytaradi. Bo'lmasa — None.
    """
    rel = getattr(image_field, "name", "") or ""
    if not rel:
        return None

    key = (rel, width)
    if key in _xato:
        return None

    out_rel = _out_rel(rel, width)
    out_abs = os.path.join(settings.MEDIA_ROOT, out_rel.replace("/", os.sep))
    src_abs = os.path.join(settings.MEDIA_ROOT, rel.replace("/", os.sep))

    if not os.path.exists(src_abs):
        _xato.add(key)
        return None

    # Tayyor nusxa bor va asl rasmdan keyin yasalgan bo'lsa — shuni beramiz
    try:
        if os.path.exists(out_abs) and os.path.getmtime(out_abs) >= os.path.getmtime(src_abs):
            return out_rel
    except OSError:
        pass

    try:
        from PIL import Image, ImageOps

        os.makedirs(os.path.dirname(out_abs), exist_ok=True)

        im = Image.open(src_abs)
        im = ImageOps.exif_transpose(im)     # telefonda olingan rasm yonboshlab qolmasin

        # Shaffof fon (PNG) — oq fonga qo'yiladi
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            fon = Image.new("RGB", im.size, (255, 255, 255))
            fon.paste(im, mask=im.split()[-1])
            im = fon
        else:
            im = im.convert("RGB")

        if im.width > width:
            h = max(1, round(im.height * width / im.width))
            im = im.resize((width, h), Image.LANCZOS)

        im.save(out_abs, "WEBP", quality=_sifat(width), method=6)
        im.close()
        return out_rel

    except Exception as e:                    # noqa: BLE001
        logger.warning("Rasmni kichraytirib bo'lmadi (%s): %s", rel, e)
        _xato.add(key)
        return None


def make_thumbs(rel, widths, qayta=False):
    """
    Bitta asl rasmni BIR MARTA ochib, bir nechta kenglikda nusxa yasaydi.
    (rasm_siqish buyrug'i uchun — 3 barobar tez ishlaydi.)
    Qaytaradi: (yasalgan_soni, otkazilgan_soni, xato_soni)
    """
    src_abs = os.path.join(settings.MEDIA_ROOT, rel.replace("/", os.sep))
    if not os.path.exists(src_abs):
        return 0, 0, len(widths)

    kerak = []
    for w in widths:
        out_abs = os.path.join(settings.MEDIA_ROOT, _out_rel(rel, w).replace("/", os.sep))
        try:
            if (not qayta) and os.path.exists(out_abs) and os.path.getmtime(out_abs) >= os.path.getmtime(src_abs):
                continue
        except OSError:
            pass
        kerak.append((w, out_abs))

    otkazildi = len(widths) - len(kerak)
    if not kerak:
        return 0, otkazildi, 0

    try:
        from PIL import Image, ImageOps

        im = Image.open(src_abs)
        im = ImageOps.exif_transpose(im)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            fon = Image.new("RGB", im.size, (255, 255, 255))
            fon.paste(im, mask=im.split()[-1])
            im = fon
        else:
            im = im.convert("RGB")

        yasaldi = 0
        for w, out_abs in sorted(kerak, reverse=True):
            os.makedirs(os.path.dirname(out_abs), exist_ok=True)
            if im.width > w:
                h = max(1, round(im.height * w / im.width))
                kichik = im.resize((w, h), Image.LANCZOS)
            else:
                kichik = im
            kichik.save(out_abs, "WEBP", quality=_sifat(w), method=6)
            if kichik is not im:
                kichik.close()
            yasaldi += 1
        im.close()
        return yasaldi, otkazildi, 0

    except Exception as e:  # noqa: BLE001
        logger.warning("Rasmni kichraytirib bo'lmadi (%s): %s", rel, e)
        return 0, otkazildi, len(kerak)


@register.simple_tag
def thumb(image_field, width=600):
    """Kichraytirilgan rasm URL'i. Xato bo'lsa — asl rasm URL'i."""
    if not image_field:
        return ""
    try:
        width = int(width)
    except (TypeError, ValueError):
        width = 600

    try:
        rel = make_thumb(image_field, width)
        if rel:
            return image_field.storage.url(rel)
    except Exception as e:                    # noqa: BLE001
        logger.warning("thumb xatosi: %s", e)

    try:
        return image_field.url
    except Exception:                         # noqa: BLE001
        return ""
