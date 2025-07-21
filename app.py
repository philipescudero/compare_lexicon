import re 

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from analisador import analisar_codigo 
from sintatico import Parser          

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
    
    tokens_lexico = resultado_lexico['tokens']
    erros_estrutura_brutos = resultado_lexico['erros_estrutura'] 

    # NOVO: Lista de tipos de erro léxicos que o analisador sintático não deve tentar processar.
    # Adicionamos 'STRING_MUITO_LONGA_ERRO' aqui.
    lexical_error_types_to_skip_in_parser = [
        'SKIP', 'NEWLINE', 'COMENTARIO', 'ERRO LÉXICO', 
        'ERRO LÉXICO - ASPAS NÃO_FECHADAS', # Assegurar nome correto
        'ERRO LÉXICO - CARACTERE_INVÁLIDO', # Assegurar nome correto
        'NUM_EXCESSIVO_ERRO', 
        'STRING_MUITO_LONGA_ERRO' 
    ]

    tokens_para_sintatico = [
        [t[0], t[1], t[2]] for t in tokens_lexico 
        if t[2] not in lexical_error_types_to_skip_in_parser
    ]

    raw_erros_sintaticos = [] 
    
    if not erros_estrutura_brutos: 
        parser = Parser(tokens_para_sintatico)
        raw_erros_sintaticos = parser.parse() 

    final_output_structured = []

    # Adiciona erros LÉXICOS/ESTRUTURAIS/INICIALIZAÇÃO/PALAVRA-CHAVE
    for erro_msg in erros_estrutura_brutos:
        linha = 0
        coluna = 0
        match_line_col = re.search(r'linha (\d+), coluna (\d+)', erro_msg)
        if match_line_col:
            linha = int(match_line_col.group(1))
            coluna = int(match_line_col.group(2))
        
        display_type = 'ERRO DE ESTRUTURA/LÉXICO' 

        # NOVO: Lógica de reclassificação de erros para 'ERRO SINTÁTICO'
        # Adiciona 'String excede o limite' para ser reclassificado
        if "Aspas não fechadas" in erro_msg or \
           "Caractere inválido" in erro_msg or \
           "Erro de Balanceamento" in erro_msg or \
           "Erro de Inicialização" in erro_msg or \
           "Erro de Palavra-Chave" in erro_msg or \
           "Número excede o limite" in erro_msg or \
           "String excede o limite" in erro_msg: # Adicionado aqui para reclassificação
             display_type = 'ERRO SINTÁTICO' 
        elif "O programa deve começar com" in erro_msg or \
             "O programa deve terminar com" in erro_msg or \
             "Tokens extras após 'BIRL!'" in erro_msg:
             display_type = 'ERRO SINTÁTICO' 

        final_output_structured.append({
            'linha': linha,
            'coluna': coluna,
            'lexema_ou_mensagem': erro_msg,
            'tipo': display_type, 
            'categoria': 'erro'
        })
    
    # Adiciona erros SINTÁTICOS (do Parser)
    if raw_erros_sintaticos:
        for linha_erro, msg_erro_sintatico in raw_erros_sintaticos:
            final_output_structured.append({
                'linha': linha_erro,
                'coluna': 0, 
                'lexema_ou_mensagem': f"Erro Sintático: {msg_erro_sintatico}",
                'tipo': 'ERRO SINTÁTICO',
                'categoria': 'erro'
            }) 
    elif not erros_estrutura_brutos: 
        final_output_structured.append({
            'linha': 0, 
            'coluna': 0,
            'lexema_ou_mensagem': "Análise Sintática: NENHUM ERRO SINTÁTICO DETECTADO.",
            'tipo': 'SUCESSO SINTÁTICO',
            'categoria': 'sucesso'
        }) 

    # Adiciona os tokens LÉXICOS originais
    for token_info in tokens_lexico:
        linha, lexema, tipo, coluna = token_info 
        final_output_structured.append({
            'linha': linha,
            'coluna': coluna,
            'lexema_ou_mensagem': lexema,
            'tipo': tipo,
            'categoria': 'token' 
        }) 

    return jsonify(final_output_structured)

if __name__ == '__main__':
    app.run(debug=True, port=5000)