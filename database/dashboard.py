from datetime import datetime, timedelta
from .db_controller import conectar

# Atualizações automáticas ao iniciar o dashboard

def total_veiculos_disponiveis():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM veiculos WHERE disponivel = 1")
    total = cursor.fetchone()[0]
    conn.close()
    return total

def total_reservas_mes():
    hoje = datetime.now()
    inicio_mes = hoje.replace(day=1).strftime('%d/%m/%Y')
    fim_mes = hoje.replace(day=28) + timedelta(days=4)
    fim_mes = fim_mes - timedelta(days=fim_mes.day)
    fim_mes = fim_mes.strftime('%d/%m/%Y')

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM reservas WHERE data_inicio BETWEEN ? AND ?", (inicio_mes, fim_mes))
    total = cursor.fetchone()[0]
    conn.close()
    return total

def total_financeiro_mes():
    hoje = datetime.now()
    inicio_mes = hoje.replace(day=1).strftime('%d/%m/%Y')
    fim_mes = hoje.replace(day=28) + timedelta(days=4)
    fim_mes = fim_mes - timedelta(days=fim_mes.day)
    fim_mes = fim_mes.strftime('%d/%m/%Y')

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor_total) FROM reservas WHERE data_inicio BETWEEN ? AND ?", (inicio_mes, fim_mes))
    total = cursor.fetchone()[0]
    conn.close()
    return total or 0

def veiculos_alugados_dias_restantes():
    hoje = datetime.now()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.marca || ' ' || v.modelo, r.data_fim
        FROM reservas r
        JOIN veiculos v ON r.veiculo_id = v.id
        WHERE r.estado = 'Sendo Usado'
    """)
    dados = []
    for modelo, data_fim in cursor.fetchall():
        try:
            data_obj = datetime.strptime(data_fim, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            data_obj = datetime.strptime(data_fim, "%Y-%m-%d")

        delta = data_obj - hoje
        dias_restantes = delta.days if delta.total_seconds() > 0 else 0
        dados.append((modelo, dias_restantes))

    conn.close()
    return dados

def ultimos_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, email FROM clientes ORDER BY id DESC LIMIT 5")
    dados = cursor.fetchall()
    conn.close()
    return dados

def veiculos_disponiveis_por_categoria_tipo():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT categoria, tipo, COUNT(*)
        FROM veiculos
        WHERE disponivel = 1
        GROUP BY categoria, tipo
    """)
    dados = cursor.fetchall()
    conn.close()
    return dados

def veiculos_revisao_ate_15_dias():
    hoje = datetime.now()
    limite = hoje + timedelta(days=15)
    hoje_str = hoje.strftime('%Y-%m-%d')
    limite_str = limite.strftime('%Y-%m-%d')
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT marca || ' ' || modelo, data_proxima_revisao
        FROM veiculos
        WHERE data_proxima_revisao BETWEEN ? AND ?
    """, (hoje_str, limite_str))
    dados = cursor.fetchall()
    conn.close()
    return dados

def veiculos_inspecao_ate_15_dias():
    hoje = datetime.now()
    limite = hoje + timedelta(days=15)
    hoje_str = hoje.strftime('%Y-%m-%d')
    limite_str = limite.strftime('%Y-%m-%d')
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT marca || ' ' || modelo, data_inspecao_obrigatoria
        FROM veiculos
        WHERE data_inspecao_obrigatoria BETWEEN ? AND ?
    """, (hoje_str, limite_str))
    dados = cursor.fetchall()
    conn.close()
    return dados

def verificar_alertas_revisao_inspecao():
    conn = conectar()
    cursor = conn.cursor()

    hoje = datetime.now().date()
    limite = hoje + timedelta(days=5)

    cursor.execute("""
        SELECT modelo, data_proxima_revisao
        FROM veiculos
        WHERE date(data_proxima_revisao) <= ?
    """, (limite.strftime("%Y-%m-%d"),))
    revisoes = cursor.fetchall()

    cursor.execute("""
        SELECT modelo, data_inspecao_obrigatoria
        FROM veiculos
        WHERE date(data_inspecao_obrigatoria) <= ?
    """, (limite.strftime("%Y-%m-%d"),))
    inspecoes = cursor.fetchall()

    conn.close()
    return revisoes, inspecoes