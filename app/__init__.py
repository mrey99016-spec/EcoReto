 import os
import sqlite3
from flask import Flask

def get_connection():
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        import psycopg2
        return psycopg2.connect(db_url)
    else:
        return sqlite3.connect('app/eco_reto.db')

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
    
    db_url = os.environ.get('DATABASE_URL')
    use_postgres = bool(db_url)

    if use_postgres:
        import psycopg2
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                usuario TEXT NOT NULL UNIQUE,
                contrasena TEXT NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS acciones (
                id SERIAL PRIMARY KEY,
                titulo TEXT NOT NULL,
                tipo TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                fecha DATE NOT NULL,
                impacto TEXT NOT NULL,
                unidad TEXT NOT NULL,
                usuario_id INTEGER REFERENCES usuarios(id)
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    else:
        with sqlite3.connect(app.config.get('DATABASE', 'app/eco_reto.db')) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, usuario TEXT NOT NULL UNIQUE, contrasena TEXT NOT NULL)")
            conn.execute("CREATE TABLE IF NOT EXISTS acciones (id INTEGER PRIMARY KEY, titulo TEXT NOT NULL, tipo TEXT NOT NULL, descripcion TEXT NOT NULL, fecha DATE NOT NULL, impacto TEXT NOT NULL, unidad TEXT NOT NULL, usuario_id INTEGER)")

    from app import routes
    app.register_blueprint(routes.bp) if hasattr(routes, 'bp') else None
    import app.routes

    return app
