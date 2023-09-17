import sys
from pathlib import Path

# Obtiene el directorio raíz del proyecto
project_root = Path(__file__).parent.parent.absolute()

# Verifica si el directorio raíz ya está en sys.path
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Imprime mensajes para verificar que todo está funcionando
print(f"Archivo conftest.py se está ejecutando en: {Path(__file__).parent.absolute()}")
print(f"Directorio raíz del proyecto: {project_root}")
print(f"sys.path actualizado: {sys.path}")

