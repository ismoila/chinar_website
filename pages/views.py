import random
from django.utils.translation import gettext as _
import re
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages



# models
from config import settings
from pages.models import BannerModel, ContactModel
from products.models import IdeaModel, Order, PhoneVerification, ProductModel, CategoryModel, ColorModel, ProfileModel, SizeModel, WishlistModel, FurnitureSet
from products.sms import send_sms

from django.core.cache import cache


def homepageview(request):
    # ── Umumiy (hammaga bir xil) ma'lumotlar — keshdan olinadi ──
    umumiy = cache.get('home_umumiy_malumot')
    if umumiy is None:
        ideas = IdeaModel.objects.prefetch_related('pins__product').all()
        sets = FurnitureSet.objects.filter(is_active=True).prefetch_related(
            'set_products__product'
        )
        banners = BannerModel.objects.filter(is_active=True)
        products = ProductModel.objects.all()
        categories = CategoryModel.objects.all()

        # Faqat HAQIQIY faol chegirmalar (muddati o'tganlari chiqmasin) —
        # chegirmalar sahifasi bilan bir xil filtr
        _now = timezone.now()
        hot_discounts = ProductModel.objects.filter(discount__gt=0).filter(
            Q(discount_start__isnull=True) | Q(discount_start__lte=_now, discount_end__gte=_now)
        )

        # ═══ Eng ko'p sotilgan (buyurtmalar bo'yicha) ═══
        from django.db.models import Sum, Count
        best_sellers = list(
            ProductModel.objects.annotate(sold=Sum('orderitem__quantity'))
            .filter(sold__gt=0).order_by('-sold')[:40]
        )
        if len(best_sellers) < 40:   # "Yana ko'rsatish" uchun reyting bo'yicha to'ldiramiz
            extra = ProductModel.objects.exclude(
                pk__in=[p.pk for p in best_sellers]
            ).order_by('-rating', '-created_at')[:40 - len(best_sellers)]
            best_sellers += list(extra)

        # ═══ Biz tavsiya qilamiz — har kuni boshqa mahsulotlar ═══
        # Kun sanasi seed bo'ladi: bir kun davomida bir xil, ertasiga yangi to'plam
        import random as _random
        import datetime as _dt
        _ids = list(
            ProductModel.objects.exclude(pk__in=[p.pk for p in best_sellers[:5]])
            .values_list('pk', flat=True)
        )
        _rng = _random.Random(_dt.date.today().toordinal())
        _rng.shuffle(_ids)
        _pick = _ids[:10]
        _rec_map = {p.pk: p for p in ProductModel.objects.filter(pk__in=_pick)}
        recommended = [_rec_map[i] for i in _pick if i in _rec_map]

        umumiy = {
            'ideas': ideas,
            'sets': sets,
            "banners": banners,
            "products": products,
            "categories": categories,
            'hot_discounts': hot_discounts,
            'best_sellers': best_sellers,
            'recommended': recommended,
        }
        cache.set('home_umumiy_malumot', umumiy, 60 * 15)  # 15 daqiqa saqlanadi

    # ── Shaxsiy ma'lumotlar — har doim yangidan hisoblanadi ──
    user_profile = None
    if request.user.is_authenticated:
        user_profile, _ = ProfileModel.objects.get_or_create(
            user=request.user,
            defaults={"phone": request.user.username}
        )

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = WishlistModel.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

    context = {
        **umumiy,
        'wishlist_ids': wishlist_ids,
        "user_profile": user_profile,
        **get_common_context(request),
    }
    return render(request, 'home.html', context=context)

def get_common_context(request):
    wishlist_count = 0
    cart_count = 0
    if request.user.is_authenticated:
        from products.models import WishlistModel
        wishlist_count = WishlistModel.objects.filter(user=request.user).count()
    cart_data = request.session.get("data", [])
    cart_count = len(cart_data)
    return {
        'wishlist_count': wishlist_count,
        'cart_count': cart_count,
    }

def aboutpageview(request):
    categories = CategoryModel.objects.all()
    context = {
"categories": categories,
**get_common_context(request),
}
    return render(request, 'about.html', context=context)

def locationpageview(request):
    categories = CategoryModel.objects.all()
    context = {
"categories": categories,
**get_common_context(request),
}
    return render(request, 'location.html', context=context)

