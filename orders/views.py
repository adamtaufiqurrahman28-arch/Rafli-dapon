from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import LoginForm, MenuItemForm, OrderAdminUpdateForm, OrderCreateForm, RestaurantForm
from .models import MenuItem, Order, OrderItem, Restaurant, Setting


def rupiah_text(value):
    try:
        number = int(value or 0)
    except (TypeError, ValueError):
        return "Rp -"
    return "Rp. {:,}".format(number).replace(",", ".")


def indonesia_date_text(date_value):
    days = {
        0: "Senin",
        1: "Selasa",
        2: "Rabu",
        3: "Kamis",
        4: "Jumat",
        5: "Sabtu",
        6: "Minggu",
    }
    months = {
        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember",
    }
    return f"{days[date_value.weekday()]}, {date_value.day} {months[date_value.month]} {date_value.year}"


def public_order(request):
    restaurants = Restaurant.objects.filter(is_active=True).prefetch_related("menu_items", "categories")
    menu_items = MenuItem.objects.filter(is_active=True, is_daily=True).select_related("restaurant", "category")

    if request.method == "POST":
        form = OrderCreateForm(request.POST, request.FILES)
        selected_ids = request.POST.getlist("menu_items")
        if form.is_valid():
            order = form.save(commit=False)
            order.pickup_window = Setting.get_value("pickup_window", "11.00 - 12.00 WIB")
            custom_order = form.cleaned_data.get("custom_order", "").strip()
            if custom_order:
                order.notes = custom_order
            if request.FILES.get("proof_image"):
                order.payment_status = "waiting_confirmation"
            order.save()

            total = Decimal("0")
            for item in MenuItem.objects.filter(id__in=selected_ids, is_active=True):
                qty_raw = request.POST.get(f"qty_{item.id}", "1")
                try:
                    qty = max(1, int(qty_raw))
                except ValueError:
                    qty = 1
                unit_price = item.price
                subtotal = (unit_price or Decimal("0")) * qty
                OrderItem.objects.create(
                    order=order,
                    menu_item=item,
                    item_name=item.name,
                    qty=qty,
                    unit_price=unit_price,
                    subtotal=subtotal,
                )
                total += subtotal

            if custom_order:
                OrderItem.objects.create(
                    order=order,
                    item_name="Order custom",
                    qty=1,
                    unit_price=None,
                    subtotal=0,
                    notes=custom_order,
                )

            order.total_price = total
            if total > 0:
                order.order_status = "price_set"
                if order.payment_status == "unpaid":
                    order.payment_status = "unpaid"
            order.save(update_fields=["total_price", "order_status", "payment_status", "updated_at"])
            messages.success(request, "Pesanan berhasil dibuat. Simpan kode order untuk cek status.")
            return redirect("order_success", order_code=order.order_code)
    else:
        form = OrderCreateForm()

    context = {
        "form": form,
        "restaurants": restaurants,
        "menu_items": menu_items,
        "settings": {
            "qris_name": Setting.get_value("qris_name", "Lunch Order RNZ"),
            "qris_note": Setting.get_value("qris_note", "Pastikan nominal sesuai total pesanan."),
            "bank_account": Setting.get_value("bank_account", "4061208229"),
            "bank_name": Setting.get_value("bank_name", "Transfer Bank"),
            "bank_owner": Setting.get_value("bank_owner", "RAFLI DAFRIAN"),
            "order_window": Setting.get_value("order_window", "09.00 - 10.50 WIB"),
            "pickup_window": Setting.get_value("pickup_window", "11.00 - 12.00 WIB"),
        },
    }
    return render(request, "orders/order_form.html", context)


def order_success(request, order_code):
    order = get_object_or_404(Order.objects.prefetch_related("items"), order_code=order_code)
    settings = {
        "qris_name": Setting.get_value("qris_name", "Lunch Order RNZ"),
        "qris_note": Setting.get_value("qris_note", "Pastikan nominal sesuai total pesanan."),
        "bank_account": Setting.get_value("bank_account", "4061208229"),
        "bank_name": Setting.get_value("bank_name", "Transfer Bank"),
        "bank_owner": Setting.get_value("bank_owner", "RAFLI DAFRIAN"),
    }
    return render(request, "orders/order_success.html", {"order": order, "settings": settings})


def check_status(request):
    query = request.GET.get("q", "").strip()
    orders = Order.objects.none()
    if query:
        orders = Order.objects.filter(
            Q(order_code__icontains=query) | Q(customer_name__icontains=query) | Q(whatsapp__icontains=query)
        ).prefetch_related("items")[:20]
    return render(request, "orders/check_status.html", {"query": query, "orders": orders})


def admin_login(request):
    if request.user.is_authenticated:
        return redirect("admin_dashboard")
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.cleaned_data["user"])
        return redirect("admin_dashboard")
    return render(request, "orders/admin/login.html", {"form": form})


@login_required
def admin_logout(request):
    logout(request)
    return redirect("admin_login")


