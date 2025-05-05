"""
Módulo que define la clase Producto para el sistema de inventario.
"""

class Producto:
    """
    Clase que representa un producto en el inventario.
    """
    
    def __init__(self, id, nombre, precio, stock, categoria):
        """
        Inicializa un nuevo producto.
        
        Args:
            id (int): Identificador único del producto.
            nombre (str): Nombre del producto.
            precio (float): Precio del producto.
            stock (int): Cantidad disponible en inventario.
            categoria (str): Categoría a la que pertenece el producto.
        """
        self.id = id
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
        self.categoria = categoria
    
    def to_dict(self):
        """
        Convierte el producto a un diccionario para su serialización.
        
        Returns:
            dict: Representación del producto como diccionario.
        """
        return {
            'id': self.id,
            'nombre': self.nombre,
            'precio': self.precio,
            'stock': self.stock,
            'categoria': self.categoria
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Producto a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos del producto.
            
        Returns:
            Producto: Una nueva instancia de Producto.
        """
        return cls(
            id=data['id'],
            nombre=data['nombre'],
            precio=data['precio'],
            stock=data['stock'],
            categoria=data['categoria']
        )
    
    def __str__(self):
        """
        Representación en cadena del producto.
        
        Returns:
            str: Representación legible del producto.
        """
        return f"Producto(id={self.id}, nombre='{self.nombre}', precio={self.precio}, " \
               f"stock={self.stock}, categoria='{self.categoria}')"