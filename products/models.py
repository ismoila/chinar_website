from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from products.validators import rating_value_validate
from django.contrib.auth.models import User
import random
from django.utils import timezone
from datetime import timedelta
import random
from django.utils.text import slugify
from unidecode import unidecode
# from django.utils import timezone

# Create your models here.
class CategoryModel(models.Model):
    image = models.ImageField(upload_to="category")
    name = models.CharField(max_length=24)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

        
class SizeModel(models.Model):
    title = models.CharField(max_length=24)

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        verbose_name = "Size"
        verbose_name_plural = "Sizes"

class ColorModel(models.Model):
    GROUP_CHOICES = [
        ('weave',  "To'qima"),
        ('rope',   "Eshilgan arqon"),
        ('rattan', "Rattan tayoqcha"),
        ('fabric', "Mato"),
    ]
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    group = models.CharField(max_length=20, choices=GROUP_CHOICES,
                             default='weave', verbose_name="Kategoriya")
    image = models.ImageField(upload_to="colors", null=True, blank=True) 

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = "Color"
        verbose_name_plural = "Colors"


class ProductModel(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    price = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products")
    discount = models.PositiveIntegerField(default=0)
    discount_days = models.PositiveIntegerField(default=0)
    discount_start = models.DateTimeField(null=True, blank=True)
    discount_end = models.DateTimeField(null=True, blank=True)
    rating = models.PositiveIntegerField(default=1, validators=[rating_value_validate])
    category = models.ForeignKey(CategoryModel, on_delete=models.CASCADE, related_name="products")
    sizes = models.ManyToManyField(SizeModel, blank=True)
    colors = models.ManyToManyField(ColorModel)
    group_code = models.CharField(max_length=50, blank=True, db_index=True,
                              help_text="Bir modelning barcha rang variantlari uchun bir xil kod")
    # ── Mijoz uchun ma'lumot (ixtiyoriy, bo'sh qolsa saytda ko'rinmaydi) ──
    description = models.TextField(blank=True, default="",
                              verbose_name="Tavsif",
                              help_text="Mahsulot haqida matn: nima uchun qulay, qayerga mos keladi, "
                                        "parvarishi. 2-4 gap yetarli. Bo'sh qolsa saytda ko'rinmaydi.")
    material = models.CharField(max_length=200, blank=True, default="",
                              verbose_name="Material",
                              help_text="Masalan: Polirotang + alyumin karkas")

    # ── SEO ──
    meta_title = models.CharField(
        max_length=70, blank=True, default="",
        verbose_name="SEO sarlavha (title)",
        help_text="Google qidiruv natijasida chiqadigan sarlavha. Bo'sh qolsa, mahsulot nomi ishlatiladi. Maksimal 70 belgi."
    )
    meta_description = models.CharField(
        max_length=160, blank=True, default="",
        verbose_name="SEO tavsif (description)",
        help_text="Google qidiruv natijasida sarlavha ostida chiqadigan qisqa matn. Bo'sh qolsa, mahsulot tavsifidan olinadi. Maksimal 160 belgi."
    )

    # ── Ombor ──
    in_stock = models.BooleanField(default=True,
                              verbose_name="Sotuvda bor",
                              help_text="Belgini olib tashlasangiz, saytda 'Vaqtincha yo'q' deb "
                                        "ko'rinadi va savatga qo'shib bo'lmaydi. Mahsulot o'chmaydi.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # ── Slug generatsiyasi — har doim O'ZBEKCHA nomdan yasaladi ──
        if not self.slug:
            manba_nom = getattr(self, 'name_uz', None) or self.name
            base_slug = slugify(unidecode(manba_nom))[:80]
            slug = base_slug
            counter = 1
            while ProductModel.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # ── Discount logikasi ──
        if self.discount > 0 and self.discount_days > 0:
            self.discount_start = timezone.now()
            self.discount_end = timezone.now() + timedelta(days=self.discount_days)
        if self.discount == 0:
            self.discount_start = None
            self.discount_end = None
            self.discount_days = 0
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('product_detail', kwargs={'slug': self.slug})

    # ── Reyting: sharhlardan hisoblanadi (qo'lda yozilmaydi) ──
    @property
    def sharhlar_soni(self):
        return self.reviews.count() if hasattr(self, "reviews") else 0

    @property
    def ortacha_reyting(self):
        """Sharhlar bo'yicha o'rtacha baho. Sharh bo'lmasa — None."""
        from django.db.models import Avg
        if not hasattr(self, "reviews"):
            return None
        natija = self.reviews.aggregate(o=Avg("rating"))["o"]
        return round(natija, 1) if natija else None

    @property
    def is_discount_active(self):
        now = timezone.now()
        if self.discount and self.discount > 0:
            if self.discount_start and self.discount_end:
                return self.discount_start <= now <= self.discount_end
            return True
        return False

    @property
    def get_real_price(self):
        if self.is_discount_active:
            total = self.price - ((self.price / 100) * self.discount)
            return int(total)
        return self.price

    @property
    def days_left(self):
        if self.discount_end and self.is_discount_active:
            diff = self.discount_end - timezone.now()
            return diff.days
        return 0

    @property
    def is_new(self):
        current_time = timezone.now()
        diff = (current_time - self.created_at).days
        return diff <= 1

    @property
    def get_price_uzs(self):
        sp = self.size_prices.first()
        if sp:
            return sp.price_uzs
        from pages.utils import get_usd_to_uzs_rate
        rate = get_usd_to_uzs_rate()
        raw = self.get_real_price * rate
        rounded = round(raw / 1000) * 1000
        return int(rounded)

    def price_uzs_for_size(self, size_title=None):
        if size_title:
            sp = self.size_prices.filter(title=size_title).first()
            if sp:
                return sp.price_uzs
        return int(self.get_price_uzs)

    def original_uzs_for_size(self, size_title=None):
        if size_title:
            sp = self.size_prices.filter(title=size_title).first()
            if sp:
                return sp.original_price_uzs
        return int(self.get_original_price_uzs)

    @property
    def get_original_price_uzs(self):
        sp = self.size_prices.first()
        if sp:
            return sp.original_price_uzs
        from pages.utils import get_usd_to_uzs_rate
        rate = get_usd_to_uzs_rate()
        raw = self.price * rate
        rounded = round(raw / 1000) * 1000
        return int(rounded)

    class Meta:
        ordering = ['order']
        verbose_name = "Product"
        verbose_name_plural = "Products"

class ProductColorModel(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name="color_variants")
    color = models.ForeignKey(ColorModel, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} — {self.color.name}"

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Product color"
        verbose_name_plural = "Product colors"


class ProductColorImageModel(models.Model):
    product_color = models.ForeignKey(ProductColorModel, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="product_colors")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.product_color} rasmi"
    

class WishlistModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} | {self.product.name}"
    
    

