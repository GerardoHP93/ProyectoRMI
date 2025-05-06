"""
Punto de entrada principal para la interfaz gráfica del sistema de inventario.
"""
import sys
from cliente.interfaz_gui import main as iniciar_gui

import os
import sys
import tkinter as tk

# Imprimir información de diagnóstico
print("Python version:", sys.version)
print("Tkinter version:", tk.TkVersion)
print("TCL_LIBRARY:", os.environ.get("TCL_LIBRARY", "Not set"))
print("TK_LIBRARY:", os.environ.get("TK_LIBRARY", "Not set"))
print("Tkinter executable:", tk.__file__)


# Buscar archivos TCL en ubicaciones alternativas
tcl_lib_paths = [
    r"C:\Users\Gerardo Herrera\AppData\Local\Programs\Python\Python313\tcl\tcl8.6",
    r"C:\Users\Gerardo Herrera\AppData\Local\Programs\Python\Python313\Lib\tcl8.6",
    r"C:\Program Files\Tcl\lib\tcl8.6"
]

for path in tcl_lib_paths:
    if os.path.exists(path) and os.path.exists(os.path.join(path, "init.tcl")):
        os.environ["TCL_LIBRARY"] = path
        tk_path = path.replace("tcl8.6", "tk8.6")
        if os.path.exists(tk_path):
            os.environ["TK_LIBRARY"] = tk_path
        break


def main():
    """
    Función principal para iniciar la interfaz gráfica.
    """
    print("Iniciando interfaz gráfica del sistema de inventario...")
    
    # Preguntar por la IP del servidor
    print("\n=== Configuración de conexión ===")
    print("1. Conectar a servidor local")
    print("2. Conectar a servidor remoto")
    opcion = input("Seleccione una opción: ")
    
    host_ip = None
    if opcion == "2":
        host_ip = input("Ingrese la dirección IP del servidor: ")
    
    try:
        # Iniciar la interfaz gráfica
        iniciar_gui(host_ip)
    except KeyboardInterrupt:
        print("\nProceso interrumpido por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()