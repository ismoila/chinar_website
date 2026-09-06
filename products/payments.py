"""
Payme (Merchant API) va Click (SHOP API) to'lov integratsiyasi.

OQIM:
  1) create_order: mijoz Payme/Click tanlasa -> build_payme_url / build_click_url
     orqali provayderning to'lov sahifasiga yo'naltiriladi.
  2) Mijoz kartadan to'laydi. Provayder serveri bizning callback'larga so'rov yuboradi:
        Payme  -> POST /payments/payme/      (JSON-RPC)
        Click  -> POST /payments/click/prepare/  va  /payments/click/complete/
  3) To'lov muvaffaqiyatli bo'lsa Order.payment_status = 'paid' bo'ladi
     va admin Telegram botga xabar ketadi.

SOZLASH (settings.py):
  PAYME_MERCHANT_ID, PAYME_SECRET_KEY, PAYME_TEST_MODE
  CLICK_MERCHANT_ID, CLICK_SERVICE_ID, CLICK_SECRET_KEY
Kabinetlarda callback URL sifatida ko'rsating:
  Payme: https://SIZNING-DOMEN/payments/payme/
  Click: https://SIZNING-DOMEN/payments/click/prepare/ va .../click/complete/
"""

import base64
import hashlib
import json
from urllib.parse import quote

from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from products.models import Order, PaymentTransaction


# ═══════════════════════════════════════════
#  YORDAMCHILAR
# ═══════════════════════════════════════════

def _ms(dt):
    """Datetime -> millisekund (Payme talabi)"""
    return int(dt.timestamp() * 1000) if dt else 0


def _notify_paid(order, provider):
    """To'lov kelganda admin Telegram botga xabar"""
    try:
        import requests as _req
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        chat_id = getattr(settings, 'TELEGRAM_ADMIN_CHAT_ID', '')
        if token and chat_id:
            _req.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": (f"💰 TO'LOV KELDI ({provider.upper()})\n"
                             f"📦 #{order.order_id}\n"
                             f"💵 {order.total_price:,} so'm".replace(',', ' ') + "\n"
                             f"👤 {order.first_name} {order.last_name}, {order.phone}"),
                },
                timeout=10,
            )
    except Exception:
        pass


# ═══════════════════════════════════════════
#  TO'LOV SAHIFASIGA YO'NALTIRISH URL'LARI
# ═══════════════════════════════════════════

def payme_configured():
    return bool(getattr(settings, 'PAYME_MERCHANT_ID', ''))


def click_configured():
    return bool(getattr(settings, 'CLICK_SERVICE_ID', '')) and bool(getattr(settings, 'CLICK_MERCHANT_ID', ''))


def build_payme_url(order, return_url=''):
    """Payme checkout sahifasi (summa TIYINda)"""
    amount_tiyin = int(order.total_price) * 100
    params = f"m={settings.PAYME_MERCHANT_ID};ac.order_id={order.order_id};a={amount_tiyin}"
    if return_url:
        params += f";c={return_url}"
    encoded = base64.b64encode(params.encode()).decode()
    host = "checkout.test.paycom.uz" if getattr(settings, 'PAYME_TEST_MODE', True) else "checkout.paycom.uz"
    return f"https://{host}/{encoded}"


def build_click_url(order, return_url=''):
    """Click to'lov sahifasi (summa SO'Mda)"""
    url = (f"https://my.click.uz/services/pay"
           f"?service_id={settings.CLICK_SERVICE_ID}"
           f"&merchant_id={settings.CLICK_MERCHANT_ID}"
           f"&amount={int(order.total_price)}"
           f"&transaction_param={order.order_id}")
    if return_url:
        url += f"&return_url={quote(return_url, safe='')}"
    return url


# ═══════════════════════════════════════════
#  PAYME MERCHANT API (JSON-RPC)
# ═══════════════════════════════════════════

# Payme xato kodlari
PAYME_ERR_AUTH = -32504
PAYME_ERR_METHOD = -32601
PAYME_ERR_AMOUNT = -31001
PAYME_ERR_TRANS_NOT_FOUND = -31003
PAYME_ERR_CANNOT_PERFORM = -31008
PAYME_ERR_ORDER_NOT_FOUND = -31050   # account xatolari: -31050..-31099


def _payme_error(request_id, code, message):
    return JsonResponse({
        "id": request_id,
        "error": {"code": code, "message": {"uz": message, "ru": message, "en": message}},
    })


def _payme_result(request_id, result):
    return JsonResponse({"id": request_id, "result": result})


def _payme_auth_ok(request):
    auth = request.headers.get('Authorization', '')
    if not auth.startswith('Basic '):
        return False
    try:
        decoded = base64.b64decode(auth.split(' ', 1)[1]).decode()
    except Exception:
        return False
    # login istalgan bo'lishi mumkin (odatda "Paycom"), parol = bizning kalit
    password = decoded.split(':', 1)[1] if ':' in decoded else ''
    return bool(settings.PAYME_SECRET_KEY) and password == settings.PAYME_SECRET_KEY


