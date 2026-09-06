from django.core.management.base import BaseCommand
from products.models import ProductModel, CategoryModel


class Command(BaseCommand):
    help = "Noto'g'ri kategoriyalarni tuzatish (London Eco, Lavantera)"

    def handle(self, *args, **options):
        fixes = {
            # FM-5010 London Eco — oyoqli kreslo, osma emas → Chairs
            'FM-5010': 2,
            # FM-1015 Lavantera — katta kreslo → Sofas & Armchairs
            'FM-1015': 4,
        }
        for code, cat_id in fixes.items():
            p = ProductModel.objects.filter(name__contains=code).first()
            if not p:
                self.stdout.write(f'{code}: topilmadi')
                continue
            try:
                cat = CategoryModel.objects.get(id=cat_id)
            except CategoryModel.DoesNotExist:
                self.stdout.write(f'{code}: kategoriya {cat_id} yo\'q')
                continue
            old = p.category.name
            p.category = cat
            p.save()
            self.stdout.write(f'{p.name}: {old} -> {cat.name}')
        self.stdout.write(self.style.SUCCESS('Tayyor'))
