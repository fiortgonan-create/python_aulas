from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request
import mysql.connector

app = Flask(__name__)

# Configuração do banco de dados com as credenciais que você já usa
bd_config = {
  'host': 'localhost',
  'user': 'root',
  'password': 'escola',
  'database': 'help_desk'
  
}

# ==========================================
# 1. TELA E LÓGICA DE LOGIN
# ==========================================
@app.route('/')
def tela_login():
    return render_template('login.html')

@app.route('/autenticar', methods=['POST'])
def autenticar():
    email = request.form['email']
    senha = request.form['senha']
    
    try:
        conectar = mysql.connector.connect(**bd_config)
        cursor = conectar.cursor(dictionary=True)
        
        # Busca na tabela 'cadastro' conforme definido por vocês
        query = "SELECT id_cliente, nome_completo FROM cadastro WHERE email = %s AND senha = %s"
        cursor.execute(query, (email, senha))
        usuario = cursor.fetchone()
        
        cursor.close()
        conectar.close()
        
        if usuario:
            # Passa o ID do cliente logado na URL para a próxima tela saber quem é
            return redirect(url_for('tela_solicitacao', id_cliente=usuario['id_cliente']))
        else:
            return "E-mail ou senha incorretos! Volte e tente novamente."
            
    except mysql.connector.Error as erro:
        return f"Erro ao autenticar: {erro}"


# ==========================================
# 2. TELA E LÓGICA DE CADASTRO DE USUÁRIO
# ==========================================
@app.route('/cadastro')
def tela_cadastro():
    return render_template('cadastro.html')

@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    # Captura todos os campos da tabela 'cadastro' vindos do formulário HTML
    nome_completo = request.form['nome_completo']
    celular = request.form['celular']
    cpf = request.form['cpf']
    email = request.form['email']
    senha = request.form['senha']
    data_nascimento = request.form['data_nascimento']
    cidade = request.form['cidade']
    
    try:
        conectar = mysql.connector.connect(**bd_config)
        cursor = conectar.cursor()
        
        query = """
            INSERT INTO cadastro (nome_completo, celular, cpf, email, senha, data_nascimento, cidade) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valores = (nome_completo, celular, cpf, email, senha, data_nascimento, cidade)
        cursor.execute(query, valores)
        
        conectar.commit()
        cursor.close()
        conectar.close()
        
        return redirect(url_for('tela_login'))
        
    except mysql.connector.Error as erro:
        return f"Erro ao cadastrar usuário: {erro}"


# ==========================================
# 3. TELA E LÓGICA DE SOLICITAÇÃO (CHAMADOS)
# ==========================================
# Captura o id_cliente vindo do login para registrar o chamado no nome correto
@app.route('/solicitacao/<int:id_cliente>')
def tela_solicitacao(id_cliente):
    # Exibe a tela de chamados passando o ID do cliente para o HTML
    return render_template('solicitacao.html', id_cliente=id_cliente)

@app.route('/criar_chamado', methods=['POST'])
def criar_chamado():
    id_cliente = request.form['id_cliente']
    descricao = request.form['descricao']
    
    # Valores padrão para um chamado novo
    data_abertura = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status = 'Aberto'
    id_tecnico = None # Começa sem técnico atribuído
    data_fechamento = None
    valor = 0.0
    
    try:
        conectar = mysql.connector.connect(**bd_config)
        cursor = conectar.cursor()
        
        # Gravação na tabela 'chamados'
        query_chamado = """
            INSERT INTO chamados (id_cliente, id_tecnico, descricao, data_abertura, data_fechamento, status, valor) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valores_chamado = (id_cliente, id_tecnico, descricao, data_abertura, data_fechamento, status, valor)
        cursor.execute(query_chamado, valores_chamado)
        
        # Recupera o ID do chamado que acabou de ser gerado para usar no histórico
        id_chamado_gerado = cursor.lastrowid
        
        # Registo inicial automático na tabela 'historico' conforme sua modelagem
        query_historico = """
            INSERT INTO historico (id_chamado, data_evento, descricao) 
            VALUES (%s, %s, %s)
        """
        valores_historico = (id_chamado_gerado, data_abertura, "Chamado aberto pelo cliente.")
        cursor.execute(query_historico, valores_historico)
        
        conectar.commit()
        cursor.close()
        conectar.close()
        
        return f"Chamado nº {id_chamado_gerado} aberto com sucesso!"
        
    except mysql.connector.Error as erro:
        return f"Erro ao criar chamado: {erro}"


if __name__ == '__main__':
    app.run(debug=True)
