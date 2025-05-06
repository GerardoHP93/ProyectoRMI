"""
Servidor Pyro que expone la funcionalidad del inventario.
"""
import os
import sys
import time
import Pyro4
from servidor.inventario import Inventario
from servidor.producto import Producto
from common.constantes import (
    NOMBRE_SERVIDOR, HOST_SERVIDOR, PUERTO_SERVIDOR, RUTA_DATOS, 
    NS_HOST, NS_PORT
)

@Pyro4.expose
class ServidorInventario:
    """
    Servidor que expone métodos remotos para gestionar el inventario.
    """
    
    def __init__(self):
        """
        Inicializa el servidor con una instancia de Inventario.
        """
        # Crear la ruta completa para el archivo de inventario
        ruta_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ruta_completa = os.path.join(ruta_base, RUTA_DATOS)
        
        # Asegurarse de que el directorio para el archivo exista
        directorio = os.path.dirname(ruta_completa)
        if not os.path.exists(directorio):
            try:
                os.makedirs(directorio, exist_ok=True)
                print(f"Directorio creado: {directorio}")
            except Exception as e:
                print(f"Error al crear directorio: {e}")
        
        self.inventario = Inventario(ruta_completa)
        print(f"Inventario inicializado. Productos cargados: {len(self.inventario.productos)}")
    
    def agregar_producto(self, id, nombre, precio, stock, categoria):
        """
        Agrega un nuevo producto al inventario.
        
        Args:
            id (int): Identificador único del producto.
            nombre (str): Nombre del producto.
            precio (float): Precio del producto.
            stock (int): Cantidad disponible en inventario.
            categoria (str): Categoría a la que pertenece el producto.
            
        Returns:
            dict: Resultado de la operación.
        """
        try:
            # Convertir tipos de datos por seguridad
            id = int(id)
            precio = float(precio)
            stock = int(stock)
            
            producto = Producto(id, nombre, precio, stock, categoria)
            resultado = self.inventario.agregar_producto(producto)
            
            if resultado:
                self.inventario.guardar_en_archivo()
                return {"exito": True, "mensaje": "Producto agregado correctamente"}
            else:
                return {"exito": False, "mensaje": "Ya existe un producto con ese ID"}
        
        except Exception as e:
            return {"exito": False, "mensaje": f"Error: {str(e)}"}
    
    def modificar_producto(self, id_producto, datos):
        """
        Modifica un producto existente en el inventario.
        
        Args:
            id_producto (int): ID del producto a modificar.
            datos (dict): Datos a actualizar.
            
        Returns:
            dict: Resultado de la operación.
        """
        try:
            id_producto = int(id_producto)
            
            # Convertir tipos de datos si están presentes
            if 'precio' in datos:
                datos['precio'] = float(datos['precio'])
            if 'stock' in datos:
                datos['stock'] = int(datos['stock'])
            
            resultado = self.inventario.modificar_producto(id_producto, datos)
            
            if resultado:
                self.inventario.guardar_en_archivo()
                return {"exito": True, "mensaje": "Producto modificado correctamente"}
            else:
                return {"exito": False, "mensaje": "Producto no encontrado"}
        
        except Exception as e:
            return {"exito": False, "mensaje": f"Error: {str(e)}"}
    
    def eliminar_producto(self, id_producto):
        """
        Elimina un producto del inventario.
        
        Args:
            id_producto (int): ID del producto a eliminar.
            
        Returns:
            dict: Resultado de la operación.
        """
        try:
            id_producto = int(id_producto)
            resultado = self.inventario.eliminar_producto(id_producto)
            
            if resultado:
                self.inventario.guardar_en_archivo()
                return {"exito": True, "mensaje": "Producto eliminado correctamente"}
            else:
                return {"exito": False, "mensaje": "Producto no encontrado"}
        
        except Exception as e:
            return {"exito": False, "mensaje": f"Error: {str(e)}"}
    
    def obtener_producto(self, id_producto):
        """
        Obtiene la información de un producto por su ID.
        
        Args:
            id_producto (int): ID del producto a consultar.
            
        Returns:
            dict: Datos del producto o mensaje de error.
        """
        try:
            id_producto = int(id_producto)
            producto = self.inventario.obtener_producto(id_producto)
            
            if producto:
                return {
                    "exito": True,
                    "producto": producto.to_dict()
                }
            else:
                return {"exito": False, "mensaje": "Producto no encontrado"}
        
        except Exception as e:
            return {"exito": False, "mensaje": f"Error: {str(e)}"}
    
    def listar_productos(self, categoria=None):
        """
        Lista todos los productos, opcionalmente filtrados por categoría.
        
        Args:
            categoria (str, optional): Categoría por la que filtrar.
            
        Returns:
            dict: Lista de productos o mensaje de error.
        """
        try:
            productos = self.inventario.listar_productos(categoria)
            productos_dict = [p.to_dict() for p in productos]
            
            return {
                "exito": True,
                "productos": productos_dict,
                "total": len(productos_dict)
            }
        
        except Exception as e:
            return {"exito": False, "mensaje": f"Error: {str(e)}"}
    
    def vender_producto(self, id_producto, cantidad):
        """
        Registra la venta de un producto, reduciendo su stock.
        
        Args:
            id_producto (int): ID del producto vendido.
            cantidad (int): Cantidad vendida.
            
        Returns:
            dict: Resultado de la operación.
        """
        try:
            id_producto = int(id_producto)
            cantidad = int(cantidad)
            
            exito, mensaje = self.inventario.vender_producto(id_producto, cantidad)
            
            if exito:
                self.inventario.guardar_en_archivo()
            
            return {"exito": exito, "mensaje": mensaje}
        
        except Exception as e:
            return {"exito": False, "mensaje": f"Error: {str(e)}"}


