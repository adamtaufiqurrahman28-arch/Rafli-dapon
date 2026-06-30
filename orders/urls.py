from django.urls import path

from . import views

urlpatterns = [
    path("", views.public_order, name="public_order"),
    path("success/<str:order_code>/", views.order_success, name="order_success"),
    path("status/", views.check_status, name="check_status"),
    path("admin/login/", views.admin_login, name="admin_login"),
    path("admin/logout/", views.admin_logout, name="admin_logout"),
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/orders/", views.admin_orders, name="admin_orders"),
    path("admin/orders/<int:pk>/", views.admin_order_detail, name="admin_order_detail"),
    path("admin/recap/", views.admin_recap, name="admin_recap"),
    path("admin/restaurants/", views.admin_restaurants, name="admin_restaurants"),
    path("admin/menu/", views.admin_menu_items, name="admin_menu_items"),
]
