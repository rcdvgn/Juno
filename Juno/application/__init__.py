from flask import Flask
import mysql.connector

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'chave_segura'
    
    from .views import views

    app.register_blueprint(views, url_prefix = '/')


    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="zR6FFQyoa6i6"
    )

    db = mydb.cursor()

    db.execute("CREATE DATABASE IF NOT EXISTS juno")

    db.execute("CREATE TABLE IF NOT EXISTS juno.usuarios (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(50), email VARCHAR(50), senha VARCHAR(150))")
    
    # lembrar, ano nao pode ser INT pois durante seu processo de chacagem de existencia ha de transformar o input em int para checar compatibilidade no banco, caso input nao seja numerico tal conversao resultaria em erro
    db.execute("CREATE TABLE IF NOT EXISTS juno.consultas (uid INT, criacao VARCHAR(50), ano VARCHAR(10), populacao INT, img VARCHAR(100), FOREIGN KEY (uid) REFERENCES usuarios(id) ON DELETE CASCADE)")

    return app


