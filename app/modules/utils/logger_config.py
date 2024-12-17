import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    # Crear el directorio de logs si no existe
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configurar el logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Configurar el formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler para archivo
    file_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger