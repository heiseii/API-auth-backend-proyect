import re
from django.core.exceptions import ValidationError


class StrongPasswordValidator:
   
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    SPECIAL_CHARACTERS = r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\]"

    def validate(self, password, user=None):
        errors = []

        if len(password) < self.MIN_LENGTH:
            errors.append(f"La contraseña debe tener al menos {self.MIN_LENGTH} caracteres.")

        if len(password) > self.MAX_LENGTH:
            errors.append(f"La contraseña no puede superar los {self.MAX_LENGTH} caracteres.")

        if not re.search(r"[A-Z]", password):
            errors.append("La contraseña debe contener al menos una letra mayúscula.")

        if not re.search(r"[a-z]", password):
            errors.append("La contraseña debe contener al menos una letra minúscula.")

        if not re.search(r"\d", password):
            errors.append("La contraseña debe contener al menos un número.")

        if not re.search(self.SPECIAL_CHARACTERS, password):
            errors.append("La contraseña debe contener al menos un carácter especial (!@#$%^&*...).")

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return (
            f"La contraseña debe tener entre {self.MIN_LENGTH} y {self.MAX_LENGTH} caracteres, "
            "e incluir mayúsculas, minúsculas, números y caracteres especiales."
        )