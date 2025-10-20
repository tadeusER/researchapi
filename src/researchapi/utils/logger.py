import logging
import os

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Crear manejador y establecer nivel
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Crear formatter
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Agregar formatter al manejador
    ch.setFormatter(formatter)

    # Agregar manejador al logger
    logger.addHandler(ch)

    # Asegurarse de que la carpeta logs exista
    log_dir = '../logs'
    if not os.path.exists(log_dir):
        log_dir = '.'

    # Crear un manejador de archivos para registrar los errores
    fh = logging.FileHandler(f'{log_dir}/apiresearch.log')
    fh.setLevel(logging.ERROR)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger
