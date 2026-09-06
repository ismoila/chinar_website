"""
Stul (FM-1016 Milano va FM-1025 Sergio) uchun 6 ta rang variantini
haqiqiy foto-sessiya rasmlari bilan yuklaydi.
Ishlatish:  python manage.py load_chair_colors
Xavfsiz: qayta ishga tushirilsa dublikat yaratmaydi.
"""
from django.core.management.base import BaseCommand
from products.models import ProductModel, ColorModel, ProductColorModel, ProductColorImageModel

# rang nomi (bazadagi ColorModel.name) -> rasm slug
COLOR_SETS = [
    ('Slate gray',      'slate-gray'),
    ('Natural wood',    'natural-wood'),
    ('Dark gray-brown', 'dark-gray-brown'),
    ('Ivory',           'ivory'),
    ('Taupe beige',     'taupe-beige'),
    ('Greige',          'greige'),
]

PRODUCT_CODES = ['FM-1016', 'FM-1025']   # Milano va Sergio


class Command(BaseCommand):
    help = "Stul rang variantlari + foto galereya"

    def handle(self, *args, **options):
        for code in PRODUCT_CODES:
            product = ProductModel.objects.filter(name__contains=code).first()
            if product is None:
                self.stdout.write(self.style.WARNING(f'{code} topilmadi, o`tkazib yuborildi'))
                continue
            for order, (color_name, slug) in enumerate(COLOR_SETS):
                color = ColorModel.objects.filter(name=color_name).first()
                if color is None:
                    self.stdout.write(self.style.WARNING(f'Rang topilmadi: {color_name}'))
                    continue
                pc, created = ProductColorModel.objects.get_or_create(
                    product=product, color=color, defaults={'order': order})
                for i in range(1, 5):
                    img_name = f'product_colors/CHAIR-{slug}-{i}.jpg'
                    if not ProductColorImageModel.objects.filter(
                            product_color=pc, image=img_name).exists():
                        pci = ProductColorImageModel(product_color=pc, order=i)
                        pci.image.name = img_name
                        pci.save()
                self.stdout.write(f'  {product.name} — {color_name} {"(yangi)" if created else ""}')
        self.stdout.write(self.style.SUCCESS('Tayyor'))
