"""
SEO uchun yordamchi teglar.

    {% load seo %}
    {% lang_url 'ru' %}   →  hozirgi sahifaning ruscha manzili (/uz/... → /ru/...)
"""

import re

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def lang_url(context, lang):
    """Joriy sahifa yo'lini boshqa til prefiksi bilan qaytaradi."""
    request = context.get("request")
    path = request.path if request else "/"
    yangi, n = re.subn(r"^/(uz|ru|en)(/|$)", "/%s\\2" % lang, path)
    if n == 0:                       # prefiks bo'lmasa (masalan /sitemap.xml)
        yangi = "/%s%s" % (lang, path)
    return yangi
