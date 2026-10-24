import os
import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from datetime import date

rutas = Blueprint('rutas', __name__)

def get_conexion():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        import psycopg2
        return psycopg2.connect(db_url), True  # True = es postgres
    else:
        conn = sqlite3.connect(current_app.config['DATABASE'])
        return conn, False

@rutas.route('/')
def index():
    conn, es_postgres = get_conexion()
    cur = conn.cursor()
    if es_postgres:
        cur.execute("SELECT id, titulo, categoria, descripcion, propuesta_por FROM acciones ORDER BY id DESC")
    else:
        # por si en local aún tienes la tabla vieja, intenta con la nueva
        try:
            cur.execute("SELECT id, titulo, categoria, descripcion, propuesta_por FROM acciones ORDER BY id DESC")
        except:
            cur.execute("SELECT id, titulo, descripcion FROM acciones ORDER BY id DESC")
    acciones = cur.fetchall()
    conn.close()
    return render_template('index.html', acciones=acciones)

@rutas.route('/nueva', methods=['GET', 'POST'])
def nueva():
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        categoria = request.form.get('categoria', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        propuesta_por = request.form.get('propuesta_por', 'Anónimo').strip()

        if not titulo or not descripcion:
            flash("Falta título o descripción", "error")
            return redirect(url_for('rutas.nueva'))

        conn, es_postgres = get_conexion()
        cur = conn.cursor()
        if es_postgres:
            cur.execute(
                "INSERT INTO acciones (titulo, categoria, descripcion, propuesta_por) VALUES (%s, %s, %s, %s)",
                (titulo, categoria, descripcion, propuesta_por)
            )
        else:
            cur.execute(
                "INSERT INTO acciones (titulo, categoria, descripcion, propuesta_por) VALUES (?, ?, ?, ?)",
                (titulo, categoria, descripcion, propuesta_por)
            )
        conn.commit()
        conn.close()
        flash("¡Acción ecológica guardada!", "ok")
        return redirect(url_for('rutas.index'))

    return render_template('nueva.html')

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
