#!/usr/bin/env python
"""
Punto de entrada principal para el cliente del sistema de inventario.
"""
import sys
from cliente.interfaz_cli import InterfazCLI

def main():
    """
    Función principal para iniciar el cliente.
    """
    print("Iniciando cliente del sistema de inventario...")
    
    try:
        # Crear y ejecutar la interfaz CLI
        interfaz = InterfazCLI()
        interfaz.ejecutar()
    except KeyboardInterrupt:
        print("\nProceso interrumpido por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()