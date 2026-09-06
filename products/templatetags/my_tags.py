from django import template
from django.db.models import Sum

from products.models import ProductModel

register = template.Library()

@register.simple_tag
def get_cart_info(request, coupon=None):
    cart_data = request.session.get("data", [])
    if not cart_data:
        return 0, 0.0
    quantity = len(cart_data)
    total_price = 0
    for data in cart_data:
        try:
            product = ProductModel.objects.get(pk=data['pk'])
        except ProductModel.DoesNotExist:
            continue
        size = (data.get('size') or '').strip()
        total_price += product.price_uzs_for_size(size) * int(data['quantity'])
    if coupon:
        total_price = total_price - ((total_price / 100) * coupon.discount)
    return quantity, int(total_price)


@register.filter(name='each_total_price')
def each_total_price(price, quantity):
    total_price = price * float(quantity)
    return "{:.2f}".format(total_price)


@register.filter
def in_cart(request, pk):
    cart = request.session.get("data", [])
    for item in cart:
        if item["pk"] == pk:
            return True
    return False

@register.filter
def uzbek_price(value):
    try:
        value = int(value)
        return f"{value:,}".replace(",", " ")
    except (ValueError, TypeError):
        return value
    
@register.filter
def uzs_format(value):
    try:
        value = int(value)
        return f"{value:,}".replace(",", ".")
    except (ValueError, TypeError):
        return value

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
@register.simple_tag(takes_context=True)
def in_cart(context, pk):
    """Mahsulot savatda bormi — sessiyadan tekshiradi (hamma sahifada ishlaydi)."""
    request = context.get('request')
    if not request:
        return False
    data = request.session.get('data', [])
    return any(str(item.get('pk')) == str(pk) for item in data)

@register.simple_tag
def partner_logos():
    """assets/images/partners papkasidagi hamkor logolarini avtomatik topadi."""
    import os
    from django.conf import settings
    from django.templatetags.static import static as static_url
    seen, result = set(), []
    roots = list(getattr(settings, 'STATICFILES_DIRS', [])) + [os.path.join(settings.BASE_DIR, 'static')]
    for root in roots:
        d = os.path.join(str(root), 'images', 'partners')
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.svg')) and f not in seen:
                seen.add(f)
                result.append(static_url('images/partners/' + f))
    return result

@register.simple_tag(takes_context=True)
def my_review_vote(context, review_id):
    """User shu sharhga qanday ovoz berganini qaytaradi: 'like' / 'dislike' / ''."""
    request = context.get('request')
    if not request:
        return ''
    return request.session.get('review_votes', {}).get(str(review_id), '')

@register.filter
def basename(path):
    """Fayl nomini qaytaradi (papkasidan qat'i nazar taqqoslash uchun)."""
    import os
    return os.path.basename(str(path))
