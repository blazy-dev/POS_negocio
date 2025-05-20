import tkinter as tk
import tkinter.font as tkfont
from ui.venta_panel import VentaPanel
from ui.inventario_panel import InventarioPanel
from ui.registro_ventas import RegistroVentasFrame

class POSApp:
    def __init__(self, root, db_module):
        self.root = root
        self.db = db_module
        self.root.title("Sistema POS - Almacén")
        self.root.geometry("1000x700")  # Ventana más grande para asegurar visibilidad
        self.modo_oscuro = False  # Estado inicial
        self.colores = self._obtener_colores()
        self.root.configure(bg=self.colores['bg'])  # Fondo según modo
        
        # Barra de menú
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        self.menu_bar.add_command(label="Principal", command=self._mostrar_vista_principal)
        self.menu_bar.add_command(label="Registro de ventas", command=self.mostrar_registro_ventas)
        
        # Menú de preferencias
        self.preferencias_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.preferencias_menu.add_command(label="Modo claro", command=lambda: self.cambiar_modo(False))
        self.preferencias_menu.add_command(label="Modo oscuro", command=lambda: self.cambiar_modo(True))
        self.menu_bar.add_cascade(label="Preferencias", menu=self.preferencias_menu)
        
        # Crear fuentes personalizadas
        self.titulo_font = tkfont.Font(family="Arial", size=16, weight="bold")
        self.subtitulo_font = tkfont.Font(family="Arial", size=12, weight="bold")
        self.normal_font = tkfont.Font(family="Arial", size=10)
        
        # Nuevas fuentes para mejorar la legibilidad
        self.venta_font = tkfont.Font(family="Verdana", size=11)
        self.venta_titulo_font = tkfont.Font(family="Verdana", size=14, weight="bold")
        self.precio_font = tkfont.Font(family="Consolas", size=12, weight="bold")  # Fuente monoespaciada para precios
        
        # Crear tablas si no existen
        self.db.crear_tablas()
        
        # Frame central intercambiable
        self.central_frame = tk.Frame(root, bg=self.colores['bg'])
        self.central_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self._mostrar_vista_principal()
    
    def _mostrar_vista_principal(self):
        for widget in self.central_frame.winfo_children():
            widget.destroy()
        self.panel_izquierdo = tk.Frame(self.central_frame, bg="#ffffff", relief="ridge", bd=1)
        self.panel_izquierdo.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.panel_derecho = tk.Frame(self.central_frame, bg="#ffffff", relief="ridge", bd=1)
        self.panel_derecho.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        self.venta_panel = VentaPanel(self, self.panel_izquierdo, self.db)
        self.inventario_panel = InventarioPanel(self, self.panel_derecho, self.db)
    
    def mostrar_registro_ventas(self):
        for widget in self.central_frame.winfo_children():
            widget.destroy()
        RegistroVentasFrame(self.central_frame, self.db, self._mostrar_vista_principal)
    
    def actualizar_inventario(self):
        """Actualiza la vista de inventario"""
        self.inventario_panel.cargar_productos()
    
    def actualizar_categorias(self):
        """Actualiza el combobox de categorías en el panel de inventario"""
        self.inventario_panel.cargar_categorias()

    def _obtener_colores(self):
        if self.modo_oscuro:
            return {
                'bg': '#23272e',         # Fondo general
                'panel': '#2c313a',      # Paneles y frames
                'texto': '#f5f6fa',      # Texto principal
                'boton': '#3b4252',      # Fondo de botones neutros
                'boton_fg': '#f5f6fa',   # Texto de botones
                'borde': '#444c56',      # Bordes y separadores
                'azul': '#2980b9',       # Botón azul
                'verde': '#27ae60',      # Botón verde
                'rojo': '#e74c3c',       # Botón rojo
                'gris': '#444c56',       # Gris para tablas
                'treeview_bg': '#23272e', # Fondo de Treeview
                'treeview_fg': '#f5f6fa', # Texto de Treeview
                'treeview_heading_bg': '#2c313a', # Encabezado de Treeview
                'treeview_heading_fg': '#f5f6fa', # Texto encabezado
                'treeview_selected_bg': '#2980b9', # Fila seleccionada
                'treeview_selected_fg': '#fff',    # Texto fila seleccionada
            }
        else:
            return {
                'bg': '#f0f0f0',
                'panel': '#ffffff',
                'texto': '#222',
                'boton': '#3498db',
                'boton_fg': '#fff',
                'borde': '#e9ecef',
                'azul': '#3498db',
                'verde': '#27ae60',
                'rojo': '#e74c3c',
                'gris': '#e9ecef',
                'treeview_bg': '#fff',
                'treeview_fg': '#222',
                'treeview_heading_bg': '#e9ecef',
                'treeview_heading_fg': '#222',
                'treeview_selected_bg': '#3498db',
                'treeview_selected_fg': '#fff',
            }

    def cambiar_modo(self, oscuro):
        self.modo_oscuro = oscuro
        self.colores = self._obtener_colores()
        self.root.configure(bg=self.colores['bg'])
        self.central_frame.configure(bg=self.colores['bg'])
        # Aquí deberíamos notificar a los paneles para que actualicen sus colores
        # Por ahora, recargamos la vista principal
        self._mostrar_vista_principal()
        # Actualizar menú
        if self.modo_oscuro:
            self.preferencias_menu.entryconfig(0, label="Modo claro")
            self.preferencias_menu.entryconfig(1, label="Modo oscuro ✓")
        else:
            self.preferencias_menu.entryconfig(0, label="Modo claro ✓")
            self.preferencias_menu.entryconfig(1, label="Modo oscuro")
