from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from analisador import analisar_codigo # Importa seu analisador léxico
from sintatico import Parser          # Importa a classe Parser do módulo sintatico

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
    
    # 1. Chama a função de análise LÉXICA
    resultado_lexico = analisar_codigo(codigo)
    
    # Extrai os tokens léxicos e os erros combinados (léxicos e de estrutura básica)
    tokens_lexico = resultado_lexico['tokens']
    erros_lexico_e_estrutura = resultado_lexico['erros_estrutura']
    
    # Prepara os tokens para o analisador SINTÁTICO (apenas tokens válidos e significativos)
    tokens_para_sintatico = [
        t for t in tokens_lexico 
        if t[2] not in [
            'SKIP', 'NEWLINE', 'COMENTARIO', 'ERRO LÉXICO', 
            'ERRO LÉXICO - ASPAS NÃO FECHADAS', 'ERRO LÉXICO - CARACTERE INVÁLIDO'
        ]
    ]

    raw_erros_sintaticos = [] # Vai receber as tuplas (linha, mensagem_limpa) do sintático
    
    # Condição para chamar o analisador SINTÁTICO: só se não houver erros léxicos/de estrutura iniciais
    if not erros_lexico_e_estrutura: 
        parser = Parser(tokens_para_sintatico)
        raw_erros_sintaticos = parser.parse() # Executa a análise sintática e coleta os erros como tuplas

    # 4. Combina todos os resultados para enviar ao frontend
    final_output = []

    # Adiciona erros LÉXICOS/ESTRUTURAIS/INICIALIZAÇÃO/PALAVRA-CHAVE primeiro
    for erro_msg in erros_lexico_e_estrutura:
        # Mantém o formato para esses erros, eles já vêm formatados do analisador.py
        final_output.append([0, erro_msg, 'ERRO DE ESTRUTURA/LÉXICO']) 
    
    # NOVO: Adiciona erros SINTÁTICOS, extraindo a linha da tupla e formatando
    if raw_erros_sintaticos:
        for linha_erro, msg_erro_sintatico in raw_erros_sintaticos:
            final_output.append([linha_erro, f"Erro Sintático: {msg_erro_sintatico}", 'ERRO SINTÁTICO']) 
    elif not erros_lexico_e_estrutura: # Se NÃO houve erros léxicos/estrutura E NÃO houve erros sintáticos
        final_output.append([0, "Análise Sintática: NENHUM ERRO SINTÁTICO DETECTADO.", 'SUCESSO SINTÁTICO']) 

    # Adiciona os tokens LÉXICOS originais APÓS todas as mensagens de erro/sucesso
    final_output.extend(tokens_lexico) 

    return jsonify(final_output)

if __name__ == '__main__':
    app.run(debug=True, port=5000)