import requests
from django.conf import settings

API = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

STATUS_LABELS = {
    'pending': '⏳ Ожидает', 'confirmed': '✅ Подтвержден',
    'shipping': '🚚 В доставке', 'completed': '🏁 Завершён', 'canceled': '❌ Отменён',
}
PAY_LABELS = {
    'processing': '🔄 Обрабатывается', 'paid': '💰 Оплачен', 'unpaid': '🚫 Не оплачен',
}
DELIVERY_LABELS = {'delivery': "🚚 Yetkazib berish", 'pickup': "🏬 Olib ketish"}
PAYMENT_METHOD_LABELS = {'payme': 'Payme', 'click': 'Click', 'cash': 'Naqd (Cash on Delivery)'}


def _local_time(dt):
    """Vaqtni Toshkent vaqtiga o'girib, chiroyli formatda qaytaradi"""
    if not dt:
        return ""
    try:
        from django.utils import timezone
        return timezone.localtime(dt).strftime("%d.%m.%Y  %H:%M")
    except Exception:
        return dt.strftime("%d.%m.%Y  %H:%M")


def order_text(order):
    """Buyurtma matnini tuzish."""
    when = _local_time(getattr(order, "created_at", None))
    lines = [
        f"🛒 <b>YANGI BUYURTMA</b>  #{order.order_id}",
        (f"🕒 {when}" if when else ""),
        "",
        f"👤 <b>Mijoz:</b> {order.first_name} {order.last_name}",
        f"📞 <b>Telefon:</b> {order.phone}",
        "",
        f"📦 <b>Olish turi:</b> {DELIVERY_LABELS.get(order.delivery_method, order.delivery_method)}",
    ]
    if order.delivery_method == 'delivery':
        lines.append(f"📍 <b>Manzil:</b> {order.region}, {order.district}, {order.address}"
                     + (f", {order.floor}-qavat" if order.floor else ""))
    lines += [
        f"💳 <b>To'lov turi:</b> {PAYMENT_METHOD_LABELS.get(order.payment_method, order.payment_method)}",
        "",
        "🧺 <b>Mahsulotlar:</b>",
    ]
    for item in order.items.all():
        name = item.product.name if item.product else "—"
        extras = []
        if getattr(item, 'size', ''):
            extras.append(f"o'lcham: {item.size}")
        if getattr(item, 'color', ''):
            extras.append(f"rang: {item.color}")
        extra_txt = f" ({', '.join(extras)})" if extras else ""
        lines.append(f"  • {name}{extra_txt} × {item.quantity} = {item.price * item.quantity:,} UZS".replace(",", " "))
    lines += [
        "",
        f"💵 <b>Jami:</b> {order.total_price:,} UZS".replace(",", " "),
        "" ,
        f"📌 Status: <b>{STATUS_LABELS.get(order.status)}</b>",
        f"💳 To'lov: <b>{PAY_LABELS.get(order.payment_status)}</b>",
    ]
    if order.comment:
        lines.append(f"\n💬 Izoh: {order.comment}")
    return "\n".join(lines)


def order_keyboard(order):
    """Status va to'lov boshqaruv tugmalari."""
    def btn(text, data):
        return {"text": text, "callback_data": data}
    oid = order.id
    return {"inline_keyboard": [
        [btn("✅ Tasdiqlash", f"st:{oid}:confirmed"), btn("🚚 Yetkazishda", f"st:{oid}:shipping")],
        [btn("🏁 Yakunlash", f"st:{oid}:completed"), btn("❌ Bekor qilish", f"st:{oid}:canceled")],
        [btn("💰 To'landi", f"py:{oid}:paid"), btn("🚫 To'lanmadi", f"py:{oid}:unpaid")],
    ]}


def _open_rgb(image_field, max_side=1000):
    """Rasmni ochib RGB qilib, kichraytirib qaytaradi (PIL Image yoki None)."""
    from PIL import Image
    with image_field.open('rb') as fh:
        im = Image.open(fh)
        im.load()
    if im.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', im.size, (255, 255, 255))
        im = im.convert('RGBA')
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert('RGB')
    if max(im.size) > max_side:
        k = max_side / max(im.size)
        im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    return im


def _find_color(color_name):
    """Buyurtmadagi rang nomi bo'yicha ColorModel yozuvini topish."""
    if not color_name:
        return None
    from products.models import ColorModel
    return ColorModel.objects.filter(name__iexact=color_name.strip()).first()


