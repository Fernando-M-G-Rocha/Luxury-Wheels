from datetime import datetime, timedelta
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'luxury_wheels.db')

def conectar():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# Parte dos Veículos

def obter_veiculos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM veiculos ORDER BY id")
    veiculos = cursor.fetchall()
    conn.close()
    return veiculos

def adicionar_veiculo(dados):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO veiculos (
            marca, modelo, categoria, transmissao, tipo,
            capacidade_pessoas, valor_diaria, imagem,
            data_ultima_revisao, data_proxima_revisao,
            data_inspecao_obrigatoria, em_manutencao, disponivel, imagem
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)
    """, dados)
    conn.commit()
    conn.close()

def excluir_veiculo(veiculo_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM veiculos WHERE id = ?", (veiculo_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print("[ERRO] ao excluir veículo:", e)

def atualizar_veiculo(veiculo_id, dados):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE veiculos SET
            marca = ?, modelo = ?, categoria = ?, transmissao = ?, tipo = ?,
            capacidade_pessoas = ?, valor_diaria = ?,
            data_ultima_revisao = ?, data_proxima_revisao = ?,
            data_inspecao_obrigatoria = ?, em_manutencao = ?, disponivel = ?, imagem = ?
        WHERE id = ?
    """, dados + (veiculo_id,))
    conn.commit()
    conn.close()

def buscar_veiculos(filtro):
    conn = conectar()
    cursor = conn.cursor()
    consulta = """
        SELECT * FROM veiculos
        WHERE marca LIKE ? OR modelo LIKE ? OR categoria LIKE ?
    """
    like = f"%{filtro}%"
    cursor.execute(consulta, (like, like, like))
    veiculos = cursor.fetchall()
    conn.close()
    return veiculos

# Parte dos Clientes

def obter_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    conn.close()
    return clientes

def adicionar_cliente(dados):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)", dados)
    conn.commit()
    conn.close()

def atualizar_cliente(cliente_id, dados):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clientes
        SET nome = ?, email = ?, telefone = ?
        WHERE id = ?
    """, dados + (cliente_id,))
    conn.commit()
    conn.close()

def excluir_cliente(cliente_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
    conn.commit()
    conn.close()

def buscar_clientes(filtro):
    conn = conectar()
    cursor = conn.cursor()
    like = f"%{filtro}%"
    cursor.execute("""
        SELECT * FROM clientes
        WHERE nome LIKE ? OR email LIKE ?
    """, (like, like))
    clientes = cursor.fetchall()
    conn.close()
    return clientes

# Parte das Reservas

# FORMAS DE PAGAMENTO
def obter_formas_pagamento():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM formas_pagamento")
    dados = cursor.fetchall()
    conn.close()
    return dados

# VEÍCULOS DISPONÍVEIS
def obter_veiculos_disponiveis():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM veiculos
        WHERE disponivel = 1 AND em_manutencao = 0
    """)
    dados = cursor.fetchall()
    conn.close()
    return dados

# RESERVAS - LISTAGEM DETALHADA
def obter_reservas_detalhado():
    conn = conectar()
    cursor = conn.cursor()

    query = """
        SELECT r.id,  c.nome || ' (' || c.email || ')' AS cliente, v.marca || ' ' || v.modelo || ' (' || v.categoria || ')' AS veiculo, r.data_inicio, r.data_fim, r.valor_total, fp.descricao, r.estado
        FROM reservas r
        JOIN clientes c ON r.cliente_id = c.id
        JOIN veiculos v ON r.veiculo_id = v.id
        JOIN formas_pagamento fp ON r.forma_pagamento_id = fp.id
        ORDER BY r.id;
        """

    cursor.execute(query)
    resultados = cursor.fetchall()

    cursor.close()
    conn.close()
    return resultados

# EXCLUIR RESERVA
def excluir_reserva(reserva_id):
    conn = conectar()
    cursor = conn.cursor()

    # Antes de excluir, liberar o veículo
    cursor.execute("SELECT veiculo_id FROM reservas WHERE id = ?", (reserva_id,))
    resultado = cursor.fetchone()
    if resultado:
        veiculo_id = resultado[0]
        cursor.execute("UPDATE veiculos SET disponivel = 1 WHERE id = ?", (veiculo_id,))

    cursor.execute("DELETE FROM reservas WHERE id = ?", (reserva_id,))
    conn.commit()
    conn.close()

def atualizar_reserva(reserva_id, dados):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE reservas SET
            cliente_id = ?, veiculo_id = ?, data_inicio = ?, data_fim = ?,
            forma_pagamento_id = ?, valor_total = ?, estado = ?
        WHERE id = ?
    """, dados + (reserva_id,))
    conn.commit()
    conn.close()

def obter_formas_pagamento():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, descricao FROM formas_pagamento ORDER BY descricao")
    formas = cursor.fetchall()
    conn.close()
    return formas

def adicionar_forma_pagamento(nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO formas_pagamento (descricao) VALUES (?)", (nome,))
    conn.commit()
    conn.close()

def atualizar_forma_pagamento(id_forma, nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE formas_pagamento SET descricao = ? WHERE id = ?", (nome, id_forma))
    conn.commit()
    conn.close()

def excluir_forma_pagamento(id_forma):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM formas_pagamento WHERE id = ?", (id_forma,))
    conn.commit()
    conn.close()

def get_veiculo_by_id(veiculo_id):
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM veiculos WHERE id = ?", (veiculo_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None

def criar_reserva(cliente_id, veiculo_id, data_inicio, data_fim, forma_pagamento_id, valor_total):
    from datetime import datetime
    conn = conectar()
    cursor = conn.cursor()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
            INSERT INTO reservas (cliente_id, veiculo_id, data_inicio, data_fim, forma_pagamento_id, valor_total)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (cliente_id, veiculo_id, data_inicio + " 00:00:00", data_fim + " 23:59:59", forma_pagamento_id, valor_total))

    conn.commit()
    conn.close()

def atualizar_status_veiculo(veiculo_id, disponivel):
    conn = sqlite3.connect('luxury_wheels.db')
    cursor = conn.cursor()

    cursor.execute("UPDATE veiculos SET disponivel = ? WHERE id = ?", (disponivel, veiculo_id))

    conn.commit()
    conn.close()

def get_reserva_by_id(reserva_id):
    conn = conectar()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM reservas WHERE id = ?', (reserva_id,))
    reserva = cursor.fetchone()

    conn.close()
    return dict(reserva) if reserva else None

def finalizar_reserva(reserva_id):
    conn = conectar()
    cursor = conn.cursor()

    # Exemplo: atualiza a data_fim da reserva para a data atual (podes adaptar)
    cursor.execute('''
        UPDATE reservas
        SET data_fim = DATE('now')
        WHERE id = ?
    ''', (reserva_id,))

    conn.commit()
    conn.close()

def atualizar_reservas_expiradas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE reservas
        SET estado = 'Terminada'
        WHERE estado != 'Terminada' AND datetime(data_fim) < datetime('now')
    """)

    conn.commit()
    conn.close()

def atualizar_veiculos_para_manutencao():
    from datetime import datetime, timedelta

    conn = conectar()
    cursor = conn.cursor()

    hoje = datetime.now().date()
    limite = hoje + timedelta(days=5)

    # Atualiza veículos com revisão em até 5 dias
    cursor.execute("""
        UPDATE veiculos
        SET em_manutencao = 1, disponivel = 0
        WHERE date(data_proxima_revisao) <= ? AND em_manutencao = 0
    """, (limite.strftime("%Y-%m-%d"),))

    # Atualiza veículos com inspeção em até 5 dias
    cursor.execute("""
        UPDATE veiculos
        SET em_manutencao = 1, disponivel = 0
        WHERE date(data_inspecao_obrigatoria) <= ? AND em_manutencao = 0
    """, (limite.strftime("%Y-%m-%d"),))

    print("[INFO] Verificação de manutenção executada. CHAMADO DE:", __name__)
    print("[INFO] Revisões marcadas:", cursor.rowcount)
    conn.commit()
    conn.close()

def validar_utilizador(email, senha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM utilizadores WHERE email=? AND senha=?", (email, senha))
    user = cursor.fetchone()
    conn.close()
    return user

def registrar_utilizador(nome, email, senha):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO utilizadores (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
        conn.commit()
        conn.close()
        return True
    except:
        return False