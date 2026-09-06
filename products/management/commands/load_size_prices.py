"""
Narxnomadagi (Price 01.02.2026) har o'lcham narxlarini mahsulotlarga yuklaydi.
Ishlatish:  python manage.py load_size_prices
Mahsulot nomi ichidagi FM-XXXX kodi bo'yicha moslanadi. Qayta ishga
tushirilsa dublikat yaratmaydi (mavjud o'lcham yangilanadi).
"""
from django.core.management.base import BaseCommand
from products.models import ProductModel, ProductSizePrice

SIZES = {
 "FM-3002": [
  {
   "title": "85х85 (4-1)",
   "price": 158
  },
  {
   "title": "120х85 (4-1)",
   "price": 171
  },
  {
   "title": "140х85 (6-1)",
   "price": 234
  },
  {
   "title": "160х85 (6-1)",
   "price": 247
  },
  {
   "title": "180х85 (8-1)",
   "price": 307
  },
  {
   "title": "200х100 (8-1)",
   "price": 356
  },
  {
   "title": "220х100 (8-1)",
   "price": 372
  },
  {
   "title": "240х100 (10-1)",
   "price": 439
  },
  {
   "title": "255х100 (10-1)",
   "price": 455
  },
  {
   "title": "280х100 (10-1)",
   "price": 471
  },
  {
   "title": "300х100 (12-1)",
   "price": 537
  }
 ],
 "FM-3037": [
  {
   "title": "85х85 (4-1)",
   "price": 170
  },
  {
   "title": "120х85 (6-1)",
   "price": 239
  },
  {
   "title": "140х85 (6-1)",
   "price": 252
  },
  {
   "title": "160х85 (6-1)",
   "price": 265
  },
  {
   "title": "180х85 (8-1)",
   "price": 331
  },
  {
   "title": "200х100 (8-1)",
   "price": 380
  },
  {
   "title": "220х100 (8-1)",
   "price": 396
  },
  {
   "title": "240х100 (8-1)",
   "price": 413
  },
  {
   "title": "255х100 (10-1)",
   "price": 485
  },
  {
   "title": "300х100 (10-1)",
   "price": 517
  }
 ],
 "FM-3039": [
  {
   "title": "85х85 (4-1)",
   "price": 210
  },
  {
   "title": "120х85 (6-1)",
   "price": 299
  },
  {
   "title": "140х85 (6-1)",
   "price": 312
  },
  {
   "title": "160х85 (6-1)",
   "price": 325
  },
  {
   "title": "180х85 (8-1)",
   "price": 411
  },
  {
   "title": "200х100 (8-1)",
   "price": 460
  },
  {
   "title": "220х100 (8-1)",
   "price": 476
  },
  {
   "title": "240х100 (8-1)",
   "price": 493
  },
  {
   "title": "255х100 (10-1)",
   "price": 585
  },
  {
   "title": "300х100 (10-1)",
   "price": 617
  }
 ],
 "FM-3041": [
  {
   "title": "85х85 (4-1)",
   "price": 218
  },
  {
   "title": "120х85 (6-1)",
   "price": 311
  },
  {
   "title": "140х85 (6-1)",
   "price": 324
  },
  {
   "title": "160х85 (6-1)",
   "price": 337
  },
  {
   "title": "180х85 (8-1)",
   "price": 427
  },
  {
   "title": "200х100 (8-1)",
   "price": 476
  },
  {
   "title": "220х100 (8-1)",
   "price": 492
  },
  {
   "title": "240х100 (8-1)",
   "price": 509
  },
  {
   "title": "255х100 (10-1)",
   "price": 605
  },
  {
   "title": "300х100 (10-1)",
   "price": 637
  }
 ],
 "FM-3001": [
  {
   "title": "90 (4-1)",
   "price": 172
  },
  {
   "title": "120 (6-1)",
   "price": 256
  },
  {
   "title": "140 (6-1)",
   "price": 283
  },
  {
   "title": "160 (8-1)",
   "price": 367
  },
  {
   "title": "180 (10-1)",
   "price": 457
  }
 ],
 "FM-3038": [
  {
   "title": "90 (4-1)",
   "price": 184
  },
  {
   "title": "120 (6-1)",
   "price": 274
  },
  {
   "title": "140 (6-1)",
   "price": 301
  },
  {
   "title": "160 (8-1)",
   "price": 391
  },
  {
   "title": "180 (10-1)",
   "price": 487
  }
 ],
 "FM-3040": [
  {
   "title": "90 (4-1)",
   "price": 224
  },
  {
   "title": "120 (6-1)",
   "price": 334
  },
  {
   "title": "140 (6-1)",
   "price": 361
  },
  {
   "title": "160 (8-1)",
   "price": 471
  },
  {
   "title": "180 (10-1)",
   "price": 587
  }
 ],
 "FM-3042": [
  {
   "title": "90 (4-1)",
   "price": 232
  },
  {
   "title": "120 (6-1)",
   "price": 346
  },
  {
   "title": "140 (6-1)",
   "price": 373
  },
  {
   "title": "160 (8-1)",
   "price": 487
  },
  {
   "title": "180 (10-1)",
   "price": 607
  }
 ],
 "FM-3003": [
  {
   "title": "85x85 (4-1)",
   "price": 210
  },
  {
   "title": "120х85 (4-1)",
   "price": 223
  },
  {
   "title": "140x85 (6-1)",
   "price": 312
  },
  {
   "title": "160х85 (6-1)",
   "price": 325
  },
  {
   "title": "180х85 (8-1)",
   "price": 411
  },
  {
   "title": "200x100 (8-1)",
   "price": 460
  },
  {
   "title": "280x100 (10-1)",
   "price": 601
  }
 ],
 "FM-3019": [
  {
   "title": "85x85 (4-1)",
   "price": 338
  },
  {
   "title": "120х85 (6-1)",
   "price": 491
  },
  {
   "title": "140x85 (6-1)",
   "price": 504
  },
  {
   "title": "160х85 (6-1)",
   "price": 517
  },
  {
   "title": "180х85 (8-1)",
   "price": 667
  },
  {
   "title": "200x100 (8-1)",
   "price": 716
  },
  {
   "title": "220х100 (8-1)",
   "price": 732
  },
  {
   "title": "240х100 (10-1)",
   "price": 889
  },
  {
   "title": "255x100 (10-1)",
   "price": 905
  },
  {
   "title": "300х100 (12-1)",
   "price": 1077
  }
 ],
 "FM-3034": [
  {
   "title": "85x85 (4-1)",
   "price": 322
  },
  {
   "title": "120х85 (6-1)",
   "price": 467
  },
  {
   "title": "140x85 (6-1)",
   "price": 480
  },
  {
   "title": "160х85 (6-1)",
   "price": 493
  },
  {
   "title": "180х85 (8-1)",
   "price": 635
  },
  {
   "title": "200x100 (8-1)",
   "price": 684
  },
  {
   "title": "220х100 (8-1)",
   "price": 700
  },
  {
   "title": "240х100 (10-1)",
   "price": 849
  },
  {
   "title": "255x100 (10-1)",
   "price": 865
  },
  {
   "title": "300х100 (12-1)",
   "price": 1029
  }
 ],
 "FM-3009": [
  {
   "title": "85х85 (4-1)",
   "price": 358
  },
  {
   "title": "120х85 (4-1)",
   "price": 371
  },
  {
   "title": "140x85 (6-1)",
   "price": 534
  },
  {
   "title": "160x85 (6-1)",
   "price": 547
  },
  {
   "title": "200х100 (8-1)",
   "price": 756
  },
  {
   "title": "220х100 (8-1)",
   "price": 772
  },
  {
   "title": "240х100 (8-1)",
   "price": 789
  },
  {
   "title": "255x100 (10-1)",
   "price": 955
  },
  {
   "title": "300x100 (10-1)",
   "price": 987
  }
 ],
 "FM-3045": [
  {
   "title": "85х85 (4-1)",
   "price": 246
  },
  {
   "title": "160x85 (6-1)",
   "price": 379
  },
  {
   "title": "200x100 (8-1)",
   "price": 532
  },
  {
   "title": "255х100 (10-1)",
   "price": 675
  }
 ],
 "FM-3026": [
  {
   "title": "90 (4-1)",
   "price": 224
  },
  {
   "title": "120 (6-1)",
   "price": 334
  },
  {
   "title": "140 (6-1)",
   "price": 361
  },
  {
   "title": "160 (8-1)",
   "price": 471
  },
  {
   "title": "180 (8-1)",
   "price": 511
  }
 ],
 "FM-3013": [
  {
   "title": "90 (4-1)",
   "price": 352
  },
  {
   "title": "120 (6-1)",
   "price": 526
  },
  {
   "title": "140 (6-1)",
   "price": 553
  },
  {
   "title": "160 (8-1)",
   "price": 727
  },
  {
   "title": "180 (10-1)",
   "price": 907
  }
 ],
 "FM-3014": [
  {
   "title": "90 (4-1)",
   "price": 336
  },
  {
   "title": "120 (6-1)",
   "price": 502
  },
  {
   "title": "140 (6-1)",
   "price": 529
  },
  {
   "title": "160 (8-1)",
   "price": 695
  },
  {
   "title": "180 (10-1)",
   "price": 867
  }
 ],
 "FM-3008": [
  {
   "title": "90 (4-1)",
   "price": 372
  },
  {
   "title": "120 (4-1)",
   "price": 406
  },
  {
   "title": "140 (6-1)",
   "price": 583
  },
  {
   "title": "160 (8-1)",
   "price": 767
  },
  {
   "title": "180 (8-1)",
   "price": 807
  }
 ],
 "FM-3046": [
  {
   "title": "90 (4-1)",
   "price": 260
  },
  {
   "title": "140 (6-1)",
   "price": 415
  },
  {
   "title": "160 (8-1)",
   "price": 543
  },
  {
   "title": "180 (10-1)",
   "price": 677
  }
 ],
 "FM-3043": [
  {
   "title": "85х85 (4-1)",
   "price": 426
  },
  {
   "title": "160x85 (6-1)",
   "price": 649
  },
  {
   "title": "200x100 (8-1)",
   "price": 892
  },
  {
   "title": "255x100 (10-1)",
   "price": 1125
  }
 ],
 "FM-3036": [
  {
   "title": "85х85 (4-1)",
   "price": 438
  },
  {
   "title": "160x85 (6-1)",
   "price": 667
  },
  {
   "title": "200x100 (8-1)",
   "price": 916
  },
  {
   "title": "255х100 (10-1)",
   "price": 1155
  }
 ],
 "FM-3015": [
  {
   "title": "85х85 (4-1)",
   "price": 522
  },
  {
   "title": "160x85 (6-1)",
   "price": 793
  },
  {
   "title": "200x100 (8-1)",
   "price": 1084
  },
  {
   "title": "255х100 (10-1)",
   "price": 1365
  }
 ],
 "FM-3016": [
  {
   "title": "85х85 (4-1)",
   "price": 378
  },
  {
   "title": "140x85 (6-1)",
   "price": 564
  },
  {
   "title": "160x85 (6-1)",
   "price": 577
  },
  {
   "title": "180х85 (8-1)",
   "price": 747
  },
  {
   "title": "200x100 (8-1)",
   "price": 796
  },
  {
   "title": "255x100 (10-1)",
   "price": 1005
  },
  {
   "title": "300х100 (10-1)",
   "price": 1227
  }
 ],
 "FM-3047": [
  {
   "title": "85х85 (4-1)",
   "price": 318
  },
  {
   "title": "160x85 (6-1)",
   "price": 487
  },
  {
   "title": "200x100 (8-1)",
   "price": 676
  },
  {
   "title": "255х100 (10-1)",
   "price": 855
  }
 ],
 "FM-3044": [
  {
   "title": "90 (4-1)",
   "price": 440
  },
  {
   "title": "140 (6-1)",
   "price": 685
  },
  {
   "title": "160 (8-1)",
   "price": 903
  },
  {
   "title": "180 (10-1)",
   "price": 1127
  }
 ],
 "FM-3033": [
  {
   "title": "90 (4-1)",
   "price": 452
  },
  {
   "title": "140 (6-1)",
   "price": 703
  },
  {
   "title": "160 (8-1)",
   "price": 927
  },
  {
   "title": "180 (8-1)",
   "price": 967
  }
 ],
 "FM-3035": [
  {
   "title": "90 (4-1)",
   "price": 536
  },
  {
   "title": "140 (6-1)",
   "price": 829
  },
  {
   "title": "160 (8-1)",
   "price": 1095
  },
  {
   "title": "180 (10-1)",
   "price": 1367
  }
 ],
 "FM-3017": [
  {
   "title": "90 (4-1)",
   "price": 392
  },
  {
   "title": "120 (4-1)",
   "price": 426
  },
  {
   "title": "140 (6-1)",
   "price": 613
  },
  {
   "title": "160 (8-1)",
   "price": 807
  },
  {
   "title": "180 (10-1)",
   "price": 1007
  }
 ],
 "FM-3048": [
  {
   "title": "90 (4-1)",
   "price": 332
  },
  {
   "title": "140 (6-1)",
   "price": 523
  },
  {
   "title": "160 (8-1)",
   "price": 687
  },
  {
   "title": "180 (8-1)",
   "price": 727
  }
 ],
 "FM-3049": [
  {
   "title": "85x85 (4-1)",
   "price": 378
  },
  {
   "title": "120х85 (6-1)",
   "price": 551
  },
  {
   "title": "140x85 (6-1)",
   "price": 564
  },
  {
   "title": "160х85 (6-1)",
   "price": 577
  },
  {
   "title": "180х85 (8-1)",
   "price": 747
  },
  {
   "title": "200x100 (8-1)",
   "price": 796
  },
  {
   "title": "220х100 (8-1)",
   "price": 812
  },
  {
   "title": "240х100 (10-1)",
   "price": 989
  },
  {
   "title": "255x100 (10-1)",
   "price": 1005
  }
 ],
 "FM-3051": [
  {
   "title": "85x85 (4-1)",
   "price": 298
  },
  {
   "title": "120х85 (6-1)",
   "price": 431
  },
  {
   "title": "140x85 (6-1)",
   "price": 444
  },
  {
   "title": "160х85 (6-1)",
   "price": 457
  },
  {
   "title": "180х85 (8-1)",
   "price": 587
  },
  {
   "title": "200x100 (8-1)",
   "price": 636
  },
  {
   "title": "220х100 (8-1)",
   "price": 652
  },
  {
   "title": "240х100 (10-1)",
   "price": 789
  },
  {
   "title": "255x100 (10-1)",
   "price": 805
  }
 ],
 "FM-3053": [
  {
   "title": "85х85 (4-1)",
   "price": 154
  },
  {
   "title": "120х85 (4-1)",
   "price": 167
  },
  {
   "title": "140х85 (6-1)",
   "price": 228
  },
  {
   "title": "160х85 (6-1)",
   "price": 241
  },
  {
   "title": "180х85 (8-1)",
   "price": 299
  },
  {
   "title": "200х100 (8-1)",
   "price": 348
  },
  {
   "title": "220х100 (8-1)",
   "price": 364
  },
  {
   "title": "240х100 (10-1)",
   "price": 429
  },
  {
   "title": "255х100 (10-1)",
   "price": 445
  },
  {
   "title": "280х100 (10-1)",
   "price": 461
  },
  {
   "title": "300х100 (12-1)",
   "price": 525
  }
 ],
 "FM-3050": [
  {
   "title": "90 (4-1)",
   "price": 392
  },
  {
   "title": "120 (6-1)",
   "price": 586
  },
  {
   "title": "140 (6-1)",
   "price": 613
  },
  {
   "title": "160 (8-1)",
   "price": 807
  }
 ],
 "FM-3052": [
  {
   "title": "90 (4-1)",
   "price": 312
  },
  {
   "title": "120 (6-1)",
   "price": 466
  },
  {
   "title": "140 (6-1)",
   "price": 493
  },
  {
   "title": "160 (8-1)",
   "price": 647
  },
  {
   "title": "180 (10-1)",
   "price": 807
  }
 ],
 "FM-3054": [
  {
   "title": "90 (4-1)",
   "price": 168
  },
  {
   "title": "120 (6-1)",
   "price": 250
  },
  {
   "title": "140 (6-1)",
   "price": 277
  },
  {
   "title": "160 (8-1)",
   "price": 359
  },
  {
   "title": "180 (10-1)",
   "price": 447
  }
 ]
}


class Command(BaseCommand):
    help = "O'lcham narxlarini yuklash"

    def handle(self, *args, **options):
        added, updated, matched = 0, 0, 0
        for code, sizes in SIZES.items():
            product = ProductModel.objects.filter(name__contains=code).first()
            if not product:
                self.stdout.write(f"  ? {code} — mahsulot topilmadi, o'tkazib yuborildi")
                continue
            matched += 1
            for i, sz in enumerate(sizes):
                obj, created = ProductSizePrice.objects.update_or_create(
                    product=product, title=sz['title'],
                    defaults={'price': sz['price'], 'order': i},
                )
                if created:
                    added += 1
                else:
                    updated += 1
        self.stdout.write(self.style.SUCCESS(
            f"Tayyor: {matched} mahsulot, {added} o'lcham qo'shildi, {updated} yangilandi."))