def iniciar_servidor_con_ns():
    """
    Inicia el servidor utilizando el Name Server de Pyro.
    """
    try:
        # Intentar localizar el nameserver con los parámetros de configuración
        ns = Pyro4.locateNS(host=NS_HOST, port=NS_PORT)
        print(f"Nameserver encontrado en {NS_HOST}:{NS_PORT}.")
        
        # Crear el daemon
        daemon = Pyro4.Daemon(host=HOST_SERVIDOR)
        
        # Registrar el objeto en el daemon
        uri = daemon.register(ServidorInventario())
        
        # Registrar el objeto en el nameserver
        ns.register(NOMBRE_SERVIDOR, uri)
        
        print(f"Servidor registrado como: {NOMBRE_SERVIDOR}")
        print(f"URI: {uri}")
        print("Servidor listo para recibir peticiones.")
        
        # Iniciar el bucle del daemon
        daemon.requestLoop()
    
    except Pyro4.errors.NamingError:
        print("Error al conectar con el Name Server. Asegúrate de que esté en ejecución.")
        print("Puedes iniciarlo con el comando: python -m Pyro4.naming")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error al iniciar el servidor: {e}")
        sys.exit(1)


def iniciar_servidor_sin_ns():
    """
    Inicia el servidor en modo independiente sin usar el Name Server.
    """
    try:
        """PARA IP
        # # Crear el daemon en la dirección y puerto específicos
        # daemon = Pyro4.Daemon(host=HOST_SERVIDOR, port=PUERTO_SERVIDOR)"""
        
        """PARA HAMACHI
        # Modificar la configuración para permitir conexiones remotas a través de Hamachi"""
        Pyro4.config.SERVERTYPE = "multiplex"
        Pyro4.config.SOCK_REUSE = True
        
        # Crear el daemon en la dirección y puerto específicos
        # Usando la IP de Hamachi del servidor
        daemon = Pyro4.Daemon(host=HOST_SERVIDOR, port=PUERTO_SERVIDOR)
        
        
        # Registrar el objeto en el daemon con un nombre específico
        uri = daemon.register(ServidorInventario(), objectId=NOMBRE_SERVIDOR)
        
        print(f"Servidor iniciado en: {HOST_SERVIDOR}:{PUERTO_SERVIDOR}")
        print(f"URI: {uri}")
        print("Servidor listo para recibir peticiones.")
        
        # Iniciar el bucle del daemon
        daemon.requestLoop()
    
    except Exception as e:
        print(f"Error al iniciar el servidor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Configurar Pyro para permitir que los métodos de las clases sean llamados
    Pyro4.config.SERIALIZER = "pickle"
    Pyro4.config.SERIALIZERS_ACCEPTED.add("pickle")
    
    #  Deshabilitar la necesidad de clave HMAC para desarrollo local
    Pyro4.config.REQUIRE_EXPOSE = False
    
    """ PARA VPN: Configuraciones adicionales para mejorar la conexión remota """ 
    Pyro4.config.COMMTIMEOUT = 15.0  # Aumentar tiempo de espera para conexiones lentas
    
    # Iniciar directamente en modo independiente sin intentar usar el Name Server
    print("Iniciando servidor en modo independiente...")
    iniciar_servidor_sin_ns()