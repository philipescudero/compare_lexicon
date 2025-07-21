import re

TOKEN_SPEC = [
    ('INICIO_PROGRAMA', r'\bBORA\b'),
    ('FIM_PROGRAMA', r'BIRL!'),
    ('VARIAVEL', r'\bMONSTRO\b'), 
    ('ATRIBUICAO', r'\bTASAINDODAJAULA\b'),
    ('PRINT', r'\bGRITA\b'),
    ('IF', r'\bCONFERE_AI\b'),
    ('ELIF', r'\bCONFERE_MAIS\b'),
    ('ELSE', r'\bOU_NAO\b'),
    ('WHILE', r'\bTREINA ATÉ\b'),
    ('FUNC', r'\bFICA GRANDE\b'),
    ('CALL', r'\bCHAMA\b'),

    # NOVOS TOKENS - ORDEM IMPORTANTE!
    ('BOOLEAN_VERDADEIRO', r'\bVERDADEIRO\b'),
    ('BOOLEAN_FALSO', r'\bFALSO\b'),

    ('OP_LOGICO', r'\bE\b|\bOU\b|\bNÃO\b'),

    # Operadores: compostos antes de simples
    ('OP_ATRIBUICAO_COMPOSTA', r'\+=|\-=|\*=|\/\='),
    ('OP_RELACIONAL_OU_IGUALDADE', r'>=|<=|==|!=|>|<'),
    ('OP_ARITMETICO', r'\+|\-|\*|\/'),
    
    # Delimitadores e Pontuação
    ('PARENTESES_ABRE', r'\bColoca anilha\b'), 
    ('PARENTESES_FECHA', r'\bTira anilha\b'),   
    ('VIRGULA', r','),
    ('DOIS_PONTOS', r':'),

    # LITERAIS - ESTES DEVEM VIR ANTES DE ID E QUALQUER ERRO GERAL
    ('STRING', r'"[^"\n]*"'), 
    ('NUM_DECIMAL', r'\b\d+\.\d+\b'), 
    ('NUM', r'\b\d+\b'), 

    # Comentário: Deve vir antes de ID para não confundir com palavras-chave ou IDs
    ('COMENTARIO', r'#[^\n]*'),

    ('ID', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'), 

    # Erros Específicos e Ignorados (Vêm depois dos tokens válidos)
    ('ASPAS_NAO_FECHADA', r'"[^\n]*$'), 
    ('CARACTERE_SOLTO_PARENTESES', r'[\(\)]'), 

    # Ignorados
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),

    # Erro Geral (O último da lista)
    ('MISMATCH', r'.'), # Captura qualquer caractere restante como erro
]

token_regex = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC))

# Conjunto de palavras que SÃO ID mas que poderiam ser confundidas com palavras-chave se fossem literais
POTENTIAL_KEYWORD_MISUSE = {
    'If', 'Else', 'While', 'For', 'Def', 'Call' 
}


