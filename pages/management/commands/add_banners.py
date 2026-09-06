"""
Home sahifasiga 2 ta yangi banner qo'shadi (uz/ru/en matnlar bilan).
Ishlatish:  python manage.py add_banners
Qayta ishga tushirilsa dublikat yaratmaydi.
"""
from django.core.management.base import BaseCommand
from pages.models import BannerModel

BANNERS = [
    {
        'image': 'banners/chinar-banner-green.jpg',
        'header_en': 'New Collection',
        'header_uz': "Yangi kolleksiya",
        'header_ru': 'Новая коллекция',
        'title_en': 'Garden sofas from the manufacturer',
        'title_uz': "Ishlab chiqaruvchidan bog' divanlari",
        'title_ru': 'Садовые диваны от производителя',
        'description_en': '18 models, 6 sizes from 120 to 220 cm. Order today — free delivery.',
        'description_uz': "18 ta model, 120–220 sm gacha 6 xil o'lcham. Bugun buyurtma qiling — yetkazib berish bepul.",
        'description_ru': '18 моделей, 6 размеров от 120 до 220 см. Закажите сегодня — доставка бесплатно.',
    },
    {
        'image': 'banners/chinar-banner-yellow.jpg',
        'header_en': '-25% Discount',
        'header_uz': '-25% chegirma',
        'header_ru': 'Скидка -25%',
        'title_en': 'Hot discounts on furniture sets',
        'title_uz': "Mebel to'plamlariga qaynoq chegirmalar",
        'title_ru': 'Горячие скидки на комплекты мебели',
        'description_en': 'Wicker furniture sets for garden and terrace at the best prices.',
        'description_uz': "Bog' va terassa uchun to'qilgan mebel to'plamlari — eng yaxshi narxlarda.",
        'description_ru': 'Плетёные комплекты мебели для сада и террасы по лучшим ценам.',
    },
]


class Command(BaseCommand):
    help = "Yangi home bannerlarini qo'shish"

    def handle(self, *args, **options):
        added = 0
        for b in BANNERS:
            if BannerModel.objects.filter(title_en=b['title_en']).exists():
                self.stdout.write(f"  = {b['title_en']} (mavjud)")
                continue
            banner = BannerModel(
                header=b['header_en'], title=b['title_en'], description=b['description_en'],
                header_en=b['header_en'], title_en=b['title_en'], description_en=b['description_en'],
                header_uz=b['header_uz'], title_uz=b['title_uz'], description_uz=b['description_uz'],
                header_ru=b['header_ru'], title_ru=b['title_ru'], description_ru=b['description_ru'],
                is_active=True,
            )
            banner.image.name = b['image']
            banner.save()
            added += 1
            self.stdout.write(f"  + {b['title_en']}")
        self.stdout.write(self.style.SUCCESS(f'Tayyor: {added} ta banner qo\'shildi.'))
