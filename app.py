import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)

# Configurações
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limite

# Cria upload folder se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATABASE = 'promocoes.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute(''''
        CREATE TABLE IF NOT EXISTS promocoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco_atual REAL NOT NULL,
            preco_antigo REAL,
            imagem TEXT NOT NULL,
            link TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db()
    promos = conn.execute('SELECT * FROM promocoes ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('index.html', promocoes=promos)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        nome = request.form['nome']
        preco_atual = request.form['preco_atual']
        preco_antigo = request.form.get('preco_antigo') or None
        link = request.form['link']
        file = request.files['imagem']

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            conn = get_db()
            conn.execute(''''
                INSERT INTO promocoes (nome, preco_atual, preco_antigo, imagem, link)
                VALUES (?, ?, ?, ?, ?)
            ''', (nome, preco_atual, preco_antigo, filepath, link))
            conn.commit()
            conn.close()

            return redirect(url_for('admin'))

    return render_template('admin.html')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
