from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Limita los intentos de login a 5 por minuto por IP.
    Definido en settings.py como 'login': '5/minute'
    """
    scope = "login"