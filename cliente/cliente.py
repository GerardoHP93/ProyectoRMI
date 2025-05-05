"""
Cliente que se conecta al servidor de inventario usando Pyro.
"""
import sys
import Pyro4
from common.constantes import (
    NOMBRE_SERVIDOR, HOST_SERVIDOR, PUERTO_SERVIDOR,
    NS_HOST, NS_PORT
)

class ClienteInventario:
    """
    Cliente para interactuar con el servidor de inventario.
    """
    
    def __init__(self):
        """
        Inicializa el cliente e intenta conectar con el servidor.
        """
        self.servidor = None
    
    def conectar_con_ns(self):
        """
        Intenta conectar con el servidor usando el Name Server.
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario.
        """
        try:
            # Localizar el Name Server con los parámetros de configuración
            ns = Pyro4.locateNS(host=NS_HOST, port=NS_PORT)
            
            # Obtener la URI del servidor por su nombre
            uri = ns.lookup(NOMBRE_SERVIDOR)
            
            # Conectar con el servidor
            self.servidor = Pyro4.Proxy(uri)
            
            # Verificar la conexión
            self.servidor._pyroBind()
            
            print(f"Conectado al servidor: {NOMBRE_SERVIDOR}")
            return True
        
        except Pyro4.errors.NamingError:
            print("Error: No se pudo encontrar el servidor en el Name Server.")
            return False
        
        except Exception as e:
            print(f"Error al conectar con el Name Server: {e}")
            return False
    
    def conectar_directo(self):
        """
        Intenta conectar directamente con el servidor sin usar el Name Server.
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario.
        """
        try:
            # Construir la URI manualmente
            uri = f"PYRO:{NOMBRE_SERVIDOR}@{HOST_SERVIDOR}:{PUERTO_SERVIDOR}"
            
            print(f"Intentando conexión directa a {uri}...")
            
            # Conectar con el servidor
            self.servidor = Pyro4.Proxy(uri)
            
            # Verificar la conexión con un timeout más corto
            self.servidor._pyroTimeout = 5  # 5 segundos de timeout
            self.servidor._pyroBind()
            
            print(f"Conectado directamente al servidor: {uri}")
            return True
        
        except Exception as e:
            print(f"Error al conectar directamente con el servidor: {e}")
            return False
    
    def conectar(self):
        """
        Intenta conectar con el servidor utilizando diferentes métodos.
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario.
        """
        # Intentar primero con el Name Server
        if self.conectar_con_ns():
            return True
        
        print("Intentando conexión directa...")
        # Si falla, intentar conexión directa
        return self.conectar_directo()
    
    def esta_conectado(self):
        """
        Verifica si el cliente está conectado al servidor.
        
        Returns:
            bool: True si está conectado, False en caso contrario.
        """
        return self.servidor is not None
    
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
        if not self.esta_conectado():
            return {"exito": False, "mensaje": "No conectado al servidor"}
        
        try:
            return self.servidor.agregar_producto(id, nombre, precio, stock, categoria)
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
        if not self.esta_conectado():
            return {"exito": False, "mensaje": "No conectado al servidor"}
        
        try:
            return self.servidor.modificar_producto(id_producto, datos)
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
        if not self.esta_conectado():
            return {"exito": False, "mensaje": "No conectado al servidor"}
        
        try:
            return self.servidor.eliminar_producto(id_producto)
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
        if not self.esta_conectado():
            return {"exito": False, "mensaje": "No conectado al servidor"}
        
        try:
            return self.servidor.obtener_producto(id_producto)
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
        if not self.esta_conectado():
            return {"exito": False, "mensaje": "No conectado al servidor"}
        
        try:
            return self.servidor.listar_productos(categoria)
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
        if not self.esta_conectado():
            return {"exito": False, "mensaje": "No conectado al servidor"}
        
        try:
            return self.servidor.vender_producto(id_producto, cantidad)
        except Exception as e:
            return {"exito": False, "mensaje": f"Error: {str(e)}"}


# Función para crear una instancia del cliente y conectarla
def obtener_cliente():
    """
    Crea y conecta un cliente al servidor.
    
    Returns:
        ClienteInventario: Cliente conectado o None si falla la conexión.
    """
    # Configurar Pyro para usar pickle como serializador
    Pyro4.config.SERIALIZER = "pickle"
    Pyro4.config.SERIALIZERS_ACCEPTED.add("pickle")
    
    # Deshabilitar la necesidad de clave HMAC para desarrollo local
    Pyro4.config.REQUIRE_EXPOSE = False
    
    cliente = ClienteInventario()
    
    # Intentar la conexión directa sin usar el Name Server
    if cliente.conectar_directo():
        return cliente
    else:
        print("No se pudo conectar con el servidor de inventario.")
        print("Asegúrate de que el servidor esté en ejecución.")
        return None


if __name__ == "__main__":
    # Esta sección permite probar el cliente de forma independiente
    cliente = obtener_cliente()
    
    if cliente:
        # Ejemplo de uso del cliente
        resultado = cliente.listar_productos()
        
        if resultado["exito"]:
            print(f"Total de productos: {resultado['total']}")
            for p in resultado["productos"]:
                print(f"ID: {p['id']}, Nombre: {p['nombre']}, Precio: {p['precio']}, Stock: {p['stock']}")
        else:
            print(f"Error: {resultado['mensaje']}")
    else:
        sys.exit(1)