class PhoneVerification(models.Model):
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        # Code expires after 5 minutes
        diff = timezone.now() - self.created_at
        return diff.seconds > 300

    def __str__(self):
        return f"{self.phone} - {self.code}"
    
    
class ProductImage(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - image {self.order}"
    


class FurnitureSet(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='sets/')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


    @property
    def total_uzs(self):
        """To'plam ichidagi barcha mahsulotlar narxi (UZS)"""
        return sum(int(sp.product.get_price_uzs) for sp in self.set_products.all())


class FurnitureSetProduct(models.Model):
    furniture_set = models.ForeignKey(FurnitureSet, on_delete=models.CASCADE, related_name='set_products')
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.furniture_set.name} - {self.product.name}"
    
    
class ProfileModel(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    
    
class ReviewModel(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    text = models.TextField(max_length=1000)
    rating = models.PositiveIntegerField(default=5)
    images = models.ImageField(upload_to='reviews/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.product.name}"
    
    
class ReplyModel(models.Model):
    review = models.ForeignKey(ReviewModel, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} → {self.review}"

class SearchQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='searches')
    session_key = models.CharField(max_length=40, null=True, blank=True)
    term = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        
        
class IdeaModel(models.Model):
    image = models.ImageField(upload_to="ideas")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Idea #{self.id}"


class IdeaPinModel(models.Model):
    idea = models.ForeignKey(IdeaModel, on_delete=models.CASCADE, related_name="pins")
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name="idea_pins")
    left_percent = models.PositiveIntegerField(help_text="Masalan: 40 (40% chapdan)")
    top_percent = models.PositiveIntegerField(help_text="Masalan: 50 (50% yuqoridan)")
    card_align_left = models.BooleanField(default=False, help_text="Karta chapga ochilsinmi (idea-pin-card-left)")

    def __str__(self):
        return f"{self.product.name} pin on {self.idea}"





class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Awaiting confirmation')),
        ('confirmed', _('Confirmed')),
        ('shipping', _('In delivery')),
        ('completed', _('Completed')),
        ('canceled', _('Canceled')),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('processing', _('Processing')),
        ('paid', _('Paid')),
        ('unpaid', _('Not paid')),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_id = models.CharField(max_length=20, unique=True, blank=True)

    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64, blank=True)
    phone = models.CharField(max_length=20)

    delivery_method = models.CharField(max_length=20, default='delivery')  # delivery / pickup
    region = models.CharField(max_length=64, blank=True)
    district = models.CharField(max_length=64, blank=True)
    address = models.CharField(max_length=255, blank=True)
    floor = models.CharField(max_length=20, blank=True)

    payment_method = models.CharField(max_length=20, default='cash')  # payme / click / cash
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='processing')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    comment = models.TextField(blank=True)
    total_price = models.PositiveIntegerField(default=0)

    promo_code = models.CharField(max_length=30, blank=True)
    discount_amount = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = str(random.randint(10**17, 10**18 - 1))  # Uzum-uslub 18 xonali
        super().save(*args, **kwargs)

    # tab filtri uchun
    @property
    def is_paid(self):
        return self.payment_status == 'paid'

    @property
    def is_active(self):
        return self.status in ('pending', 'confirmed', 'shipping')

    def get_payment_method_display_name(self):
        return {'payme': 'Payme', 'click': 'Click', 'cash': 'Cash on Delivery'}.get(self.payment_method, self.payment_method)

    def __str__(self):
        return f"Order {self.order_id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(ProductModel, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField(default=0)
    size = models.CharField(max_length=50, blank=True)   # tanlangan o'lcham
    color = models.CharField(max_length=50, blank=True)  # tanlangan rang

    def __str__(self):
        return f"{self.product} x{self.quantity}"

