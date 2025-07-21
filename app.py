import re # NOVO: Importação do módulo de expressões regulares

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
    # Tokens agora vêm como [linha, lexema, tipo, coluna]
    tokens_lexico = resultado_lexico['tokens']
    erros_estrutura = resultado_lexico['erros_estrutura'] # Mensagens de erro em string

    # Prepara os tokens para o analisador SINTÁTICO (apenas tokens válidos e significativos)
    # Mantemos o formato original para o sintático: [linha, lexema, tipo]
    tokens_para_sintatico = [
        [t[0], t[1], t[2]] for t in tokens_lexico 
        if t[2] not in [
            'SKIP', 'NEWLINE', 'COMENTARIO', 'ERRO LÉXICO', 
            'ERRO LÉXICO - ASPAS NÃO FECHADAS', 'ERRO LÉXICO - CARACTERE INVÁLIDO'
        ]
    ]

    raw_erros_sintaticos = [] # Vai receber as tuplas (linha, mensagem_limpa) do sintático
    
    # Condição para chamar o analisador SINTÁTICO: só se não houver erros léxicos/de estrutura iniciais
    if not erros_estrutura: 
        parser = Parser(tokens_para_sintatico)
        raw_erros_sintaticos = parser.parse() # Executa a análise sintática e coleta os erros como tuplas

    # 4. Combina todos os resultados para enviar ao frontend em um formato estruturado
    final_output_structured = []

    # Adiciona erros LÉXICOS/ESTRUTURAIS/INICIALIZAÇÃO/PALAVRA-CHAVE
    # Estes erros vêm como strings, então tentamos extrair linha e coluna se possível
    for erro_msg in erros_estrutura:
        # Tenta parsear a linha e coluna da mensagem de erro (formato: "Erro ... na linha X, coluna Y: ...")
        linha = 0
        coluna = 0
        # O re.search PRECISA do 're' importado!
        match_line_col = re.search(r'linha (\d+), coluna (\d+)', erro_msg) 
        if match_line_col:
            linha = int(match_line_col.group(1))
            coluna = int(match_line_col.group(2))
        
        final_output_structured.append({
            'linha': linha,
            'coluna': coluna,
            'lexema_ou_mensagem': erro_msg,
            'tipo': 'ERRO DE ESTRUTURA/LÉXICO',
            'categoria': 'erro' # Nova categoria para facilitar o frontend
        })
    
    # Adiciona erros SINTÁTICOS
    if raw_erros_sintaticos:
        for linha_erro, msg_erro_sintatico in raw_erros_sintaticos:
            # O analisador sintático não fornece a coluna diretamente, então usamos 0 ou N/A
            final_output_structured.append({
                'linha': linha_erro,
                'coluna': 0, # Coluna não disponível para erros sintáticos do Parser
                'lexema_ou_mensagem': f"Erro Sintático: {msg_erro_sintatico}",
                'tipo': 'ERRO SINTÁTICO',
                'categoria': 'erro'
            }) 
    elif not erros_estrutura: # Se NÃO houve erros léxicos/estrutura E NÃO houve erros sintáticos
        final_output_structured.append({
            'linha': 0, 
            'coluna': 0,
            'lexema_ou_mensagem': "Análise Sintática: NENHUM ERRO SINTÁTICO DETECTADO.",
            'tipo': 'SUCESSO SINTÁTICO',
            'categoria': 'sucesso'
        }) 

    # Adiciona os tokens LÉXICOS originais (agora com coluna)
    for token_info in tokens_lexico:
        linha, lexema, tipo, coluna = token_info # Desempacota os 4 valores
        final_output_structured.append({
            'linha': linha,
            'coluna': coluna,
            'lexema_ou_mensagem': lexema,
            'tipo': tipo,
            'categoria': 'token' # Categoria para tokens léxicos
        }) 

    return jsonify(final_output_structured)

if __name__ == '__main__':
    app.run(debug=True, port=5000)