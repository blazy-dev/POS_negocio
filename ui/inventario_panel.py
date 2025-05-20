import tkinter as tk
from tkinter import ttk, messagebox
from ui.dialogs.product_dialog import ProductoDialog
import tkinter.font as tkfont

class InventarioPanel:
    def __init__(self, parent, panel, db_module):
        self.parent = parent
        self.panel = panel
        self.db = db_module
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura la interfaz del panel de inventario"""
        colores = self.parent.colores
        # Título moderno
        titulo_frame = tk.Frame(self.panel, bg=colores['azul'], height=40)
        titulo_frame.pack(fill="x")
        titulo_frame.pack_propagate(False)
        tk.Label(titulo_frame, text="INVENTARIO", font=self.parent.titulo_font, bg=colores['azul'], fg=colores['boton_fg']).pack(pady=5)
        
        # Filtros con mejor alineación
        filtros_frame = tk.Frame(self.panel, bg=colores['bg'])
        filtros_frame.pack(fill="x", padx=10, pady=(8, 0))
        
        # Búsqueda por texto
        tk.Label(filtros_frame, text="Buscar:", font=self.parent.normal_font, bg=colores['bg'], fg=colores['texto']).pack(side="left", padx=5)
        self.entry_buscar = tk.Entry(filtros_frame, font=self.parent.normal_font, width=20, bg=colores['panel'], fg=colores['texto'], insertbackground=colores['texto'])
        self.entry_buscar.pack(side="left", padx=5, fill="x", expand=True)
        self.entry_buscar.bind("<KeyRelease>", self.filtrar_productos)
        
        # Filtro por categoría
        tk.Label(filtros_frame, text="Categoría:", font=self.parent.normal_font, bg=colores['bg'], fg=colores['texto']).pack(side="left", padx=10)
        self.categoria_var = tk.StringVar(value="Todas")
        self.combo_categoria = ttk.Combobox(filtros_frame, textvariable=self.categoria_var, 
                                          state="readonly", width=15, font=self.parent.normal_font)
        self.combo_categoria.pack(side="left", padx=5)
        self.combo_categoria.bind("<<ComboboxSelected>>", self.filtrar_por_categoria)
        
        # Tabla con fondo y bordes
        tabla_frame = tk.Frame(self.panel, bg=colores['borde'], bd=1, relief="solid")
        tabla_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear tabla de productos con Treeview
        columnas = ("codigo", "nombre", "precio_compra", "precio_venta", "stock", "categoria")
        self.tabla_productos = ttk.Treeview(tabla_frame, columns=columnas, show="headings")
        
        # Definir encabezados
        self.tabla_productos.heading("codigo", text="Código")
        self.tabla_productos.heading("nombre", text="Nombre")
        self.tabla_productos.heading("precio_compra", text="P. Compra")
        self.tabla_productos.heading("precio_venta", text="P. Venta")
        self.tabla_productos.heading("stock", text="Stock")
        self.tabla_productos.heading("categoria", text="Categoría")
        
        # Definir ancho de columnas
        self.tabla_productos.column("codigo", width=80, anchor="center")
        self.tabla_productos.column("nombre", width=150, anchor="w")
        self.tabla_productos.column("precio_compra", width=70, anchor="center")
        self.tabla_productos.column("precio_venta", width=70, anchor="center")
        self.tabla_productos.column("stock", width=50, anchor="center")
        self.tabla_productos.column("categoria", width=80, anchor="center")
        
        # Configurar selección
        self.tabla_productos.bind("<Double-1>", self.editar_producto_seleccionado)
        
        # Scrollbar para la tabla
        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla_productos.yview)
        self.tabla_productos.configure(yscroll=scrollbar.set)
        
        # Empaquetar tabla y scrollbar
        self.tabla_productos.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Estilos para Treeview
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview",
            background=colores['treeview_bg'],
            foreground=colores['treeview_fg'],
            fieldbackground=colores['treeview_bg'],
            rowheight=25,
            font=self.parent.normal_font
        )
        style.configure("Treeview.Heading",
            background=colores['treeview_heading_bg'],
            foreground=colores['treeview_heading_fg'],
            font=self.parent.normal_font
        )
        style.map("Treeview",
            background=[('selected', colores['treeview_selected_bg'])],
            foreground=[('selected', colores['treeview_selected_fg'])]
        )
        
        # Frame para botones de acción
        botones_frame = tk.Frame(self.panel, bg=colores['bg'])
        botones_frame.pack(fill="x", padx=10, pady=(0, 12))
        
        # Botón para agregar producto
        button_font = tkfont.Font(family="Verdana", size=10, weight="bold")
        self.agregar_btn = tk.Button(
            botones_frame, text="➕ AGREGAR PRODUCTO", bg=colores['azul'], fg=colores['boton_fg'],
            font=button_font, relief="raised", bd=2, padx=10, pady=12, cursor="hand2",
            command=self.mostrar_dialogo_producto
        )
        self.agregar_btn.pack(side="left", fill="x", expand=True, padx=8, pady=5)
        
        # Botón para editar producto
        self.editar_btn = tk.Button(
            botones_frame, text="✏️ EDITAR SELECCIONADO", bg=colores['verde'], fg=colores['boton_fg'],
            font=button_font, relief="raised", bd=2, padx=10, pady=12, cursor="hand2",
            command=self.editar_producto_seleccionado
        )
        self.editar_btn.pack(side="left", fill="x", expand=True, padx=8, pady=5)

        # Botón para eliminar producto
        self.eliminar_btn = tk.Button(
            botones_frame, text="❌ ELIMINAR SELECCIONADO", bg=colores['rojo'], fg=colores['boton_fg'],
            font=button_font, relief="raised", bd=2, padx=10, pady=12, cursor="hand2",
            command=self.eliminar_producto_seleccionado
        )
        self.eliminar_btn.pack(side="left", fill="x", expand=True, padx=8, pady=5)
        
        # Efecto hover
        self.agregar_btn.bind("<Enter>", lambda e: self._hover_enter(self.agregar_btn, colores['azul']))
        self.agregar_btn.bind("<Leave>", lambda e: self._hover_leave(self.agregar_btn, colores['azul']))
        self.editar_btn.bind("<Enter>", lambda e: self._hover_enter(self.editar_btn, colores['verde']))
        self.editar_btn.bind("<Leave>", lambda e: self._hover_leave(self.editar_btn, colores['verde']))
        self.eliminar_btn.bind("<Enter>", lambda e: self._hover_enter(self.eliminar_btn, colores['rojo']))
        self.eliminar_btn.bind("<Leave>", lambda e: self._hover_leave(self.eliminar_btn, colores['rojo']))
        
        # Cargar categorías y productos iniciales
        self.cargar_categorias()
        self.cargar_productos()
    
    def _hover_enter(self, button, color):
        button.config(bg=color)
    
    def _hover_leave(self, button, color):
        button.config(bg=color)
    
    def cargar_categorias(self):
        """Carga las categorías disponibles en el combobox"""
        # Guardar la categoría seleccionada actualmente
        categoria_actual = self.categoria_var.get()
        
        # Obtener todas las categorías
        categorias = self.db.obtener_categorias()
        
        # Asegurarse de que "Todas" esté al principio
        if "Todas" not in categorias:
            categorias = ["Todas"] + categorias
            
        # Actualizar el combobox
        self.combo_categoria['values'] = categorias
        
        # Restaurar la categoría seleccionada si existe, o seleccionar "Todas"
        if categoria_actual in categorias:
            self.categoria_var.set(categoria_actual)
        else:
            self.categoria_var.set("Todas")
            
        # Recargar los productos con el filtro actual
        self.cargar_productos()
    
    def cargar_productos(self):
        """Carga todos los productos a la tabla"""
        # Limpiar tabla
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)
            
        # Obtener y mostrar productos
        categoria = self.categoria_var.get()
        if categoria == "Todas":
            productos = self.db.obtener_reporte()
        else:
            productos = self.db.obtener_productos_por_categoria(categoria)
            
        for c, n, pc, pv, s, cat in productos:
            self.tabla_productos.insert("", tk.END, values=(str(c), n, f"${pc:.2f}", f"${pv:.2f}", s, cat))
    
    def filtrar_productos(self, event):
        """Filtra productos según el texto ingresado"""
        busqueda = self.entry_buscar.get().lower()
        # Limpiar tabla
        for item in self.tabla_productos.get_children():
            self.tabla_productos.delete(item)
            
        # Filtrar productos
        categoria = self.categoria_var.get()
        if categoria == "Todas":
            productos = self.db.obtener_reporte()
        else:
            productos = self.db.obtener_productos_por_categoria(categoria)
            
        for c, n, pc, pv, s, cat in productos:
            if (busqueda in c.lower() or 
                busqueda in n.lower() or 
                busqueda in str(pc).lower() or 
                busqueda in str(pv).lower() or
                busqueda in str(s).lower() or 
                busqueda in cat.lower()):
                self.tabla_productos.insert("", tk.END, values=(str(c), n, f"${pc:.2f}", f"${pv:.2f}", s, cat))
    
    def filtrar_por_categoria(self, event):
        """Filtra productos por la categoría seleccionada"""
        self.cargar_productos()
    
    def editar_producto_seleccionado(self, event=None):
        """Muestra el diálogo para editar el producto seleccionado"""
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un producto para editar.")
            return
        
        selected_item_id = seleccion[0]
        # Obtener el código del producto seleccionado usando .set() para mayor fiabilidad
        codigo = str(self.tabla_productos.set(selected_item_id, "codigo"))

        try:
            dialogo = ProductoDialog(self.parent, self.db, self.cargar_productos, codigo)
            dialogo.mostrar()
        except Exception as e:
            import traceback
            error_msg = f"Error al abrir diálogo de edición: {str(e)}\n\n{traceback.format_exc()}"
            messagebox.showerror("Error", error_msg)
            print(error_msg)
    
    def mostrar_dialogo_producto(self):
        """Muestra el diálogo para agregar un nuevo producto"""
        try:
            dialogo = ProductoDialog(self.parent, self.db, self.cargar_productos)
            dialogo.mostrar()
        except Exception as e:
            import traceback
            from tkinter import messagebox
            error_msg = f"Error al abrir diálogo: {str(e)}\n\n{traceback.format_exc()}"
            messagebox.showerror("Error", error_msg)
            print(error_msg)

    def eliminar_producto_seleccionado(self):
        """Elimina el producto seleccionado de la base de datos"""
        seleccion = self.tabla_productos.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un producto para eliminar.")
            return

        selected_item_id = seleccion[0]
        # Obtener el código y nombre del producto usando .set()
        codigo = str(self.tabla_productos.set(selected_item_id, "codigo"))
        nombre = str(self.tabla_productos.set(selected_item_id, "nombre"))

        if messagebox.askyesno("Confirmar", f"¿Estás seguro de que deseas eliminar el producto '{nombre}'?"):
            try:
                self.db.eliminar_producto(codigo)
                self.cargar_productos()
                messagebox.showinfo("Éxito", f"Producto '{nombre}' eliminado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar el producto: {str(e)}")