class PromoCode(models.Model):
    """Admin paneldan yaratiladigan promokodlar (masalan: CHINAR10 — 10% chegirma)"""
    code = models.CharField(max_length=30, unique=True)
    discount_percent = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    max_uses = models.PositiveIntegerField(default=0)
    used_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Promo code"
        verbose_name_plural = "Promo codes"

    def is_valid(self):
        if not self.is_active:
            return False
        if self.valid_until and timezone.now() > self.valid_until:
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True

    def __str__(self):
        return f"{self.code} (-{self.discount_percent}%)"


class PaymentTransaction(models.Model):
    """Payme/Click to'lov tranzaksiyalari"""
    PROVIDERS = [('payme', 'Payme'), ('click', 'Click')]

    provider = models.CharField(max_length=10, choices=PROVIDERS)
    trans_id = models.CharField(max_length=64, db_index=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    amount = models.PositiveBigIntegerField(default=0)
    state = models.IntegerField(default=0)
    reason = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    perform_time = models.DateTimeField(null=True, blank=True)
    cancel_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('provider', 'trans_id')
        verbose_name = "Payment transaction"
        verbose_name_plural = "Payment transactions"

    def __str__(self):
        return f"{self.provider} #{self.trans_id} — {self.order.order_id} ({self.state})"


class ProductSizePrice(models.Model):
    """Mahsulotning har bir o'lchami uchun alohida narx (USD)"""
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='size_prices')
    title = models.CharField(max_length=50)              # masalan: 160х85 (6-1)
    price = models.PositiveIntegerField(default=0)       # USD
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        unique_together = ('product', 'title')
        verbose_name = "Size price"
        verbose_name_plural = "Size prices"

    @property
    def price_uzs(self):
        """Chegirma qo'llangan narx (UZS) — mahsulot chegirmasi o'lchamga ham tegishli"""
        from pages.utils import get_usd_to_uzs_rate
        rate = get_usd_to_uzs_rate()
        price = self.price
        if self.product.is_discount_active:
            price = price - (price / 100) * self.product.discount
        return int(round(price * rate / 1000) * 1000)

    @property
    def original_price_uzs(self):
        """Chegirmasiz asl narx (UZS)"""
        from pages.utils import get_usd_to_uzs_rate
        rate = get_usd_to_uzs_rate()
        return int(round(self.price * rate / 1000) * 1000)

    def __str__(self):
        return f"{self.product.name} — {self.title} (${self.price})"


class CallbackRequestModel(models.Model):
    """Qo'ng'iroq so'rovi — mijoz raqam qoldiradi, biz qayta qo'ng'iroq qilamiz"""
    phone = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    handled = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Callback request"
        verbose_name_plural = "Callback requests"

    def __str__(self):
        return f"{self.phone} ({self.created_at:%d.%m.%Y %H:%M})"


class ProjectModel(models.Model):
    """Amalga oshirilgan loyihalar: kafe, mehmonxona, xususiy hovli va h.k."""
    KIND_CHOICES = [
        ('private', "Xususiy hovli"),
        ('cafe', "Kafe / restoran"),
        ('hotel', "Mehmonxona"),
        ('public', "Ofis / jamoat joyi"),
    ]
    title = models.CharField(max_length=120, verbose_name="Loyiha nomi")
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default='private', verbose_name="Turi")
    location = models.CharField(max_length=120, blank=True, verbose_name="Manzil (masalan: Toshkent, Yunusobod)")
    year = models.PositiveIntegerField(null=True, blank=True, verbose_name="Yil")
    description = models.TextField(blank=True, verbose_name="Izoh")
    cover = models.ImageField(upload_to='projects/', verbose_name="Asosiy rasm")
    products = models.ManyToManyField(ProductModel, blank=True, related_name='projects',
                                      verbose_name="Ishlatilgan mahsulotlar")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")
    is_active = models.BooleanField(default=True, verbose_name="Saytda ko'rsatilsin")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Loyiha"
        verbose_name_plural = "Loyihalar"

    def __str__(self):
        return self.title


class ProjectImageModel(models.Model):
    """Loyiha galereyasidagi qo'shimcha rasmlar"""
    project = models.ForeignKey(ProjectModel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='projects/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Loyiha rasmi"
        verbose_name_plural = "Loyiha rasmlari"

    def __str__(self):
        return f"{self.project.title} — rasm {self.pk}"
