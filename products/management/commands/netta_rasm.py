# -*- coding: utf-8 -*-
"""
Netta Stol (Oyna) va Netta Stol (Bambuk) mahsulotlariga
o'zining haqiqiy rasmini o'rnatadi.
Ishga tushirish:  python manage.py netta_rasm
"""
from django.core.management.base import BaseCommand
from products.models import ProductModel

class Command(BaseCommand):
    help = "Netta Stol mahsulotlariga rasm o'rnatadi"

    def handle(self, *args, **kwargs):
        qs = ProductModel.objects.filter(name__icontains="Netta Stol")
        n = qs.update(image="products/catalog/NETTA-STOL-2002.jpg")
        for p in qs:
            self.stdout.write(self.style.SUCCESS(f"  rasm o'rnatildi: {p.name}"))
        if not n:
            self.stdout.write(self.style.WARNING(
                "Netta Stol topilmadi — avval restore_stollar buyrug'ini ishga tushiring."))
