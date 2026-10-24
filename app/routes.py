import os
from flask import Blueprint, request, redirect, url_for, flash, current_app

rutas = Blueprint('rutas', __name__)

def get_conexion():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        import psycopg2
        conn = psycopg2.connect(db_url)
        return conn, True
    else:
        import sqlite3
        conn = sqlite3.connect(current_app.config['DATABASE'])
        return conn, False

@rutas.route('/')
def index():
    try:
        conn, es_postgres = get_conexion()
        cur = conn.cursor()
        cur.execute("SELECT id, titulo, categoria, descripcion, propuesta_por FROM acciones ORDER BY id DESC")
        acciones = cur.fetchall()
        conn.close()
        # Si tienes templates, descomenta la siguiente línea:
        # return render_template('index.html', acciones=acciones)
        html = "<h1>EcoReto - Acciones Guardadas en Neon</h1><a href='/nueva'>+ Nueva accion</a><hr>"
        for a in acciones:
            html += f"<div><b>{a[1]}</b> ({a[2]}) - {a[3]} <i>por {a[4]}</i> <form method='POST' action='/eliminar/{a[0]}' style='display:inline'><button>Eliminar</button></form></div><hr>"
        return html
    except Exception as e:
        return f"Error: {e} - Ve a Neon y crea la tabla acciones"

@rutas.route('/nueva', methods=['GET', 'POST'])
def nueva():
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        categoria = request.form.get('categoria', 'General').strip()
        descripcion = request.form.get('descripcion', '').strip()
        propuesta_por = request.form.get('propuesta_por', 'Anonimo').strip()

        conn, es_postgres = get_conexion()
        cur = conn.cursor()
        if es_postgres:
            cur.execute("INSERT INTO acciones (titulo, categoria, descripcion, propuesta_por) VALUES (%s, %s, %s, %s)", (titulo, categoria, descripcion, propuesta_por))
        else:
            cur.execute("INSERT INTO acciones (titulo, categoria, descripcion, propuesta_por) VALUES (?, ?, ?, ?)", (titulo, categoria, descripcion, propuesta_por))
        conn.commit()
        conn.close()
        return redirect(url_for('rutas.index'))

    return """
    <h2>Nueva Accion Ecologica</h2>
    <form method='POST'>
      Titulo: <input name='titulo' required><br>
      Categoria: <input name='categoria' value='Reciclaje'><br>
      Descripcion: <textarea name='descripcion' required></textarea><br>
      Propuesta por: <input name='propuesta_por'><br>
      <button>Guardar en Neon</button>
    </form>
    <a href='/'>Volver</a>
    """

@rutas.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    conn, es_postgres = get_conexion()
    cur = conn.cursor()
    if es_postgres:
        cur.execute("DELETE FROM acciones WHERE id = %s", (id,))
    else:
        cur.execute("DELETE FROM acciones WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('rutas.index'))
