import re
import secrets
import string

import unicodedata


def slugify(value: str) -> str:
    """Convierte 'Hola Mundo!' en 'hola-mundo'"""
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    return re.sub(r'[-\s]+', '-', value)


def generate_unique_slug(name: str) -> str:
    # 1. Normalización básica (reutilizando el slugify anterior)
    slug = slugify(name)

    # 2. Añadimos un sufijo aleatorio de 4 caracteres (ej: mi-casa-a8f2)
    # Esto garantiza que el topic_prefix sea único en el Broker MQTT
    suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(4))
    return f"{slug}-{suffix}"