def analisar_codigo(codigo: str) -> dict:
    """
    Realiza a análise léxica de um código-fonte BIRL e verifica a estrutura básica,
    balanceamento de delimitadores e a obrigatoriedade de 'MONSTRO' para novas variáveis.

    Args:
        codigo (str): A string contendo o código BIRL a ser analisado.

    Returns:
        dict: Um dicionário contendo:
              - 'tokens': Uma lista de listas, onde cada sub-lista contém [linha, lexema, tipo, coluna].
              - 'erros_estrutura': Uma lista de mensagens de erro de estrutura básica.
    """
    linhas_codigo = codigo.splitlines()
    resultado_tokens = []
    erros_estrutura = [] # Esta lista vai conter as mensagens de erro formatadas para o topo
    
    delimiters_stack = [] 
    delimiter_map = {
        'Tira anilha': 'PARENTESES_ABRE', 
    }

    found_bora_token = False 
    found_birl_token = False 
    
    # Conjunto para rastrear variáveis que já foram declaradas com MONSTRO
    declared_variables = set()

    previous_meaningful_token_type = None 
    last_meaningful_token_lexema = None 

    for num_linha, linha in enumerate(linhas_codigo, start=1):
        pos_coluna = 0 
        coluna_real = 1 
        
        while pos_coluna < len(linha):
            match = token_regex.match(linha, pos_coluna)

            if match:
                tipo = match.lastgroup
                lexema = match.group(tipo)
                
                coluna_inicial_lexema = coluna_real 

                if tipo == 'SKIP':
                    coluna_real += len(lexema) 
                    pass 
                elif tipo == 'NEWLINE': 
                    coluna_real = 1
                    pass
                elif tipo == 'COMENTARIO':
                    resultado_tokens.append([num_linha, lexema, tipo, coluna_inicial_lexema])
                    previous_meaningful_token_type = None 
                    last_meaningful_token_lexema = None
                    coluna_real += len(lexema)
                elif tipo == 'MISMATCH':
                    # NOVO: Adiciona a mensagem de erro léxico à lista de erros para o topo
                    erros_estrutura.append(f"Erro Léxico na linha {num_linha}, coluna {coluna_inicial_lexema}: Caractere não reconhecido '{lexema}'.")
                    # Adiciona o token MISMATCH à lista principal de tokens também
                    resultado_tokens.append([num_linha, lexema, 'ERRO LÉXICO', coluna_inicial_lexema]) 
                    previous_meaningful_token_type = None 
                    last_meaningful_token_lexema = None
                    coluna_real += len(lexema)
                elif tipo == 'ASPAS_NAO_FECHADA':
                    erros_estrutura.append(f"Erro Léxico na linha {num_linha}, coluna {coluna_inicial_lexema}: Aspas não fechadas em '{lexema}'.")
                    resultado_tokens.append([num_linha, lexema, 'ERRO LÉXICO - ASPAS NÃO FECHADAS', coluna_inicial_lexema])
                    previous_meaningful_token_type = None 
                    last_meaningful_token_lexema = None
                    coluna_real += len(lexema)
                elif tipo == 'CARACTERE_SOLTO_PARENTESES':
                    erros_estrutura.append(f"Erro Léxico na linha {num_linha}, coluna {coluna_inicial_lexema}: Caractere inválido '{lexema}'. Utilize 'Coloca anilha' e 'Tira anilha'.")
                    resultado_tokens.append([num_linha, lexema, 'ERRO LÉXICO - CARACTERE INVÁLIDO', coluna_inicial_lexema])
                    previous_meaningful_token_type = None 
                    last_meaningful_token_lexema = None
                    coluna_real += len(lexema)
                else:
                    resultado_tokens.append([num_linha, lexema, tipo, coluna_inicial_lexema])
                    
                    # --- Lógica de Validação MONSTRO ---
                    if tipo == 'ID' and previous_meaningful_token_type == 'VARIAVEL':
                        declared_variables.add(lexema) 
                    
                    if tipo == 'ID' and lexema not in declared_variables:
                        temp_pos = pos_coluna + len(lexema) 
                        next_is_assignment = False
                        temp_col_for_next = coluna_real + len(lexema) # Passa para a função de erro
                        while temp_pos < len(linha):
                            next_match = token_regex.match(linha, temp_pos)
                            if next_match:
                                next_tipo = next_match.lastgroup
                                if next_tipo == 'ATRIBUICAO':
                                    next_is_assignment = True
                                    break 
                                elif next_tipo in ['SKIP', 'NEWLINE', 'COMENTARIO']:
                                    temp_pos += len(next_match.group(next_tipo))
                                    temp_col_for_next += len(next_match.group(next_tipo))
                                else: 
                                    break 
                                
                            else: 
                                break
                        
                        if next_is_assignment: 
                            erros_estrutura.append(f"Erro de Inicialização na linha {num_linha}, coluna {coluna_inicial_lexema}: Variável '{lexema}' utilizada com atribuição ('TASAINDODAJAULA') sem declaração com 'MONSTRO'.")
                            declared_variables.add(lexema) 
                            
                    # --- Lógica de Detecção de Uso Incorreto de Palavras (tipo 'If', 'Else') ---
                    if tipo == 'ID' and lexema in POTENTIAL_KEYWORD_MISUSE:
                        erros_estrutura.append(f"Erro de Palavra-Chave na linha {num_linha}, coluna {coluna_inicial_lexema}: Uso incorreto da palavra '{lexema}'. Utilize as palavras-chave BIRL! para controle de fluxo (ex: CONFERE_AI, OU_NAO).")
                    
                    # --- Lógica de Validação BORA/BIRL! ---
                    if tipo == 'INICIO_PROGRAMA':
                        found_bora_token = True
                    elif tipo == 'FIM_PROGRAMA':
                        found_birl_token = True

                    # Lógica para verificação de balanceamento (usando a pilha)
                    if tipo == 'PARENTESES_ABRE': 
                        delimiters_stack.append((lexema, num_linha, tipo, coluna_inicial_lexema)) # Armazena a coluna
                    elif tipo == 'PARENTESES_FECHA': 
                        if not delimiters_stack:
                            erros_estrutura.append(f"Erro de Balanceamento na linha {num_linha}, coluna {coluna_inicial_lexema}: '{lexema}' encontrado sem delimitador de abertura correspondente.")
                        else:
                            last_open_delimiter_info = delimiters_stack.pop()
                            last_open_lexema = last_open_delimiter_info[0]
                            last_open_line = last_open_delimiter_info[1]
                            last_open_type = last_open_delimiter_info[2]
                            last_open_col = last_open_delimiter_info[3] # Pega a coluna de abertura
                            
                            if delimiter_map.get(lexema) != last_open_type: 
                                erros_estrutura.append(f"Erro de Balanceamento na linha {num_linha}, coluna {coluna_inicial_lexema}: '{lexema}' encontrado, mas esperava fechamento para '{last_open_lexema}' (aberto na linha {last_open_line}, coluna {last_open_col}).")
                                        
                    previous_meaningful_token_type = tipo 
                    last_meaningful_token_lexema = lexema
                    coluna_real += len(lexema)


                pos_coluna += len(lexema) 
            else:
                # Se o regex não casar, adiciona como erro léxico e avança
                # NOVO: Adiciona o erro léxico genérico à lista de erros para o topo
                erros_estrutura.append(f"Erro Léxico na linha {num_linha}, coluna {coluna_real}: Caractere não reconhecido '{linha[pos_coluna]}'.")
                resultado_tokens.append([num_linha, linha[pos_coluna], 'ERRO LÉXICO', coluna_real])
                previous_meaningful_token_type = None 
                last_meaningful_token_lexema = None
                coluna_real += 1 
                pos_coluna += 1 
        
    # --- Verificações Finais de Estrutura (Pós-Processamento) ---
    
    # 1. Validação de BORA e BIRL! 
    meaningful_sequence = [
        t for t in resultado_tokens 
        if t[2] not in [
            'SKIP', 'NEWLINE', 'COMENTARIO', 'ERRO LÉXICO', 
            'ERRO LÉXICO - ASPAS NÃO FECHADAS', 'ERRO LÉXICO - CARACTERE INVÁLIDO'
        ]
    ]

    # Para erros de BORA/BIRL!, a linha/coluna pode ser do primeiro/último token significativo, ou N/A
    bora_line = meaningful_sequence[0][0] if meaningful_sequence and meaningful_sequence[0][2] == 'INICIO_PROGRAMA' else "N/A"
    bora_col = meaningful_sequence[0][3] if meaningful_sequence and meaningful_sequence[0][2] == 'INICIO_PROGRAMA' else "N/A"
    birl_line = meaningful_sequence[-1][0] if meaningful_sequence and meaningful_sequence[-1][2] == 'FIM_PROGRAMA' else "N/A"
    birl_col = meaningful_sequence[-1][3] if meaningful_sequence and meaningful_sequence[-1][2] == 'FIM_PROGRAMA' else "N/A"


    if not meaningful_sequence or meaningful_sequence[0][2] != 'INICIO_PROGRAMA':
        erros_estrutura.append(f"Erro de Estrutura na linha {bora_line}, coluna {bora_col}: O programa deve começar com 'BORA'.")

    if not meaningful_sequence or meaningful_sequence[-1][2] != 'FIM_PROGRAMA':
        erros_estrutura.append(f"Erro de Estrutura na linha {birl_line}, coluna {birl_col}: O programa deve terminar com 'BIRL!'.")

    # 2. Erros de Balanceamento de Delimitadores (qualquer coisa que sobrou na pilha)
    while delimiters_stack:
        unclosed_lexema, unclosed_line, _, unclosed_col = delimiters_stack.pop() # Desempacota também a coluna de abertura
        erros_estrutura.append(f"Erro de Balanceamento na linha {unclosed_line}, coluna {unclosed_col}: Delimitador '{unclosed_lexema}' aberto e não fechado.")

    # Remove duplicidades nos erros de estrutura/balanceamento
    erros_estrutura = list(dict.fromkeys(erros_estrutura))

    return {'tokens': resultado_tokens, 'erros_estrutura': erros_estrutura}