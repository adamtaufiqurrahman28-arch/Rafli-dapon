from django import template

register = template.Library()


@register.filter
def rupiah(value):
    try:
        value = int(value or 0)
    except (TypeError, ValueError):
        return "Rp -"
    return "Rp {:,}".format(value).replace(",", ".")


@register.filter
def status_class(value):
    mapping = {
        "pending": "status-pending",
        "price_set": "status-info",
        "waiting_payment": "status-warning",
        "paid": "status-success",
        "processing": "status-info",
        "ready": "status-success",
        "completed": "status-success",
        "cancelled": "status-danger",
        "unpaid": "status-warning",
        "waiting_confirmation": "status-info",
        "rejected": "status-danger",
    }
    return mapping.get(value, "status-neutral")