def workerspageview(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        ContactModel.objects.create(first_name=first_name, last_name=last_name, email=email, phone=phone)
    categories = CategoryModel.objects.all()
    context = {
"categories": categories,
**get_common_context(request),
}
    return render(request, 'workers.html', context=context)

def deliverypageview(request):
    categories = CategoryModel.objects.all()
    context = {
"categories": categories,
**get_common_context(request),
}
    return render(request, 'delivery.html', context=context)

def ideapageview(request):
    ideas = IdeaModel.objects.prefetch_related('pins__product').all()
    categories = CategoryModel.objects.all()
    context = {
        'ideas': ideas,
"categories": categories,
**get_common_context(request),
}
    return render(request, 'idea.html', context=context)

def categorypageview(request):
    categories = CategoryModel.objects.all()
    context = {
        "categories": categories,
        **get_common_context(request),
    }
    return render(request, 'category.html', context=context)

def servicespageview(request):
    categories = CategoryModel.objects.all()
    context = {
        "categories": categories,
        **get_common_context(request),
    }
    return render(request, 'services.html', context=context)

@login_required
def order(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    categories = CategoryModel.objects.all()
    context = {
        "categories": categories,
        "orders": orders,
        **get_common_context(request),
    }
    return render(request, 'order.html', context=context)

from products.models import ReviewModel

from django.core.paginator import Paginator

@login_required
def review(request):
    categories = CategoryModel.objects.all()
    all_reviews = ReviewModel.objects.filter(user=request.user).select_related('product')
    
    paginator = Paginator(all_reviews, 1)  # 1 review per page
    page_number = request.GET.get('page', 1)
    user_reviews = paginator.get_page(page_number)
    
    context = {
        "categories": categories,
        "user_reviews": user_reviews,
        "all_count": all_reviews.count(),
        "published_count": all_reviews.count(),
        "pending_count": 0,
        **get_common_context(request),
    }
    return render(request, 'reviews.html', context=context)

@login_required
def profile(request):
    
    profile, created = ProfileModel.objects.get_or_create(
        user=request.user
    )

    if created:
        profile.phone = request.user.username
        profile.save()

    if request.method == "POST":
        ProfileModel.objects.filter(user=request.user).update(
            first_name=request.POST.get("first_name", ""),
            last_name=request.POST.get("last_name", ""),
            email=request.POST.get("email", ""),
            phone=request.POST.get("phone", ""),
            date_of_birth=request.POST.get("birthdate") or None,
            gender=request.POST.get("gender", ""),
        )
        return redirect("pages:profile")
    categories = CategoryModel.objects.all()
    context = {
        "categories": categories,
        "profile": profile,
        **get_common_context(request),
    }

    return render(request, "settings.html", context=context)


def send_code_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        phone_clean = re.sub(r'[\s\-\(\)]', '', phone)

        # ← These conditions must return render with error
        if not phone_clean or phone_clean == '+998':
            return render(request, 'registration/signin.html', {
                'error': 'Please enter your phone number!'
            })

        if not re.match(r'^\+998\d{9}$', phone_clean):
            return render(request, 'registration/signin.html', {
                'error': 'Value is not a valid phone number'
            })

        # ═══ HIMOYA 1: shu raqamga 60 soniyada faqat 1 ta SMS ═══
        one_min_ago = timezone.now() - timezone.timedelta(seconds=60)
        if PhoneVerification.objects.filter(
                phone=phone_clean, created_at__gte=one_min_ago).exists():
            return render(request, 'registration/signin.html', {
                'error': "Iltimos, 1 daqiqa kutib qayta urinib ko'ring."
            })

        # ═══ HIMOYA 2: shu raqamga 24 soatda ko'pi bilan 5 ta SMS ═══
        day_ago = timezone.now() - timezone.timedelta(hours=24)
        if PhoneVerification.objects.filter(
                phone=phone_clean, created_at__gte=day_ago).count() >= 5:
            return render(request, 'registration/signin.html', {
                'error': "Kunlik SMS limiti tugadi. Keyinroq qayta urinib ko'ring."
            })

        code = str(random.randint(100000, 999999))

        PhoneVerification.objects.create(
            phone=phone_clean,
            code=code
        )

        # ═══ DEV REJIM: SMS balansi yo'q — kodni terminalga chiqaramiz ═══
        # SMS qayta yoqish uchun: pastdagi print'ni qoldirib, send_sms qatorlarini izohdan chiqaring
        print("=" * 46)
        print(f"  [DEV] {phone_clean} uchun tasdiqlash kodi:  {code}")
        print("=" * 46)
        # result = send_sms(
        #     phone_clean,
        #     f"Kodni hech kimga bermang! Chinar.uz saytiga kirish uchun tasdiqlash kodi: {code}"
        # )

        request.session['verify_phone'] = phone_clean
        return redirect('pages:verify_code')

    return render(request, 'registration/signin.html')

    

def verify_code_view(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        phone = request.session.get('verify_phone')
        verification = PhoneVerification.objects.filter(
            phone=phone,
            code=code,
            is_used=False
        ).last()
        if verification and not verification.is_expired():
            verification.is_used = True
            verification.save()
            user, _ = User.objects.get_or_create(username=phone)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('pages:home')

        # Kod xato yoki muddati o'tgan
        return render(request, 'registration/signin2.html', {
            'error': 'Kod noto\'g\'ri yoki muddati tugagan. Qayta urinib ko\'ring.'
        })
    return render(request, 'registration/signin2.html')


def logout_view(request):
    logout(request)
    return redirect('pages:home')

def projectpageview(request):
    from products.models import ProjectModel
    categories = CategoryModel.objects.all()
    projects = ProjectModel.objects.filter(is_active=True).prefetch_related('images', 'products')
    kinds = []
    for key, label in ProjectModel.KIND_CHOICES:
        n = sum(1 for p in projects if p.kind == key)
        if n:
            kinds.append({'key': key, 'label': label, 'count': n})

    # Modal galereya uchun ma'lumot
    projects_json = []
    for pr in projects:
        imgs = [pr.cover.url] + [im.image.url for im in pr.images.all()]
        projects_json.append({
            'title': pr.title,
            'meta': ' · '.join(x for x in [pr.get_kind_display(), pr.location, str(pr.year or '')] if x),
            'desc': pr.description,
            'images': imgs,
            'products': [{
                'name': pp.name,
                'url': f'/products/product/{pp.pk}/',
                'image': pp.image.url if pp.image else '',
                'price': f"{int(pp.get_price_uzs):,}".replace(',', ' '),
            } for pp in pr.products.all()],
        })
    context = {
        "categories": categories,
        "projects": projects,
        "project_kinds": kinds,
        "projects_json": projects_json,
        **get_common_context(request),
    }
    return render(request, 'projects.html', context=context)


def shopping_cart(request):
    from products.models import ProductModel

    cart_data = request.session.get("data", [])
    cart_items = []
    total = 0

    for data in cart_data:
        try:
            product = ProductModel.objects.get(pk=int(data['pk']))
            quantity = int(data['quantity'])
            size = (data.get('size') or '').strip()
            color = (data.get('color') or '').strip()
            price = product.price_uzs_for_size(size)     # UZS — o'lchamga qarab
            original = product.original_uzs_for_size(size)  # chegirmasiz asl narx
            item_total = price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'size': size,
                'color': color,
                'price': price,
                'original': original,
                'item_total': item_total,
            })
        except ProductModel.DoesNotExist:
            pass

    original_total = sum(i['original'] * i['quantity'] for i in cart_items)

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = WishlistModel.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

    context = {
        'cart_items': cart_items,
        'total': total,
        'original_total': original_total,
        'count': len(cart_items),
        'wishlist_ids': wishlist_ids,
        'categories': CategoryModel.objects.all(),   # ← SHU QATOR QO'SHILDI
        **get_common_context(request),
    }
    return render(request, 'shopping_cart.html', context=context)

# views.py
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def update_cart(request):
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'status': 'error', 'message': 'invalid body'}, status=400)
    cart_data = request.session.get("data", [])

    # product_id -> yangi quantity
    updates = {}
    for row in payload.get('items', []):
        pid = str(row.get('product_id') or '')
        if not pid:
            continue
        updates[pid] = max(1, int(row.get('quantity') or 1))

    # session dagi savatni yangilash
    for entry in cart_data:
        pid = str(entry.get('pk'))
        if pid in updates:
            entry['quantity'] = updates[pid]

    request.session["data"] = cart_data
    request.session.modified = True
    return JsonResponse({'status': 'ok'})

