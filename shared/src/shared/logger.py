import sys
from loguru import logger


def setup_logger(service_name: str, log_file: str = ".logs/app.log"):
    """Configuración unificada de Loguru para todo el ecosistema home."""

    # Eliminamos el logger por defecto
    logger.remove()

    # Consola con tu formato personalizado
    logger.add(
        sys.stdout,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            f"<cyan>{service_name}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # Archivo rotativo
    logger.add(log_file, rotation="10 MB", retention="7 days")

    return logger.bind(service=service_name)