from flask import Flask, render_template, g, request, redirect, url_for, session, flash
from datetime import datetime
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'luxury_secret'

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATABASE = os.path.join(basedir, 'database', 'luxury_wheels.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    db = get_db()
    hoje = datetime.now().strftime('%Y-%m-%d')

    categoria = request.args.get('categoria')
    transmissao = request.args.get('transmissao')
    tipo = request.args.get('tipo')
    valor_max = request.args.get('valor_max', type=float)
    capacidade = request.args.get('capacidade')

    query = """
        SELECT * FROM veiculos
        WHERE disponivel = 1
        AND id NOT IN (
            SELECT veiculo_id FROM reservas
            WHERE DATE(data_fim) >= ?
            AND estado != 'Terminada'
        )
    """
    params = [hoje]

    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if transmissao:
        query += " AND transmissao = ?"
        params.append(transmissao)
    if tipo:
        query += " AND tipo LIKE ?"
        params.append(f"%{tipo}%")
    if valor_max is not None:
        query += " AND valor_diaria <= ?"
        params.append(valor_max)
    if capacidade:
        if capacidade == "1-4":
            query += " AND capacidade_pessoas <= 4"
        elif capacidade == "5-6":
            query += " AND capacidade_pessoas BETWEEN 5 AND 6"
        elif capacidade == "7+":
            query += " AND capacidade_pessoas >= 7"

    veiculos = db.execute(query, params).fetchall()
    return render_template('index.html', veiculos=veiculos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        db = get_db()
        cliente = db.execute("SELECT * FROM clientes WHERE email = ? AND senha = ?", (email, senha)).fetchone()

        if cliente:
            session['user'] = dict(cliente)
            flash('Login feito com sucesso!', 'success')
            return redirect(url_for('index'))
        flash('Email ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Sessão terminada.', 'info')
    return redirect(url_for('index'))

@app.route('/reserva/<int:veiculo_id>', methods=['GET', 'POST'])
def reserva(veiculo_id):
    if 'user' not in session:
        flash("Precisa de iniciar sessão para reservar.", "warning")
        return redirect(url_for('login'))

    db = get_db()
    veiculo = db.execute("SELECT * FROM veiculos WHERE id = ?", (veiculo_id,)).fetchone()
    formas_pagamento = db.execute("SELECT * FROM formas_pagamento").fetchall()

    if not veiculo:
        flash("Veículo não encontrado.", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']
        forma_pagamento_id = request.form['forma_pagamento_id']

        try:
            dt_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
            dt_fim = datetime.strptime(data_fim, '%Y-%m-%d')
            dias = (dt_fim - dt_inicio).days
            if dias <= 0:
                raise ValueError("Data inválida")
        except ValueError:
            flash("Datas inválidas.", "danger")
            return redirect(request.url)

        valor_total = dias * veiculo['valor_diaria']

        db.execute("""
            INSERT INTO reservas (cliente_id, veiculo_id, data_inicio, data_fim, estado, forma_pagamento_id, valor_total)
            VALUES (?, ?, ?, ?, 'Preparando Reserva', ?, ?)
        """, (session['user']['id'], veiculo_id, data_inicio, data_fim, forma_pagamento_id, valor_total))
        db.commit()

        flash(f"Reserva criada com sucesso! Total: {valor_total:.2f} €", "success")
        return redirect(url_for('index'))

    return render_template('reserva.html', veiculo=veiculo, formas_pagamento=formas_pagamento)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']

        db = get_db()
        existente = db.execute("SELECT * FROM clientes WHERE email = ?", (email,)).fetchone()
        if existente:
            flash("Este email já está registado.", "warning")
            return redirect(url_for('register'))

        db.execute("INSERT INTO clientes (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
        db.commit()

        flash("Registo efetuado com sucesso! Já pode iniciar sessão.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/minhas_reservas', methods=['GET', 'POST'])
def minhas_reservas():
    if 'user' not in session:
        flash("Precisa de iniciar sessão para ver suas reservas.", "warning")
        return redirect(url_for('login'))

    db = get_db()
    cliente_id = session['user']['id']

    if request.method == 'POST':
        reserva_id = request.form['reserva_id']

        if 'cancelar' in request.form:
            db.execute("DELETE FROM reservas WHERE id = ? AND cliente_id = ?", (reserva_id, cliente_id))
            db.commit()
            flash("Reserva cancelada com sucesso.", "info")

        elif 'atualizar' in request.form:
            nova_data_inicio = request.form['data_inicio']
            nova_data_fim = request.form['data_fim']
            db.execute("""
                UPDATE reservas SET data_inicio = ?, data_fim = ?
                WHERE id = ? AND cliente_id = ? AND DATE(data_inicio) > DATE('now')
            """, (nova_data_inicio, nova_data_fim, reserva_id, cliente_id))
            db.commit()
            flash("Reserva atualizada com sucesso.", "success")

    reservas = db.execute("""
        SELECT r.*, v.marca, v.modelo FROM reservas r
        JOIN veiculos v ON v.id = r.veiculo_id
        WHERE r.cliente_id = ?
        ORDER BY r.data_inicio DESC
    """, (cliente_id,)).fetchall()

    reservas = [dict(r) for r in reservas]
    for r in reservas:
        r['data_inicio'] = datetime.strptime(r['data_inicio'], "%Y-%m-%d").date()
        r['data_fim'] = datetime.strptime(r['data_fim'], "%Y-%m-%d").date()

    return render_template('minhas_reservas.html', reservas=reservas, current_date=datetime.now().date())

@app.context_processor
def inject_user():
    return dict(user=session.get('user'))

if __name__ == '__main__':
    app.run(debug=True)
