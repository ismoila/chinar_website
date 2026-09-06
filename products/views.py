from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from pages.views import get_common_context
from products.models import ReplyModel, ReviewModel, WishlistModel, ProductModel, CategoryModel, ColorModel
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.db.models import Max, Min, Q, Count
from django.shortcuts import render
from django.urls import reverse
from .models import SearchQuery
from django.contrib import messages
from products.telegram import send_order_notification
from .models import Order, OrderItem
from django.contrib.auth.models import User

# ═══ 360° foto-spin: mahsulot ID -> (static papka prefiksi, kadrlar soni) ═══
# Yangi mahsulot qo'shish: static/spin/<nom>/ papkaga kadrlarni qo'ying
# (nom_01.jpg, nom_02.jpg ...) va shu lug'atga yozing
PRODUCT_SPIN = {
    # (prefiks, jami kadr, qadam, teskari, kengaytma)
    # 360 o'chirilgan. Yoqish uchun quyidagi qatordan # ni olib tashlang:
    # 2: ("spin/deco38_cut/deco_", 38, 1, False, "webp"),
}

# def _spin_frames(pk):
#     """Mahsulot uchun 360° kadr havolalari ro'yxati (yo'q bo'lsa None)."""
#     from django.templatetags.static import static as static_url
#     conf = PRODUCT_SPIN.get(pk)
#     if not conf:
#         return None
#     prefix, count, step = conf[0], conf[1], conf[2]
#     reverse = conf[3] if len(conf) > 3 else False
#     ext = conf[4] if len(conf) > 4 else "jpg"
#     frames = [static_url(f"{prefix}{i:02d}.{ext}") for i in range(1, count + 1, step)]
#     if reverse:
#         frames = frames[:1] + frames[1:][::-1]   # 1-kadr joyida, qolgani teskari
    # return frames

def wishlistPageView(request):
    categories = CategoryModel.objects.all()
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlists = WishlistModel.objects.filter(user=request.user)
        # Yurakcha qizil (to'ldirilgan) ko'rinishi uchun
        wishlist_ids = list(wishlists.values_list('product_id', flat=True))
    else:
        wishlists = []
    context = {
        "wishlists": wishlists,
        "wishlist_ids": wishlist_ids,
        "categories": categories,
        **get_common_context(request),
    }
    return render(request, "wishlist.html", context=context)

def wishlist_toggle(request, product_id):
    if not request.user.is_authenticated:
        return redirect('pages:send_code')
    
    product = get_object_or_404(ProductModel, id=product_id)
    wishlist_item = WishlistModel.objects.filter(
        user=request.user,
        product=product
    ).first()

    if wishlist_item:
        wishlist_item.delete()
    else:
        WishlistModel.objects.create(
            user=request.user,
            product=product
        )

    return redirect(request.META.get('HTTP_REFERER', '/'))

def hot_discounts(request): 
    categories = CategoryModel.objects.all()
    hot_discounts = ProductModel.objects.filter(discount__gt=0)
    return render(request, 'home.html', {'hot_discounts': hot_discounts, "categories": categories, **get_common_context(request),})



def category_detail(request, pk):
    category = get_object_or_404(CategoryModel, pk=pk)
    all_products = ProductModel.objects.filter(category=category)

    # ═══ Narx diapazoni UZS'da: 0 dan eng qimmat mahsulotgacha ═══
    from pages.utils import get_usd_to_uzs_rate
    rate = get_usd_to_uzs_rate()
    price_range = all_products.aggregate(
        min_p=Min('price'),
        max_p=Max('price')
    )
    min_product_price = '0'
    max_usd = price_range['max_p'] or 1000
    max_product_price = str(int(round(max_usd * rate / 1000) * 1000))

    products = all_products
    sort = request.GET.get('sort', 'new')
    if sort == 'cheap':
        products = products.order_by('price')
    elif sort == 'expensive':
        products = products.order_by('-price')
    elif sort == 'sale':
        products = products.filter(discount__gt=0)
    else:
        products = products.order_by('-created_at')

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    # UZS kiritiladi — bazadagi USD narxga aylantirib filtrlaymiz
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price) / rate)
        except (TypeError, ValueError):
            min_price = None
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price) / rate)
        except (TypeError, ValueError):
            max_price = None

    categories = CategoryModel.objects.all()
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = WishlistModel.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

    context = {
    'category': category,
    'categories': categories,
    'products': products,
    'wishlist_ids': wishlist_ids,
    'sort': sort,
    'count': products.count(),
    'min_price': min_price,
    'max_price': max_price,
    'min_product_price': min_product_price,
    'max_product_price': max_product_price,
    'request': request,
    **get_common_context(request),
}

    return render(request, 'category_detail.html', context)

from PIL import Image
from django.contrib import messages

# Fayl yuklash uchun ruxsat etilgan formatlar va maksimal hajm
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def product_detail_view(request, slug):
    product = get_object_or_404(ProductModel, slug=slug)
    pk = product.pk  # qolgan kodda pk ishlatilgan joylar uchun (masalan session, wishlist tekshiruvi)
    # Galereyada asosiy rasm bilan BIR XIL fayl bo'lsa (papkasi boshqa bo'lsa ham),
    # uni chiqarib tashlaymiz — sahifada rasm ikki marta ko'rinmasin
    import os as _os
    _main_name = _os.path.basename(product.image.name) if product.image else ''
    images = [
        img for img in product.images.all()
        if _os.path.basename(img.image.name) != _main_name
    ]
    categories = CategoryModel.objects.all()
    reviews = product.reviews.prefetch_related("replies").all()
    related_products = ProductModel.objects.filter(
        category=product.category
    ).exclude(pk=product.pk)
    in_wishlist = False
    wishlist_ids = []

    color_variants = product.color_variants.prefetch_related("images", "color")
    # Mahsulotning O'Z ranglari (admin "Colors" maydonidan) — guruhlangan
    product_colors = list(product.colors.all())
    color_groups = []
    for key, label in ColorModel.GROUP_CHOICES:
        items = [c for c in product_colors if c.group == key]
        if items:
            color_groups.append({'label': label, 'colors': items})
    all_colors = product_colors
    size_prices = product.size_prices.all()

    if request.user.is_authenticated:
        in_wishlist = WishlistModel.objects.filter(
            user=request.user,
            product=product
        ).exists()

        wishlist_ids = WishlistModel.objects.filter(
            user=request.user
        ).values_list("product_id", flat=True)

    viewed = request.session.get("recently_viewed", [])

    if pk in viewed:
        viewed.remove(pk)
    viewed.insert(0, pk)
    viewed = viewed[:10]
    request.session["recently_viewed"] = viewed
    recently_viewed = []
    for product_id in viewed:
        if product_id != pk:
            try:
                recently_viewed.append(
                    ProductModel.objects.get(pk=product_id)
                )
            except ProductModel.DoesNotExist:
                pass

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        text = request.POST.get("text", "").strip()
        rating_raw = request.POST.get("rating", "5")
        image = request.FILES.get("image")

        errors = []

        # ── Ism ──
        if not name or len(name) > 100:
            errors.append("Ism noto'g'ri kiritilgan.")

        # ── Sharh matni ──
        if not text or len(text) < 3:
            errors.append("Sharh matni juda qisqa.")
        elif len(text) > 1000:
            errors.append("Sharh matni 1000 belgidan oshmasligi kerak.")

        # ── Baho (rating) — faqat 1-5 oralig'idagi butun son ──
        try:
            rating = int(rating_raw)
            if rating < 1 or rating > 5:
                raise ValueError
        except (ValueError, TypeError):
            errors.append("Baho noto'g'ri.")
            rating = 5  # fallback qiymat

        # ── Telefon (ixtiyoriy, lekin uzunligi cheklansin) ──
        if phone and len(phone) > 20:
            errors.append("Telefon raqami noto'g'ri.")

        # ── Rasm — format, hajm va haqiqiy rasm ekanligini tekshirish ──
        if image:
            ext = _os.path.splitext(image.name)[1].lower()
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                errors.append("Faqat JPG, PNG yoki WEBP formatidagi rasm yuklash mumkin.")
            elif image.size > MAX_IMAGE_SIZE:
                errors.append("Rasm hajmi 5MB dan oshmasligi kerak.")
            else:
                try:
                    img = Image.open(image)
                    img.verify()  # fayl haqiqatan ham rasm ekanini tekshiradi
                    image.seek(0)  # keyinroq saqlash uchun faylni boshiga qaytarish
                except Exception:
                    errors.append("Fayl buzilgan yoki rasm emas.")

        # ── Agar xatolar bo'lsa — bazaga yozmasdan qaytarish ──
        if errors:
            for e in errors:
                messages.error(request, e)
            return redirect(request.path + "#reviews")

        # ── Hammasi to'g'ri — saqlash ──
        ReviewModel.objects.create(
            product=product,
            user=request.user if request.user.is_authenticated else None,
            name=name,
            phone=phone,
            text=text,
            rating=rating,
            images=image,
        )
        messages.success(request, "Sharhingiz uchun rahmat!")
        return redirect(request.path + "#reviews")

    context = {
        "product": product,
        "images": images,
        "categories": categories,
        "reviews": reviews,
        "review_count": reviews.count(),
        "in_wishlist": in_wishlist,
        "wishlist_ids": wishlist_ids,
        "related_products": related_products,
        "recently_viewed": recently_viewed,
        "color_variants": color_variants,
        "all_colors": all_colors,
        "color_groups": color_groups,
        "size_prices": size_prices,
        # "spin_frames": _spin_frames(pk),
        **get_common_context(request),
    }
    return render(request, "shop_details.html", context=context)

def review_vote(request, review_id, vote_type):
    """Har bir user faqat BITTA ovoz beradi (like YOKI dislike),
    qayta bosса — bekor qilinadi, boshqasini bossa — almashadi."""
    if request.method == 'POST' and vote_type in ('like', 'dislike'):
        from products.models import ReviewModel
        review = get_object_or_404(ReviewModel, id=review_id)
        votes = request.session.get('review_votes', {})
        key = str(review_id)
        prev = votes.get(key)

        if prev == vote_type:
            # xuddi shu tugma qayta bosildi — ovozni olib tashlash
            if vote_type == 'like':
                review.likes = max(0, review.likes - 1)
            else:
                review.dislikes = max(0, review.dislikes - 1)
            votes.pop(key, None)
            current = None
        else:
            # avvalgi ovozni bekor qilib, yangisini qo'yish
            if prev == 'like':
                review.likes = max(0, review.likes - 1)
            elif prev == 'dislike':
                review.dislikes = max(0, review.dislikes - 1)
            if vote_type == 'like':
                review.likes += 1
            else:
                review.dislikes += 1
            votes[key] = vote_type
            current = vote_type

        review.save()
        request.session['review_votes'] = votes
        request.session.modified = True
        return JsonResponse({
            'likes': review.likes,
            'dislikes': review.dislikes,
            'vote': current,
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def reply_review(request, review_id):
    # Faqat CHINAR xodimlari (is_staff) javob yoza oladi
    if not request.user.is_staff:
        return HttpResponseForbidden("Sizda bu amalni bajarish huquqi yo'q.")

    if request.method == 'POST':
        review = get_object_or_404(ReviewModel, id=review_id)
        text = request.POST.get('text', '').strip()

        errors = []
        if not text or len(text) < 3:
            errors.append("Javob matni juda qisqa.")
        elif len(text) > 1000:
            errors.append("Javob matni 1000 belgidan oshmasligi kerak.")

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            ReplyModel.objects.create(
                review=review,
                user=request.user,
                name="CHINAR",
                text=text,
            )
            messages.success(request, "Javob qo'shildi.")

        return redirect(request.META.get('HTTP_REFERER', '/') + '#reviews')
    return redirect('/')




@login_required
def add_to_cart(request, pk, quantity):
    current_path_url = request.META.get("HTTP_REFERER", "/")
    cart_data = request.session.get("data", [])
    
    size = request.GET.get('size', '').strip()
    color = request.GET.get('color', '').strip()

    already_in = any(str(item["pk"]) == str(pk) for item in cart_data)

    if already_in:
        cart_data = [item for item in cart_data if str(item["pk"]) != str(pk)]
        messages.info(request, _("Product removed from cart"))
    else:
        # Ombor: "vaqtincha yo'q" mahsulot savatga tushmasin
        # (havolani qo'lda yozib kirilsa ham)
        _mahsulot = ProductModel.objects.filter(pk=pk).first()
        if _mahsulot is not None and not getattr(_mahsulot, "in_stock", True):
            messages.error(request, _("This product is temporarily out of stock"))
            return redirect(current_path_url)
        cart_data.append({"pk": pk, "quantity": quantity, "size": size, "color": color})
        messages.success(request, _("Product added to cart"))

    request.session["data"] = cart_data
    request.session.modified = True
    
    return redirect(current_path_url)


@login_required
def remove_from_cart(request, pk):
    current_path_url = request.META.get("HTTP_REFERER") or '/cart/'


    cart_data = request.session.get("data", [])

    new_cart = [
        item for item in cart_data
        if int(item["pk"]) != pk
    ]

    request.session["data"] = new_cart

    messages.info(request, _("Product removed from cart"))

    return redirect(current_path_url)


@login_required
def update_cart(request):
    """Savatdagi miqdorlarni yangilash — size va color SAQLANADI"""
    current_path_url = request.META.get("HTTP_REFERER") or '/cart/'

    cart_data = request.session.get("data", [])
    key1_values = request.POST.getlist('pk')
    key2_values = request.POST.getlist('quantity')

    qty_map = {}
    for pk, quantity in zip(key1_values, key2_values):
        try:
            qty_map[str(pk)] = max(1, int(quantity))
        except (TypeError, ValueError):
            continue

    for entry in cart_data:
        pid = str(entry.get('pk'))
        if pid in qty_map:
            entry['quantity'] = qty_map[pid]   # size/color tegilmaydi

    request.session['data'] = cart_data
    request.session.modified = True
    return redirect(current_path_url)





def _multilang_search(query):
    """name va category name bo'yicha mavjud til maydonlarida qidiradi"""
    product_fields  = {f.name for f in ProductModel._meta.get_fields()}
    category_fields = {f.name for f in CategoryModel._meta.get_fields()}

    q = Q(name__icontains=query) | Q(category__name__icontains=query)
    for suffix in ('_en', '_uz', '_ru'):
        if f'name{suffix}' in product_fields:
            q |= Q(**{f'name{suffix}__icontains': query})
        if f'name{suffix}' in category_fields:
            q |= Q(**{f'category__name{suffix}__icontains': query})
    return q


def _multilang_category_search(query):
    category_fields = {f.name for f in CategoryModel._meta.get_fields()}
    q = Q(name__icontains=query)
    for suffix in ('_en', '_uz', '_ru'):
        if f'name{suffix}' in category_fields:
            q |= Q(**{f'name{suffix}__icontains': query})
    return q


def _save_search(request, term):
    if not term:
        return
    if not request.session.session_key:
        request.session.create()

    SearchQuery.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=None if request.user.is_authenticated else request.session.session_key,
        term=term,
    )


def _get_recent_searches(request, limit=5):
    if request.user.is_authenticated:
        qs = SearchQuery.objects.filter(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        qs = SearchQuery.objects.filter(session_key=request.session.session_key)

    terms = list(
        qs.order_by('-created_at')
          .values_list('term', flat=True)
    )

    seen = set()
    unique_terms = []
    for term in terms:
        if term not in seen:
            seen.add(term)
            unique_terms.append(term)
        if len(unique_terms) >= limit:
            break

    return unique_terms


def clear_recent_searches(request):
    if request.user.is_authenticated:
        SearchQuery.objects.filter(user=request.user).delete()
    elif request.session.session_key:
        SearchQuery.objects.filter(session_key=request.session.session_key).delete()
    return JsonResponse({'success': True})


def search_dropdown_data(request):
    """Dropdown ochilganda (input bosilganda) chaqiriladi"""
    recent = _get_recent_searches(request)

    popular = (
        SearchQuery.objects.values('term')
        .annotate(count=Count('term'))
        .order_by('-count')[:5]
    )

    # "Tavsiya etamiz" — tasodifiy 6 ta mahsulot
    recommended = []
    for p in ProductModel.objects.exclude(image='').order_by('?')[:12]:
        try:
            price = f"{int(p.get_price_uzs):,}".replace(',', ' ')
        except Exception:
            price = ''
        recommended.append({
            'name': p.name,
            'url': reverse('products:product_detail', args=[p.pk]),
            'image': p.image.url if p.image else '',
            'price': price,
        })

    return JsonResponse({
        'recent': recent,
        'popular': [p['term'] for p in popular],
        'recommended': recommended,
    })


def remove_recent_search(request):
    """Bitta qidiruv tarixini o'chirish (X tugmasi)."""
    term = request.POST.get('term', '') or request.GET.get('term', '')
    qs = SearchQuery.objects.filter(term=term)
    if request.user.is_authenticated:
        qs = qs.filter(user=request.user)
    elif request.session.session_key:
        qs = qs.filter(session_key=request.session.session_key)
    else:
        qs = qs.none()
    qs.delete()
    return JsonResponse({'success': True})


def search_suggest(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse({'products': [], 'categories': []})

    # Avval nomi mos kelganlar; bo'lmasa kategoriya bo'yicha
    _pf1 = {f.name for f in ProductModel._meta.get_fields()}
    _nq1 = Q(name__icontains=query)
    for _s1 in ('_en', '_uz', '_ru'):
        if f'name{_s1}' in _pf1:
            _nq1 |= Q(**{f'name{_s1}__icontains': query})
    _name_only = ProductModel.objects.filter(_nq1).distinct()
    if _name_only.exists():
        products = _name_only[:8]
    else:
        products = ProductModel.objects.filter(
            _multilang_search(query)
        ).distinct()[:8]

    categories = CategoryModel.objects.filter(
        _multilang_category_search(query)
    )[:3]

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(
            WishlistModel.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    data = {
        'categories': [
            {'name': c.name, 'url': reverse('products:category_detail', kwargs={'pk': c.id})}
            for c in categories
        ],
        'products': [
            {
                'name': p.name,
                'url': reverse('products:product_detail', args=[p.id]),
                'add_to_cart_url': reverse('products:add_to_cart', kwargs={'pk': p.id, 'quantity': 1}),
                'image': p.image.url if p.image else '',
                'price': f'{p.get_price_uzs:,.0f}'.replace(',', ' '),
                'in_wishlist': p.id in wishlist_ids,
                'available': True,  # o'zingizning stock logikangizga moslang
            }
            for p in products
        ]
    }
    return JsonResponse(data)


def search_results(request):
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'new')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if query:
        _save_search(request, query)

    products = ProductModel.objects.none()

    if query:
        # ═══ Avval faqat NOMI mos kelganlarni izlaymiz. ═══
        # Nom bo'yicha natija bo'lsa — faqat o'shalar ko'rsatiladi
        # (masalan "king" deb izlaganda "RoCKING chairs" kategoriyasidagi
        #  boshqa mahsulotlar aralashib chiqmasin).
        _pf0 = {f.name for f in ProductModel._meta.get_fields()}
        _nq = Q(name__icontains=query)
        for _s in ('_en', '_uz', '_ru'):
            if f'name{_s}' in _pf0:
                _nq |= Q(**{f'name{_s}__icontains': query})
        name_only = ProductModel.objects.filter(_nq).distinct()
        if name_only.exists():
            products = name_only
        else:
            # Nomda topilmasa — kategoriya nomi bo'yicha ham izlaymiz
            products = ProductModel.objects.filter(
                _multilang_search(query)
            ).distinct()

        # UZS kiritiladi — bazadagi USD narxga aylantirib filtrlaymiz
        from pages.utils import get_usd_to_uzs_rate
        _rate = get_usd_to_uzs_rate()
        if min_price:
            try:
                products = products.filter(price__gte=float(min_price) / _rate)
            except (TypeError, ValueError):
                min_price = None
        if max_price:
            try:
                products = products.filter(price__lte=float(max_price) / _rate)
            except (TypeError, ValueError):
                max_price = None

        # ═══ Avval NOMI mos kelganlar, keyin faqat kategoriyasi mos kelganlar ═══
        from django.db.models import Case, When, Value, IntegerField
        _pf = {f.name for f in ProductModel._meta.get_fields()}
        _name_q = Q(name__icontains=query)
        for _sfx in ('_en', '_uz', '_ru'):
            if f'name{_sfx}' in _pf:
                _name_q |= Q(**{f'name{_sfx}__icontains': query})
        products = products.annotate(
            _rel=Case(When(_name_q, then=Value(0)), default=Value(1), output_field=IntegerField())
        )

        if sort == 'cheap':
            products = products.order_by('_rel', 'price')
        elif sort == 'expensive':
            products = products.order_by('_rel', '-price')
        elif sort == 'sale':
            products = products.filter(discount__gt=0).order_by('_rel', '-created_at')
        else:
            products = products.order_by('_rel', '-created_at')

    # Price range for the slider (butun katalog bo'yicha, faqat natijalar emas)
    price_range = ProductModel.objects.aggregate(
        min_p=Min('price'), max_p=Max('price')
    )
    from pages.utils import get_usd_to_uzs_rate as _r
    min_product_price = '0'
    max_product_price = str(int(round((price_range['max_p'] or 1000) * _r() / 1000) * 1000))

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = list(
            WishlistModel.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    context = {
        'query': query,
        'products': products,
        'count': products.count(),
        'sort': sort,
        'min_price': min_price,
        'max_price': max_price,
        'min_product_price': min_product_price,
        'max_product_price': max_product_price,
        'wishlist_ids': wishlist_ids,
        'categories': CategoryModel.objects.all(),     # ← QO'SHILDI (pills uchun)
        **get_common_context(request),                 # ← QO'SHILDI (cart/wishlist badge uchun)
    }
    return render(request, 'search.html', context)


@login_required
def create_order(request):
    if request.method != "POST":
        return redirect('pages:checkout')

    cart_data = request.session.get("data", [])
    if not cart_data:
        return redirect('pages:shopping_cart')

    # savatdan mahsulot va summani yig'ish
    items = []
    total = 0
    for row in cart_data:
        try:
            product = ProductModel.objects.get(pk=row['pk'])
        except ProductModel.DoesNotExist:
            continue
        qty = int(row.get('quantity', 1))
        size = (row.get('size') or '').strip()
        color = (row.get('color') or '').strip()
        price = product.price_uzs_for_size(size)     # UZS — tanlangan o'lcham narxi

        total += price * qty
        items.append((product, qty, price, size, color))

    if not items:
        return redirect('pages:shopping_cart')

    # ═══ Promokod chegirmasi ═══
    from products.models import PromoCode
    promo_discount = 0
    promo_code_str = request.session.get('promo_code', '')
    if promo_code_str:
        try:
            promo = PromoCode.objects.get(code=promo_code_str)
            if promo.is_valid():
                promo_discount = total * promo.discount_percent // 100
                promo.used_count += 1
                promo.save()
            else:
                promo_code_str = ''
        except PromoCode.DoesNotExist:
            promo_code_str = ''

    # buyurtma yaratish
    order = Order.objects.create(
        user=request.user,
        first_name=request.POST.get('first_name', ''),
        last_name=request.POST.get('last_name', ''),
        phone=request.POST.get('phone', ''),
        delivery_method=request.POST.get('delivery_method', 'delivery'),
        region=request.POST.get('region', ''),
        district=request.POST.get('city', ''),
        address=request.POST.get('address', ''),
        floor=request.POST.get('floor', ''),
        payment_method=request.POST.get('payment', 'cash'),
        comment=request.POST.get('comment', ''),
        total_price=total - promo_discount,
        promo_code=promo_code_str,
        discount_amount=promo_discount,
    )

    for product, qty, price, size, color in items:
        OrderItem.objects.create(order=order, product=product, quantity=qty, price=price, size=size, color=color)

    # savat va promokodni tozalash
    request.session["data"] = []
    request.session.pop('promo_code', None)
    request.session.modified = True
    send_order_notification(order)

    messages.success(request, _("Your order has been received!"))

    # ═══ Payme/Click tanlangan bo'lsa — to'lov sahifasiga yo'naltiramiz ═══
    from products import payments as pay
    return_url = request.build_absolute_uri('/profile/')
    if order.payment_method == 'payme' and pay.payme_configured():
        return redirect(pay.build_payme_url(order, return_url))
    if order.payment_method == 'click' and pay.click_configured():
        return redirect(pay.build_click_url(order, return_url))

    return redirect('pages:order')   # "Мои заказы" sahifasiga

from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def callback_request(request):
    """Suzuvchi tugma: mijoz raqam qoldiradi — admin'ga tushadi"""
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)
    phone = (request.POST.get('phone') or '').strip()
    digits = ''.join(ch for ch in phone if ch.isdigit())
    if len(digits) < 7:
        return JsonResponse({'ok': False, 'error': _("Enter a valid phone number")}, status=400)
    from products.models import CallbackRequestModel
    from products.telegram import send_callback_notification
    cb = CallbackRequestModel.objects.create(phone=phone)
    send_callback_notification(cb)
    return JsonResponse({'ok': True})


@csrf_exempt
def one_click_order(request):
    """1-klik buyurtma: faqat telefon raqam — operator qo'ng'iroq qilib tasdiqlaydi"""
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)
    phone = (request.POST.get('phone') or '').strip()
    digits = ''.join(ch for ch in phone if ch.isdigit())
    if len(digits) < 7:
        return JsonResponse({'ok': False, 'error': _("Enter a valid phone number")}, status=400)
    try:
        product = ProductModel.objects.get(pk=request.POST.get('product_id'))
    except (ProductModel.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'ok': False}, status=404)

    size = (request.POST.get('size') or '').strip()
    color = (request.POST.get('color') or '').strip()
    name = (request.POST.get('name') or '').strip()

    # Narx: tanlangan o'lcham bo'lsa — o'sha o'lcham narxi
    price = int(product.get_price_uzs)
    if size:
        sp = product.size_prices.filter(title=size).first()
        if sp:
            price = int(sp.price_uzs)

    # Buyurtma egasi: kirgan user yoki "1-klik" tizim useri
    if request.user.is_authenticated:
        user = request.user
    else:
        user, _created = User.objects.get_or_create(
            username='oneclick_guest',
            defaults={'first_name': '1-klik'},
        )

    order = Order.objects.create(
        user=user,
        first_name=name or "1-klik mijoz",
        phone=phone,
        delivery_method='delivery',
        payment_method='cash',
        comment="⚡ 1-KLIK BUYURTMA — operator qo'ng'iroq qilib, manzil va tafsilotlarni aniqlaydi",
        total_price=price,
    )
    OrderItem.objects.create(order=order, product=product, quantity=1, price=price, size=size, color=color)
    send_order_notification(order)
    return JsonResponse({'ok': True, 'order_id': order.order_id})


def buy_now(request, pk):
    """Hozir xarid qilish: mahsulotni savatga qo'shib, to'g'ridan-to'g'ri checkoutga olib boradi"""
    # Ombor: "vaqtincha yo'q" mahsulotni sotib bo'lmaydi
    _mahsulot = ProductModel.objects.filter(pk=pk).first()
    if _mahsulot is not None and not getattr(_mahsulot, "in_stock", True):
        messages.error(request, _("This product is temporarily out of stock"))
        return redirect('products:product_detail', pk=pk)
    cart_data = request.session.get("data", [])
    if not any(str(item["pk"]) == str(pk) for item in cart_data):
        size = request.GET.get('size', '').strip()
        color = request.GET.get('color', '').strip()
        cart_data.append({"pk": pk, "quantity": 1, "size": size, "color": color})
        request.session["data"] = cart_data
        request.session.modified = True
    return redirect('pages:checkout')


def product_options(request, pk):
    """Karta '+' tugmasi uchun: mahsulotning o'lcham va rang variantlari (JSON)"""
    try:
        p = ProductModel.objects.prefetch_related('size_prices', 'colors').get(pk=pk)
    except ProductModel.DoesNotExist:
        return JsonResponse({'ok': False}, status=404)

    sizes = [{
        'title': sp.title,
        'price': f"{int(sp.price_uzs):,}".replace(',', ' '),
    } for sp in p.size_prices.all()]

    groups = []
    all_colors = list(p.colors.all())
    for key, label in ColorModel.GROUP_CHOICES:
        items = [{
            'name': c.name,
            'code': c.code or '',
            'image': c.image.url if c.image else '',
        } for c in all_colors if c.group == key]
        if items:
            groups.append({'label': str(label), 'colors': items})

    return JsonResponse({
        'ok': True,
        'name': p.name,
        'image': p.image.url if p.image else '',
        'price': f"{int(p.get_price_uzs):,}".replace(',', ' '),
        'sizes': sizes,
        'groups': groups,
    })
