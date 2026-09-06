# -*- coding: utf-8 -*-
"""
Netta Stol FMA-2002 ni qaytadan, TOZA holda qo'shadi:
- eski "Netta Stol (Oyna)" va "Netta Stol (Bambuk)" ni o'chiradi (bo'lsa)
- BITTA "Netta Stol | FMA-2002" mahsulotini yaratadi
- o'z rasmi bilan (media/products/catalog/NETTA-STOL-2002.jpg)
- katalogdagi to'liq jadval: har o'lcham Oyna va Bambuk variantida

Ishga tushirish:  python manage.py netta_stol
"""
from django.core.management.base import BaseCommand
from products.models import ProductModel, CategoryModel, ProductSizePrice

NAME = "Netta Stol | FMA-2002"
IMAGE = "products/catalog/NETTA-STOL-2002.jpg"

# (o'lcham nomi, narx USD) — avval Oyna (arzonroq), keyin Bambuk
SIZES = [
    ("85x85 (Oyna)", 52), ("120x85 (Oyna)", 68), ("140x85 (Oyna)", 84),
    ("160x85 (Oyna)", 100), ("180x85 (Oyna)", 115), ("200x100 (Oyna)", 142),
    ("220x100 (Oyna)", 157),
    ("85x85 (Bambuk)", 89), ("120x85 (Bambuk)", 115), ("140x85 (Bambuk)", 130),
    ("160x85 (Bambuk)", 148), ("180x85 (Bambuk)", 163), ("200x100 (Bambuk)", 182),
    ("220x100 (Bambuk)", 195),
]

class Command(BaseCommand):
    help = "Netta Stol FMA-2002 ni qaytadan qo'shadi (Oyna + Bambuk bitta kartada)"

    def handle(self, *args, **kwargs):
        # eski variantlarni tozalaymiz
        old = ProductModel.objects.filter(name__in=[
            "Netta Stol (Oyna) | FMA-2002",
            "Netta Stol (Bambuk) | FMA-2002",
            NAME,
        ])
        for p in old:
            self.stdout.write(f"  o'chirildi: {p.name}")
        old.delete()

        cat, _ = CategoryModel.objects.get_or_create(
            name="Table", defaults={"image": "category/table.jpg"}
        )
        p = ProductModel.objects.create(
            name=NAME, name_en=NAME,
            price=SIZES[0][1],
            image=IMAGE,
            category=cat,
        )
        for i, (title, price) in enumerate(SIZES):
            ProductSizePrice.objects.create(product=p, title=title, price=price, order=i)
        self.stdout.write(self.style.SUCCESS(
            f"Tayyor: {p.name} qo'shildi — {len(SIZES)} ta o'lcham/variant, rasm: {IMAGE}"
        ))