@login_required
def admin_dashboard(request):
    today = timezone.localdate()
    orders = Order.objects.filter(order_date=today)
    stats = {
        "total_orders": orders.count(),
        "revenue": orders.filter(payment_status="paid").aggregate(total=Sum("total_price"))["total"] or 0,
        "paid": orders.filter(payment_status="paid").count(),
        "waiting": orders.exclude(payment_status="paid").count(),
    }
    by_status = orders.values("order_status").annotate(total=Count("id")).order_by("order_status")
    payment_summary = orders.values("payment_method").annotate(total=Sum("total_price"), count=Count("id")).order_by("payment_method")
    latest = orders.prefetch_related("items")[:8]
    return render(
        request,
        "orders/admin/dashboard.html",
        {
            "today": today,
            "stats": stats,
            "by_status": by_status,
            "payment_summary": payment_summary,
            "latest": latest,
        },
    )


@login_required
def admin_orders(request):
    status = request.GET.get("status", "")
    date = request.GET.get("date", "")
    q = request.GET.get("q", "").strip()
    orders = Order.objects.select_related("restaurant").prefetch_related("items")
    if status:
        orders = orders.filter(Q(order_status=status) | Q(payment_status=status))
    if date:
        orders = orders.filter(order_date=date)
    if q:
        orders = orders.filter(Q(order_code__icontains=q) | Q(customer_name__icontains=q) | Q(notes__icontains=q))
    paginator = Paginator(orders, 12)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "orders/admin/order_list.html", {"page": page, "status": status, "date": date, "q": q})


@login_required
def admin_order_detail(request, pk):
    order = get_object_or_404(Order.objects.select_related("restaurant").prefetch_related("items"), pk=pk)
    if request.method == "POST":
        form = OrderAdminUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Pesanan berhasil diperbarui.")
            return redirect("admin_order_detail", pk=order.pk)
    else:
        form = OrderAdminUpdateForm(instance=order)
    return render(request, "orders/admin/order_detail.html", {"order": order, "form": form})


@login_required
def admin_recap(request):
    date_raw = request.GET.get("date")
    try:
        selected_date = timezone.datetime.strptime(date_raw, "%Y-%m-%d").date() if date_raw else timezone.localdate()
    except ValueError:
        selected_date = timezone.localdate()

    orders = Order.objects.filter(order_date=selected_date).select_related("restaurant").prefetch_related("items").order_by("created_at")
    order_window = Setting.get_value("order_window", "09.00 - 10.50 WIB")
    pickup_window = Setting.get_value("pickup_window", "11.00 - 12.00 WIB")
    bank_account = Setting.get_value("bank_account", "4061208229")
    bank_owner = Setting.get_value("bank_owner", "RAFLI DAFRIAN")

    lines = []
    lines.append("Update List Pemesanan Hari Ini")
    lines.append(f"Hari/Tanggal: {indonesia_date_text(selected_date)}")
    lines.append(f"Waktu pesan : Pukul {order_window}")
    lines.append(f"Waktu pengambilan : {pickup_window}")
    lines.append("")
    lines.append("Berikut list pesanan hari ini :")
    for idx, order in enumerate(orders, start=1):
        done = " (done)" if order.is_done else ""
        lines.append(f"{idx}. {order.customer_name} ({order.restaurant_label})")
        for item in order.items.all():
            if item.notes and item.item_name == "Order custom":
                lines.append(f"- {item.notes}")
            else:
                suffix = f" x{item.qty}" if item.qty > 1 else ""
                lines.append(f"- {item.item_name}{suffix}")
        lines.append(f"{rupiah_text(order.total_price)}{done}")
    if not orders.exists():
        lines.append("1.")
        lines.append("-")
        lines.append("Rp.")
    lines.append("")
    lines.append(f"Pembayaran Transfer : {bank_account} (A/N {bank_owner}).")
    lines.append("Pembayaran Cash : Boleh di kasihkan dulu uangnya sebelum pengambilan pesanan yaa...")
    lines.append("Note : Minta tolong untuk yang order makanan bisa langsung bayar transfer/cash setelah harga sudah ada di list pesanan ya....🙏")
    lines.append("")
    lines.append("TERIMA KASIH😊")
    recap_text = "\n".join(lines)
    return render(request, "orders/admin/recap.html", {"orders": orders, "selected_date": selected_date, "recap_text": recap_text})


@login_required
def admin_restaurants(request):
    restaurants = Restaurant.objects.all()
    form = RestaurantForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Resto berhasil ditambahkan.")
        return redirect("admin_restaurants")
    return render(request, "orders/admin/restaurants.html", {"restaurants": restaurants, "form": form})


@login_required
def admin_menu_items(request):
    items = MenuItem.objects.select_related("restaurant", "category")
    form = MenuItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Menu berhasil ditambahkan.")
        return redirect("admin_menu_items")
    return render(request, "orders/admin/menu_items.html", {"items": items, "form": form})
