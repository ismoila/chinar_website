"""
Yangi FMA modellar katalogidagi mahsulotlarni yuklaydi (NEW MODELS broshyura).
Narxlar katalogda ko'rsatilmagan — hammasi 0 qilib qo'yiladi,
admin panel orqali to'g'ri narxni kiritib qo'ying.
Ishlatish:  python manage.py load_new_models
Xavfsiz: qayta ishga tushirilsa dublikat yaratmaydi.
"""
from django.core.management.base import BaseCommand
from products.models import ProductModel, CategoryModel

# nom, kod, kategoriya id
NEW_MODELS = [
    ('Madonna 2 | FMA-1002',     'FMA-1002', 2),
    ('Bodrum | FMA-1003',        'FMA-1003', 2),
    ('Bodrum Lounge | FMA-1004', 'FMA-1004', 2),
    ('Agata | FMA-1008',         'FMA-1008', 2),
    ('Freya | FMA-1011',         'FMA-1011', 2),
    ('Berlin | FMA-1012',        'FMA-1012', 2),
    ('Freya 2 | FMA-1014',       'FMA-1014', 2),
    ('Bodrum 2 | FMA-1015',      'FMA-1015', 2),
    ('Amelia | FMA-1018',        'FMA-1018', 2),
    ('Netta 2 | FMA-1021',       'FMA-1021', 2),
    ('Eline | FMA-1022',         'FMA-1022', 2),
    ('Gaia | FMA-1023',          'FMA-1023', 2),
    ('Netta | FMA-1026',         'FMA-1026', 2),
    ('Netta Set | FMA-3001',     'FMA-3001', 3),
    ('Monaco | FMA-5001',        'FMA-5001', 1),
]


class Command(BaseCommand):
    help = "Yangi FMA modellarni yuklash"

    def handle(self, *args, **options):
        added, skipped = 0, 0
        for name, code, cat_id in NEW_MODELS:
            if ProductModel.objects.filter(name__contains=code).exists():
                skipped += 1
                continue
            try:
                category = CategoryModel.objects.get(pk=cat_id)
            except CategoryModel.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Kategoriya {cat_id} topilmadi: {name}'))
                continue
            p = ProductModel(name=name, price=0, category=category)
            p.image.name = f"products/catalog/{code}.jpg"
            p.save()
            added += 1
            self.stdout.write(f'  + {name}')
        self.stdout.write(self.style.SUCCESS(
            f"Tayyor: {added} ta yangi, {skipped} ta allaqachon mavjud. "
            f"Narxlarni admin paneldan kiriting!"))
