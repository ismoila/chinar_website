"""
DevSMS balansini tekshirish.
Ishlatish:  python manage.py sms_balance
"""
from django.core.management.base import BaseCommand
from products.sms import get_balance


class Command(BaseCommand):
    help = "DevSMS balansini ko'rsatadi"

    def handle(self, *args, **options):
        data = get_balance()
        if not data.get('success'):
            self.stdout.write(self.style.ERROR(f"Xato: {data.get('error') or data}"))
            return
        d = data.get('data', {})
        st = d.get('statistics', {})
        self.stdout.write(self.style.SUCCESS(f"Balans:      {d.get('balance')} so'm"))
        self.stdout.write(f"SMS narxi:   {d.get('sms_price')} so'm")
        self.stdout.write(f"Bugun:       {st.get('today_sms')} ta SMS ({st.get('today_spent')} so'm)")
        self.stdout.write(f"Shu oy:      {st.get('month_sms')} ta SMS ({st.get('month_spent')} so'm)")
        self.stdout.write(f"Jami:        {st.get('total_sms')} ta SMS ({st.get('total_spent')} so'm)")
