"""
Kategoriya nomlaridagi xatolarni tuzatadi.

Ishga tushirish:  python manage.py nomlarni_tuzatish

Faqat quyida sanab o'tilgan kategoriyalar tegiladi, boshqalarga tegilmaydi.
Ikki marta ishga tushirsangiz ham zarari yo'q — o'zgargani qayta yozilmaydi.
"""

from django.core.management.base import BaseCommand

from products.models import CategoryModel

# eski nomi  ->  yangi nomlar (en / uz / ru)
TUZATISHLAR = {
    "Collections Sits": {
        "name_en": "Collections",
        "name_uz": "Kolleksiyalar",
        "name_ru": "Коллекции",
    },
}


class Command(BaseCommand):
    help = "Kategoriya nomlaridagi xato va chala tarjimalarni tuzatadi"

    def handle(self, *args, **opts):
        ozgardi = 0

        for eski_nom, yangi in TUZATISHLAR.items():
            kat = (CategoryModel.objects.filter(name=eski_nom).first()
                   or CategoryModel.objects.filter(name_en=eski_nom).first()
                   or CategoryModel.objects.filter(name=yangi["name_en"]).first())
            if kat is None:
                self.stdout.write(f"  - '{eski_nom}' topilmadi, o'tkazib yuborildi")
                continue

            oldin = (kat.name, kat.name_uz, kat.name_ru)

            kat.name = yangi["name_en"]
            kat.name_en = yangi["name_en"]
            kat.name_uz = yangi["name_uz"]
            kat.name_ru = yangi["name_ru"]
            kat.save()

            keyin = (kat.name, kat.name_uz, kat.name_ru)
            if oldin != keyin:
                ozgardi += 1
                self.stdout.write("  Tuzatildi:")
                self.stdout.write(f"     en: {oldin[0]!r}  ->  {keyin[0]!r}")
                self.stdout.write(f"     uz: {oldin[1]!r}  ->  {keyin[1]!r}")
                self.stdout.write(f"     ru: {oldin[2]!r}  ->  {keyin[2]!r}")
            else:
                self.stdout.write(f"  '{kat.name}' allaqachon to'g'ri")

        self.stdout.write("")
        self.stdout.write("─" * 46)
        self.stdout.write(f"  Jami o'zgartirildi: {ozgardi} ta kategoriya")

        # Nazorat uchun barcha kategoriyalarni ko'rsatamiz
        self.stdout.write("")
        self.stdout.write("  Hozirgi kategoriyalar:")
        for k in CategoryModel.objects.all().order_by("name"):
            soni = k.products.count()
            self.stdout.write(f"     {soni:>3} ta | {k.name} | {k.name_uz} | {k.name_ru}")
        self.stdout.write("─" * 46)
