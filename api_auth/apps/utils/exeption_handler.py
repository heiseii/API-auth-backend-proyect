from rest_framework.views import exception_handler
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied


# Mapa de códigos semánticos por status HTTP

ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "AUTHENTICATION_REQUIRED",
    403: "PERMISSION_DENIED",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    429: "TOO_MANY_REQUESTS",
    500: "INTERNAL_SERVER_ERROR",
}


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        status_code = response.status_code
        data = response.data

        # Extraer mensaje principal
        if isinstance(data, dict) and "detail" in data:
            message = str(data["detail"])
            fields = {}
        elif isinstance(data, dict):
            # Errores de validación de serializer — tienen campos específicos
            message = "Error de validación."
            fields = _format_fields(data)
        elif isinstance(data, list):
            message = str(data[0]) if data else "Error desconocido."
            fields = {}
        else:
            message = str(data)
            fields = {}

        # Código semántico según el status
        code = ERROR_CODES.get(status_code, "ERROR")

        # Casos especiales con códigos más descriptivos
        if status_code == 401:
            code = "AUTHENTICATION_REQUIRED"
        elif status_code == 403:
            code = "PERMISSION_DENIED"
        elif status_code == 429:
            code = "TOO_MANY_REQUESTS"
            message = "Demasiadas solicitudes. Esperá un momento antes de intentar de nuevo."

        response.data = {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "fields": fields
            }
        }

    return response


def _format_fields(data):
    
    fields = {}
    for field, errors in data.items():
        if isinstance(errors, list):
            fields[field] = [str(e) for e in errors]
        else:
            fields[field] = [str(errors)]
    return fields