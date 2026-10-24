import os
import sqlite3
from flask import Flask

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'eco-reto-clave-local')
    app.config['DATABASE'] = os.path.join(app.instance_path, 'eco_reto.db')
    os.makedirs(app.instance_path, exist_ok=True)

    db_url = os.getenv("DATABASE_URL")

    if db_url:
        try:
            import psycopg2
            with psycopg2.connect(db_url) as conexion:
                cur = conexion.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS acciones (
                        id SERIAL PRIMARY KEY,
                        titulo TEXT NOT NULL,
                        categoria TEXT NOT NULL,
                        descripcion TEXT NOT NULL,
                        propuesta_por TEXT
                    );
                """)
                conexion.commit()
        except Exception as e:
            print(f"Error conectando a Neon: {e}")
    else:
        with sqlite3.connect(app.config['DATABASE']) as conexion:
            conexion.execute("CREATE TABLE IF NOT EXISTS acciones (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, categoria TEXT, descripcion TEXT, propuesta_por TEXT);")
            conexion.commit()

    from app.routes import rutas
    app.register_blueprint(rutas)
    return app