@login_required
def checkout(request):
    cart_data = request.session.get("data", [])
    cart_items = []
    total = 0

    for data in cart_data:
        try:
            product = ProductModel.objects.get(pk=data['pk'])
            quantity = int(data['quantity'])
            size = (data.get('size') or '').strip()
            color = (data.get('color') or '').strip()
            price = product.price_uzs_for_size(size)     # UZS — o'lchamga qarab
            item_total = price * quantity
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'size': size,
                'color': color,
                'price': price,
                'item_total': item_total,
            })
        except ProductModel.DoesNotExist:
            pass

    # ═══ Promokod chegirmasi ═══
    from products.models import PromoCode
    promo_discount = 0
    promo_code_str = request.session.get('promo_code', '')
    if promo_code_str:
        try:
            promo = PromoCode.objects.get(code=promo_code_str)
            if promo.is_valid():
                promo_discount = total * promo.discount_percent // 100
            else:
                request.session.pop('promo_code', None)
                promo_code_str = ''
        except PromoCode.DoesNotExist:
            request.session.pop('promo_code', None)
            promo_code_str = ''

    grand_total = total - promo_discount

    categories = CategoryModel.objects.all()
    context = {
        'cart_items': cart_items,
        'total': total,
        'count': len(cart_items),
        'promo_code': promo_code_str,
        'promo_discount': promo_discount,
        'grand_total': grand_total,
        'categories': categories,
        **get_common_context(request),
    }
    return render(request, 'checkout.html', context)


