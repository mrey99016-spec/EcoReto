from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
from datetime import date

bp = Blueprint('bp', __name__)

def get_db():
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        import psycopg2
        conn = psycopg2.connect(db_url)
        return conn, True
    conn = sqlite3.connect('app/eco_reto.db')
    conn.row_factory = sqlite3.Row
    return conn, False

def q(query, is_pg):
    return query.replace('?', '%s') if is_pg else query

def init_tables():
    conn, is_pg = get_db()
    cur = conn.cursor()
    if is_pg:
        cur.execute("CREATE TABLE IF NOT EXISTS usuarios (id SERIAL PRIMARY KEY, usuario TEXT UNIQUE NOT NULL, contrasena TEXT NOT NULL)")
        cur.execute("CREATE TABLE IF NOT EXISTS acciones (id SERIAL PRIMARY KEY, titulo TEXT NOT NULL, tipo TEXT NOT NULL, descripcion TEXT NOT NULL, fecha DATE NOT NULL, impacto TEXT NOT NULL, unidad TEXT NOT NULL, usuario_id INTEGER)")
    else:
        cur.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT UNIQUE NOT NULL, contrasena TEXT NOT NULL)")
        cur.execute("CREATE TABLE IF NOT EXISTS acciones (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT NOT NULL, tipo TEXT NOT NULL, descripcion TEXT NOT NULL, fecha DATE NOT NULL, impacto TEXT NOT NULL, unidad TEXT NOT NULL, usuario_id INTEGER)")
    conn.commit()
    cur.close()
    conn.close()

init_tables()

@bp.route('/')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('bp.login'))
    conn, is_pg = get_db()
    cur = conn.cursor()
    cur.execute(q("SELECT * FROM acciones WHERE usuario_id = ? ORDER BY fecha DESC", is_pg), (session['usuario_id'],))
    acciones = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', acciones=acciones)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        conn, is_pg = get_db()
        cur = conn.cursor()
        cur.execute(q("SELECT * FROM usuarios WHERE usuario = ?", is_pg), (usuario,))
        u = cur.fetchone()
        cur.close()
        conn.close()
        if u and check_password_hash(u[2], contrasena):
            session['usuario_id'] = u[0]
            session['usuario'] = u[1]
            return redirect(url_for('bp.index'))
        flash('Usuario o contraseña mal')
    return render_template('login.html')

@bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        conn, is_pg = get_db()
        cur = conn.cursor()
        try:
            cur.execute(q("INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)", is_pg), (usuario, generate_password_hash(contrasena)))
            conn.commit()
            return redirect(url_for('bp.login'))
        except:
            conn.rollback()
            flash('Usuario ya existe')
        finally:
            cur.close()
            conn.close()
    return render_template('registro.html')

@bp.route('/nueva', methods=['GET', 'POST'])
def nueva():
    if 'usuario_id' not in session:
        return redirect(url_for('bp.login'))
    if request.method == 'POST':
        conn, is_pg = get_db()
        cur = conn.cursor()
        cur.execute(q("INSERT INTO acciones (titulo, tipo, descripcion, fecha, impacto, unidad, usuario_id) VALUES (?, ?, ?, ?, ?, ?, ?)", is_pg), (request.form['titulo'], request.form['tipo'], request.form['descripcion'], request.form['fecha'], request.form['impacto'], request.form['unidad'], session['usuario_id']))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('bp.index'))
    return render_template('formulario.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('bp.login'))

@bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    conn, is_pg = get_db()
    cur = conn.cursor()
    cur.execute(q("DELETE FROM acciones WHERE id = ? AND usuario_id = ?", is_pg), (id, session['usuario_id']))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('bp.index'))

@bp.route('/detalle/<int:id>')
def detalle(id):
    conn, is_pg = get_db()
    cur = conn.cursor()
    cur.execute(q("SELECT * FROM acciones WHERE id = ? AND usuario_id = ?", is_pg), (id, session['usuario_id']))
    accion = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('detalle.html', accion=accion)
