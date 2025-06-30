from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from analisador import analisar_codigo

app = Flask(__name__)
CORS(app)

# Rota para a página HOME
@app.route('/')
def home():
    print("Servindo index.html (Página Home)...")
    return render_template('index.html')

# Rota para a página do Analisador
@app.route('/analisador')
def page_analisador():
    print("Servindo analisador.html (Página do Analisador)...")
    return render_template('analisador.html')

# Rota para a página da Tabela de Tokens
@app.route('/tabela-tokens')
def page_tabela_tokens():
    print("Servindo tabela_tokens.html (Página da Tabela de Tokens)...")
    return render_template('tabela_tokens.html')

@app.route('/analisar', methods=['POST'])
def analisar():
    data = request.get_json()
    codigo = data.get('codigo', '')
    
    # Chama a função de análise que agora retorna um dicionário
    resultado_analise = analisar_codigo(codigo)
    
    # Extrai os tokens e os erros de estrutura
    tokens = resultado_analise['tokens']
    erros_estrutura = resultado_analise['erros_estrutura']
    
    # Combina os resultados para enviar ao frontend
    final_output = []
    for erro_msg in erros_estrutura:
        # Usamos uma linha 0 para erros de estrutura para que apareçam primeiro e sejam facilmente identificados
        final_output.append([0, erro_msg, 'ERRO DE ESTRUTURA']) 
    
    final_output.extend(tokens) # Adiciona os tokens normais após os erros de estrutura

    return jsonify(final_output) # Retorna a lista combinada

if __name__ == '__main__':
    app.run(debug=True, port=5000)