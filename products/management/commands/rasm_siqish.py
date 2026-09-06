"""
Barcha rasmlarning kichik (WebP) nusxalarini oldindan yasab qo'yadi.

Ishga tushirish:

    python manage.py rasm_siqish

Nima qiladi:
  • media/ dagi har bir rasmdan 200 / 600 / 1200 px WebP nusxa yasaydi
  • ularni media/cache/<kenglik>/ ichiga saqlaydi
  • ASL FAYLLARGA TEGMAYDI

Bir marta ishga tushirish kifoya. Yangi mahsulot qo'shganingizda
nusxa birinchi ochilganda o'zi yasaladi, yoki shu buyruqni qayta bering.
"""

import os
import time

from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import models

from products.templatetags.rasm import make_thumbs, _out_rel

KENGLIKLAR = [200, 600, 1200, 2000]


class Command(BaseCommand):
    help = "Barcha rasmlardan kichik WebP nusxalar yasaydi (sayt tez ochilishi uchun)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--kengliklar",
            default=",".join(str(k) for k in KENGLIKLAR),
            help="Vergul bilan: 200,600,1200,2000",
        )
        parser.add_argument(
            "--qayta",
            action="store_true",
            help="Tayyor nusxalar bo'lsa ham qaytadan yasash (sifat o'zgarganda)",
        )

    def handle(self, *args, **opts):
        from django.conf import settings

        kengliklar = [int(x) for x in str(opts["kengliklar"]).split(",") if x.strip()]

        # 1) Bazadagi barcha rasm maydonlarini yig'amiz
        yollar = set()
        for model in apps.get_models():
            rasm_maydonlari = [
                f.name for f in model._meta.get_fields()
                if isinstance(f, models.ImageField) or isinstance(f, models.FileField)
            ]
            if not rasm_maydonlari:
                continue
            try:
                qs = model.objects.all().only("id", *rasm_maydonlari)
                for obj in qs.iterator():
                    for fname in rasm_maydonlari:
                        f = getattr(obj, fname, None)
                        nomi = getattr(f, "name", "") or ""
                        if nomi and not nomi.startswith("cache/"):
                            yollar.add(nomi)
            except Exception as e:  # noqa: BLE001
                self.stderr.write(f"  ! {model.__name__}: {e}")

        jami = len(yollar)
        self.stdout.write(f"\nBazada {jami} ta rasm topildi. Kengliklar: {kengliklar}\n")
        if not jami:
            return

        boshlandi = time.time()
        asl_hajm = yangi_hajm = 0
        yasaldi = otkazildi = xato = 0

        for i, rel in enumerate(sorted(yollar), 1):
            src = os.path.join(settings.MEDIA_ROOT, rel.replace("/", os.sep))
            try:
                asl_hajm += os.path.getsize(src)
            except OSError:
                xato += 1
                continue

            y, o, x = make_thumbs(rel, kengliklar, qayta=opts.get("qayta", False))
            yasaldi += y
            otkazildi += o
            xato += x

            for w in kengliklar:
                out = os.path.join(
                    settings.MEDIA_ROOT, _out_rel(rel, w).replace("/", os.sep)
                )
                try:
                    yangi_hajm += os.path.getsize(out)
                except OSError:
                    pass

            if i % 10 == 0 or i == jami:
                otgan = time.time() - boshlandi
                qolgan = (otgan / i) * (jami - i)
                self.stdout.write(
                    f"  {i}/{jami}  ({i * 100 // jami}%)   "
                    f"~{int(qolgan // 60)} daq {int(qolgan % 60)} son qoldi"
                )

        mb = 1024 * 1024
        self.stdout.write("\n" + "=" * 46)
        self.stdout.write(f"  Yasaldi        : {yasaldi} ta")
        self.stdout.write(f"  Allaqachon bor : {otkazildi} ta")
        self.stdout.write(f"  Xato           : {xato} ta")
        self.stdout.write(f"  Asl rasmlar    : {asl_hajm / mb:.0f} MB")
        self.stdout.write(f"  Kichik nusxalar: {yangi_hajm / mb:.0f} MB")
        if yangi_hajm:
            self.stdout.write(
                f"  Sayt {asl_hajm / max(yangi_hajm, 1):.0f} barobar yengillashdi"
            )
        self.stdout.write("=" * 46 + "\n")
