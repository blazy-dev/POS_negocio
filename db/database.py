import sqlite3
import datetime

DB_NAME = "pos.db"

def conectar():
    """Conecta a la base de datos y retorna el objeto conexión y cursor."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    return conn, cursor

def crear_tablas():
    """Crea las tablas necesarias si no existen."""
    conn, cursor = conectar()
    
    # Primero verificamos si la tabla ya existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos'")
    tabla_existe = cursor.fetchone()
    
    if not tabla_existe:
        # Si la tabla no existe, la creamos con los campos de precios separados
        cursor.execute("""
            CREATE TABLE productos (
                codigo TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                precio_compra REAL NOT NULL,
                precio_venta REAL NOT NULL,
                stock INTEGER NOT NULL,
                categoria TEXT DEFAULT 'General'
            )
        """)
    else:
        # Si la tabla ya existe, verificamos si tiene las columnas actualizadas
        cursor.execute("PRAGMA table_info(productos)")
        columnas = cursor.fetchall()
        nombres_columnas = [col[1] for col in columnas]
        
        tiene_precio_compra = 'precio_compra' in nombres_columnas
        tiene_precio_venta = 'precio_venta' in nombres_columnas
        tiene_precio = 'precio' in nombres_columnas
        tiene_categoria = 'categoria' in nombres_columnas
        
        # Si la tabla tiene la estructura antigua (un solo precio), hay que migrarla
        if tiene_precio and not (tiene_precio_compra and tiene_precio_venta):
            # Creamos tabla temporal con nueva estructura
            cursor.execute("""
                CREATE TABLE productos_temp (
                    codigo TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    precio_compra REAL NOT NULL,
                    precio_venta REAL NOT NULL,
                    stock INTEGER NOT NULL,
                    categoria TEXT DEFAULT 'General'
                )
            """)
            
            # Copiamos los datos existentes (precio se usa tanto para compra como venta inicialmente)
            if tiene_categoria:
                cursor.execute("""
                    INSERT INTO productos_temp (codigo, nombre, precio_compra, precio_venta, stock, categoria)
                    SELECT codigo, nombre, precio, precio, stock, categoria FROM productos
                """)
            else:
                cursor.execute("""
                    INSERT INTO productos_temp (codigo, nombre, precio_compra, precio_venta, stock, categoria)
                    SELECT codigo, nombre, precio, precio, stock, 'General' FROM productos
                """)
            
            # Eliminamos tabla original y renombramos la temporal
            cursor.execute("DROP TABLE productos")
            cursor.execute("ALTER TABLE productos_temp RENAME TO productos")
        
        # Si no tiene la columna 'categoria', la añadimos
        elif not tiene_categoria:
            cursor.execute("ALTER TABLE productos ADD COLUMN categoria TEXT DEFAULT 'General'")
    
    # Tabla ventas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ventas'")
    if not cursor.fetchone():
        cursor.execute("""
            CREATE TABLE ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                total REAL NOT NULL
            )
        """)
    
    # Tabla detalle_ventas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='detalle_ventas'")
    if not cursor.fetchone():
        cursor.execute("""
            CREATE TABLE detalle_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                codigo TEXT NOT NULL,
                nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id)
            )
        """)
    
    conn.commit()
    conn.close()

def buscar_producto(codigo):
    """Busca un producto por su código de barras."""
    conn, cursor = conectar()
    cursor.execute("SELECT nombre, precio_compra, precio_venta, stock, categoria FROM productos WHERE codigo = ?", (codigo,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado

def agregar_producto(codigo, nombre, precio_compra, precio_venta, stock, categoria='General'):
    """Agrega un nuevo producto a la base de datos."""
    conn, cursor = conectar()
    cursor.execute("INSERT INTO productos VALUES (?, ?, ?, ?, ?, ?)", 
                   (codigo, nombre, precio_compra, precio_venta, stock, categoria))
    conn.commit()
    conn.close()

def actualizar_producto(codigo, nombre=None, precio_compra=None, precio_venta=None, stock=None, categoria=None):
    """Actualiza un producto existente en la base de datos."""
    conn, cursor = conectar()
    
    # Primero obtenemos los datos actuales del producto
    cursor.execute("SELECT nombre, precio_compra, precio_venta, stock, categoria FROM productos WHERE codigo = ?", (codigo,))
    resultado = cursor.fetchone()
    
    if not resultado:
        conn.close()
        raise ValueError(f"No existe un producto con el código {codigo}")
    
    nombre_actual, precio_compra_actual, precio_venta_actual, stock_actual, categoria_actual = resultado
    
    # Actualizamos solo los campos que se han especificado
    nuevo_nombre = nombre if nombre is not None else nombre_actual
    nuevo_precio_compra = precio_compra if precio_compra is not None else precio_compra_actual
    nuevo_precio_venta = precio_venta if precio_venta is not None else precio_venta_actual
    nuevo_stock = stock if stock is not None else stock_actual
    nueva_categoria = categoria if categoria is not None else categoria_actual
    
    cursor.execute("""
        UPDATE productos 
        SET nombre = ?, precio_compra = ?, precio_venta = ?, stock = ?, categoria = ? 
        WHERE codigo = ?
    """, (nuevo_nombre, nuevo_precio_compra, nuevo_precio_venta, nuevo_stock, nueva_categoria, codigo))
    
    conn.commit()
    conn.close()

def actualizar_stock(codigo, cantidad):
    """Descuenta stock tras una venta."""
    conn, cursor = conectar()
    cursor.execute("UPDATE productos SET stock = stock - ? WHERE codigo = ?", (cantidad, codigo))
    conn.commit()
    conn.close()

def obtener_reporte():
    """Devuelve todos los productos para el reporte."""
    conn, cursor = conectar()
    cursor.execute("SELECT codigo, nombre, precio_compra, precio_venta, stock, categoria FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return productos

def obtener_categorias():
    """Devuelve todas las categorías únicas existentes."""
    conn, cursor = conectar()
    cursor.execute("SELECT DISTINCT categoria FROM productos ORDER BY categoria")
    categorias = [categoria[0] for categoria in cursor.fetchall()]
    conn.close()
    return categorias

def obtener_productos_por_categoria(categoria):
    """Devuelve los productos filtrados por categoría."""
    conn, cursor = conectar()
    if categoria == "Todas":
        cursor.execute("SELECT codigo, nombre, precio_compra, precio_venta, stock, categoria FROM productos")
    else:
        cursor.execute("SELECT codigo, nombre, precio_compra, precio_venta, stock, categoria FROM productos WHERE categoria = ?", (categoria,))
    productos = cursor.fetchall()
    conn.close()
    return productos

def guardar_venta(total, productos):
    """
    Guarda una venta y su detalle.
    productos: lista de tuplas (codigo, nombre, cantidad, precio_unitario)
    """
    conn, cursor = conectar()
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO ventas (fecha, total) VALUES (?, ?)", (fecha, total))
    venta_id = cursor.lastrowid
    for codigo, nombre, cantidad, precio_unitario in productos:
        cursor.execute("""
            INSERT INTO detalle_ventas (venta_id, codigo, nombre, cantidad, precio_unitario)
            VALUES (?, ?, ?, ?, ?)
        """, (venta_id, codigo, nombre, cantidad, precio_unitario))
    conn.commit()
    conn.close()
    return venta_id

def obtener_ventas():
    """Devuelve lista de ventas: (id, fecha, total)"""
    conn, cursor = conectar()
    cursor.execute("SELECT id, fecha, total FROM ventas ORDER BY fecha DESC")
    ventas = cursor.fetchall()
    conn.close()
    return ventas

def obtener_detalle_venta(venta_id):
    """Devuelve el detalle de una venta: (codigo, nombre, cantidad, precio_unitario)"""
    conn, cursor = conectar()
    cursor.execute("""
        SELECT codigo, nombre, cantidad, precio_unitario
        FROM detalle_ventas WHERE venta_id = ?
    """, (venta_id,))
    detalle = cursor.fetchall()
    conn.close()
    return detalle

def obtener_ventas_por_fecha(fecha_inicio, fecha_fin):
    """Devuelve ventas entre dos fechas (inclusive)"""
    conn, cursor = conectar()
    cursor.execute("SELECT id, fecha, total FROM ventas WHERE fecha BETWEEN ? AND ? ORDER BY fecha DESC", (fecha_inicio, fecha_fin))
    ventas = cursor.fetchall()
    conn.close()
    return ventas

def eliminar_venta(venta_id):
    """Elimina una venta y su detalle de la base de datos."""
    conn, cursor = conectar()
    try:
        # Primero eliminamos el detalle de la venta
        cursor.execute("DELETE FROM detalle_ventas WHERE venta_id = ?", (venta_id,))
        # Luego eliminamos la venta
        cursor.execute("DELETE FROM ventas WHERE id = ?", (venta_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def eliminar_producto(codigo):
    """Elimina un producto de la base de datos."""
    conn, cursor = conectar()
    try:
        # Verificar si el producto existe
        cursor.execute("SELECT codigo FROM productos WHERE codigo = ?", (codigo,))
        if not cursor.fetchone():
            raise ValueError(f"No existe un producto con el código {codigo}")
            
        # Eliminar el producto
        cursor.execute("DELETE FROM productos WHERE codigo = ?", (codigo,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def actualizar_codigo_producto(codigo_actual, nuevo_codigo):
    """Actualiza el código de un producto en cascada (productos y detalle_ventas)."""
    conn, cursor = conectar()
    try:
        # Verificar que el nuevo código no exista
        cursor.execute("SELECT codigo FROM productos WHERE codigo = ?", (nuevo_codigo,))
        if cursor.fetchone():
            raise ValueError(f"Ya existe un producto con el código {nuevo_codigo}")
        # Actualizar en productos
        cursor.execute("UPDATE productos SET codigo = ? WHERE codigo = ?", (nuevo_codigo, codigo_actual))
        # Actualizar en detalle_ventas
        cursor.execute("UPDATE detalle_ventas SET codigo = ? WHERE codigo = ?", (nuevo_codigo, codigo_actual))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
