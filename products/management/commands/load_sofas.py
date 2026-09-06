"""
Narxnoma (Price 01.02.2026) 6-sahifasidagi divanlarni yuklaydi.
Ishlatish:  python manage.py load_sofas
Xavfsiz: qayta ishga tushirilsa dublikat yaratmaydi.
Beatriss divani saytda bor — unga faqat o'lcham narxlari qo'shiladi.
"""
from django.core.management.base import BaseCommand
from products.models import ProductModel, CategoryModel, SizeModel, ProductSizePrice

SIZES = ['120 см', '140 см', '160 см', '180 см', '200 см', '220 см']

# nom, rasm kodi, [120, 140, 160, 180, 200, 220] USD narxlari
SOFAS = [
    ('Chanel 1 | Sofa',      'SOFA-CHANEL1',      [140, 163, 187, 210, 233, 257]),
    ('Chanel 2 | Sofa',      'SOFA-CHANEL2',      [132, 154, 176, 198, 220, 242]),
    ('Deko | Sofa',          'SOFA-DEKO',         [47, 54, 62, 70, 78, 85]),
    ('Deko Comfort | Sofa',  'SOFA-DEKO-COMFORT', [65, 76, 87, 98, 109, 119]),
    ('Lavantera | Sofa',     'SOFA-LAVANTERA',    [225, 263, 300, 338, 375, 413]),
    ('Milano | Sofa',        'SOFA-MILANO',       [60, 70, 80, 90, 100, 110]),
    ('King 2 | Sofa',        'SOFA-KING2',        [178, 208, 237, 267, 297, 326]),
    ('King 1 | Sofa',        'SOFA-KING1',        [178, 208, 237, 267, 297, 326]),
    ('Madrid | Sofa',        'SOFA-MADRID',       [160, 187, 213, 240, 267, 293]),
    ('Avangard | Sofa',      'SOFA-AVANGARD',     [218, 254, 290, 326, 363, 399]),
    ('Paris | Sofa',         'SOFA-PARIS',        [115, 134, 153, 172, 191, 210]),
    ('Victoria | Sofa',      'SOFA-VICTORIA',     [129, 150, 171, 193, 214, 236]),
    ('Afina | Sofa',         'SOFA-AFINA',        [70, 82, 94, 105, 117, 129]),
    ('Safiya | Sofa',        'SOFA-SAFIYA',       [74, 86, 98, 111, 123, 135]),
    ('Bosfor | Sofa',        'SOFA-BOSFOR',       [83, 97, 111, 125, 139, 153]),
    ('Cesar | Sofa',         'SOFA-CESAR',        [148, 172, 197, 222, 246, 271]),
    ('Madina 2 | Sofa',      'SOFA-MADINA2',      [111, 129, 148, 166, 185, 203]),
]

# Saytda mavjud Beatriss divaniga qo'shiladigan o'lcham narxlari
BEATRISS_PRICES = [190, 222, 253, 285, 317, 348]

CATEGORY_ID = 4   # Sofas & Armchairs


class Command(BaseCommand):
    help = "Narxnomadagi divanlarni yuklash"

    def handle(self, *args, **options):
        try:
            category = CategoryModel.objects.get(pk=CATEGORY_ID)
        except CategoryModel.DoesNotExist:
            self.stdout.write(self.style.ERROR('Sofas & Armchairs kategoriyasi topilmadi'))
            return

        added, skipped = 0, 0
        for name, img_code, prices in SOFAS:
            product = ProductModel.objects.filter(name=name).first()
            if product is None:
                product = ProductModel(
                    name=name,
                    price=int(prices[0]),   # eng kichik o'lcham — bazaviy narx (USD)
                    category=category,
                )
                product.image.name = f"products/catalog/{img_code}.jpg"
                product.save()
                added += 1
                self.stdout.write(f"  + {name}")
            else:
                skipped += 1

            for title, usd in zip(SIZES, prices):
                size, _ = SizeModel.objects.get_or_create(title=title)
                product.sizes.add(size)
                ProductSizePrice.objects.update_or_create(
                    product=product, title=title,
                    defaults={'price': int(usd), 'order': SIZES.index(title)},
                )

        # Beatriss — mavjud mahsulotga o'lcham narxlari
        beatriss = ProductModel.objects.filter(
            name__icontains='Beatriss', category_id=CATEGORY_ID
        ).first()
        if beatriss:
            for i, (title, usd) in enumerate(zip(SIZES, BEATRISS_PRICES)):
                size, _ = SizeModel.objects.get_or_create(title=title)
                beatriss.sizes.add(size)
                ProductSizePrice.objects.update_or_create(
                    product=beatriss, title=title,
                    defaults={'price': int(usd), 'order': i},
                )
            self.stdout.write(f"  ~ {beatriss.name}: o'lcham narxlari yangilandi")

        self.stdout.write(self.style.SUCCESS(
            f"Tayyor: {added} ta divan qo'shildi, {skipped} ta mavjud edi."))
