from django import forms
from django.contrib.auth import authenticate

from .models import MenuItem, Order, Restaurant, Setting


class LoginForm(forms.Form):
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={"placeholder": "rafli", "class": "form-control"}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"placeholder": "Password", "class": "form-control"}))

    def clean(self):
        cleaned = super().clean()
        username = cleaned.get("username")
        password = cleaned.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError("Username atau password tidak valid.")
            cleaned["user"] = user
        return cleaned


class OrderCreateForm(forms.ModelForm):
    custom_order = forms.CharField(
        label="Order custom / catatan detail",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Contoh: Nasi + kangkung + otak-otak + kikil + tahu kotak. Atau: Nasi Padang tanpa nangka + ayam bakar dada.",
            }
        ),
    )

    class Meta:
        model = Order
        fields = [
            "customer_name",
            "whatsapp",
            "division",
            "restaurant",
            "custom_restaurant_name",
            "payment_method",
            "proof_image",
        ]
        widgets = {
            "customer_name": forms.TextInput(attrs={"placeholder": "Contoh: Putri"}),
            "whatsapp": forms.TextInput(attrs={"placeholder": "Opsional"}),
            "division": forms.TextInput(attrs={"placeholder": "Opsional"}),
            "custom_restaurant_name": forms.TextInput(attrs={"placeholder": "Contoh: Resto Padang / Bu Nani / campuran"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["restaurant"].queryset = Restaurant.objects.filter(is_active=True)
        self.fields["restaurant"].empty_label = "Resto lain / campuran"
        self.fields["restaurant"].required = False
        self.fields["proof_image"].required = False
        self.fields["proof_image"].label = "Upload bukti bayar"

        for field in self.fields.values():
            css = "form-control"
            if isinstance(field.widget, forms.Select):
                css = "form-select"
            if isinstance(field.widget, forms.FileInput):
                css = "form-control"
            field.widget.attrs.setdefault("class", css)


class OrderAdminUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["total_price", "payment_method", "payment_status", "order_status", "admin_notes"]
        widgets = {
            "admin_notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Catatan admin..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = "form-control"
            if isinstance(field.widget, forms.Select):
                css = "form-select"
            field.widget.attrs.setdefault("class", css)


class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ["name", "slug", "description", "order_mode", "is_active", "sort_order"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ["restaurant", "category", "name", "description", "price", "is_active", "is_daily", "sort_order"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault("class", "form-select")
            else:
                field.widget.attrs.setdefault("class", "form-control")
