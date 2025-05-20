import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import tkinter.font as tkfont

class VentaPanel:
    def __init__(self, parent, panel, db_module):
        self.parent = parent
        self.panel = panel
        self.db = db_module
        
        # Variables
        self.total = 0
        self.venta_actual = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz del panel de venta"""
        colores = self.parent.colores
        # Contenedor principal vertical
        self.panel.grid_rowconfigure(2, weight=1)
        self.panel.grid_columnconfigure(0, weight=1)
        
        # Título principal
        header_frame = tk.Frame(self.panel, bg=colores['azul'], height=40)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_propagate(False)
        tk.Label(header_frame, text="VENTA ACTUAL", font=self.parent.venta_titulo_font, 
                 bg=colores['azul'], fg=colores['boton_fg']).pack(pady=5)
        
        # Frame para escanear código y mostrar info
        scan_frame = tk.Frame(self.panel, bg=colores['panel'], bd=1, relief="solid")
        scan_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5,0))
        scan_frame.grid_columnconfigure(1, weight=1)
        
        # Frame para botones de acción rápida
        action_frame = tk.Frame(scan_frame, bg=colores['panel'])
        action_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        button_font = tkfont.Font(family="Verdana", size=9, weight="bold")
        self.impresion_btn = tk.Button(
            action_frame,
            text="🖨️ IMPRESIÓN",
            bg=colores['azul'],
            fg=colores['boton_fg'],
            font=button_font,
            relief="raised",
            bd=2,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self.agregar_impresion
        )
        self.impresion_btn.pack(side="left", padx=5)
        self.impresion_btn.bind("<Enter>", lambda e: self._hover_enter(self.impresion_btn, colores['azul']))
        self.impresion_btn.bind("<Leave>", lambda e: self._hover_leave(self.impresion_btn, colores['azul']))
        
        tk.Label(scan_frame, text="Escanear Código:", font=self.parent.venta_font, 
                 bg=colores['panel'], fg=colores['texto']).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_codigo = tk.Entry(scan_frame, font=self.parent.venta_font, width=20, bd=2, relief="solid", bg=colores['bg'], fg=colores['texto'], insertbackground=colores['texto'])
        self.entry_codigo.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.entry_codigo.focus_set()
        self.entry_codigo.bind("<Return>", self.procesar_codigo)
        
        # Info del producto escaneado en una línea separada
        self.info = tk.Label(scan_frame, text="", font=self.parent.venta_font, 
                             bg=colores['panel'], fg=colores['azul'], anchor="w")
        self.info.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=(0,5))
        
        # Frame para productos y total
        main_frame = tk.Frame(self.panel, bg=colores['panel'])
        main_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Frame para la lista de productos
        lista_container = tk.Frame(main_frame, bg=colores['panel'], bd=1, relief="solid")
        lista_container.grid(row=0, column=0, sticky="nsew")
        lista_container.grid_rowconfigure(1, weight=1)
        lista_container.grid_columnconfigure(0, weight=1)
        
        # Título de la lista
        tk.Label(lista_container, text="PRODUCTOS EN ESTA VENTA", font=self.parent.venta_font, 
                 bg=colores['borde'], fg=colores['texto'], anchor="w").grid(row=0, column=0, sticky="ew", padx=10, pady=2)
        
        # Treeview para productos
        self.lista = ttk.Treeview(lista_container, columns=("nombre", "precio", "stock"), show="headings", height=6)
        self.lista.heading("nombre", text="Producto")
        self.lista.heading("precio", text="Precio")
        self.lista.heading("stock", text="Stock")
        self.lista.column("nombre", width=180, anchor="w")
        self.lista.column("precio", width=70, anchor="center")
        self.lista.column("stock", width=50, anchor="center")
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview",
            background=colores['treeview_bg'],
            foreground=colores['treeview_fg'],
            fieldbackground=colores['treeview_bg'],
            rowheight=25,
            font=self.parent.venta_font
        )
        style.configure("Treeview.Heading",
            background=colores['treeview_heading_bg'],
            foreground=colores['treeview_heading_fg'],
            font=self.parent.venta_font
        )
        style.map("Treeview",
            background=[('selected', colores['treeview_selected_bg'])],
            foreground=[('selected', colores['treeview_selected_fg'])]
        )
        self.lista.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        scrollbar = ttk.Scrollbar(lista_container, orient="vertical", command=self.lista.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.lista.configure(yscrollcommand=scrollbar.set)
        
        # Frame para el total
        total_frame = tk.Frame(main_frame, bg=colores['borde'], relief="solid", bd=1, height=70)
        total_frame.grid(row=2, column=0, sticky="ew", pady=(5,0))
        total_frame.grid_propagate(False)
        
        tk.Label(total_frame, text="TOTAL:", font=self.parent.venta_titulo_font, bg=colores['borde'], fg=colores['texto']).pack(side="left", padx=(30,5), pady=10)
        self.label_total = tk.Label(total_frame, text="$0.00", font=self.parent.precio_font, bg=colores['borde'], fg=colores['azul'])
        self.label_total.pack(side="left", padx=5, pady=10)
        
        # Frame para los botones en la parte inferior
        botones_frame = tk.Frame(self.panel, bg=colores['panel'])
        botones_frame.grid(row=3, column=0, sticky="ew", padx=0, pady=0)
        botones_frame.grid_columnconfigure(0, weight=1)
        botones_frame.grid_columnconfigure(1, weight=1)
        
        button_font = tkfont.Font(family="Verdana", size=10, weight="bold")
        self.eliminar_btn = tk.Button(
            botones_frame, 
            text="❌ ELIMINAR", 
            bg=colores['rojo'], fg=colores['boton_fg'],
            font=button_font, relief="raised", bd=2,
            padx=10, pady=12, cursor="hand2",
            command=self.eliminar_producto
        )
        self.eliminar_btn.grid(row=0, column=0, sticky="ew", padx=(10,5), pady=10)
        self.finalizar_btn = tk.Button(
            botones_frame, 
            text="✓ FINALIZAR", 
            bg=colores['verde'], fg=colores['boton_fg'],
            font=button_font, relief="raised", bd=2,
            padx=10, pady=12, cursor="hand2",
            command=self.finalizar_venta
        )
        self.finalizar_btn.grid(row=0, column=1, sticky="ew", padx=(5,10), pady=10)
        self.eliminar_btn.bind("<Enter>", lambda e: self._hover_enter(self.eliminar_btn, colores['rojo']))
        self.eliminar_btn.bind("<Leave>", lambda e: self._hover_leave(self.eliminar_btn, colores['rojo']))
        self.finalizar_btn.bind("<Enter>", lambda e: self._hover_enter(self.finalizar_btn, colores['verde']))
        self.finalizar_btn.bind("<Leave>", lambda e: self._hover_leave(self.finalizar_btn, colores['verde']))
    
    def _hover_enter(self, button, color):
        button.config(bg=color)
    def _hover_leave(self, button, color):
        button.config(bg=color)
    def procesar_codigo(self, event):
        codigo = self.entry_codigo.get().strip()
        self.entry_codigo.delete(0, tk.END)
        producto = self.db.buscar_producto(codigo)
        if producto:
            nombre, precio_compra, precio_venta, stock, categoria = producto
            if stock > 0:
                cantidad_en_venta = sum(1 for item in self.venta_actual if item[0] == codigo)
                if cantidad_en_venta < stock:
                    self.venta_actual.append((codigo, nombre, precio_compra, precio_venta, categoria))
                    stock_restante = stock - cantidad_en_venta - 1
                    self.lista.insert("", "end", values=(nombre, f"${precio_venta:.2f}", f"{stock_restante}"))
                    self.total += precio_venta
                    self.actualizar_totales()
                    self.info.config(text=f"{nombre} | ${precio_venta:.2f} | Cat: {categoria}")
                else:
                    self.info.config(text="¡No hay más stock disponible para este producto!")
            else:
                self.info.config(text="¡Sin stock!")
        else:
            self.info.config(text="Producto no encontrado.")
        self.entry_codigo.focus_set()
    def actualizar_totales(self):
        self.label_total.config(text=f"${self.total:.2f}")
    def finalizar_venta(self):
        if not self.venta_actual:
            messagebox.showinfo("Venta", "No hay productos en la venta.")
            return
        # Agrupar productos por código para obtener cantidades
        resumen = {}
        for codigo, nombre, _, precio_venta, _ in self.venta_actual:
            if codigo not in resumen:
                resumen[codigo] = {"nombre": nombre, "cantidad": 1, "precio_unitario": precio_venta}
            else:
                resumen[codigo]["cantidad"] += 1
        productos_guardar = [
            (codigo, datos["nombre"], datos["cantidad"], datos["precio_unitario"])
            for codigo, datos in resumen.items()
        ]
        # Guardar en la base de datos
        from db import database
        database.guardar_venta(self.total, productos_guardar)
        self.venta_actual.clear()
        for item in self.lista.get_children():
            self.lista.delete(item)
        self.total = 0
        self.actualizar_totales()
        self.info.config(text="Venta finalizada.")
        messagebox.showinfo("Venta", "¡Venta finalizada con éxito!")
        self.parent.actualizar_inventario()
        self.entry_codigo.focus_set()
    def eliminar_producto(self):
        seleccion = self.lista.selection()
        if not seleccion:
            messagebox.showwarning("Atención", "Selecciona un producto para eliminar.")
            return
        seleccion_id = seleccion[0]
        todos_los_items = self.lista.get_children()
        idx = todos_los_items.index(seleccion_id)
        _, _, _, precio_venta, _ = self.venta_actual[idx]
        self.total -= precio_venta
        self.lista.delete(seleccion_id)
        del self.venta_actual[idx]
        self.actualizar_totales()
        self.entry_codigo.focus_set()
    def agregar_impresion(self):
        """Agrega una venta de impresión con importe personalizado"""
        try:
            importe = simpledialog.askfloat("Impresión", "Ingrese el importe de la impresión:", 
                                          minvalue=0.01, maxvalue=9999.99)
            if importe is not None:  # Si el usuario no canceló
                self.venta_actual.append(("IMP", "Impresión", 0, importe, "Impresiones"))
                self.lista.insert("", "end", values=("Impresión", f"${importe:.2f}", "N/A"))
                self.total += importe
                self.actualizar_totales()
                self.info.config(text=f"Impresión | ${importe:.2f}")
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese un importe válido")
