"""
Chinor narxnomasidan (Price 01.02.2026) ajratilgan mahsulotlarni bazaga yuklaydi.
Ishlatish:  python manage.py load_catalog
Xavfsiz: mavjud mahsulotlarga tegmaydi, faqat yo'qlarini qo'shadi.
Qayta ishga tushirilsa ham dublikat yaratmaydi.
"""
from django.core.management.base import BaseCommand
from products.models import ProductModel, CategoryModel, SizeModel

PRODUCTS = [
 {
  "name": "Deko Orena | FM-3001",
  "model": "FM-3001",
  "price": 172,
  "category_id": 3,
  "sizes": [
   "90",
   "120",
   "140",
   "160",
   "180"
  ]
 },
 {
  "name": "Victoria Orena | FM-3008",
  "model": "FM-3008",
  "price": 372,
  "category_id": 3,
  "sizes": [
   "90",
   "120",
   "140",
   "160",
   "180"
  ]
 },
 {
  "name": "Victoria | FM-3009",
  "model": "FM-3009",
  "price": 358,
  "category_id": 3,
  "sizes": [
   "85х85",
   "120х85",
   "140x85",
   "160x85",
   "200х100",
   "220х100",
   "240х100",
   "255x100",
   "300x100"
  ]
 },
 {
  "name": "Chanel 1 Orena | FM-3013",
  "model": "FM-3013",
  "price": 352,
  "category_id": 3,
  "sizes": [
   "90",
   "120",
   "140",
   "160",
   "180"
  ]
 },
 {
  "name": "Chanel 2 Orena | FM-3014",
  "model": "FM-3014",
  "price": 336,
  "category_id": 3,
  "sizes": [
   "90",
   "120",
   "140",
   "160",
   "180"
  ]
 },
 {
  "name": "Avangard Katta | FM-3015",
  "model": "FM-3015",
  "price": 522,
  "category_id": 3,
  "sizes": [
   "85х85",
   "160x85",
   "200x100",
   "255х100"
  ]
 },
 {
  "name": "Madrid | FM-3016",
  "model": "FM-3016",
  "price": 378,
  "category_id": 3,
  "sizes": [
   "85х85",
   "140x85",
   "160x85",
   "180х85",
   "200x100",
   "255x100",
   "300х100"
  ]
 },
 {
  "name": "Chanel 1 | FM-3019",
  "model": "FM-3019",
  "price": 338,
  "category_id": 3,
  "sizes": [
   "85x85",
   "120х85",
   "140x85",
   "160х85",
   "180х85",
   "200x100",
   "220х100",
   "240х100",
   "255x100",
   "300х100"
  ]
 },
 {
  "name": "Deco Comfort Orena | FM-3026",
  "model": "FM-3026",
  "price": 224,
  "category_id": 3,
  "sizes": [
   "90",
   "120",
   "140",
   "160",
   "180"
  ]
 },
 {
  "name": "Beatriss Orena | FM-3033",
  "model": "FM-3033",
  "price": 452,
  "category_id": 3,
  "sizes": [
   "90",
   "140",
   "160",
   "180"
  ]
 },
 {
  "name": "Chanel 2 | FM-3034",
  "model": "FM-3034",
  "price": 322,
  "category_id": 3,
  "sizes": [
   "85x85",
   "120х85",
   "140x85",
   "160х85",
   "180х85",
   "200x100",
   "220х100",
   "240х100",
   "255x100",
   "300х100"
  ]
 },
 {
  "name": "Avangard Katta Orena | FM-3035",
  "model": "FM-3035",
  "price": 536,
  "category_id": 3,
  "sizes": [
   "90",
   "140",
   "160",
   "180"
  ]
 },
 {
  "name": "Beatriss | FM-3036",
  "model": "FM-3036",
  "price": 438,
  "category_id": 3,
  "sizes": [
   "85х85",
   "160x85",
   "200x100",
   "255х100"
  ]
 },
 {
  "name": "Milano | FM-3037",
  "model": "FM-3037",
  "price": 170,
  "category_id": 3,
  "sizes": [
   "85х85",
   "120х85",
   "140х85",
   "160х85",
   "180х85",
   "200х100",
   "220х100",
   "240х100",
   "255х100",
   "300х100"
  ]
 },
 {
  "name": "Milano Orena | FM-3038",
  "model": "FM-3038",
  "price": 184,
  "category_id": 3,
  "sizes": [
   "90",
   "120",
   "140",
   "160",
   "180"
  ]
 },
 {
  "name": "Afina | FM-3039",
  "model": "FM-3039",
  "price": 210,
  "category_id": 3,
  "sizes": [
   "85х85",
   "120х85",
   "140х85",
   "160х85",
   "180х85",
   "200х100",
   "220х100",
   "240х100",
   "255х100",
   "300х100"
  ]
 },
 {
  "name": "Afina Orena | FM-3040",
  "model": "FM-3040",
  "price": 224,
  "category_id": 3,
  "sizes": [
   "90",
   "120",
   "140",
   "160",
   "180"
  ]
 },
 {
  "name": "Safiya | FM-3041",
  "model": "FM-3041",
  "price": 218,
  "category_id": 3,
  "sizes": [
   "85х85",
   "120х85",
   "140х85",
   "160х85",
   "180х85",
   "200х100",
   "220х100",
   "240х100",
   "255х100",
   "300х100"
  ]
 },
 {
  "name": "Safiya Orena | FM-3042",
  "model": "FM-3042",
  "price": 232,
  "category_id": 3,
  "sizes": [
   "90",
   "120",
   "140",
   "160",
   "180"
  ]
 },
 {
  "name": "King 2 | FM-3043",
  "model": "FM-3043",
  "price": 426,
  "category_id": 3,
  "sizes": [
   "85х85",
   "160x85",
   "200x100",
   "255x100"
  ]
 },
 {
  "name": "King 1 | FM-3044",
  "model": "FM-3044",
  "price": 440,
  "category_id": 3,
  "sizes": [
   "90",
   "140",
   "160",
   "180"
  ]
 },
 {
  "name": "Basfor | FM-3045",
  "model": "FM-3045",
  "price": 246,
  "category_id": 3,
  "sizes": [
   "85х85",
   "160x85",
   "200x100",
   "255х100"
  ]
 },
 {
  "name": "Basor Orena | FM-3046",
  "model": "FM-3046",
  "price": 260,
  "category_id": 3,
  "sizes": [
   "90",
   "140",
   "160",
   "180"
  ]
 },
 {
  "name": "Paris | FM-3047",
  "model": "FM-3047",
  "price": 318,
  "category_id": 3,
  "sizes": [
   "85х85",
   "160x85",
   "200x100",
   "255х100"
  ]
 },
 {
  "name": "Paris Orena | FM-3048",
  "model": "FM-3048",
  "price": 332,
  "category_id": 3,
  "sizes": [
   "90",
   "140",
   "160",
   "180"
  ]
 },
 {
  "name": "Cesar | FM-3049",
  "model": "FM-3049",
  "price": 378,
  "category_id": 3,
  "sizes": [
   "85x85",
   "120х85",
   "140x85",
   "160х85",
   "180х85",
   "200x100",
   "220х100",
   "240х100",
   "255x100"
  ]
 },
 {
  "name": "Cesar Orena | FM-3050",
  "model": "FM-3050",
  "price": 392,
  "category_id": 3,
  "sizes": [
   "90",
   "120",
   "140",
   "160"
  ]
 },
 {
  "name": "Madina 2 | FM-3051",
  "model": "FM-3051",
  "price": 298,
  "category_id": 3,
  "sizes": [
   "85x85",
   "120х85",
   "140x85",
   "160х85",
   "180х85",
   "200x100",
   "220х100",
   "240х100",
   "255x100"
  ]
 },
 {
  "name": "Madina 2 Orena | FM-3052",
  "model": "FM-3052",
  "price": 312,
  "category_id": 3,
  "sizes": [
   "90",
   "120",
   "140",
   "160",
   "180"
  ]
 },
 {
  "name": "Asia | FM-3053",
  "model": "FM-3053",
  "price": 154,
  "category_id": 3,
  "sizes": [
   "85х85",
   "120х85",
   "140х85",
   "160х85",
   "180х85",
   "200х100",
   "220х100",
   "240х100",
   "255х100",
   "280х100",
   "300х100"
  ]
 },
 {
  "name": "Asia Orena | FM-3054",
  "model": "FM-3054",
  "price": 168,
  "category_id": 3,
  "sizes": [
   "90",
   "120",
   "140",
   "160",
   "180"
  ]
 },
 {
  "name": "Moon Eco | FM-5013",
  "model": "FM-5013",
  "price": 130,
  "category_id": 1,
  "sizes": []
 },
 {
  "name": "Laura Eco | FM-5011",
  "model": "FM-5011",
  "price": 130,
  "category_id": 1,
  "sizes": []
 },
 {
  "name": "Kalakolchik Eco | FM-5023",
  "model": "FM-5023",
  "price": 130,
  "category_id": 1,
  "sizes": []
 },
 {
  "name": "Galaxy Eco | FM-5014",
  "model": "FM-5014",
  "price": 130,
  "category_id": 1,
  "sizes": []
 },
 {
  "name": "London Eco | FM-5010",
  "model": "FM-5010",
  "price": 130,
  "category_id": 1,
  "sizes": []
 },
 {
  "name": "Deko Comfort K | FM-4005 | & Pillow",
  "model": "FM-4005",
  "price": 55,
  "category_id": 7,
  "sizes": []
 },
 {
  "name": "Madrid K | FM-4004 | & Pillow",
  "model": "FM-4004",
  "price": 130,
  "category_id": 7,
  "sizes": []
 },
 {
  "name": "Madrid | FM-1010 | & Pillow",
  "model": "FM-1010",
  "price": 80,
  "category_id": 2,
  "sizes": []
 },
 {
  "name": "Milano | FM-1016 | & Pillow",
  "model": "FM-1016",
  "price": 28,
  "category_id": 2,
  "sizes": []
 },
 {
  "name": "Asia | FM-1021 | & Pillow",
  "model": "FM-1021",
  "price": 24,
  "category_id": 2,
  "sizes": []
 },
 {
  "name": "Avangard | FM-1011 | & Pillow",
  "model": "FM-1011",
  "price": 116,
  "category_id": 2,
  "sizes": []
 },
 {
  "name": "Victoria | FM-1013 | & Pillow",
  "model": "FM-1013",
  "price": 75,
  "category_id": 2,
  "sizes": []
 },
 {
  "name": "Paris | FM-1024 | & Pillow",
  "model": "FM-1024",
  "price": 65,
  "category_id": 2,
  "sizes": []
 },
 {
  "name": "Lavantera | FM-1015 | & Pillow",
  "model": "FM-1015",
  "price": 131,
  "category_id": 2,
  "sizes": []
 },
 {
  "name": "Sergio | FM-1025 | & Pillow",
  "model": "FM-1025",
  "price": 28,
  "category_id": 2,
  "sizes": []
 },
 {
  "name": "Dream | FM-6001",
  "model": "FM-6001",
  "price": 50,
  "category_id": 5,
  "sizes": []
 },
 {
  "name": "Sun | FM-6005",
  "model": "FM-6005",
  "price": 135,
  "category_id": 5,
  "sizes": []
 }
]


class Command(BaseCommand):
    help = "Chinor katalogidagi mahsulotlarni yuklash"

    def handle(self, *args, **options):
        added, skipped = 0, 0
        for p in PRODUCTS:
            if ProductModel.objects.filter(name=p['name']).exists():
                skipped += 1
                continue
            try:
                category = CategoryModel.objects.get(pk=p['category_id'])
            except CategoryModel.DoesNotExist:
                category = CategoryModel.objects.first()

            product = ProductModel(
                name=p['name'],
                price=int(p['price']),          # USD — sayt avtomatik so'mga aylantiradi
                category=category,
            )
            # rasm: media/products/catalog/FM-XXXX.jpg (oldindan joylashtirilgan)
            product.image.name = f"products/catalog/{p['model']}.jpg"
            product.save()

            for size_title in p.get('sizes', []):
                size, _ = SizeModel.objects.get_or_create(title=size_title)
                product.sizes.add(size)

            added += 1
            self.stdout.write(f"  + {p['name']}")

        self.stdout.write(self.style.SUCCESS(
            f"Tayyor: {added} ta qo'shildi, {skipped} ta allaqachon mavjud edi."))
