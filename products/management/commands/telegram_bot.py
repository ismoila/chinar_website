import time
import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from products.models import Order
from products.telegram import API, order_text, order_keyboard, STATUS_LABELS, PAY_LABELS


class Command(BaseCommand):
    help = "Telegram bot — buyurtma statuslarini boshqarish"

    def handle(self, *args, **options):
        self.stdout.write("Bot ishga tushdi...")
        offset = 0
        while True:
            try:
                r = requests.get(f"{API}/getUpdates",
                                 params={"offset": offset, "timeout": 30}, timeout=40).json()
                for upd in r.get("result", []):
                    offset = upd["update_id"] + 1
                    cb = upd.get("callback_query")
                    if not cb:
                        continue
                    self.handle_callback(cb)
            except Exception as e:
                self.stdout.write(f"Xato: {e}")
                time.sleep(5)

    def handle_callback(self, cb):
        data = cb.get("data", "")          # "st:12:confirmed" yoki "py:12:paid"
        parts = data.split(":")
        if len(parts) != 3:
            return
        kind, oid, value = parts
        try:
            order = Order.objects.get(id=oid)
        except Order.DoesNotExist:
            self.answer(cb["id"], "Buyurtma topilmadi")
            return

        if kind == "st" and value in dict(Order.STATUS_CHOICES):
            order.status = value
            order.save()
            self.answer(cb["id"], f"Status: {STATUS_LABELS.get(value)}")
        elif kind == "py" and value in dict(Order.PAYMENT_STATUS_CHOICES):
            order.payment_status = value
            order.save()
            self.answer(cb["id"], f"To'lov: {PAY_LABELS.get(value)}")
        else:
            return

        # Xabar matnini yangilash (yangi status ko'rinsin)
        msg = cb["message"]
        requests.post(f"{API}/editMessageText", json={
            "chat_id": msg["chat"]["id"],
            "message_id": msg["message_id"],
            "text": order_text(order),
            "parse_mode": "HTML",
            "reply_markup": order_keyboard(order),
        }, timeout=10)

    def answer(self, cb_id, text):
        requests.post(f"{API}/answerCallbackQuery",
                      json={"callback_query_id": cb_id, "text": text}, timeout=10)