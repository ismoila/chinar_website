"""
Narxnoma (Price 01.02.2026) 9-sahifasidagi stollar, shirma va cupboardni yuklaydi.
Ishlatish:  python manage.py load_tables
Xavfsiz: qayta ishga tushirilsa dublikat yaratmaydi.
"""
from django.core.management.base import BaseCommand
from products.models import ProductModel, CategoryModel, SizeModel, ProductSizePrice

CATEGORY_ID = 6   # Table

# nom, rasm fayli, [(o'lcham, USD), ...]
TABLES = [
    ('Dining Table | FM-2001', 'FM-2001', [
        ('85x85', 58), ('120x85', 71), ('140x85', 84), ('160x85', 97),
        ('180x85', 107), ('200x100', 156), ('220x100', 172), ('240x100', 189),
        ('255x100', 205), ('280x100', 221), ('300x100', 237)]),
    ('Round Table | FM-2002', 'FM-2002', [
        ('90 см', 72), ('120 см', 106), ('140 см', 133), ('160 см', 167), ('180 см', 207)]),
    ('Dining Table | FM-2007', 'FM-2007', [
        ('90x90', 58), ('120x85', 71), ('140x85', 84), ('160x85', 97),
        ('180x85', 107), ('200x100', 156), ('220x100', 172), ('240x100', 189),
        ('255x100', 205), ('320x100', 267)]),
    ('Dining Table | FM-2008', 'FM-2008', [
        ('90x90', 78), ('120x85', 88), ('140x85', 104), ('160x85', 117),
        ('180x85', 127), ('200x100', 176), ('220x100', 189), ('240x100', 201),
        ('255x100', 220), ('320x100', 284)]),
    ('Dining Table | FM-2011', 'FM-2011', [
        ('140x85', 121), ('160x85', 137), ('180x85', 153), ('200x100', 196),
        ('220x100', 215), ('240x100', 234), ('255x100', 253), ('320x100', 310)]),
    ('Dining Table Lux | FM-2011', 'FM-2011L', [
        ('140x85', 148), ('160x85', 168), ('180x85', 187), ('200x100', 241),
        ('220x100', 264), ('240x100', 287)]),
    ('Coffee Table | FM-2009', 'FM-2009', [
        ('110x70', 130)]),
    ('Side Table | FM-2010', 'FM-2010', [
        ('50 Ø', 65), ('60 Ø', 75)]),
    ('Shirma (Screen) | FM-6004', 'SHIRMA-6004', [
        ('180x50', 50)]),
    ('Cupboard | FM-7001', 'CUPBOARD-7001', []),   # yagona narx: 180$
]

CUPBOARD_PRICE = 180


class Command(BaseCommand):
    help = "Narxnoma 9-sahifasi: stollar, shirma, cupboard"

    def handle(self, *args, **options):
        try:
            category = CategoryModel.objects.get(pk=CATEGORY_ID)
        except CategoryModel.DoesNotExist:
            self.stdout.write(self.style.ERROR('Table kategoriyasi topilmadi'))
            return

        added, skipped = 0, 0
        for name, img_code, sizes in TABLES:
            product = ProductModel.objects.filter(name=name).first()
            if product is None:
                base_price = sizes[0][1] if sizes else CUPBOARD_PRICE
                product = ProductModel(
                    name=name,
                    price=int(base_price),   # bazaviy narx USD
                    category=category,
                )
                product.image.name = f"products/catalog/{img_code}.jpg"
                product.save()
                added += 1
                self.stdout.write(f"  + {name}")
            else:
                skipped += 1

            for order, (title, usd) in enumerate(sizes):
                size, _ = SizeModel.objects.get_or_create(title=title)
                product.sizes.add(size)
                ProductSizePrice.objects.update_or_create(
                    product=product, title=title,
                    defaults={'price': int(usd), 'order': order},
                )

        self.stdout.write(self.style.SUCCESS(
            f"Tayyor: {added} ta yangi, {skipped} ta mavjud edi"))