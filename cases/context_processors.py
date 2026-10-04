from django.conf import settings


def app(request):
    return {"APP_NAME": "Fuatilia", "APP_TAGLINE": "Your case. Your evidence. Your next move.", "DEBUG": settings.DEBUG}
