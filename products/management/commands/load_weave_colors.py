"""
AIKO'dagi "Цвет плетения" (to'qima ranglari) to'plamini ColorModel'ga yuklaydi.
Bu ranglar mahsulot sahifasidagi rang tanlash doirachalarida chiqadi.
Ishlatish:  python manage.py load_weave_colors
Xavfsiz: mavjud nom qayta yaratilmaydi.
"""
from django.core.management.base import BaseCommand
from products.models import ColorModel

WEAVE_COLORS = [
    # 1-to'plam — to'qima
    ('Smoky Taupe',   '#736B6A', 'weave'),
    ('Mocha Melange', '#937F6E', 'weave'),
    ('Amber Beige',   '#A68467', 'weave'),
    ('Steel Gray',    '#5D666B', 'weave'),
    ('Stone Melange', '#A8A699', 'weave'),
    ('Cream White',   '#DAD1B4', 'weave'),
    # 2-to'plam — eshilgan arqon
    ('Driftwood',     '#938B7C', 'rope'),
    ('Sand Rope',     '#A58D70', 'rope'),
    ('Golden Beige',  '#B8A382', 'rope'),
    ('Walnut',        '#80634C', 'rope'),
    ('Caramel',       '#B28B63', 'rope'),
    ('Ash Gray',      '#898984', 'rope'),
    # 3-to'plam — rattan tayoqcha
    ('Graphite',      '#454848', 'rattan'),
    ('Sand',          '#C6A87E', 'rattan'),
    ('Chestnut',      '#7B4A30', 'rattan'),
    # 4-to'plam — mato
    ('Latte',         '#BEA48B', 'fabric'),
    ('Scarlet Red',   '#D8253B', 'fabric'),
    ('Turquoise',     '#6EA9B3', 'fabric'),
]

# Avvalgi 6 ta stul rangi ham to'qima guruhiga kiradi
OLD_WEAVE = ['Dark gray-brown', 'Taupe beige', 'Natural wood',
             'Slate gray', 'Greige', 'Ivory']


class Command(BaseCommand):
    help = "To'qima ranglarini yuklash"

    def handle(self, *args, **options):
        added = 0
        for name, code, group in WEAVE_COLORS:
            obj, created = ColorModel.objects.get_or_create(
                name=name, defaults={'code': code, 'group': group})
            if created:
                added += 1
                self.stdout.write(f'  + {name} {code}')
            elif obj.group != group:
                obj.group = group
                obj.save(update_fields=['group'])
        # eski ranglar guruhini belgilash
        ColorModel.objects.filter(name__in=OLD_WEAVE).update(group='weave')
        self.stdout.write(self.style.SUCCESS(f'Tayyor: {added} ta yangi rang, guruhlar belgilandi'))
