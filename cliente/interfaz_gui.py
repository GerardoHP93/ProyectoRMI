"""
Interfaz gráfica de usuario para el cliente de inventario.
"""
import os
os.environ['TCL_LIBRARY'] = r"C:\Users\Gerardo Herrera\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time

from cliente.cliente import obtener_cliente

# Intenta establecer la ruta correcta para TCL
tcl_lib = r"C:\Users\Gerardo Herrera\AppData\Local\Programs\Python\Python313\tcl"  # Ajusta esta ruta
if os.path.exists(tcl_lib):
    os.environ["TCL_LIBRARY"] = tcl_lib
    os.environ["TK_LIBRARY"] = os.path.join(os.path.dirname(tcl_lib), "tk")

import tkinter as tk

class InterfazGUI:
    """
    Interfaz gráfica para interactuar con el servidor de inventario.
    """
    
    def __init__(self, root, host_ip=None):
        """
        Inicializa la interfaz gráfica.
        
        Args:
            root: Ventana principal de Tkinter.
            host_ip (str, optional): Dirección IP del servidor
        """
        self.root = root
        self.host_ip = host_ip
        self.root.title("Sistema de Gestión de Inventario")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
        
        # Aplicar un tema más moderno
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")  # 'clam', 'alt', 'default', 'classic'
        except tk.TclError:
            pass  # Si el tema no está disponible, usará el tema por defecto
        
        # Colores y estilos
        self.bg_color = "#f0f0f0"
        self.accent_color = "#4a7abc"
        self.text_color = "#333333"
        self.header_color = "#2c3e50"
        
        self.root.config(bg=self.bg_color)
        
        # Estilos personalizados
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Header.TLabel", 
                             background=self.header_color, 
                             foreground="white", 
                             font=("Arial", 14, "bold"),
                             padding=10)
        self.style.configure("Title.TLabel", 
                             background=self.bg_color, 
                             foreground=self.text_color, 
                             font=("Arial", 16, "bold"),
                             padding=10)
        self.style.configure("Info.TLabel", 
                             background=self.bg_color, 
                             foreground=self.text_color, 
                             font=("Arial", 12))
        self.style.configure("TButton", 
                             background=self.accent_color, 
                             foreground="white",
                             font=("Arial", 11))
        self.style.map("TButton",
                       background=[("active", "#3a5a8c"), ("pressed", "#2c4a7c")])
        
        # Variables para el filtrado
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.category_var.set("Todas")
        
        # Variable para productos
        self.productos = []
        self.categorias = ["Todas"]
        
        # Inicializar el cliente
        self.cliente = None
        
        # Crear el marco principal
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Inicializar la interfaz
        self.init_ui()
        
        # Conectar al servidor en un hilo separado
        self.conectando = True
        self.thread_conexion = threading.Thread(target=self.conectar_servidor)
        self.thread_conexion.daemon = True
        self.thread_conexion.start()
        
        # Mostrar pantalla de carga
        self.mostrar_pantalla_carga()
    
    def init_ui(self):
        """
        Inicializa la interfaz de usuario.
        """
        # Crear un marco para el encabezado
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        
        # Título
        title_label = ttk.Label(
            header_frame, 
            text="Sistema de Gestión de Inventario",
            style="Title.TLabel"
        )
        title_label.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Marco para búsqueda y filtros (lado derecho del encabezado)
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Entrada de búsqueda
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind("<KeyRelease>", self.filtrar_productos)
        
        # Selector de categoría
        ttk.Label(search_frame, text="Categoría:").pack(side=tk.LEFT, padx=(0, 5))
        self.category_combobox = ttk.Combobox(
            search_frame, 
            textvariable=self.category_var, 
            values=self.categorias,
            state="readonly", 
            width=15
        )
        self.category_combobox.pack(side=tk.LEFT)
        self.category_combobox.bind("<<ComboboxSelected>>", self.filtrar_productos)
        
        # Frame para los botones de acción
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Botones de acción
        ttk.Button(
            button_frame, 
            text="Agregar Producto", 
            command=self.abrir_agregar_producto
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Modificar Producto", 
            command=self.abrir_modificar_producto
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Eliminar Producto", 
            command=self.eliminar_producto
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Vender Producto", 
            command=self.abrir_vender_producto
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Actualizar", 
            command=self.cargar_productos
        ).pack(side=tk.RIGHT, padx=5)
        
        # Marco para la tabla de productos
        table_frame = ttk.Frame(self.main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Crear la tabla (Treeview)
        self.tree = ttk.Treeview(
            table_frame,
            columns=("id", "nombre", "precio", "stock", "categoria"),
            show="headings"
        )
        
        # Definir encabezados
        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("precio", text="Precio")
        self.tree.heading("stock", text="Stock")
        self.tree.heading("categoria", text="Categoría")
        
        # Definir anchos de columna
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("nombre", width=300)
        self.tree.column("precio", width=100, anchor=tk.E)
        self.tree.column("stock", width=100, anchor=tk.CENTER)
        self.tree.column("categoria", width=150)
        
        # Agregar scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Posicionar la tabla y scrollbars
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        vsb.pack(fill=tk.Y, side=tk.RIGHT)
        hsb.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Agregar evento de doble clic
        self.tree.bind("<Double-1>", self.mostrar_detalles_producto)
        
        # Barra de estado
        self.status_bar = ttk.Label(
            self.main_frame, 
            text="Listo",
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(5, 0))
    
    def mostrar_pantalla_carga(self):
        """
        Muestra una pantalla de carga mientras se conecta al servidor.
        """
        # Crear una ventana de carga
        self.loading_window = tk.Toplevel(self.root)
        self.loading_window.title("Conectando")
        self.loading_window.geometry("300x150")
        self.loading_window.resizable(False, False)
        self.loading_window.transient(self.root)
        self.loading_window.grab_set()
        
        # Centrar en la pantalla
        self.loading_window.update_idletasks()
        width = self.loading_window.winfo_width()
        height = self.loading_window.winfo_height()
        x = (self.loading_window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.loading_window.winfo_screenheight() // 2) - (height // 2)
        self.loading_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Contenido
        loading_frame = ttk.Frame(self.loading_window)
        loading_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(
            loading_frame, 
            text="Conectando al servidor...",
            font=("Arial", 12, "bold")
        ).pack(pady=(0, 10))
        
        # Barra de progreso
        self.progress = ttk.Progressbar(
            loading_frame, 
            orient="horizontal",
            length=250, 
            mode="indeterminate"
        )
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        self.loading_label = ttk.Label(
            loading_frame, 
            text="Estableciendo conexión...",
            font=("Arial", 10)
        )
        self.loading_label.pack(pady=10)
        
        # Actualizar mensaje periódicamente
        self.actualizar_mensaje_carga()
    
    def actualizar_mensaje_carga(self):
        """
        Actualiza el mensaje de carga periódicamente.
        """
        if self.conectando:
            mensajes = [
                "Estableciendo conexión...",
                "Conectando al servidor...",
                "Buscando servidor...",
                "Iniciando sistema..."
            ]
            
            # Obtener el índice actual
            try:
                texto_actual = self.loading_label.cget("text")
                idx = mensajes.index(texto_actual)
                # Pasar al siguiente mensaje (circularmente)
                idx = (idx + 1) % len(mensajes)
            except (ValueError, AttributeError):
                idx = 0
            
            try:
                self.loading_label.config(text=mensajes[idx])
                self.root.after(800, self.actualizar_mensaje_carga)
            except tk.TclError:
                # La ventana podría haberse cerrado
                pass
    
    def conectar_servidor(self):
        """
        Conecta con el servidor en un hilo separado.
        """
        self.cliente = obtener_cliente(self.host_ip)
        self.conectando = False
        
        # Actualizar la interfaz en el hilo principal
        self.root.after(0, self.finalizar_conexion)
    
    def finalizar_conexion(self):
        """
        Finaliza el proceso de conexión y actualiza la interfaz.
        """
        try:
            self.loading_window.destroy()
        except (AttributeError, tk.TclError):
            pass
        
        if self.cliente:
            # Conexión exitosa
            self.cargar_productos()
            self.status_bar.config(text="Conectado al servidor")
        else:
            # Error de conexión
            messagebox.showerror(
                "Error de conexión",
                "No se pudo conectar con el servidor. Por favor, asegúrate de que el servidor esté en ejecución."
            )
            self.root.destroy()
    
    def cargar_productos(self):
        """
        Carga los productos desde el servidor.
        """
        if not self.cliente:
            return
        
        try:
            # Mostrar mensaje de carga
            self.status_bar.config(text="Cargando productos...")
            self.root.update_idletasks()
            
            # Obtener productos
            resultado = self.cliente.listar_productos()
            
            if resultado["exito"]:
                # Limpiar tabla actual
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                self.productos = resultado["productos"]
                
                # Obtener categorías únicas
                categorias = set()
                for p in self.productos:
                    categorias.add(p["categoria"])
                
                self.categorias = ["Todas"] + sorted(list(categorias))
                self.category_combobox.config(values=self.categorias)
                
                # Aplicar filtros actuales
                self.filtrar_productos()
                
                # Actualizar barra de estado
                self.status_bar.config(text=f"Productos cargados: {len(self.productos)}")
            else:
                messagebox.showerror("Error", resultado["mensaje"])
                self.status_bar.config(text="Error al cargar productos")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar productos: {str(e)}")
            self.status_bar.config(text="Error al cargar productos")
    
    def filtrar_productos(self, event=None):
        """
        Filtra los productos según los criterios de búsqueda.
        """
        # Limpiar tabla actual
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtener criterios de filtrado
        busqueda = self.search_var.get().lower()
        categoria = self.category_var.get()
        
        # Aplicar filtros
        productos_filtrados = []
        for p in self.productos:
            # Filtro de categoría
            if categoria != "Todas" and p["categoria"] != categoria:
                continue
            
            # Filtro de búsqueda
            if busqueda and not (
                busqueda in str(p["id"]).lower() or
                busqueda in p["nombre"].lower() or
                busqueda in p["categoria"].lower()
            ):
                continue
            
            productos_filtrados.append(p)
        
        # Insertar productos filtrados
        for p in productos_filtrados:
            self.tree.insert(
                "", tk.END,
                values=(
                    p["id"],
                    p["nombre"],
                    f"${p['precio']:.2f}",
                    p["stock"],
                    p["categoria"]
                )
            )
        
        # Actualizar barra de estado
        self.status_bar.config(text=f"Productos mostrados: {len(productos_filtrados)}")
    
    def mostrar_detalles_producto(self, event):
        """
        Muestra los detalles de un producto al hacer doble clic.
        """
        # Obtener el ítem seleccionado
        seleccion = self.tree.selection()
        if not seleccion:
            return
        
        item = self.tree.item(seleccion[0])
        id_producto = int(item["values"][0])
        
        # Obtener detalles del producto
        resultado = self.cliente.obtener_producto(id_producto)
        
        if resultado["exito"]:
            p = resultado["producto"]
            
            # Crear ventana de detalles
            detalles_window = tk.Toplevel(self.root)
            detalles_window.title(f"Detalles del Producto: {p['nombre']}")
            detalles_window.geometry("400x300")
            detalles_window.resizable(False, False)
            detalles_window.transient(self.root)
            detalles_window.grab_set()
            
            # Centrar en la pantalla
            detalles_window.update_idletasks()
            width = detalles_window.winfo_width()
            height = detalles_window.winfo_height()
            x = (detalles_window.winfo_screenwidth() // 2) - (width // 2)
            y = (detalles_window.winfo_screenheight() // 2) - (height // 2)
            detalles_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
            
            # Contenido
            details_frame = ttk.Frame(detalles_window)
            details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Título
            ttk.Label(
                details_frame, 
                text=p["nombre"],
                font=("Arial", 14, "bold")
            ).pack(anchor=tk.W, pady=(0, 15))
            
            # Detalles
            ttk.Label(details_frame, text=f"ID: {p['id']}", font=("Arial", 11)).pack(anchor=tk.W, pady=3)
            ttk.Label(details_frame, text=f"Categoría: {p['categoria']}", font=("Arial", 11)).pack(anchor=tk.W, pady=3)
            ttk.Label(details_frame, text=f"Precio: ${p['precio']:.2f}", font=("Arial", 11)).pack(anchor=tk.W, pady=3)
            ttk.Label(details_frame, text=f"Stock: {p['stock']} unidades", font=("Arial", 11)).pack(anchor=tk.W, pady=3)
            
            # Separador
            ttk.Separator(details_frame, orient='horizontal').pack(fill=tk.X, pady=15)
            
            # Botones
            button_frame = ttk.Frame(details_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Button(
                button_frame, 
                text="Modificar",
                command=lambda: [detalles_window.destroy(), self.abrir_modificar_producto(id_producto)]
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                button_frame, 
                text="Vender",
                command=lambda: [detalles_window.destroy(), self.abrir_vender_producto(id_producto)]
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                button_frame, 
                text="Cerrar",
                command=detalles_window.destroy
            ).pack(side=tk.RIGHT, padx=5)
        else:
            messagebox.showerror("Error", resultado["mensaje"])
    
    def abrir_agregar_producto(self):
        """
        Abre la ventana para agregar un nuevo producto.
        """
        # Crear ventana de agregar producto
        agregar_window = tk.Toplevel(self.root)
        agregar_window.title("Agregar Nuevo Producto")
        agregar_window.geometry("400x350")
        agregar_window.resizable(False, False)
        agregar_window.transient(self.root)
        agregar_window.grab_set()
        
        # Centrar en la pantalla
        agregar_window.update_idletasks()
        width = agregar_window.winfo_width()
        height = agregar_window.winfo_height()
        x = (agregar_window.winfo_screenwidth() // 2) - (width // 2)
        y = (agregar_window.winfo_screenheight() // 2) - (height // 2)
        agregar_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Contenido
        form_frame = ttk.Frame(agregar_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(
            form_frame, 
            text="Agregar Nuevo Producto",
            font=("Arial", 14, "bold")
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Variables
        id_var = tk.StringVar()
        nombre_var = tk.StringVar()
        precio_var = tk.StringVar()
        stock_var = tk.StringVar()
        categoria_var = tk.StringVar()
        
        # Formulario
        # ID
        id_frame = ttk.Frame(form_frame)
        id_frame.pack(fill=tk.X, pady=5)
        ttk.Label(id_frame, text="ID:", width=10).pack(side=tk.LEFT)
        ttk.Entry(id_frame, textvariable=id_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Nombre
        nombre_frame = ttk.Frame(form_frame)
        nombre_frame.pack(fill=tk.X, pady=5)
        ttk.Label(nombre_frame, text="Nombre:", width=10).pack(side=tk.LEFT)
        ttk.Entry(nombre_frame, textvariable=nombre_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Precio
        precio_frame = ttk.Frame(form_frame)
        precio_frame.pack(fill=tk.X, pady=5)
        ttk.Label(precio_frame, text="Precio:", width=10).pack(side=tk.LEFT)
        ttk.Entry(precio_frame, textvariable=precio_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Stock
        stock_frame = ttk.Frame(form_frame)
        stock_frame.pack(fill=tk.X, pady=5)
        ttk.Label(stock_frame, text="Stock:", width=10).pack(side=tk.LEFT)
        ttk.Entry(stock_frame, textvariable=stock_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Categoría
        categoria_frame = ttk.Frame(form_frame)
        categoria_frame.pack(fill=tk.X, pady=5)
        ttk.Label(categoria_frame, text="Categoría:", width=10).pack(side=tk.LEFT)
        
        # Si hay categorías disponibles (excepto "Todas"), mostrarlas en el combobox
        categorias_unicas = [cat for cat in self.categorias if cat != "Todas"]
        if categorias_unicas:
            categoria_combobox = ttk.Combobox(
                categoria_frame, 
                textvariable=categoria_var,
                values=categorias_unicas
            )
            categoria_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        else:
            ttk.Entry(categoria_frame, textvariable=categoria_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Separador
        ttk.Separator(form_frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Función para validar y guardar
        def guardar_producto():
            try:
                # Validar campos
                id_str = id_var.get().strip()
                nombre = nombre_var.get().strip()
                precio_str = precio_var.get().strip()
                stock_str = stock_var.get().strip()
                categoria = categoria_var.get().strip()
                
                # Verificar campos obligatorios
                if not id_str or not nombre or not precio_str or not stock_str:
                    messagebox.showerror("Error", "Todos los campos son obligatorios.")
                    return
                
                # Convertir tipos
                try:
                    id_producto = int(id_str)
                    precio = float(precio_str)
                    stock = int(stock_str)
                except ValueError:
                    messagebox.showerror("Error", "Formato de datos incorrecto. Verifica los valores ingresados.")
                    return
                
                # Validar valores
                if precio <= 0:
                    messagebox.showerror("Error", "El precio debe ser mayor que cero.")
                    return
                
                if stock < 0:
                    messagebox.showerror("Error", "El stock no puede ser negativo.")
                    return
                
                # Enviar datos al servidor
                resultado = self.cliente.agregar_producto(
                    id_producto, nombre, precio, stock, categoria
                )
                
                if resultado["exito"]:
                    messagebox.showinfo("Éxito", resultado["mensaje"])
                    agregar_window.destroy()
                    self.cargar_productos()
                else:
                    messagebox.showerror("Error", resultado["mensaje"])
            
            except Exception as e:
                messagebox.showerror("Error", f"Error al agregar producto: {str(e)}")
        
        # Botones
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame, 
            text="Guardar",
            command=guardar_producto
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancelar",
            command=agregar_window.destroy
        ).pack(side=tk.RIGHT, padx=5)
    
    def abrir_modificar_producto(self, id_producto=None):
        """
        Abre la ventana para modificar un producto existente.
        
        Args:
            id_producto (int, optional): ID del producto a modificar. Si es None,
                                         se utilizará el seleccionado en la tabla.
        """
        if id_producto is None:
            # Obtener el ítem seleccionado
            seleccion = self.tree.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor, seleccione un producto para modificar.")
                return
            
            item = self.tree.item(seleccion[0])
            id_producto = int(item["values"][0])
        
        # Obtener datos del producto
        resultado = self.cliente.obtener_producto(id_producto)
        
        if not resultado["exito"]:
            messagebox.showerror("Error", resultado["mensaje"])
            return
        
        producto = resultado["producto"]
        
        # Crear ventana de modificación
        modificar_window = tk.Toplevel(self.root)
        modificar_window.title(f"Modificar Producto: {producto['nombre']}")
        modificar_window.geometry("400x350")
        modificar_window.resizable(False, False)
        modificar_window.transient(self.root)
        modificar_window.grab_set()
        
        # Centrar en la pantalla
        modificar_window.update_idletasks()
        width = modificar_window.winfo_width()
        height = modificar_window.winfo_height()
        x = (modificar_window.winfo_screenwidth() // 2) - (width // 2)
        y = (modificar_window.winfo_screenheight() // 2) - (height // 2)
        modificar_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Contenido
        form_frame = ttk.Frame(modificar_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(
            form_frame, 
            text=f"Modificar Producto: {producto['nombre']}",
            font=("Arial", 14, "bold")
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Variables
        nombre_var = tk.StringVar(value=producto["nombre"])
        precio_var = tk.StringVar(value=str(producto["precio"]))
        stock_var = tk.StringVar(value=str(producto["stock"]))
        categoria_var = tk.StringVar(value=producto["categoria"])
        
        # Formulario
        # Nombre
        nombre_frame = ttk.Frame(form_frame)
        nombre_frame.pack(fill=tk.X, pady=5)
        ttk.Label(nombre_frame, text="Nombre:", width=10).pack(side=tk.LEFT)
        ttk.Entry(nombre_frame, textvariable=nombre_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Precio
        precio_frame = ttk.Frame(form_frame)
        precio_frame.pack(fill=tk.X, pady=5)
        ttk.Label(precio_frame, text="Precio:", width=10).pack(side=tk.LEFT)
        ttk.Entry(precio_frame, textvariable=precio_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Stock
        stock_frame = ttk.Frame(form_frame)
        stock_frame.pack(fill=tk.X, pady=5)
        ttk.Label(stock_frame, text="Stock:", width=10).pack(side=tk.LEFT)
        ttk.Entry(stock_frame, textvariable=stock_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Categoría
        categoria_frame = ttk.Frame(form_frame)
        categoria_frame.pack(fill=tk.X, pady=5)
        ttk.Label(categoria_frame, text="Categoría:", width=10).pack(side=tk.LEFT)
        
# Si hay categorías disponibles (excepto "Todas"), mostrarlas en el combobox
        categorias_unicas = [cat for cat in self.categorias if cat != "Todas"]
        if categorias_unicas:
            categoria_combobox = ttk.Combobox(
                categoria_frame, 
                textvariable=categoria_var,
                values=categorias_unicas
            )
            categoria_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        else:
            ttk.Entry(categoria_frame, textvariable=categoria_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Separador
        ttk.Separator(form_frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Función para validar y guardar
        def guardar_modificaciones():
            try:
                # Validar campos
                nombre = nombre_var.get().strip()
                precio_str = precio_var.get().strip()
                stock_str = stock_var.get().strip()
                categoria = categoria_var.get().strip()
                
                # Preparar datos a actualizar
                datos_actualizados = {}
                
                if nombre and nombre != producto["nombre"]:
                    datos_actualizados["nombre"] = nombre
                
                if precio_str and float(precio_str) != producto["precio"]:
                    precio = float(precio_str)
                    if precio <= 0:
                        messagebox.showerror("Error", "El precio debe ser mayor que cero.")
                        return
                    datos_actualizados["precio"] = precio
                
                if stock_str and int(stock_str) != producto["stock"]:
                    stock = int(stock_str)
                    if stock < 0:
                        messagebox.showerror("Error", "El stock no puede ser negativo.")
                        return
                    datos_actualizados["stock"] = stock
                
                if categoria and categoria != producto["categoria"]:
                    datos_actualizados["categoria"] = categoria
                
                if not datos_actualizados:
                    messagebox.showinfo("Información", "No se realizaron cambios.")
                    modificar_window.destroy()
                    return
                
                # Enviar datos al servidor
                resultado = self.cliente.modificar_producto(id_producto, datos_actualizados)
                
                if resultado["exito"]:
                    messagebox.showinfo("Éxito", resultado["mensaje"])
                    modificar_window.destroy()
                    self.cargar_productos()
                else:
                    messagebox.showerror("Error", resultado["mensaje"])
            
            except ValueError:
                messagebox.showerror("Error", "Formato de datos incorrecto. Verifica los valores ingresados.")
        
        # Botones
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            button_frame, 
            text="Guardar",
            command=guardar_modificaciones
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancelar",
            command=modificar_window.destroy
        ).pack(side=tk.RIGHT, padx=5)
    
    def eliminar_producto(self):
        """
        Elimina un producto seleccionado.
        """
        # Obtener el ítem seleccionado
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un producto para eliminar.")
            return
        
        item = self.tree.item(seleccion[0])
        id_producto = int(item["values"][0])
        nombre_producto = item["values"][1]
        
        # Confirmar eliminación
        confirmar = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de eliminar el producto '{nombre_producto}'?"
        )
        
        if not confirmar:
            return
        
        # Enviar solicitud al servidor
        resultado = self.cliente.eliminar_producto(id_producto)
        
        if resultado["exito"]:
            messagebox.showinfo("Éxito", resultado["mensaje"])
            self.cargar_productos()
        else:
            messagebox.showerror("Error", resultado["mensaje"])
    
    def abrir_vender_producto(self, id_producto=None):
        """
        Abre la ventana para vender un producto.
        
        Args:
            id_producto (int, optional): ID del producto a vender. Si es None,
                                        se solicita al usuario que lo ingrese.
        """
        if id_producto is None:
            # Obtener el ítem seleccionado en la tabla
            seleccion = self.tree.selection()
            if seleccion:
                item = self.tree.item(seleccion[0])
                id_producto = int(item["values"][0])
            else:
                # Pedir al usuario que ingrese el ID
                id_str = simpledialog.askstring(
                    "Vender Producto", 
                    "Ingrese el ID del producto a vender:"
                )
                
                if id_str is None:
                    return  # Usuario canceló
                
                try:
                    id_producto = int(id_str)
                except ValueError:
                    messagebox.showerror("Error", "El ID debe ser un número entero.")
                    return
        
        # Obtener datos del producto
        resultado = self.cliente.obtener_producto(id_producto)
        
        if not resultado["exito"]:
            messagebox.showerror("Error", resultado["mensaje"])
            return
        
        producto = resultado["producto"]
        
        # Verificar stock
        if producto["stock"] <= 0:
            messagebox.showwarning("Advertencia", "Este producto no tiene unidades disponibles para vender.")
            return
        
        # Crear ventana de venta
        vender_window = tk.Toplevel(self.root)
        vender_window.title(f"Vender Producto: {producto['nombre']}")
        vender_window.geometry("400x350")
        vender_window.resizable(False, False)
        vender_window.transient(self.root)
        vender_window.grab_set()
        
        # Centrar en la pantalla
        vender_window.update_idletasks()
        width = vender_window.winfo_width()
        height = vender_window.winfo_height()
        x = (vender_window.winfo_screenwidth() // 2) - (width // 2)
        y = (vender_window.winfo_screenheight() // 2) - (height // 2)
        vender_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Contenido
        form_frame = ttk.Frame(vender_window)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        ttk.Label(
            form_frame, 
            text=f"Vender Producto: {producto['nombre']}",
            font=("Arial", 14, "bold")
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Información del producto
        info_frame = ttk.Frame(form_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(info_frame, text=f"Producto: {producto['nombre']}", font=("Arial", 11)).pack(anchor=tk.W, pady=3)
        ttk.Label(info_frame, text=f"Precio: ${producto['precio']:.2f}", font=("Arial", 11)).pack(anchor=tk.W, pady=3)
        ttk.Label(info_frame, text=f"Stock disponible: {producto['stock']} unidades", font=("Arial", 11)).pack(anchor=tk.W, pady=3)
        
        # Separador
        ttk.Separator(form_frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Cantidad a vender
        cantidad_var = tk.StringVar(value="1")
        
        cantidad_frame = ttk.Frame(form_frame)
        cantidad_frame.pack(fill=tk.X, pady=10)
        ttk.Label(cantidad_frame, text="Cantidad:").pack(side=tk.LEFT, padx=(0, 10))
        
        # Spinbox para seleccionar cantidad
        spinbox = ttk.Spinbox(
            cantidad_frame,
            from_=1,
            to=producto["stock"],
            textvariable=cantidad_var,
            width=5
        )
        spinbox.pack(side=tk.LEFT)
        
        # Función para calcular el total
        def calcular_total(*args):
            try:
                cantidad = int(cantidad_var.get())
                total = cantidad * producto["precio"]
                total_label.config(text=f"Total: ${total:.2f}")
            except ValueError:
                total_label.config(text="Total: $0.00")
        
        cantidad_var.trace_add("write", calcular_total)
        
        # Total
        total_frame = ttk.Frame(form_frame)
        total_frame.pack(fill=tk.X, pady=10)
        total_label = ttk.Label(
            total_frame, 
            text=f"Total: ${producto['precio']:.2f}",
            font=("Arial", 12, "bold")
        )
        total_label.pack(anchor=tk.E)
        
        # Función para realizar la venta
        def realizar_venta():
            try:
                cantidad = int(cantidad_var.get())
                
                if cantidad <= 0 or cantidad > producto["stock"]:
                    messagebox.showerror("Error", "Cantidad inválida.")
                    return
                
                # Confirmar venta
                confirmar = messagebox.askyesno(
                    "Confirmar Venta",
                    f"¿Confirmar venta de {cantidad} unidades de '{producto['nombre']}' por ${cantidad * producto['precio']:.2f}?"
                )
                
                if not confirmar:
                    return
                
                # Enviar solicitud al servidor
                resultado = self.cliente.vender_producto(id_producto, cantidad)
                
                if resultado["exito"]:
                    messagebox.showinfo("Éxito", resultado["mensaje"])
                    vender_window.destroy()
                    self.cargar_productos()
                else:
                    messagebox.showerror("Error", resultado["mensaje"])
            
            except ValueError:
                messagebox.showerror("Error", "La cantidad debe ser un número entero.")
        
        # Botones
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Button(
            button_frame, 
            text="Realizar Venta",
            command=realizar_venta
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancelar",
            command=vender_window.destroy
        ).pack(side=tk.RIGHT, padx=5)

# Al final del archivo cliente/interfaz_gui.py, fuera de la clase InterfazGUI

def main(host_ip=None):
    """
    Función principal para iniciar la interfaz gráfica.
    
    Args:
        host_ip (str, optional): Dirección IP del servidor
    """
    root = tk.Tk()
    app = InterfazGUI(root, host_ip)
    root.mainloop()


if __name__ == "__main__":
    main()