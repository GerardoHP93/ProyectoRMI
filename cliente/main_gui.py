#!/usr/bin/env python
"""
Punto de entrada principal para la interfaz gráfica del sistema de inventario.
"""
import sys
from cliente.interfaz_gui import main as iniciar_gui

def main():
    """
    Función principal para iniciar la interfaz gráfica.
    """
    print("Iniciando interfaz gráfica del sistema de inventario...")
    
    try:
        # Iniciar la interfaz gráfica
        iniciar_gui()
    except KeyboardInterrupt:
        print("\nProceso interrumpido por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()