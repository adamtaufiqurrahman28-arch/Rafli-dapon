from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from orders.models import MenuCategory, MenuItem, Order, OrderItem, Restaurant, Setting


class Command(BaseCommand):
    help = "Seed sample data untuk Lunch Order RNZ."

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(username="rafli", defaults={"email": "rafli@lunchorder.local", "is_staff": True, "is_superuser": True})
        user.email = "rafli@lunchorder.local"
        user.is_staff = True
        user.is_superuser = True
        user.set_password("P@ssw0rd")
        user.save()

        settings_data = {
            "order_window": ("09.00 - 10.50 WIB", "Waktu pesan"),
            "pickup_window": ("11.00 - 12.00 WIB", "Waktu pengambilan"),
            "qris_name": ("Lunch Order RNZ", "Nama QRIS"),
            "qris_note": ("Pastikan nominal sesuai total pesanan.", "Catatan QRIS"),
            "bank_account": ("4061208229", "Nomor rekening"),
            "bank_name": ("Transfer Bank", "Nama bank"),
            "bank_owner": ("RAFLI DAFRIAN", "Atas nama rekening"),
        }
        for key, (value, label) in settings_data.items():
            Setting.objects.update_or_create(key=key, defaults={"value": value, "label": label})

        gracia, _ = Restaurant.objects.update_or_create(
            slug="waroeng-manado-gracia",
            defaults={"name": "Waroeng Manado Gracia", "order_mode": "mixed", "sort_order": 1, "is_active": True},
        )
        bu_nani, _ = Restaurant.objects.update_or_create(
            slug="bu-nani",
            defaults={"name": "Bu Nani", "order_mode": "custom", "sort_order": 2, "is_active": True},
        )
        resto_ayam, _ = Restaurant.objects.update_or_create(
            slug="resto-ayam",
            defaults={"name": "Resto Ayam", "order_mode": "custom", "sort_order": 3, "is_active": True},
        )
        resto_padang, _ = Restaurant.objects.update_or_create(
            slug="resto-padang",
            defaults={"name": "Resto Padang", "order_mode": "custom", "sort_order": 4, "is_active": True},
        )

        special, _ = MenuCategory.objects.update_or_create(restaurant=gracia, name="Spesial Paket Menu Hari Ini", defaults={"sort_order": 1})
        ramesan, _ = MenuCategory.objects.update_or_create(restaurant=gracia, name="Pilihan Menu Ramesan", defaults={"sort_order": 2})
        gorengan, _ = MenuCategory.objects.update_or_create(restaurant=gracia, name="Gorengan", defaults={"sort_order": 3})

        items = [
            (special, "Nasi Daun Jeruk + Ayam Goreng", "Pilihan ayam: dada/paha. Include tempe dan lalapan.", 20000),
            (special, "Paket Nasi Daun Jeruk Plus Sei Sapi Sambal Matah", "Dengan sayur tumis.", 27000),
            (special, "Paket Rawon Daging + Nasi", "Paket rawon daging lengkap.", 32000),
            (special, "Paket Sop Daging Basudara + Nasi", "Paket sop daging basudara.", 30000),
            (ramesan, "Telur Balado", "", None),
            (ramesan, "Pesmol Ikan Kembung", "", None),
            (ramesan, "Cakalang Asap Rica", "", None),
            (ramesan, "Cumi Balado", "", None),
            (ramesan, "Dada Tuna Lada Hitam", "", None),
            (ramesan, "Sei Sapi Sambal Matah", "", None),
            (ramesan, "Opor Ayam", "", None),
            (ramesan, "Ayam Suwir Balado", "", None),
            (ramesan, "Puyunghay Ayam", "", None),
            (ramesan, "Ayam Saus Tiram", "", None),
            (ramesan, "Sop Bakso Lohua", "", None),
            (ramesan, "Ayam Goreng Rempah (Paha/Dada)", "", None),
            (ramesan, "Capcay Bakso", "", None),
            (ramesan, "Tumis Toge", "", None),
            (ramesan, "Tumis Kangkung", "", None),
            (ramesan, "Tempe Orek Kecap", "", None),
            (ramesan, "Mie Goreng Bakso", "", None),
            (gorengan, "Bakwan Jagung", "", 3000),
            (gorengan, "Donat Kentang", "", 5000),
        ]
        for idx, (category, name, description, price) in enumerate(items, start=1):
            MenuItem.objects.update_or_create(
                restaurant=gracia,
                name=name,
                defaults={
                    "category": category,
                    "description": description,
                    "price": price,
                    "is_active": True,
                    "is_daily": True,
                    "sort_order": idx,
                },
            )

        if not Order.objects.filter(order_date=timezone.localdate()).exists():
            samples = [
                ("Putri", resto_ayam, "nasi + ayam bakar paha + risol 1 + sambal terasi", 21000, "qris", "unpaid", "price_set"),
                ("Bintang", resto_ayam, "Tempe Mendoan 2", 4000, "qris", "paid", "completed"),
                ("Bintang", resto_padang, "Bintang nitip: Nasi Padang: Nasi (Tanpa Nangka) + Ayam Bakar Dada", 17000, "transfer", "paid", "completed"),
                ("Puri", resto_ayam, "sambel campur (ijo+merah), tahu kotak/mendoan 1", 5000, "cash", "unpaid", "price_set"),
                ("Andra", bu_nani, "Nasi, kangkung, otak2, kikil, tahu kotak tempe 1", 18000, "transfer", "paid", "completed"),
                ("Filbi", bu_nani, "Nasi + usus + bihun + toge + tahu kotak", 15000, "qris", "paid", "completed"),
            ]
            for name, resto, note, price, method, pay_status, status in samples:
                order = Order.objects.create(
                    customer_name=name,
                    whatsapp="08xxxxxxxxxx",
                    division="Marketing",
                    restaurant=resto,
                    notes=note,
                    total_price=Decimal(price),
                    payment_method=method,
                    payment_status=pay_status,
                    order_status=status,
                )
                OrderItem.objects.create(order=order, item_name=note, qty=1, unit_price=price, subtotal=price)

        self.stdout.write(self.style.SUCCESS("Seed selesai. Login admin: rafli / P@ssw0rd"))
