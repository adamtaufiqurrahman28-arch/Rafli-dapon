from decimal import Decimal

from django.db import models
from django.utils import timezone


class Restaurant(models.Model):
    CATALOG = "catalog"
    CUSTOM = "custom"
    MIXED = "mixed"
    ORDER_MODE_CHOICES = [
        (CATALOG, "Catalog"),
        (CUSTOM, "Custom"),
        (MIXED, "Mixed"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order_mode = models.CharField(max_length=20, choices=ORDER_MODE_CHOICES, default=MIXED)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class MenuCategory(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=120)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name_plural = "Menu categories"

    def __str__(self):
        return f"{self.restaurant.name} - {self.name}"


class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name="menu_items")
    category = models.ForeignKey(MenuCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="items")
    name = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_daily = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["restaurant__sort_order", "sort_order", "name"]

    def __str__(self):
        return self.name

    @property
    def has_fixed_price(self):
        return self.price is not None


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("price_set", "Harga Ditetapkan"),
        ("waiting_payment", "Menunggu Pembayaran"),
        ("paid", "Sudah Bayar"),
        ("processing", "Diproses"),
        ("ready", "Siap Diambil"),
        ("completed", "Selesai"),
        ("cancelled", "Dibatalkan"),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("unpaid", "Belum Bayar"),
        ("waiting_confirmation", "Menunggu Konfirmasi"),
        ("paid", "Sudah Bayar"),
        ("rejected", "Ditolak"),
    ]
    PAYMENT_METHOD_CHOICES = [
        ("qris", "QRIS"),
        ("transfer", "Transfer"),
        ("cash", "Cash"),
    ]

    order_code = models.CharField(max_length=32, unique=True, blank=True)
    order_date = models.DateField(default=timezone.localdate)
    customer_name = models.CharField(max_length=100)
    whatsapp = models.CharField(max_length=30, blank=True)
    division = models.CharField(max_length=100, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    custom_restaurant_name = models.CharField(max_length=120, blank=True)
    pickup_window = models.CharField(max_length=60, default="11.00 - 12.00 WIB")
    notes = models.TextField(blank=True, help_text="Catatan pesanan atau order custom")
    total_price = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="qris")
    payment_status = models.CharField(max_length=30, choices=PAYMENT_STATUS_CHOICES, default="unpaid")
    order_status = models.CharField(max_length=30, choices=ORDER_STATUS_CHOICES, default="pending")
    proof_image = models.ImageField(upload_to="proofs/", null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_code} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.order_code:
            today = self.order_date or timezone.localdate()
            prefix = today.strftime("ORD-%Y%m%d")
            last_count = Order.objects.filter(order_code__startswith=prefix).count() + 1
            self.order_code = f"{prefix}-{last_count:04d}"
        super().save(*args, **kwargs)

    @property
    def restaurant_label(self):
        if self.restaurant:
            return self.restaurant.name
        return self.custom_restaurant_name or "Resto lain / campuran"

    @property
    def is_done(self):
        return self.payment_status == "paid" or self.order_status in {"paid", "processing", "ready", "completed"}


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, blank=True)
    item_name = models.CharField(max_length=220)
    qty = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    notes = models.CharField(max_length=220, blank=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.item_name

    def save(self, *args, **kwargs):
        if self.unit_price is not None:
            self.subtotal = Decimal(self.unit_price) * self.qty
        super().save(*args, **kwargs)


class Setting(models.Model):
    key = models.CharField(max_length=80, unique=True)
    value = models.TextField(blank=True)
    label = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["key"]

    def __str__(self):
        return self.key

    @classmethod
    def get_value(cls, key, default=""):
        item = cls.objects.filter(key=key).first()
        return item.value if item else default
