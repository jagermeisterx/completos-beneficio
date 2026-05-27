import sqlite3
import os
from datetime import datetime
from pathlib import Path

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.getenv("DB_PATH", os.path.join(_PROJECT_ROOT, "data", "completada.db"))
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin123")

PRODUCTOS_INICIALES = [
    ("Pan Copihue (a granel)", 400, "producto"),
    ("Salchichas", 400, "producto"),
    ("Mayonesa (Kg)", 4, "producto"),
    ("Mostaza (Kg)", 3, "producto"),
    ("Ketchup (Kg)", 4, "producto"),
    ("Palta (Kg)", 25, "producto"),
    ("Tomate (Kg)", 20, "producto"),
    ("Vasos (Mangas 50 un. 200cc)", 10, "producto"),
    ("Bebidas 3L", 25, "producto"),
    ("Jugo (Botellas)", 10, "producto"),
    ("Sal (Kg)", 1, "producto"),
    ("Ají en pasta (Bolsita)", 1, "producto"),
    ("Dinero ($)", 0, "dinero"),
]


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            cantidad_requerida INTEGER NOT NULL DEFAULT 0,
            cantidad_donada INTEGER NOT NULL DEFAULT 0,
            tipo TEXT NOT NULL DEFAULT 'producto',
            evento_cerrado INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS donaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT NOT NULL,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        );
    """)

    cur = conn.execute("SELECT COUNT(*) FROM productos")
    count = cur.fetchone()[0]

    if count == 0:
        for nombre, cantidad, tipo in PRODUCTOS_INICIALES:
            conn.execute(
                "INSERT INTO productos (nombre, cantidad_requerida, tipo) VALUES (?, ?, ?)",
                (nombre, cantidad, tipo),
            )
        conn.commit()

    conn.close()


def get_inventario():
    conn = get_connection()
    rows = conn.execute(
        """SELECT id, nombre, cantidad_requerida, cantidad_donada, tipo, evento_cerrado
           FROM productos ORDER BY id"""
    ).fetchall()
    conn.close()

    resultado = []
    for r in rows:
        faltante = max(0, r["cantidad_requerida"] - r["cantidad_donada"])
        resultado.append({
            "id": r["id"],
            "nombre": r["nombre"],
            "requerido": r["cantidad_requerida"],
            "donado": r["cantidad_donada"],
            "faltante": faltante,
            "tipo": r["tipo"],
            "completo": r["tipo"] == "producto" and faltante == 0,
            "evento_cerrado": bool(r["evento_cerrado"]),
        })
    return resultado


def get_inventario_publico():
    inventario = get_inventario()
    return [p for p in inventario if p["tipo"] == "producto"]


def crear_donacion(nombre, apellido, producto_id, cantidad):
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")

        producto = conn.execute(
            "SELECT * FROM productos WHERE id = ?", (producto_id,)
        ).fetchone()

        if not producto:
            conn.rollback()
            return {"error": "Producto no encontrado"}

        if producto["evento_cerrado"]:
            conn.rollback()
            return {"error": "El evento está cerrado, no se aceptan más donaciones"}

        if producto["tipo"] == "producto":
            faltante = producto["cantidad_requerida"] - producto["cantidad_donada"]
            if cantidad <= 0:
                conn.rollback()
                return {"error": "La cantidad debe ser mayor a cero"}
            if cantidad > faltante:
                conn.rollback()
                return {"error": f"La cantidad supera el faltante ({faltante})"}

        if cantidad <= 0:
            conn.rollback()
            return {"error": "La cantidad debe ser mayor a cero"}

        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "INSERT INTO donaciones (fecha_hora, nombre, apellido, producto_id, cantidad) VALUES (?, ?, ?, ?, ?)",
            (ahora, nombre.strip(), apellido.strip(), producto_id, cantidad),
        )

        conn.execute(
            "UPDATE productos SET cantidad_donada = cantidad_donada + ? WHERE id = ?",
            (cantidad, producto_id),
        )

        conn.commit()
        return {"ok": True, "mensaje": "Donación registrada exitosamente. ¡Gracias!"}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        conn.close()


def get_donaciones():
    conn = get_connection()
    rows = conn.execute(
        """SELECT d.id, d.fecha_hora, d.nombre, d.apellido,
                  p.nombre as producto_nombre, p.tipo as producto_tipo,
                  d.cantidad
           FROM donaciones d
           JOIN productos p ON d.producto_id = p.id
           ORDER BY d.fecha_hora DESC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_resumen_por_persona():
    conn = get_connection()
    rows = conn.execute(
        """SELECT d.nombre, d.apellido,
                  GROUP_CONCAT(
                      CASE WHEN p.tipo = 'dinero' THEN '$' || d.cantidad
                           ELSE d.cantidad || ' ' || p.nombre
                      END, ', '
                  ) as items,
                  SUM(CASE WHEN p.tipo = 'dinero' THEN d.cantidad ELSE 0 END) as total_dinero
           FROM donaciones d
           JOIN productos p ON d.producto_id = p.id
           GROUP BY d.nombre, d.apellido
           ORDER BY d.apellido, d.nombre"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_total_dinero():
    conn = get_connection()
    row = conn.execute(
        """SELECT SUM(cantidad) as total
           FROM donaciones d
           JOIN productos p ON d.producto_id = p.id
           WHERE p.tipo = 'dinero'"""
    ).fetchone()
    conn.close()
    return row["total"] or 0


def cerrar_evento():
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("UPDATE productos SET evento_cerrado = 1")
        conn.commit()
        return {"ok": True, "mensaje": "Evento cerrado exitosamente"}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        conn.close()
