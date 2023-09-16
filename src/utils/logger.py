import logging

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

    return logger