@require_POST
def apply_promo(request):
    """Checkout sahifasidan AJAX orqali promokodni tekshirish"""
    from products.models import PromoCode
    try:
        payload = json.loads(request.body)
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': "Noto'g'ri so'rov"})

    code = (payload.get('code') or '').strip().upper()
    if not code:
        request.session.pop('promo_code', None)
        return JsonResponse({'success': False, 'error': 'Promokod kiriting'})

    try:
        promo = PromoCode.objects.get(code__iexact=code)
    except PromoCode.DoesNotExist:
        request.session.pop('promo_code', None)
        return JsonResponse({'success': False, 'error': 'Promokod topilmadi'})

    if not promo.is_valid():
        request.session.pop('promo_code', None)
        return JsonResponse({'success': False, 'error': 'Promokod muddati tugagan yoki faol emas'})

    request.session['promo_code'] = promo.code
    request.session.modified = True
    return JsonResponse({'success': True, 'code': promo.code, 'percent': promo.discount_percent})




def discounts_view(request):
    now = timezone.now()
    products = ProductModel.objects.filter(discount__gt=0).filter(
        Q(discount_start__isnull=True) | Q(discount_start__lte=now, discount_end__gte=now)
    )

    sort = request.GET.get('sort', 'new')
    if sort == 'cheap':
        products = products.order_by('price')
    elif sort == 'expensive':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = WishlistModel.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

    context = {
        'products': products,
        'wishlist_ids': wishlist_ids,
        'count': products.count(),
        'sort': sort,
        **get_common_context(request),
    }
    return render(request, 'discounts.html', context)


def news_view(request):
    """Yangi mahsulotlar (NEW MODELS — FMA seriyasi). AIKO 'Novinki' uslubida."""
    from pages.utils import get_usd_to_uzs_rate
    from django.db.models import Min, Max
    # Nom faqat inglizcha maydonda to'ldirilgan — barcha til maydonlarini tekshiramiz
    # (aks holda uz/ru tillarida ro'yxat bo'sh chiqadi)
    _nq = Q(name__icontains='FMA-')
    for _s in ('_uz', '_ru', '_en'):
        try:
            ProductModel._meta.get_field(f'name{_s}')
            _nq |= Q(**{f'name{_s}__icontains': 'FMA-'})
        except Exception:
            pass
    all_products = ProductModel.objects.filter(_nq)

    rate = get_usd_to_uzs_rate()
    price_range = all_products.aggregate(min_p=Min('price'), max_p=Max('price'))
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

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = WishlistModel.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)

    context = {
        'products': products,
        'categories': CategoryModel.objects.all(),
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
    return render(request, 'news.html', context)


from products.telegram import API as ADMIN_BOT_API  # admin bot API

@login_required
def cancel_order(request, order_id):
    if request.method != "POST":
        return redirect('pages:order')

    try:
        order = Order.objects.get(order_id=order_id, user=request.user)
    except Order.DoesNotExist:
        return redirect('pages:order')

    # Faqat hali tasdiqlanmagan buyurtma bekor qilinadi
    if order.status == 'pending':
        reason = (request.POST.get('reason') or '').strip()
        other = (request.POST.get('reason_text') or '').strip()
        if other:
            reason = f"{reason}: {other}" if reason else other

        order.status = 'canceled'
        if reason:
            order.comment = (order.comment + "\n" if order.comment else "") + f"Bekor qilish sababi: {reason}"
        order.save()
        messages.success(request, _("Order canceled."))

        # Admin botga xabar
        try:
            import requests as _req
            _req.post(f"{ADMIN_BOT_API}/sendMessage", json={
                "chat_id": settings.TELEGRAM_ADMIN_CHAT_ID,
                "text": f"❌ Mijoz buyurtmani BEKOR QILDI\n"
                        f"📦 #{order.order_id}\n"
                        f"👤 {order.first_name} {order.last_name}, {order.phone}\n"
                        f"📝 Sabab: {reason or 'korsatilmagan'}",
            }, timeout=10)
        except Exception:
            pass
    else:
        messages.error(request, _("This order is already confirmed. To cancel it, call +998 99 659 55 55."))
    return redirect('pages:order')

def journal_view(request):
    """CHINAR katalogi — alohida oynada flipbook"""
    from django.shortcuts import render
    return render(request, 'journal.html')
