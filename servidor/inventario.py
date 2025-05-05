"""
Módulo para la gestión del inventario de productos.
"""
import json
import os
from servidor.producto import Producto

class Inventario:
    """
    Clase que gestiona el inventario de productos.
    """
    
    def __init__(self, ruta_archivo=None):
        """
        Inicializa el inventario, opcionalmente cargando datos de un archivo.
        
        Args:
            ruta_archivo (str, optional): Ruta al archivo de persistencia.
        """
        self.productos = {}
        self.ruta_archivo = ruta_archivo
        
        # Si se proporciona una ruta y el archivo existe, cargar datos
        if ruta_archivo and os.path.exists(ruta_archivo):
            self.cargar_desde_archivo()
    
    def agregar_producto(self, producto):
        """
        Agrega un nuevo producto al inventario.
        
        Args:
            producto (Producto): Producto a agregar.
            
        Returns:
            bool: True si se agregó correctamente, False si ya existía.
        """
        if producto.id in self.productos:
            return False
        
        self.productos[producto.id] = producto
        return True
    
    def modificar_producto(self, id_producto, datos_actualizados):
        """
        Modifica los datos de un producto existente.
        
        Args:
            id_producto (int): ID del producto a modificar.
            datos_actualizados (dict): Diccionario con los campos a actualizar.
            
        Returns:
            bool: True si se modificó correctamente, False si no existe.
        """
        if id_producto not in self.productos:
            return False
        
        producto = self.productos[id_producto]
        
        # Actualizar solo los campos proporcionados
        for campo, valor in datos_actualizados.items():
            if hasattr(producto, campo):
                setattr(producto, campo, valor)
        
        return True
    
    def eliminar_producto(self, id_producto):
        """
        Elimina un producto del inventario.
        
        Args:
            id_producto (int): ID del producto a eliminar.
            
        Returns:
            bool: True si se eliminó correctamente, False si no existe.
        """
        if id_producto not in self.productos:
            return False
        
        del self.productos[id_producto]
        return True
    
    def obtener_producto(self, id_producto):
        """
        Obtiene un producto por su ID.
        
        Args:
            id_producto (int): ID del producto a obtener.
            
        Returns:
            Producto: El producto encontrado o None si no existe.
        """
        return self.productos.get(id_producto)
    
    def listar_productos(self, filtro_categoria=None):
        """
        Lista todos los productos, opcionalmente filtrados por categoría.
        
        Args:
            filtro_categoria (str, optional): Categoría por la que filtrar.
            
        Returns:
            list: Lista de productos que cumplen el criterio.
        """
        if filtro_categoria:
            return [p for p in self.productos.values() if p.categoria == filtro_categoria]
        else:
            return list(self.productos.values())
    
    def vender_producto(self, id_producto, cantidad):
        """
        Reduce el stock de un producto al realizar una venta.
        
        Args:
            id_producto (int): ID del producto vendido.
            cantidad (int): Cantidad vendida.
            
        Returns:
            tuple: (éxito, mensaje) donde éxito es un booleano y mensaje describe el resultado.
        """
        if id_producto not in self.productos:
            return False, "Producto no encontrado"
        
        producto = self.productos[id_producto]
        
        if producto.stock < cantidad:
            return False, f"Stock insuficiente. Disponible: {producto.stock}"
        
        producto.stock -= cantidad
        return True, f"Venta realizada. Nuevo stock: {producto.stock}"
    
    def guardar_en_archivo(self):
        """
        Guarda el inventario en un archivo JSON.
        
        Returns:
            bool: True si se guardó correctamente, False en caso contrario.
        """
        if not self.ruta_archivo:
            return False
        
        try:
            # Crear el directorio si no existe
            os.makedirs(os.path.dirname(self.ruta_archivo), exist_ok=True)
            
            # Convertir productos a formato serializable
            datos = {str(id_): producto.to_dict() for id_, producto in self.productos.items()}
            
            with open(self.ruta_archivo, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, indent=4, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error al guardar inventario: {e}")
            return False
    
    def cargar_desde_archivo(self):
        """
        Carga el inventario desde un archivo JSON.
        
        Returns:
            bool: True si se cargó correctamente, False en caso contrario.
        """
        if not self.ruta_archivo:
            return False
        
        # Si el archivo no existe, no es un error, simplemente retornamos False
        if not os.path.exists(self.ruta_archivo):
            print(f"Archivo de inventario no encontrado: {self.ruta_archivo}")
            print("Se iniciará con un inventario vacío.")
            return False
        
        try:
            with open(self.ruta_archivo, 'r', encoding='utf-8') as archivo:
                datos = json.load(archivo)
            
            # Convertir diccionarios a objetos Producto
            self.productos = {
                int(id_): Producto.from_dict(producto_dict)
                for id_, producto_dict in datos.items()
            }
            
            return True
        except json.JSONDecodeError:
            # Si el archivo está vacío o no es JSON válido, empezamos con un inventario vacío
            print(f"El archivo de inventario está vacío o no es un JSON válido. Se iniciará con un inventario vacío.")
            return False
        except Exception as e:
            print(f"Error al cargar inventario: {e}")
            return False