"""
"Exclusive 2026.pdf" katalogidagi mahsulotlarni yuklaydi.
Narxlar USD'da — saytda avtomatik so'mga aylanadi.
Ishlatish:  python manage.py load_exclusive
Xavfsiz: bir xil nomli mahsulot qayta yaratilmaydi.
"""
from django.core.management.base import BaseCommand
from products.models import ProductModel, CategoryModel, SizeModel, ProductSizePrice

# nom, rasm kodi, kategoriya id, bazaviy narx USD, [(o'lcham, USD), ...]
PRODUCTS = [
    # Stollar (Table = 6)
    ('Stol | FMA-2001', 'EXC-STOL-2001', 6, 70, [
        ('85x85', 70), ('120x85', 85), ('140x85', 100), ('160x85', 117), ('180x85', 130)]),
    ('Stol | FMA-2002', 'EXC-STOL-2002', 6, 75, [
        ('85x85', 75), ('120x85', 90), ('140x85', 105), ('160x85', 122), ('180x85', 135)]),
    ('Netta Jurnal | FMA-2001', 'EXC-NETTA-JURNAL', 6, 70, [
        ('50 см', 70), ('60 см', 81)]),
    ('Netta Stol (Bambuk) | FMA-2002', 'EXC-STOL-2002', 6, 89, [
        ('85x85', 89), ('120x85', 115), ('140x85', 130), ('160x85', 148),
        ('180x85', 163), ('200x100', 182), ('220x100', 195)]),
    ('Netta Stol (Oyna) | FMA-2002', 'EXC-STOL-2002', 6, 52, [
        ('85x85', 52), ('120x85', 68), ('140x85', 84), ('160x85', 100),
        ('180x85', 115), ('200x100', 142), ('220x100', 157)]),
    # Osma kreslo (Hanging Chairs = 1)
    ('Monaco | FMA-5001', 'EXC-MONACO', 1, 168, []),
    # Stullar (Chairs = 2)
    ('Netta | FMA-1001',        'EXC-NETTA',        2, 65,  []),
    ('Madonna | FMA-1002',      'EXC-MADONNA',      2, 97,  []),
    ('Bodrum | FMA-1003',       'EXC-BODRUM',       2, 74,  []),
    ('Bodrum Katta | FMA-1004', 'EXC-BODRUM-KATTA', 2, 95,  []),
    ('Lola | FMA-1004',         'EXC-LOLA',         2, 35,  []),
    ('Berlin | FMA-1005',       'EXC-BERLIN',       2, 80,  []),
    ('Agata | FMA-1006',        'EXC-AGATA-1006',   2, 80,  []),
    ('Agata | FMA-1007',        'EXC-AGATA-1007',   2, 90,  []),
    ('Netta 2 | FMA-1008',      'EXC-NETTA2',       2, 100, []),
    ('Gaia | FMA-1009',         'EXC-GAIA',         2, 150, []),
    ('Madina Arqon | FMA-1010', 'EXC-MADINA-ARQON', 2, 70,  []),
    ('Aura | FMA-1011',         'EXC-AURA',         2, 35,  []),
    ('Netta Luxe | FMA-1011',   'EXC-NETTA-LUXE',   2, 75,  []),
]


class Command(BaseCommand):
    help = "Exclusive 2026 katalogini yuklash"

    def handle(self, *args, **options):
        added, skipped = 0, 0
        for name, img_code, cat_id, base_usd, sizes in PRODUCTS:
            if ProductModel.objects.filter(name=name).exists():
                skipped += 1
                continue
            try:
                category = CategoryModel.objects.get(pk=cat_id)
            except CategoryModel.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Kategoriya {cat_id} yo`q: {name}'))
                continue
            p = ProductModel(name=name, price=int(base_usd), category=category)
            p.image.name = f"products/catalog/{img_code}.jpg"
            p.save()
            added += 1
            for order, (title, usd) in enumerate(sizes):
                size, _ = SizeModel.objects.get_or_create(title=title)
                p.sizes.add(size)
                ProductSizePrice.objects.update_or_create(
                    product=p, title=title,
                    defaults={'price': int(usd), 'order': order})
            self.stdout.write(f'  + {name}')
        self.stdout.write(self.style.SUCCESS(
            f'Tayyor: {added} ta yangi, {skipped} ta mavjud edi'))
