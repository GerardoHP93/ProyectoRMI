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
        # Preguntar por la IP del servidor
        print("\n=== Configuración de conexión ===")
        print("1. Conectar a servidor local")
        print("2. Conectar a servidor remoto")
        opcion = input("Seleccione una opción: ")
        
        host_ip = None
        if opcion == "2":
            host_ip = input("Ingrese la dirección IP del servidor: ")
        
        # Crear y ejecutar la interfaz CLI con la IP proporcionada
        interfaz = InterfazCLI(host_ip)
        interfaz.ejecutar()
    except KeyboardInterrupt:
        print("\nProceso interrumpido por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()