from django.conf import settings


def branding(request):
    return {
        "APP_NAME": settings.APP_NAME,
        "POWERED_BY": settings.POWERED_BY,
        "DEFAULT_PICKUP_WINDOW": settings.DEFAULT_PICKUP_WINDOW,
        "DEFAULT_ORDER_WINDOW": settings.DEFAULT_ORDER_WINDOW,
    }
