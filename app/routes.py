import os
import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, g
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

bp = Blueprint('rutas', __name__)

def get_conn():
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        import psycopg2
        conn = psycopg2.connect(db_url)
        conn.autocommit = False
        return conn, True  # True = es postgres
    else:
        conn = sqlite3.connect('app/eco_reto.db')
        conn.row_factory = sqlite3.Row
        return conn, False

def qmark_to_psycopg(query, is_pg):
    if is_pg:
        return query.replace('?', '%s')
    return query

@bp.route('/')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('rutas.login'))
    conn, is_pg = get_conn()
    cur = conn.cursor()
    if is_pg:
        cur.execute("SELECT * FROM acciones WHERE usuario_id = %s ORDER BY fecha DESC", (session['usuario_id'],))
    else:
        cur.execute("SELECT * FROM acciones WHERE usuario_id = ? ORDER BY fecha DESC", (session['usuario_id'],))
    acciones = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', acciones=acciones)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        contrasena = request.form.get('contrasena', '').strip()
        conn, is_pg = get_conn()
        cur = conn.cursor()
        cur.execute(qmark_to_psycopg("SELECT * FROM usuarios WHERE usuario = ?", is_pg), (usuario,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and check_password_hash(user[2] if not is_pg else user[2], contrasena):
            session['usuario_id'] = user[0] if not is_pg else user[0]
            session['usuario'] = usuario
            return redirect(url_for('rutas.index'))
        flash('Usuario o contraseña incorrectos', 'error')
    return render_template('login.html')

@bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        contrasena = request.form.get('contrasena', '').strip()
        if not usuario or not contrasena:
            flash('Rellena todos los datos', 'error')
            return render_template('registro.html')
        conn, is_pg = get_conn()
        cur = conn.cursor()
        try:
            hashed = generate_password_hash(contrasena)
            cur.execute(qmark_to_psycopg("INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)", is_pg), (usuario, hashed))
            conn.commit()
            flash('Usuario creado, ya puedes iniciar sesión', 'ok')
            return redirect(url_for('rutas.login'))
        except Exception as e:
            conn.rollback()
            flash('Ese usuario ya existe', 'error')
        finally:
            cur.close()
            conn.close()
    return render_template('registro.html')

@bp.route('/nueva', methods=['GET', 'POST'])
def nueva():
    if 'usuario_id' not in session:
        return redirect(url_for('rutas.login'))
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        tipo = request.form.get('tipo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        impacto = request.form.get('impacto', '').strip()
        unidad = request.form.get('unidad', '').strip()
        fecha = request.form.get('fecha') or str(date.today())
        if not titulo or not descripcion:
            flash('Rellena los datos del formulario', 'error')
            return render_template('formulario.html')
        conn, is_pg = get_conn()
        cur = conn.cursor()
        cur.execute(qmark_to_psycopg("INSERT INTO acciones (titulo, tipo, descripcion, fecha, impacto, unidad, usuario_id) VALUES (?, ?, ?, ?, ?, ?, ?)", is_pg), (titulo, tipo, descripcion, fecha, impacto, unidad, session['usuario_id']))
        conn.commit()
        cur.close()
        conn.close()
        flash('Acción guardada', 'ok')
        return redirect(url_for('rutas.index'))
    return render_template('formulario.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('rutas.login'))

# Deja tus rutas de editar, eliminar y detalle igual pero usando get_conn() y qmark_to_psycopg
@bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    conn, is_pg = get_conn()
    cur = conn.cursor()
    cur.execute(qmark_to_psycopg("DELETE FROM acciones WHERE id = ? AND usuario_id = ?", is_pg), (id, session['usuario_id']))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('rutas.index'))

@bp.route('/detalle/<int:id>')
def detalle(id):
    conn, is_pg = get_conn()
    cur = conn.cursor()
    cur.execute(qmark_to_psycopg("SELECT * FROM acciones WHERE id = ? AND usuario_id = ?", is_pg), (id, session['usuario_id']))
    accion = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('detalle.html', accion=accion)