def _paste_swatch(base, swatch):
    """Mahsulot rasmining o'ng-pastki burchagiga tanlangan rang namunasini joylash."""
    from PIL import Image, ImageDraw
    W, H = base.size
    s = max(90, int(min(W, H) * 0.30))          # namuna kvadrati
    b = max(3, s // 22)                          # oq ramka
    sw = swatch.resize((s, s), Image.LANCZOS)

    card = Image.new('RGB', (s + 2*b, s + 2*b), (255, 255, 255))
    card.paste(sw, (b, b))
    r = int(s * 0.16)
    mask = Image.new('L', card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.size[0]-1, card.size[1]-1], radius=r, fill=255)

    m = int(min(W, H) * 0.035)
    base.paste(card, (W - card.size[0] - m, H - card.size[1] - m), mask)
    return base


def _small_photo(image_field, max_side=1000, color_name=''):
    """Mahsulot rasmi (+ tanlangan rang namunasi) JPEG baytlari."""
    from io import BytesIO
    try:
        im = _open_rgb(image_field, max_side)
        col = _find_color(color_name)
        if col is not None and col.image:
            try:
                im = _paste_swatch(im, _open_rgb(col.image, 600))
            except Exception:
                pass                             # rang rasmi ochilmasa — mahsulot rasmi qolsin
        buf = BytesIO()
        im.save(buf, 'JPEG', quality=87)
        return buf.getvalue()
    except Exception:
        # Pillow ishlamasa — faylni o'zini yuboramiz
        try:
            with image_field.open('rb') as fh:
                return fh.read()
        except Exception:
            return None


def item_caption(item):
    """Rasm ostidagi izoh: mahsulot nomi, o'lcham/rang, soni va narxi."""
    name = item.product.name if item.product else "—"
    extras = []
    if getattr(item, 'size', ''):
        extras.append(f"o'lcham: {item.size}")
    if getattr(item, 'color', ''):
        extras.append(f"rang: {item.color}")
    extra_txt = f"\n{', '.join(extras)}" if extras else ""
    total = f"{item.price * item.quantity:,}".replace(",", " ")
    return f"<b>{name}</b>{extra_txt}\n× {item.quantity} = {total} UZS"


def send_order_photos(order):
    """Buyurtmadagi mahsulot rasmlarini albom qilib yuborish."""
    import json
    items = [i for i in order.items.all() if i.product and i.product.image]
    if not items:
        return
    items = items[:10]          # Telegram albomga maksimum 10 ta rasm

    media, files = [], {}
    for idx, item in enumerate(items):
        data = _small_photo(item.product.image, color_name=getattr(item, 'color', ''))
        if not data:
            continue
        key = f"photo{idx}"
        files[key] = (f"{key}.jpg", data, "image/jpeg")
        media.append({
            "type": "photo",
            "media": f"attach://{key}",
            "caption": item_caption(item),
            "parse_mode": "HTML",
        })
    if not media:
        return

    if len(media) == 1:
        # Bitta mahsulot — oddiy rasm (izoh to'liq ko'rinadi)
        key = media[0]["media"].replace("attach://", "")
        requests.post(f"{API}/sendPhoto", data={
            "chat_id": settings.TELEGRAM_ADMIN_CHAT_ID,
            "caption": media[0]["caption"],
            "parse_mode": "HTML",
        }, files={"photo": files[key]}, timeout=60)
    else:
        requests.post(f"{API}/sendMediaGroup", data={
            "chat_id": settings.TELEGRAM_ADMIN_CHAT_ID,
            "media": json.dumps(media),
        }, files=files, timeout=90)


def send_order_notification(order):
    """Yangi buyurtma haqida admin'ga yuborish (avval mahsulot rasmlari, keyin matn)."""
    try:
        send_order_photos(order)
    except Exception as e:
        print(f"Telegram rasm xato: {e}")   # rasm ketmasa ham matn ketsin
    try:
        requests.post(f"{API}/sendMessage", json={
            "chat_id": settings.TELEGRAM_ADMIN_CHAT_ID,
            "text": order_text(order),
            "parse_mode": "HTML",
            "reply_markup": order_keyboard(order),
        }, timeout=10)
    except Exception as e:
        print(f"Telegram xato: {e}")   # bot ishlamasa ham sayt buzilmasin

def send_callback_notification(cb):
    """Qo'ng'iroq so'rovi haqida admin'ga yuborish."""
    try:
        requests.post(f"{API}/sendMessage", json={
            "chat_id": settings.TELEGRAM_ADMIN_CHAT_ID,
            "text": (f"📞 <b>QO'NG'IROQ SO'ROVI</b>\n"
                     f"🕒 {_local_time(getattr(cb, 'created_at', None))}\n\n"
                     f"Mijoz raqam qoldirdi: <b>{cb.phone}</b>\n"
                     f"Tez orada qo'ng'iroq qilib bering!"),
            "parse_mode": "HTML",
        }, timeout=10)
    except Exception as e:
        print(f"Telegram xato: {e}")
