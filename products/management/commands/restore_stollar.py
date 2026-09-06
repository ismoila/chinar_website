# -*- coding: utf-8 -*-
"""
O'chirib yuborilgan stol mahsulotlarini qayta tiklash.
Ishga tushirish:  python manage.py restore_stollar
Xavfsiz: bir xil nomli mahsulot bazada bo'lsa, takrorlamaydi.
"""
import json
from django.core.management.base import BaseCommand
from products.models import ProductModel, CategoryModel, ProductSizePrice

DATA = json.loads(r"""[
 {
  "name": "Dining Table | FM-2001",
  "name_en": "Dining Table | FM-2001",
  "name_uz": null,
  "name_ru": null,
  "price": 58.0,
  "image": "products/catalog/FM-2001.jpg",
  "sizes": [
   {
    "title": "85x85",
    "price": 58.0
   },
   {
    "title": "120x85",
    "price": 71.0
   },
   {
    "title": "140x85",
    "price": 84.0
   },
   {
    "title": "160x85",
    "price": 97.0
   },
   {
    "title": "180x85",
    "price": 107.0
   },
   {
    "title": "200x100",
    "price": 156.0
   },
   {
    "title": "220x100",
    "price": 172.0
   },
   {
    "title": "240x100",
    "price": 189.0
   },
   {
    "title": "255x100",
    "price": 205.0
   },
   {
    "title": "280x100",
    "price": 221.0
   },
   {
    "title": "300x100",
    "price": 237.0
   }
  ]
 },
 {
  "name": "Round Table | FM-2002",
  "name_en": "Round Table | FM-2002",
  "name_uz": null,
  "name_ru": null,
  "price": 72.0,
  "image": "products/catalog/FM-2002.jpg",
  "sizes": [
   {
    "title": "90 см",
    "price": 72.0
   },
   {
    "title": "120 см",
    "price": 106.0
   },
   {
    "title": "140 см",
    "price": 133.0
   },
   {
    "title": "160 см",
    "price": 167.0
   },
   {
    "title": "180 см",
    "price": 207.0
   }
  ]
 },
 {
  "name": "Dining Table | FM-2007",
  "name_en": "Dining Table | FM-2007",
  "name_uz": null,
  "name_ru": null,
  "price": 58.0,
  "image": "products/catalog/FM-2007.jpg",
  "sizes": [
   {
    "title": "90x90",
    "price": 58.0
   },
   {
    "title": "120x85",
    "price": 71.0
   },
   {
    "title": "140x85",
    "price": 84.0
   },
   {
    "title": "160x85",
    "price": 97.0
   },
   {
    "title": "180x85",
    "price": 107.0
   },
   {
    "title": "200x100",
    "price": 156.0
   },
   {
    "title": "220x100",
    "price": 172.0
   },
   {
    "title": "240x100",
    "price": 189.0
   },
   {
    "title": "255x100",
    "price": 205.0
   },
   {
    "title": "320x100",
    "price": 267.0
   }
  ]
 },
 {
  "name": "Dining Table | FM-2008",
  "name_en": "Dining Table | FM-2008",
  "name_uz": null,
  "name_ru": null,
  "price": 78.0,
  "image": "products/catalog/FM-2008.jpg",
  "sizes": [
   {
    "title": "90x90",
    "price": 78.0
   },
   {
    "title": "120x85",
    "price": 88.0
   },
   {
    "title": "140x85",
    "price": 104.0
   },
   {
    "title": "160x85",
    "price": 117.0
   },
   {
    "title": "180x85",
    "price": 127.0
   },
   {
    "title": "200x100",
    "price": 176.0
   },
   {
    "title": "220x100",
    "price": 189.0
   },
   {
    "title": "240x100",
    "price": 201.0
   },
   {
    "title": "255x100",
    "price": 220.0
   },
   {
    "title": "320x100",
    "price": 284.0
   }
  ]
 },
 {
  "name": "Dining Table | FM-2011",
  "name_en": "Dining Table | FM-2011",
  "name_uz": null,
  "name_ru": null,
  "price": 121.0,
  "image": "products/catalog/FM-2011.jpg",
  "sizes": [
   {
    "title": "140x85",
    "price": 121.0
   },
   {
    "title": "160x85",
    "price": 137.0
   },
   {
    "title": "180x85",
    "price": 153.0
   },
   {
    "title": "200x100",
    "price": 196.0
   },
   {
    "title": "220x100",
    "price": 215.0
   },
   {
    "title": "240x100",
    "price": 234.0
   },
   {
    "title": "255x100",
    "price": 253.0
   },
   {
    "title": "320x100",
    "price": 310.0
   }
  ]
 },
 {
  "name": "Dining Table Lux | FM-2011",
  "name_en": "Dining Table Lux | FM-2011",
  "name_uz": null,
  "name_ru": null,
  "price": 148.0,
  "image": "products/catalog/FM-2011L.jpg",
  "sizes": [
   {
    "title": "140x85",
    "price": 148.0
   },
   {
    "title": "160x85",
    "price": 168.0
   },
   {
    "title": "180x85",
    "price": 187.0
   },
   {
    "title": "200x100",
    "price": 241.0
   },
   {
    "title": "220x100",
    "price": 264.0
   },
   {
    "title": "240x100",
    "price": 287.0
   }
  ]
 },
 {
  "name": "Coffee Table | FM-2009",
  "name_en": "Coffee Table | FM-2009",
  "name_uz": null,
  "name_ru": null,
  "price": 130.0,
  "image": "products/catalog/FM-2009.jpg",
  "sizes": [
   {
    "title": "110x70",
    "price": 130.0
   }
  ]
 },
 {
  "name": "Side Table | FM-2010",
  "name_en": "Side Table | FM-2010",
  "name_uz": null,
  "name_ru": null,
  "price": 65.0,
  "image": "products/catalog/FM-2010.jpg",
  "sizes": [
   {
    "title": "50 Ø",
    "price": 65.0
   },
   {
    "title": "60 Ø",
    "price": 75.0
   }
  ]
 },
 {
  "name": "Shirma (Screen) | FM-6004",
  "name_en": "Shirma (Screen) | FM-6004",
  "name_uz": null,
  "name_ru": null,
  "price": 50.0,
  "image": "products/catalog/SHIRMA-6004.jpg",
  "sizes": [
   {
    "title": "180x50",
    "price": 50.0
   }
  ]
 },
 {
  "name": "Cupboard | FM-7001",
  "name_en": "Cupboard | FM-7001",
  "name_uz": null,
  "name_ru": null,
  "price": 180.0,
  "image": "products/catalog/CUPBOARD-7001.jpg",
  "sizes": []
 },
 {
  "name": "Stol | FMA-2001",
  "name_en": "Stol | FMA-2001",
  "name_uz": null,
  "name_ru": null,
  "price": 70.0,
  "image": "products/catalog/EXC-STOL-2001.jpg",
  "sizes": [
   {
    "title": "85x85",
    "price": 70.0
   },
   {
    "title": "120x85",
    "price": 85.0
   },
   {
    "title": "140x85",
    "price": 100.0
   },
   {
    "title": "160x85",
    "price": 117.0
   },
   {
    "title": "180x85",
    "price": 130.0
   }
  ]
 },
 {
  "name": "Stol | FMA-2002",
  "name_en": "Stol | FMA-2002",
  "name_uz": null,
  "name_ru": null,
  "price": 75.0,
  "image": "products/catalog/EXC-STOL-2002.jpg",
  "sizes": [
   {
    "title": "85x85",
    "price": 75.0
   },
   {
    "title": "120x85",
    "price": 90.0
   },
   {
    "title": "140x85",
    "price": 105.0
   },
   {
    "title": "160x85",
    "price": 122.0
   },
   {
    "title": "180x85",
    "price": 135.0
   }
  ]
 },
 {
  "name": "Netta Jurnal | FMA-2001",
  "name_en": "Netta Jurnal | FMA-2001",
  "name_uz": null,
  "name_ru": null,
  "price": 70.0,
  "image": "products/catalog/EXC-NETTA-JURNAL.jpg",
  "sizes": [
   {
    "title": "50 см",
    "price": 70.0
   },
   {
    "title": "60 см",
    "price": 81.0
   }
  ]
 },
 {
  "name": "Netta Stol (Bambuk) | FMA-2002",
  "name_en": "Netta Stol (Bambuk) | FMA-2002",
  "name_uz": null,
  "name_ru": null,
  "price": 89.0,
  "image": "products/catalog/EXC-STOL-2002.jpg",
  "sizes": [
   {
    "title": "85x85",
    "price": 89.0
   },
   {
    "title": "120x85",
    "price": 115.0
   },
   {
    "title": "140x85",
    "price": 130.0
   },
   {
    "title": "160x85",
    "price": 148.0
   },
   {
    "title": "180x85",
    "price": 163.0
   },
   {
    "title": "200x100",
    "price": 182.0
   },
   {
    "title": "220x100",
    "price": 195.0
   }
  ]
 },
 {
  "name": "Netta Stol (Oyna) | FMA-2002",
  "name_en": "Netta Stol (Oyna) | FMA-2002",
  "name_uz": null,
  "name_ru": null,
  "price": 52.0,
  "image": "products/catalog/EXC-STOL-2002.jpg",
  "sizes": [
   {
    "title": "85x85",
    "price": 52.0
   },
   {
    "title": "120x85",
    "price": 68.0
   },
   {
    "title": "140x85",
    "price": 84.0
   },
   {
    "title": "160x85",
    "price": 100.0
   },
   {
    "title": "180x85",
    "price": 115.0
   },
   {
    "title": "200x100",
    "price": 142.0
   },
   {
    "title": "220x100",
    "price": 157.0
   }
  ]
 }
]""")

class Command(BaseCommand):
    help = "Katalogdagi stol mahsulotlarini qayta tiklaydi"

    def handle(self, *args, **kwargs):
        cat, _ = CategoryModel.objects.get_or_create(
            name="Table", defaults={"image": "category/table.jpg"}
        )
        added = skipped = 0
        for item in DATA:
            if ProductModel.objects.filter(name=item["name"]).exists():
                self.stdout.write(f"  bor, o'tkazildi: {item['name']}")
                skipped += 1
                continue
            p = ProductModel.objects.create(
                name=item["name"],
                name_en=item.get("name_en") or item["name"],
                name_uz=item.get("name_uz"),
                name_ru=item.get("name_ru"),
                price=item["price"],
                image=item["image"],
                category=cat,
            )
            for i, s in enumerate(item.get("sizes", [])):
                ProductSizePrice.objects.create(
                    product=p, title=s["title"], price=s["price"], order=i
                )
            self.stdout.write(self.style.SUCCESS(
                f"  + qo'shildi: {p.name} ({len(item.get('sizes', []))} o'lcham)"
            ))
            added += 1
        self.stdout.write(self.style.SUCCESS(
            f"Tayyor: {added} ta qo'shildi, {skipped} ta allaqachon bor edi."
        ))