def _get_order_by_account(params):
    account = params.get('account') or {}
    order_id = str(account.get('order_id') or '').strip()
    if not order_id:
        return None
    try:
        return Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return None


@csrf_exempt
def payme_callback(request):
    """Payme serveri chaqiradigan yagona JSON-RPC endpoint"""
    if request.method != 'POST':
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return JsonResponse({"error": "invalid json"}, status=400)

    request_id = payload.get('id')
    method = payload.get('method', '')
    params = payload.get('params', {}) or {}

    if not _payme_auth_ok(request):
        return _payme_error(request_id, PAYME_ERR_AUTH, "Avtorizatsiya xatosi")

    # ---------- CheckPerformTransaction ----------
    if method == 'CheckPerformTransaction':
        order = _get_order_by_account(params)
        if order is None:
            return _payme_error(request_id, PAYME_ERR_ORDER_NOT_FOUND, "Buyurtma topilmadi")
        if order.status == 'canceled':
            return _payme_error(request_id, PAYME_ERR_ORDER_NOT_FOUND, "Buyurtma bekor qilingan")
        if order.payment_status == 'paid':
            return _payme_error(request_id, PAYME_ERR_ORDER_NOT_FOUND, "Buyurtma allaqachon to'langan")
        if int(params.get('amount', 0)) != int(order.total_price) * 100:
            return _payme_error(request_id, PAYME_ERR_AMOUNT, "Summa noto'g'ri")
        return _payme_result(request_id, {"allow": True})

    # ---------- CreateTransaction ----------
    if method == 'CreateTransaction':
        trans_id = str(params.get('id', ''))
        existing = PaymentTransaction.objects.filter(provider='payme', trans_id=trans_id).first()
        if existing:
            if existing.state != 1:
                return _payme_error(request_id, PAYME_ERR_CANNOT_PERFORM, "Tranzaksiya holati noto'g'ri")
            return _payme_result(request_id, {
                "create_time": _ms(existing.created_at),
                "transaction": str(existing.id),
                "state": 1,
            })

        order = _get_order_by_account(params)
        if order is None:
            return _payme_error(request_id, PAYME_ERR_ORDER_NOT_FOUND, "Buyurtma topilmadi")
        if order.payment_status == 'paid' or order.status == 'canceled':
            return _payme_error(request_id, PAYME_ERR_ORDER_NOT_FOUND, "Buyurtma to'lovga yopiq")
        if int(params.get('amount', 0)) != int(order.total_price) * 100:
            return _payme_error(request_id, PAYME_ERR_AMOUNT, "Summa noto'g'ri")

        # shu buyurtma bo'yicha boshqa faol payme tranzaksiya bo'lsa - rad etamiz
        if PaymentTransaction.objects.filter(provider='payme', order=order, state=1).exclude(trans_id=trans_id).exists():
            return _payme_error(request_id, PAYME_ERR_CANNOT_PERFORM, "Buyurtma band")

        tx = PaymentTransaction.objects.create(
            provider='payme', trans_id=trans_id, order=order,
            amount=int(order.total_price), state=1,
        )
        return _payme_result(request_id, {
            "create_time": _ms(tx.created_at),
            "transaction": str(tx.id),
            "state": 1,
        })

    # ---------- PerformTransaction ----------
    if method == 'PerformTransaction':
        trans_id = str(params.get('id', ''))
        tx = PaymentTransaction.objects.filter(provider='payme', trans_id=trans_id).first()
        if tx is None:
            return _payme_error(request_id, PAYME_ERR_TRANS_NOT_FOUND, "Tranzaksiya topilmadi")
        if tx.state == 1:
            tx.state = 2
            tx.perform_time = timezone.now()
            tx.save()
            order = tx.order
            order.payment_status = 'paid'
            order.save()
            _notify_paid(order, 'payme')
        if tx.state == 2:
            return _payme_result(request_id, {
                "transaction": str(tx.id),
                "perform_time": _ms(tx.perform_time),
                "state": 2,
            })
        return _payme_error(request_id, PAYME_ERR_CANNOT_PERFORM, "Tranzaksiya holati noto'g'ri")

    # ---------- CancelTransaction ----------
    if method == 'CancelTransaction':
        trans_id = str(params.get('id', ''))
        tx = PaymentTransaction.objects.filter(provider='payme', trans_id=trans_id).first()
        if tx is None:
            return _payme_error(request_id, PAYME_ERR_TRANS_NOT_FOUND, "Tranzaksiya topilmadi")
        if tx.state in (1, 2):
            was_paid = (tx.state == 2)
            tx.state = -1 if tx.state == 1 else -2
            tx.cancel_time = timezone.now()
            tx.reason = params.get('reason')
            tx.save()
            if was_paid:
                order = tx.order
                order.payment_status = 'unpaid'
                order.save()
        return _payme_result(request_id, {
            "transaction": str(tx.id),
            "cancel_time": _ms(tx.cancel_time),
            "state": tx.state,
        })

    # ---------- CheckTransaction ----------
    if method == 'CheckTransaction':
        trans_id = str(params.get('id', ''))
        tx = PaymentTransaction.objects.filter(provider='payme', trans_id=trans_id).first()
        if tx is None:
            return _payme_error(request_id, PAYME_ERR_TRANS_NOT_FOUND, "Tranzaksiya topilmadi")
        return _payme_result(request_id, {
            "create_time": _ms(tx.created_at),
            "perform_time": _ms(tx.perform_time),
            "cancel_time": _ms(tx.cancel_time),
            "transaction": str(tx.id),
            "state": tx.state,
            "reason": tx.reason,
        })

    # ---------- GetStatement ----------
    if method == 'GetStatement':
        frm = int(params.get('from', 0))
        to = int(params.get('to', 0))
        txs = PaymentTransaction.objects.filter(provider='payme')
        result = []
        for tx in txs:
            ct = _ms(tx.created_at)
            if frm <= ct <= to:
                result.append({
                    "id": tx.trans_id,
                    "time": ct,
                    "amount": tx.amount * 100,
                    "account": {"order_id": tx.order.order_id},
                    "create_time": ct,
                    "perform_time": _ms(tx.perform_time),
                    "cancel_time": _ms(tx.cancel_time),
                    "transaction": str(tx.id),
                    "state": tx.state,
                    "reason": tx.reason,
                })
        return _payme_result(request_id, {"transactions": result})

    return _payme_error(request_id, PAYME_ERR_METHOD, "Metod topilmadi")


