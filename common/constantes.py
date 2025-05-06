"""
Constantes y configuraciones compartidas entre el cliente y el servidor.
"""

# Nombre del servidor Pyro
NOMBRE_SERVIDOR = "inventario.servidor"

# # Host y puerto por defecto para el servidor Pyro
# HOST_SERVIDOR = "0.0.0.0"  # Permite conexiones desde cualquier IP

# Host y puerto para el servidor Pyro (configuración para Hamachi)
# Reemplazar con la dirección IP de Hamachi del servidor
HOST_SERVIDOR = "25.65.114.71"  # Reemplaza X.X.X con la IP de Hamachi del servidor
PUERTO_SERVIDOR = 9090

# Ruta para el archivo de persistencia del inventario
RUTA_DATOS = "servidor/datos/inventario.json"

# Configuración del Name Server de Pyro
# NS_HOST = "0.0.0.0"  # Cambiado de "localhost" para permitir conexiones remotas

# Configuración del Name Server de Pyro
NS_HOST = "25.65.114.71"  # Misma IP de Hamachi que HOST_SERVIDOR
NS_PORT = 9090
NS_PORT = 9090

# Mensajes de estado
MSG_EXITO = "Operación completada con éxito"
MSG_ERROR = "Error al realizar la operación"
MSG_NO_ENCONTRADO = "Producto no encontrado"
MSG_PRODUCTO_EXISTE = "Ya existe un producto con ese ID"
MSG_STOCK_INSUFICIENTE = "Stock insuficiente para realizar la venta"