import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
from tkcalendar import DateEntry
import tkinter.font as tkfont
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class RegistroVentasFrame(tk.Frame):
    def __init__(self, parent, db, volver_callback):
        super().__init__(parent, bg=getattr(parent.master, 'colores', {'bg':'#f5f5f5'})['bg'])
        self.pack(fill="both", expand=True)
        self.db = db
        self.volver_callback = volver_callback
        self.colores = getattr(
            parent.master, 'colores',
            {
                'bg': '#f5f5f5',
                'panel': '#f5f5f5',
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
        )
        self._build_ui()

    def _build_ui(self):
        c = self.colores
        # Título
        titulo_frame = tk.Frame(self, bg=c['azul'], height=40)
        titulo_frame.pack(fill="x")
        titulo_frame.pack_propagate(False)
        tk.Label(titulo_frame, text="REGISTRO DE VENTAS", font=("Arial", 16, "bold"), bg=c['azul'], fg=c['boton_fg']).pack(pady=5)

        # Filtros
        filtros_frame = tk.Frame(self, bg=c['bg'])
        filtros_frame.pack(fill="x", padx=15, pady=(10, 0))

        # Filtro de fechas con calendario
        tk.Label(filtros_frame, text="Desde:", font=("Arial", 10), bg=c['bg'], fg=c['texto']).pack(side="left")
        self.fecha_desde = DateEntry(filtros_frame, width=12, background=c['azul'], foreground=c['boton_fg'], borderwidth=2, date_pattern='yyyy-mm-dd')
        self.fecha_desde.pack(side="left", padx=2)

        tk.Label(filtros_frame, text="Hasta:", font=("Arial", 10), bg=c['bg'], fg=c['texto']).pack(side="left", padx=(10,0))
        self.fecha_hasta = DateEntry(filtros_frame, width=12, background=c['azul'], foreground=c['boton_fg'], borderwidth=2, date_pattern='yyyy-mm-dd')
        self.fecha_hasta.pack(side="left", padx=2)

        # Búsqueda por texto
        tk.Label(filtros_frame, text="Buscar:", font=("Arial", 10), bg=c['bg'], fg=c['texto']).pack(side="left", padx=(10,0))
        self.busqueda = tk.Entry(filtros_frame, width=20, bg=c['panel'], fg=c['texto'], insertbackground=c['texto'])
        self.busqueda.pack(side="left", padx=2)

        # Botón de filtrar
        button_font = tkfont.Font(family="Verdana", size=9, weight="bold")
        filtrar_btn = tk.Button(
            filtros_frame, 
            text="🔍 FILTRAR", 
            bg=c['azul'], 
            fg=c['boton_fg'],
            font=button_font,
            relief="raised",
            bd=2,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self._cargar_ventas
        )
        filtrar_btn.pack(side="left", padx=10)

        # Frame principal
        main_frame = tk.Frame(self, bg=c['bg'])
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # Tabla de ventas
        columnas = ("id", "fecha", "total", "productos")
        self.tree = ttk.Treeview(main_frame, columns=columnas, show="headings", height=14)
        self.tree.heading("id", text="ID")
        self.tree.heading("fecha", text="Fecha/Hora")
        self.tree.heading("total", text="Total")
        self.tree.heading("productos", text="Productos (resumen)")
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("fecha", width=150, anchor="center")
        self.tree.column("total", width=80, anchor="center")
        self.tree.column("productos", width=450, anchor="w")

        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview",
            background=c['treeview_bg'],
            foreground=c['treeview_fg'],
            fieldbackground=c['treeview_bg'],
            rowheight=25,
            font=("Arial", 10)
        )
        style.configure("Treeview.Heading",
            background=c['treeview_heading_bg'],
            foreground=c['treeview_heading_fg'],
            font=("Arial", 10, "bold")
        )
        style.map("Treeview",
            background=[('selected', c['treeview_selected_bg'])],
            foreground=[('selected', c['treeview_selected_fg'])]
        )

        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Eventos
        self.tree.bind("<Double-1>", self._ver_detalle)
        self.tree.bind("<Delete>", self._eliminar_venta)

        # Frame de botones
        botones_frame = tk.Frame(self, bg=c['bg'])
        botones_frame.pack(fill="x", padx=15, pady=10)

        # Botón eliminar
        self.eliminar_btn = tk.Button(
            botones_frame,
            text="❌ ELIMINAR VENTA",
            bg=c['rojo'],
            fg=c['boton_fg'],
            font=button_font,
            relief="raised",
            bd=2,
            padx=10,
            pady=7,
            cursor="hand2",
            command=lambda: self._eliminar_venta(None)
        )
        self.eliminar_btn.pack(side="left", padx=5)

        # Botón generar PDF
        self.pdf_btn = tk.Button(
            botones_frame,
            text="📄 GENERAR PDF",
            bg=c['verde'],
            fg=c['boton_fg'],
            font=button_font,
            relief="raised",
            bd=2,
            padx=10,
            pady=7,
            cursor="hand2",
            command=self._generar_pdf
        )
        self.pdf_btn.pack(side="left", padx=5)

        # Efectos hover
        self.eliminar_btn.bind("<Enter>", lambda e: self._hover_enter(self.eliminar_btn, c['rojo']))
        self.eliminar_btn.bind("<Leave>", lambda e: self._hover_leave(self.eliminar_btn, c['rojo']))
        self.pdf_btn.bind("<Enter>", lambda e: self._hover_enter(self.pdf_btn, c['verde']))
        self.pdf_btn.bind("<Leave>", lambda e: self._hover_leave(self.pdf_btn, c['verde']))

        # Cargar ventas iniciales
        self._cargar_ventas()

    def _hover_enter(self, button, color):
        button.config(bg=color)

    def _hover_leave(self, button, color):
        button.config(bg=color)

    def _cargar_ventas(self):
        """Carga las ventas según los filtros seleccionados"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Obtener fechas del calendario
        desde = self.fecha_desde.get_date().strftime("%Y-%m-%d")
        hasta = self.fecha_hasta.get_date().strftime("%Y-%m-%d")
        busqueda = self.busqueda.get().strip().lower()

        try:
            ventas = self.db.obtener_ventas_por_fecha(desde + " 00:00:00", hasta + " 23:59:59")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar ventas: {str(e)}")
            return

        for venta in ventas:
            venta_id, fecha, total = venta
            detalle = self.db.obtener_detalle_venta(venta_id)
            resumen = ", ".join(f"{nombre} x{cantidad}" for _, nombre, cantidad, _ in detalle)
            
            if busqueda and busqueda not in resumen.lower():
                continue
                
            self.tree.insert("", tk.END, values=(venta_id, fecha, f"${total:.2f}", resumen))

    def _ver_detalle(self, event):
        """Muestra el detalle de la venta seleccionada"""
        item = self.tree.selection()
        if not item:
            return
        venta_id = self.tree.item(item[0])["values"][0]
        mostrar_detalle_venta(self, self.db, venta_id)

    def _eliminar_venta(self, event):
        """Elimina la venta seleccionada"""
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una venta para eliminar.")
            return

        venta_id = self.tree.item(item[0])["values"][0]
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que deseas eliminar esta venta?"):
            try:
                self.db.eliminar_venta(venta_id)
                self._cargar_ventas()  # Recargar la lista
                messagebox.showinfo("Éxito", "Venta eliminada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar la venta: {str(e)}")

    def _generar_pdf(self):
        """Genera un PDF con las ventas filtradas"""
        # Obtener las ventas filtradas
        desde = self.fecha_desde.get_date().strftime("%Y-%m-%d")
        hasta = self.fecha_hasta.get_date().strftime("%Y-%m-%d")
        busqueda = self.busqueda.get().strip().lower()

        try:
            ventas = self.db.obtener_ventas_por_fecha(desde + " 00:00:00", hasta + " 23:59:59")
        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener ventas: {str(e)}")
            return

        # Filtrar por búsqueda si existe
        ventas_filtradas = []
        for venta in ventas:
            venta_id, fecha, total = venta
            detalle = self.db.obtener_detalle_venta(venta_id)
            resumen = ", ".join(f"{nombre} x{cantidad}" for _, nombre, cantidad, _ in detalle)
            if not busqueda or busqueda in resumen.lower():
                ventas_filtradas.append((venta_id, fecha, total, detalle))

        if not ventas_filtradas:
            messagebox.showinfo("Información", "No hay ventas para generar el reporte.")
            return

        # Pedir ubicación para guardar el PDF
        archivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Guardar reporte como"
        )
        
        if not archivo:
            return

        try:
            # Crear el PDF
            doc = SimpleDocTemplate(archivo, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30
            )
            elements.append(Paragraph("REPORTE DE VENTAS", title_style))
            elements.append(Spacer(1, 12))

            # Información del filtro
            filter_style = ParagraphStyle(
                'FilterStyle',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.gray
            )
            elements.append(Paragraph(f"Período: {desde} al {hasta}", filter_style))
            if busqueda:
                elements.append(Paragraph(f"Búsqueda: {busqueda}", filter_style))
            elements.append(Spacer(1, 20))

            # Tabla de ventas
            data = [["ID", "Fecha", "Total", "Productos"]]
            for venta_id, fecha, total, detalle in ventas_filtradas:
                resumen = ", ".join(f"{nombre} x{cantidad}" for _, nombre, cantidad, _ in detalle)
                data.append([str(venta_id), fecha, f"${total:.2f}", resumen])

            # Crear tabla
            table = Table(data, colWidths=[1*inch, 2*inch, 1*inch, 3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (3, 0), (3, -1), 'LEFT'),
            ]))
            elements.append(table)

            # Pie de página
            elements.append(Spacer(1, 20))
            footer_style = ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.gray,
                alignment=1
            )
            elements.append(Paragraph(f"Generado el {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))

            # Generar PDF
            doc.build(elements)
            messagebox.showinfo("Éxito", "Reporte generado correctamente.")
            
            # Abrir el PDF
            import os
            os.startfile(archivo)

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar el PDF: {str(e)}")

def mostrar_detalle_venta(parent, database, venta_id):
    """Muestra una ventana con el detalle de la venta"""
    colores = getattr(parent.master, 'colores', {
        'bg': '#f5f5f5', 'panel': '#fff', 'texto': '#222', 'boton': '#3498db', 'boton_fg': '#fff',
        'borde': '#e9ecef', 'azul': '#3498db', 'verde': '#27ae60', 'rojo': '#e74c3c', 'gris': '#e9ecef',
        'treeview_bg': '#fff', 'treeview_fg': '#222', 'treeview_heading_bg': '#e9ecef', 'treeview_heading_fg': '#222',
        'treeview_selected_bg': '#3498db', 'treeview_selected_fg': '#fff',
    })
    detalle = database.obtener_detalle_venta(venta_id)
    win = tk.Toplevel(parent)
    win.title(f"Detalle de venta #{venta_id}")
    win.geometry("500x350")
    win.configure(bg=colores['bg'])
    # Título
    titulo_frame = tk.Frame(win, bg=colores['azul'], height=40)
    titulo_frame.pack(fill="x")
    titulo_frame.pack_propagate(False)
    tk.Label(titulo_frame, text=f"DETALLE DE VENTA #{venta_id}", font=("Arial", 14, "bold"), bg=colores['azul'], fg=colores['boton_fg']).pack(pady=8)
    # Frame principal
    frame = tk.Frame(win, bg=colores['panel'])
    frame.pack(fill="both", expand=True, padx=15, pady=10)
    # Tabla de detalle
    cols = ("Código", "Nombre", "Cantidad", "Precio unitario")
    tree = ttk.Treeview(frame, columns=cols, show="headings", height=10)
    for col in cols:
        tree.heading(col, text=col)
    tree.column("Código", width=80, anchor="center")
    tree.column("Nombre", width=180, anchor="w")
    tree.column("Cantidad", width=80, anchor="center")
    tree.column("Precio unitario", width=120, anchor="center")
    # Estilos para Treeview
    style = ttk.Style()
    style.theme_use('default')
    style.configure("Treeview",
        background=colores['treeview_bg'],
        foreground=colores['treeview_fg'],
        fieldbackground=colores['treeview_bg'],
        rowheight=25,
        font=("Arial", 10)
    )
    style.configure("Treeview.Heading",
        background=colores['treeview_heading_bg'],
        foreground=colores['treeview_heading_fg'],
        font=("Arial", 10, "bold")
    )
    style.map("Treeview",
        background=[('selected', colores['treeview_selected_bg'])],
        foreground=[('selected', colores['treeview_selected_fg'])]
    )
    # Insertar datos
    for codigo, nombre, cantidad, precio_unitario in detalle:
        tree.insert("", tk.END, values=(codigo, nombre, cantidad, f"${precio_unitario:.2f}"))
    tree.pack(fill="both", expand=True)
    # Botón cerrar
    button_font = tkfont.Font(family="Verdana", size=10, weight="bold")
    cerrar_btn = tk.Button(
        win, 
        text="CERRAR", 
        bg=colores['rojo'], 
        fg=colores['boton_fg'],
        font=button_font,
        relief="raised",
        bd=2,
        padx=15,
        pady=5,
        cursor="hand2",
        command=win.destroy
    )
    cerrar_btn.pack(pady=10)
    cerrar_btn.bind("<Enter>", lambda e: cerrar_btn.config(bg=colores['rojo']))
    cerrar_btn.bind("<Leave>", lambda e: cerrar_btn.config(bg=colores['rojo'])) 