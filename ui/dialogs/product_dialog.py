import tkinter as tk
from tkinter import messagebox, ttk

class ProductoDialog:
    def __init__(self, parent, db_module, on_save_callback, codigo_editar=None):
        self.parent = parent
        self.db = db_module
        self.on_save_callback = on_save_callback
        self.codigo_editar = codigo_editar  # Si es None, estamos creando; si no, estamos editando
        
        # Verificar si estamos recibiendo la ventana root o el objeto POSApp
        # y obtener las fuentes apropiadamente
        if hasattr(parent, 'titulo_font') and hasattr(parent, 'normal_font'):
            # Si es POSApp, obtener directamente
            self.titulo_font = parent.titulo_font
            self.normal_font = parent.normal_font
            # Guardar referencia a la ventana root
            self.root = parent.root
        else:
            # Buscar el objeto POSApp a través de los atributos
            # Si no lo encontramos, crear fuentes predeterminadas
            import tkinter.font as tkfont
            self.titulo_font = tkfont.Font(family="Arial", size=16, weight="bold")
            self.normal_font = tkfont.Font(family="Arial", size=10)
            # En este caso, el parent ya es root
            self.root = parent
    
    def mostrar(self):
        """Muestra el diálogo para agregar o editar un producto"""
        # Crear ventana
        self.ventana = tk.Toplevel(self.root)
        # Obtener colores del tema
        colores = getattr(self.parent, 'colores', {
            'bg': '#f5f5f5', 'panel': '#fff', 'texto': '#222', 'boton': '#3498db', 'boton_fg': '#fff',
            'borde': '#e9ecef', 'azul': '#3498db', 'verde': '#27ae60', 'rojo': '#e74c3c', 'gris': '#e9ecef'
        })
        # Determinar si estamos editando o creando
        if self.codigo_editar:
            self.ventana.title("Editar producto")
            titulo_texto = "EDITAR PRODUCTO"
        else:
            self.ventana.title("Agregar nuevo producto")
            titulo_texto = "AGREGAR NUEVO PRODUCTO"
        self.ventana.geometry("450x600")
        self.ventana.configure(bg=colores['bg'])
        self.ventana.resizable(False, False)
        # ================ REDISEÑO USANDO GRID =================
        # Título
        titulo_frame = tk.Frame(self.ventana, bg=colores['azul'], height=50)
        titulo_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        titulo_frame.grid_propagate(False)
        tk.Label(titulo_frame, text=titulo_texto, font=self.titulo_font, bg=colores['azul'], fg=colores['boton_fg']).pack(pady=10)
        # Contenedor principal
        form_frame = tk.Frame(self.ventana, bg=colores['panel'], padx=20, pady=20)
        form_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        self.ventana.grid_rowconfigure(1, weight=1)
        self.ventana.grid_columnconfigure(0, weight=1)
        # Código
        tk.Label(form_frame, text="Código de barras:", font=self.normal_font, bg=colores['panel'], fg=colores['texto'], anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.codigo_entry = tk.Entry(form_frame, font=self.normal_font, bd=2, relief="solid", bg=colores['bg'], fg=colores['texto'], insertbackground=colores['texto'])
        self.codigo_entry.grid(row=1, column=0, sticky="ew", ipady=5, pady=(0, 15))
        if self.codigo_editar:
            self.codigo_entry.insert(0, self.codigo_editar)
            self.codigo_entry.config(state="normal")  # Ahora editable
        # Nombre
        tk.Label(form_frame, text="Nombre del producto:", font=self.normal_font, bg=colores['panel'], fg=colores['texto'], anchor="w").grid(row=2, column=0, sticky="w", pady=(0, 5))
        self.nombre_entry = tk.Entry(form_frame, font=self.normal_font, bd=2, relief="solid", bg=colores['bg'], fg=colores['texto'], insertbackground=colores['texto'])
        self.nombre_entry.grid(row=3, column=0, sticky="ew", ipady=5, pady=(0, 15))
        # Precio de compra
        tk.Label(form_frame, text="Precio de compra ($):", font=self.normal_font, bg=colores['panel'], fg=colores['texto'], anchor="w").grid(row=4, column=0, sticky="w", pady=(0, 5))
        self.precio_compra_entry = tk.Entry(form_frame, font=self.normal_font, bd=2, relief="solid", bg=colores['bg'], fg=colores['texto'], insertbackground=colores['texto'])
        self.precio_compra_entry.grid(row=5, column=0, sticky="ew", ipady=5, pady=(0, 15))
        # Precio de venta
        tk.Label(form_frame, text="Precio de venta ($):", font=self.normal_font, bg=colores['panel'], fg=colores['texto'], anchor="w").grid(row=6, column=0, sticky="w", pady=(0, 5))
        self.precio_venta_entry = tk.Entry(form_frame, font=self.normal_font, bd=2, relief="solid", bg=colores['bg'], fg=colores['texto'], insertbackground=colores['texto'])
        self.precio_venta_entry.grid(row=7, column=0, sticky="ew", ipady=5, pady=(0, 15))
        # Etiqueta de margen
        self.margen_label = tk.Label(form_frame, text="Margen: 0%", font=self.normal_font, bg=colores['panel'], fg="#666666")
        self.margen_label.grid(row=8, column=0, sticky="w", pady=(0, 10))
        self.precio_compra_entry.bind("<KeyRelease>", self.actualizar_margen)
        self.precio_venta_entry.bind("<KeyRelease>", self.actualizar_margen)
        # Stock
        tk.Label(form_frame, text="Stock:", font=self.normal_font, bg=colores['panel'], fg=colores['texto'], anchor="w").grid(row=9, column=0, sticky="w", pady=(0, 5))
        self.stock_entry = tk.Entry(form_frame, font=self.normal_font, bd=2, relief="solid", bg=colores['bg'], fg=colores['texto'], insertbackground=colores['texto'])
        self.stock_entry.grid(row=10, column=0, sticky="ew", ipady=5, pady=(0, 20))
        separator_cat = tk.Frame(form_frame, height=8, bg=colores['panel'])
        separator_cat.grid(row=11, column=0)
        cat_frame = tk.Frame(form_frame, bg=colores['panel'])
        cat_frame.grid(row=12, column=0, sticky="ew", pady=(0, 10))
        cat_frame.grid_columnconfigure(1, weight=1)
        tk.Label(cat_frame, text="Categoría:", font=self.normal_font, bg=colores['panel'], fg=colores['texto'], anchor="w").grid(row=0, column=0, sticky="w")
        categorias = self.db.obtener_categorias()
        if not categorias:
            categorias = ["General"]
        self.categoria_var = tk.StringVar(value=categorias[0])
        self.categoria_combo = ttk.Combobox(cat_frame, textvariable=self.categoria_var, values=categorias, font=self.normal_font)
        self.categoria_combo.grid(row=0, column=1, sticky="ew", ipady=5)
        tk.Label(form_frame, text="(Puede seleccionar una existente o escribir una nueva)", font=("Arial", 8), bg=colores['panel'], fg="#888").grid(row=13, column=0, sticky="w", pady=(0, 10))
        self.mensaje = tk.Label(form_frame, text="", fg="red", bg=colores['panel'], font=self.normal_font)
        self.mensaje.grid(row=14, column=0, sticky="ew", pady=5)
        form_frame.grid_columnconfigure(0, weight=1)
        # ================== BOTONES DE ACCIÓN ===================
        botones_frame = tk.Frame(self.ventana, bg=colores['borde'], height=70)
        botones_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        botones_frame.grid_propagate(False)
        self.cancelar_btn = tk.Button(
            botones_frame, text="CANCELAR", bg=colores['rojo'], fg=colores['boton_fg'], font=self.normal_font, relief="raised", bd=2, width=15, height=2, command=self.ventana.destroy
        )
        self.cancelar_btn.place(relx=0.25, rely=0.5, anchor="center")
        self.guardar_btn = tk.Button(
            botones_frame, text="GUARDAR", bg=colores['verde'], fg=colores['boton_fg'], font=self.normal_font, relief="raised", bd=2, width=15, height=2, command=self.validar_y_guardar
        )
        self.guardar_btn.place(relx=0.75, rely=0.5, anchor="center")
        # Si estamos editando, cargamos los datos del producto
        if self.codigo_editar:
            self.cargar_datos_producto()
        # Enfocar primer campo editable
        self.codigo_entry.focus_set()
        # Centrar ventana en pantalla
        self.ventana.update_idletasks()
        ancho = self.ventana.winfo_width()
        alto = self.ventana.winfo_height()
        x = (self.ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (alto // 2)
        self.ventana.geometry(f'{ancho}x{alto}+{x}+{y}')
    
    def actualizar_margen(self, event=None):
        """Calcula y muestra el margen de ganancia al modificar los precios"""
        try:
            precio_compra = float(self.precio_compra_entry.get())
            precio_venta = float(self.precio_venta_entry.get())
            
            if precio_compra > 0:
                margen = ((precio_venta - precio_compra) / precio_compra) * 100
                self.margen_label.config(text=f"Margen: {margen:.2f}%")
                
                # Cambiar color según el margen
                if margen < 0:
                    self.margen_label.config(fg="#e74c3c")  # Rojo - pérdida
                elif margen < 10:
                    self.margen_label.config(fg="#f39c12")  # Naranja - bajo
                elif margen < 30:
                    self.margen_label.config(fg="#2ecc71")  # Verde - bueno
                else:
                    self.margen_label.config(fg="#2980b9")  # Azul - excelente
        except:
            self.margen_label.config(text="Margen: --", fg="#666666")
    
    def cargar_datos_producto(self):
        """Carga los datos del producto a editar"""
        try:
            # Obtener datos del producto
            datos = self.db.buscar_producto(self.codigo_editar)
            if datos:
                nombre, precio_compra, precio_venta, stock, categoria = datos
                # Insertar datos en los campos
                self.codigo_entry.delete(0, tk.END)
                self.codigo_entry.insert(0, str(self.codigo_editar))  # Siempre string, respeta ceros
                self.nombre_entry.delete(0, tk.END)
                self.nombre_entry.insert(0, nombre)
                self.precio_compra_entry.delete(0, tk.END)
                self.precio_compra_entry.insert(0, str(precio_compra))
                self.precio_venta_entry.delete(0, tk.END)
                self.precio_venta_entry.insert(0, str(precio_venta))
                self.stock_entry.delete(0, tk.END)
                self.stock_entry.insert(0, str(stock))
                # Establecer categoría
                if categoria in self.categoria_combo['values']:
                    self.categoria_var.set(categoria)
                else:
                    valores = list(self.categoria_combo['values'])
                    valores.append(categoria)
                    self.categoria_combo['values'] = valores
                    self.categoria_var.set(categoria)
                # Actualizar el margen
                self.actualizar_margen()
        except Exception as e:
            self.mensaje.config(text=f"Error al cargar datos: {str(e)}")
    
    def validar_y_guardar(self):
        # Obtener datos
        codigo = self.codigo_entry.get().strip()
        nombre = self.nombre_entry.get().strip()
        categoria = self.categoria_var.get().strip()
        # Validar campos obligatorios
        if not codigo or not nombre:
            self.mensaje.config(text="Código y nombre son obligatorios")
            return
        # Si no se proporciona categoría, usar "General"
        if not categoria:
            categoria = "General"
        try:
            precio_compra = float(self.precio_compra_entry.get())
            if precio_compra <= 0:
                self.mensaje.config(text="El precio de compra debe ser mayor a 0")
                return
        except ValueError:
            self.mensaje.config(text="El precio de compra debe ser un número válido")
            return
        try:
            precio_venta = float(self.precio_venta_entry.get())
            if precio_venta <= 0:
                self.mensaje.config(text="El precio de venta debe ser mayor a 0")
                return
        except ValueError:
            self.mensaje.config(text="El precio de venta debe ser un número válido")
            return
        try:
            stock = int(self.stock_entry.get())
            if stock < 0:
                self.mensaje.config(text="El stock no puede ser negativo")
                return
        except ValueError:
            self.mensaje.config(text="El stock debe ser un número entero")
            return
        # Intentar guardar
        try:
            if self.codigo_editar:
                # Si el código fue cambiado, actualizar en cascada
                if codigo != self.codigo_editar:
                    self.db.actualizar_codigo_producto(self.codigo_editar, codigo)
                # Actualizar el resto de los datos
                self.db.actualizar_producto(
                    codigo=codigo,
                    nombre=nombre,
                    precio_compra=precio_compra,
                    precio_venta=precio_venta,
                    stock=stock,
                    categoria=categoria
                )
                mensaje_exito = f"Producto '{nombre}' actualizado correctamente"
            else:
                # Estamos creando un nuevo producto
                self.db.agregar_producto(
                    codigo=codigo,
                    nombre=nombre,
                    precio_compra=precio_compra,
                    precio_venta=precio_venta,
                    stock=stock,
                    categoria=categoria
                )
                mensaje_exito = f"Producto '{nombre}' agregado correctamente"
            self.ventana.destroy()  # Cerrar ventana
            messagebox.showinfo("Éxito", mensaje_exito)
            # Ejecutar callback para actualizar UI
            if self.on_save_callback:
                self.on_save_callback()
            # Actualizar la lista de categorías en la aplicación principal
            if hasattr(self.parent, 'actualizar_categorias'):
                self.parent.actualizar_categorias()
        except Exception as e:
            self.mensaje.config(text=f"Error: {str(e)}")
