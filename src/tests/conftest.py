import sys
from pathlib import Path

# Obtiene el directorio raíz del proyecto
project_root = Path(__file__).parent.parent.absolute()

print(f"Archivo conftest.py se está ejecutando en: {Path(__file__).parent.absolute()}")
print(f"Agregando el siguiente directorio al sys.path: {project_root}")

# Añade el directorio raíz del proyecto al sys.path
sys.path.append(str(project_root))

