# Generated manually for Lunch Order RNZ MVP
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('slug', models.SlugField(unique=True)),
                ('description', models.TextField(blank=True)),
                ('order_mode', models.CharField(choices=[('catalog', 'Catalog'), ('custom', 'Custom'), ('mixed', 'Mixed')], default='mixed', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['sort_order', 'name']},
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=80, unique=True)),
                ('value', models.TextField(blank=True)),
                ('label', models.CharField(blank=True, max_length=120)),
            ],
            options={'ordering': ['key']},
        ),
        migrations.CreateModel(
            name='MenuCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='orders.restaurant')),
            ],
            options={'verbose_name_plural': 'Menu categories', 'ordering': ['sort_order', 'name']},
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=180)),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(blank=True, decimal_places=0, max_digits=12, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_daily', models.BooleanField(default=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='orders.menucategory')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='menu_items', to='orders.restaurant')),
            ],
            options={'ordering': ['restaurant__sort_order', 'sort_order', 'name']},
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_code', models.CharField(blank=True, max_length=32, unique=True)),
                ('order_date', models.DateField(default=django.utils.timezone.localdate)),
                ('customer_name', models.CharField(max_length=100)),
                ('whatsapp', models.CharField(blank=True, max_length=30)),
                ('division', models.CharField(blank=True, max_length=100)),
                ('custom_restaurant_name', models.CharField(blank=True, max_length=120)),
                ('pickup_window', models.CharField(default='11.00 - 12.00 WIB', max_length=60)),
                ('notes', models.TextField(blank=True, help_text='Catatan pesanan atau order custom')),
                ('total_price', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('payment_method', models.CharField(choices=[('qris', 'QRIS'), ('transfer', 'Transfer'), ('cash', 'Cash')], default='qris', max_length=20)),
                ('payment_status', models.CharField(choices=[('unpaid', 'Belum Bayar'), ('waiting_confirmation', 'Menunggu Konfirmasi'), ('paid', 'Sudah Bayar'), ('rejected', 'Ditolak')], default='unpaid', max_length=30)),
                ('order_status', models.CharField(choices=[('pending', 'Pending'), ('price_set', 'Harga Ditetapkan'), ('waiting_payment', 'Menunggu Pembayaran'), ('paid', 'Sudah Bayar'), ('processing', 'Diproses'), ('ready', 'Siap Diambil'), ('completed', 'Selesai'), ('cancelled', 'Dibatalkan')], default='pending', max_length=30)),
                ('proof_image', models.ImageField(blank=True, null=True, upload_to='proofs/')),
                ('admin_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('restaurant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='orders.restaurant')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=220)),
                ('qty', models.PositiveIntegerField(default=1)),
                ('unit_price', models.DecimalField(blank=True, decimal_places=0, max_digits=12, null=True)),
                ('subtotal', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('notes', models.CharField(blank=True, max_length=220)),
                ('menu_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.menuitem')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order')),
            ],
            options={'ordering': ['id']},
        ),
    ]