# ═══════════════════════════════════════════
#  CLICK SHOP API (Prepare / Complete)
# ═══════════════════════════════════════════

def _click_sign_ok(data, with_prepare_id=False):
    sign_time = data.get('sign_time', '')
    raw = (
        str(data.get('click_trans_id', '')) +
        str(data.get('service_id', '')) +
        settings.CLICK_SECRET_KEY +
        str(data.get('merchant_trans_id', ''))
    )
    if with_prepare_id:
        raw += str(data.get('merchant_prepare_id', ''))
    raw += str(data.get('amount', '')) + str(data.get('action', '')) + sign_time
    return hashlib.md5(raw.encode()).hexdigest() == data.get('sign_string', '')


def _click_response(data, error, error_note, prepare_id=None, confirm_id=None):
    resp = {
        "click_trans_id": data.get('click_trans_id'),
        "merchant_trans_id": data.get('merchant_trans_id'),
        "error": error,
        "error_note": error_note,
    }
    if prepare_id is not None:
        resp["merchant_prepare_id"] = prepare_id
    if confirm_id is not None:
        resp["merchant_confirm_id"] = confirm_id
    return JsonResponse(resp)


@csrf_exempt
def click_prepare(request):
    data = request.POST
    if not _click_sign_ok(data):
        return _click_response(data, -1, "SIGN CHECK FAILED")

    order_id = str(data.get('merchant_trans_id', '')).strip()
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return _click_response(data, -5, "Order not found")

    if order.payment_status == 'paid':
        return _click_response(data, -4, "Already paid")
    if order.status == 'canceled':
        return _click_response(data, -9, "Order canceled")

    try:
        amount = int(float(data.get('amount', 0)))
    except (ValueError, TypeError):
        amount = 0
    if amount != int(order.total_price):
        return _click_response(data, -2, "Incorrect amount")

    tx = PaymentTransaction.objects.create(
        provider='click',
        trans_id=str(data.get('click_trans_id', '')),
        order=order,
        amount=amount,
        state=0,   # prepared
    )
    return _click_response(data, 0, "Success", prepare_id=tx.id)


@csrf_exempt
def click_complete(request):
    data = request.POST
    if not _click_sign_ok(data, with_prepare_id=True):
        return _click_response(data, -1, "SIGN CHECK FAILED")

    try:
        tx = PaymentTransaction.objects.get(
            provider='click', id=int(data.get('merchant_prepare_id', 0)))
    except (PaymentTransaction.DoesNotExist, ValueError, TypeError):
        return _click_response(data, -6, "Transaction not found")

    order = tx.order

    # Click xato yuborgan bo'lsa (mijoz to'lovni bekor qilgan)
    if str(data.get('error', '0')) not in ('0', ''):
        tx.state = -1
        tx.cancel_time = timezone.now()
        tx.save()
        return _click_response(data, -9, "Payment cancelled", confirm_id=tx.id)

    if tx.state == 1:
        return _click_response(data, 0, "Already confirmed", confirm_id=tx.id)

    tx.state = 1
    tx.perform_time = timezone.now()
    tx.save()
    order.payment_status = 'paid'
    order.save()
    _notify_paid(order, 'click')
    return _click_response(data, 0, "Success", confirm_id=tx.id)
