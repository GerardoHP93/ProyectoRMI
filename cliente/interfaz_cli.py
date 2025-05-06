"""
Interfaz de línea de comandos para el cliente de inventario.
"""
import os
import sys
from cliente.cliente import obtener_cliente

class InterfazCLI:
    """
    Interfaz de línea de comandos para interactuar con el servidor de inventario.
    """
    
    def __init__(self, host_ip=None):
        """
        Inicializa la interfaz de línea de comandos.
        
        Args:
            host_ip (str, optional): Dirección IP del servidor
        """
        self.cliente = obtener_cliente(host_ip)
        
        if not self.cliente:
            print("No se pudo inicializar el cliente. Saliendo...")
            sys.exit(1)
    
    def limpiar_pantalla(self):
        """
        Limpia la pantalla de la terminal.
        """
        # Comando para limpiar la pantalla (funciona en Windows y Unix/Linux/Mac)
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def mostrar_menu_principal(self):
        """
        Muestra el menú principal de la aplicación.
        """
        self.limpiar_pantalla()
        print("=" * 50)
        print("       SISTEMA DE GESTIÓN DE INVENTARIO")
        print("=" * 50)
        print("1. Listar productos")
        print("2. Buscar producto por ID")
        print("3. Agregar nuevo producto")
        print("4. Modificar producto")
        print("5. Eliminar producto")
        print("6. Vender producto")
        print("7. Filtrar productos por categoría")
        print("0. Salir")
        print("=" * 50)
    
    def ejecutar(self):
        """
        Ejecuta el bucle principal de la interfaz.
        """
        while True:
            self.mostrar_menu_principal()
            opcion = input("Seleccione una opción: ")
            
            if opcion == "1":
                self.listar_productos()
            elif opcion == "2":
                self.buscar_producto()
            elif opcion == "3":
                self.agregar_producto()
            elif opcion == "4":
                self.modificar_producto()
            elif opcion == "5":
                self.eliminar_producto()
            elif opcion == "6":
                self.vender_producto()
            elif opcion == "7":
                self.filtrar_por_categoria()
            elif opcion == "0":
                print("¡Gracias por usar el sistema de inventario!")
                break
            else:
                input("Opción no válida. Presione Enter para continuar...")
    
    def listar_productos(self):
        """
        Muestra todos los productos del inventario.
        """
        self.limpiar_pantalla()
        print("=" * 50)
        print("             LISTA DE PRODUCTOS")
        print("=" * 50)
        
        resultado = self.cliente.listar_productos()
        
        if resultado["exito"]:
            productos = resultado["productos"]
            
            if productos:
                print(f"{'ID':<5} {'NOMBRE':<30} {'PRECIO':<10} {'STOCK':<8} {'CATEGORÍA':<15}")
                print("-" * 70)
                
                for p in productos:
                    print(f"{p['id']:<5} {p['nombre']:<30} ${p['precio']:<9.2f} {p['stock']:<8} {p['categoria']:<15}")
                
                print("-" * 70)
                print(f"Total de productos: {resultado['total']}")
            else:
                print("No hay productos en el inventario.")
        else:
            print(f"Error: {resultado['mensaje']}")
        
        input("\nPresione Enter para continuar...")
    
    def buscar_producto(self):
        """
        Busca un producto por su ID.
        """
        self.limpiar_pantalla()
        print("=" * 50)
        print("             BUSCAR PRODUCTO")
        print("=" * 50)
        
        try:
            id_producto = int(input("Ingrese el ID del producto: "))
            
            resultado = self.cliente.obtener_producto(id_producto)
            
            if resultado["exito"]:
                p = resultado["producto"]
                print("\nInformación del producto:")
                print(f"ID: {p['id']}")
                print(f"Nombre: {p['nombre']}")
                print(f"Precio: ${p['precio']:.2f}")
                print(f"Stock: {p['stock']} unidades")
                print(f"Categoría: {p['categoria']}")
            else:
                print(f"\nError: {resultado['mensaje']}")
        
        except ValueError:
            print("\nError: El ID debe ser un número entero.")
        
        input("\nPresione Enter para continuar...")
    
    def agregar_producto(self):
        """
        Agrega un nuevo producto al inventario.
        """
        self.limpiar_pantalla()
        print("=" * 50)
        print("             AGREGAR PRODUCTO")
        print("=" * 50)
        
        try:
            id_producto = int(input("ID del producto: "))
            nombre = input("Nombre del producto: ")
            precio = float(input("Precio del producto: "))
            stock = int(input("Stock inicial: "))
            categoria = input("Categoría: ")
            
            if nombre.strip() == "" or precio <= 0 or stock < 0:
                print("\nError: Datos inválidos. Verifique los valores ingresados.")
                input("\nPresione Enter para continuar...")
                return
            
            resultado = self.cliente.agregar_producto(
                id_producto, nombre, precio, stock, categoria
            )
            
            print(f"\n{resultado['mensaje']}")
        
        except ValueError:
            print("\nError: Formato de datos incorrecto.")
        
        input("\nPresione Enter para continuar...")
    
    def modificar_producto(self):
        """
        Modifica un producto existente.
        """
        self.limpiar_pantalla()
        print("=" * 50)
        print("           MODIFICAR PRODUCTO")
        print("=" * 50)
        
        try:
            id_producto = int(input("Ingrese el ID del producto a modificar: "))
            
            # Verificar si el producto existe
            resultado = self.cliente.obtener_producto(id_producto)
            
            if not resultado["exito"]:
                print(f"\nError: {resultado['mensaje']}")
                input("\nPresione Enter para continuar...")
                return
            
            producto = resultado["producto"]
            datos_actualizados = {}
            
            print("\nDeje en blanco los campos que no desea modificar:")
            
            nombre = input(f"Nombre [{producto['nombre']}]: ")
            if nombre.strip():
                datos_actualizados["nombre"] = nombre
            
            precio_str = input(f"Precio [${producto['precio']}]: ")
            if precio_str.strip():
                precio = float(precio_str)
                if precio <= 0:
                    print("\nError: El precio debe ser mayor que cero.")
                    input("\nPresione Enter para continuar...")
                    return
                datos_actualizados["precio"] = precio
            
            stock_str = input(f"Stock [{producto['stock']}]: ")
            if stock_str.strip():
                stock = int(stock_str)
                if stock < 0:
                    print("\nError: El stock no puede ser negativo.")
                    input("\nPresione Enter para continuar...")
                    return
                datos_actualizados["stock"] = stock
            
            categoria = input(f"Categoría [{producto['categoria']}]: ")
            if categoria.strip():
                datos_actualizados["categoria"] = categoria
            
            if not datos_actualizados:
                print("\nNo se realizaron cambios.")
                input("\nPresione Enter para continuar...")
                return
            
            resultado = self.cliente.modificar_producto(id_producto, datos_actualizados)
            print(f"\n{resultado['mensaje']}")
        
        except ValueError:
            print("\nError: Formato de datos incorrecto.")
        
        input("\nPresione Enter para continuar...")
    
    def eliminar_producto(self):
        """
        Elimina un producto del inventario.
        """
        self.limpiar_pantalla()
        print("=" * 50)
        print("            ELIMINAR PRODUCTO")
        print("=" * 50)
        
        try:
            id_producto = int(input("Ingrese el ID del producto a eliminar: "))
            
            # Verificar si el producto existe
            resultado = self.cliente.obtener_producto(id_producto)
            
            if not resultado["exito"]:
                print(f"\nError: {resultado['mensaje']}")
                input("\nPresione Enter para continuar...")
                return
            
            producto = resultado["producto"]
            
            print("\nInformación del producto a eliminar:")
            print(f"Nombre: {producto['nombre']}")
            print(f"Precio: ${producto['precio']:.2f}")
            print(f"Stock: {producto['stock']} unidades")
            print(f"Categoría: {producto['categoria']}")
            
            confirmacion = input("\n¿Está seguro de eliminar este producto? (s/n): ")
            
            if confirmacion.lower() == "s":
                resultado = self.cliente.eliminar_producto(id_producto)
                print(f"\n{resultado['mensaje']}")
            else:
                print("\nOperación cancelada.")
        
        except ValueError:
            print("\nError: El ID debe ser un número entero.")
        
        input("\nPresione Enter para continuar...")
    
    def vender_producto(self):
        """
        Registra la venta de un producto.
        """
        self.limpiar_pantalla()
        print("=" * 50)
        print("              VENTA DE PRODUCTO")
        print("=" * 50)
        
        try:
            id_producto = int(input("Ingrese el ID del producto a vender: "))
            
            # Verificar si el producto existe
            resultado = self.cliente.obtener_producto(id_producto)
            
            if not resultado["exito"]:
                print(f"\nError: {resultado['mensaje']}")
                input("\nPresione Enter para continuar...")
                return
            
            producto = resultado["producto"]
            
            print(f"\nProducto: {producto['nombre']}")
            print(f"Precio: ${producto['precio']:.2f}")
            print(f"Stock disponible: {producto['stock']} unidades")
            
            cantidad = int(input("\nCantidad a vender: "))
            
            if cantidad <= 0:
                print("\nError: La cantidad debe ser mayor que cero.")
                input("\nPresione Enter para continuar...")
                return
            
            if cantidad > producto['stock']:
                print("\nError: Stock insuficiente.")
                input("\nPresione Enter para continuar...")
                return
            
            # Calcular el total de la venta
            total = cantidad * producto['precio']
            
            print(f"\nTotal de la venta: ${total:.2f}")
            
            confirmacion = input("¿Confirmar venta? (s/n): ")
            
            if confirmacion.lower() == "s":
                resultado = self.cliente.vender_producto(id_producto, cantidad)
                print(f"\n{resultado['mensaje']}")
            else:
                print("\nVenta cancelada.")
        
        except ValueError:
            print("\nError: Formato de datos incorrecto.")
        
        input("\nPresione Enter para continuar...")
    
    def filtrar_por_categoria(self):
        """
        Filtra productos por categoría.
        """
        self.limpiar_pantalla()
        print("=" * 50)
        print("         FILTRAR POR CATEGORÍA")
        print("=" * 50)
        
        # Obtener todas las categorías únicas
        resultado = self.cliente.listar_productos()
        
        if not resultado["exito"]:
            print(f"Error: {resultado['mensaje']}")
            input("\nPresione Enter para continuar...")
            return
        
        productos = resultado["productos"]
        
        if not productos:
            print("No hay productos en el inventario.")
            input("\nPresione Enter para continuar...")
            return
        
        categorias = sorted(set(p["categoria"] for p in productos))
        
        print("Categorías disponibles:")
        for i, cat in enumerate(categorias, 1):
            print(f"{i}. {cat}")
        
        try:
            opcion = int(input("\nSeleccione una categoría (0 para volver): "))
            
            if opcion == 0:
                return
            
            if opcion < 1 or opcion > len(categorias):
                print("\nOpción no válida.")
                input("\nPresione Enter para continuar...")
                return
            
            categoria = categorias[opcion - 1]
            
            # Filtrar productos
            resultado = self.cliente.listar_productos(categoria)
            
            self.limpiar_pantalla()
            print("=" * 50)
            print(f"         PRODUCTOS DE CATEGORÍA: {categoria.upper()}")
            print("=" * 50)
            
            if resultado["exito"]:
                productos = resultado["productos"]
                
                if productos:
                    print(f"{'ID':<5} {'NOMBRE':<30} {'PRECIO':<10} {'STOCK':<8}")
                    print("-" * 55)
                    
                    for p in productos:
                        print(f"{p['id']:<5} {p['nombre']:<30} ${p['precio']:<9.2f} {p['stock']:<8}")
                    
                    print("-" * 55)
                    print(f"Total de productos en esta categoría: {len(productos)}")
                else:
                    print(f"No hay productos en la categoría '{categoria}'.")
            else:
                print(f"Error: {resultado['mensaje']}")
        
        except ValueError:
            print("\nError: Formato de datos incorrecto.")
        
        input("\nPresione Enter para continuar...")