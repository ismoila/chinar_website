"""
sitemap.xml — Google va Yandex saytdagi barcha sahifalarni topishi uchun.
Har bir sahifa 3 tilda (uz / ru / en) ro'yxatga kiradi.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from products.models import ProductModel, CategoryModel
from blog.models import BlogPost


class MahsulotSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    i18n = True
    alternates = True
    x_default = True

    def items(self):
        return ProductModel.objects.all().order_by("id")

    def location(self, obj):
        return reverse("products:product_detail", args=[obj.slug])

    def lastmod(self, obj):
        return obj.updated_at


class KategoriyaSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7
    i18n = True
    alternates = True
    x_default = True

    def items(self):
        return CategoryModel.objects.all().order_by("id")

    def location(self, obj):
        return reverse("products:category_detail", args=[obj.pk])


class SahifaSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5
    i18n = True
    alternates = True
    x_default = True

    def items(self):
        return [
            "pages:home", "pages:category", "pages:about", "pages:services",
            "pages:projects", "pages:idea", "pages:delivery", "pages:address",
            "pages:designers", "pages:discounts", "pages:news", "pages:journal",
        ]

    def location(self, name):
        return reverse(name)


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6
    i18n = True
    alternates = True

    def items(self):
        return BlogPost.objects.filter(is_published=True).order_by('-created_at')

    def location(self, obj):
        return obj.get_absolute_url()

    def lastmod(self, obj):
        return obj.created_at

SITEMAPLAR = {
    "mahsulotlar": MahsulotSitemap,
    "kategoriyalar": KategoriyaSitemap,
    "sahifalar": SahifaSitemap,
    "blog": BlogSitemap,
}