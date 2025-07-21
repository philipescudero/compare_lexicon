import re

TOKEN_SPEC = [
    ('INICIO_PROGRAMA', r'\bBORA\b'),
    ('FIM_PROGRAMA', r'BIRL!'),
    ('VARIAVEL', r'\bMONSTRO\b'), # CORRIGIDO: Certificando que é 'VARIAVEL'
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
    
    # Delimitadores e Pontuação - CORRIGIDO AQUI: USANDO \b PARA PALAVRAS INTEIRAS E ESPAÇO
    ('PARENTESES_ABRE', r'\bColoca anilha\b'), # Regex para "Coloca anilha" (com espaço, iniciais maiúsculas)
    ('PARENTESES_FECHA', r'\bTira anilha\b'),   # Regex para "Tira anilha" (com espaço, iniciais maiúsculas)
    ('VIRGULA', r','),
    ('DOIS_PONTOS', r':'),

    # LITERAIS - ESTES DEVEM VIR ANTES DE ID E QUALQUER ERRO GERAL
    ('STRING', r'"[^"\n]*"'), # String bem formada (abre e fecha na mesma linha)
    ('NUM_DECIMAL', r'\b\d+\.\d+\b'), # Números decimais (Ex: 123.45) - DEVE VIR ANTES DE NUM
    ('NUM', r'\b\d+\b'), # Números inteiros - DEVE VIR ANTES DE ID

    # Comentário: Deve vir antes de ID para não confundir com palavras-chave ou IDs
    ('COMENTARIO', r'#[^\n]*'),

    ('ID', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'), # ID deve vir DEPOIS de todas as palavras-chave fixas e números.

    # Erros Específicos e Ignorados (Vêm depois dos tokens válidos)
    ('ASPAS_NAO_FECHADA', r'"[^\n]*$'), # Aspa que abre mas não fecha na mesma linha
    ('CARACTERE_SOLTO_PARENTESES', r'[\(\)]'), # Caracteres ( e ) agora serão erros léxicos explícitos

    # Ignorados
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),

    # Erro Geral (O último da lista)
    ('MISMATCH', r'.'), # Captura qualquer caractere restante como erro
]

token_regex = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC))

# Conjunto de palavras que SÃO ID mas que poderiam ser confundidas com palavras-chave se fossem literais
POTENTIAL_KEYWORD_MISUSE = {
    'If', 'Else', 'While', 'For', 'Def', 'Call' # Adicione outras palavras comuns aqui
}


def analisar_codigo(codigo: str) -> dict:
    """
    Realiza a análise léxica de um código-fonte BIRL e verifica a estrutura básica,
    balanceamento de delimitadores e a obrigatoriedade de 'MONSTRO' para novas variáveis.

    Args:
        codigo (str): A string contendo o código BIRL a ser analisado.

    Returns:
        dict: Um dicionário contendo:
              - 'tokens': Uma lista de listas, onde cada sub-lista contém [linha, lexema, tipo].
              - 'erros_estrutura': Uma lista de mensagens de erro de estrutura básica.
    """
    linhas_codigo = codigo.splitlines()
    resultado_tokens = []
    erros_estrutura = []
    
    delimiters_stack = [] 
    # O delimiter_map também deve usar o lexema exato que será reconhecido
    delimiter_map = {
        'Tira anilha': 'PARENTESES_ABRE', # Lexema completo de fechamento
    }

    found_bora_token = False 
    found_birl_token = False 
    
    # Conjunto para rastrear variáveis que já foram declaradas com MONSTRO
    declared_variables = set()

    previous_meaningful_token_type = None 
    last_meaningful_token_lexema = None 

    for num_linha, linha in enumerate(linhas_codigo, start=1):
        pos_coluna = 0
        
        while pos_coluna < len(linha):
            match = token_regex.match(linha, pos_coluna)

            if match:
                tipo = match.lastgroup
                lexema = match.group(tipo)
                
                # Ignoramos SKIP e NEWLINE na saída
                if tipo == 'SKIP' or tipo == 'NEWLINE':
                    pass 
                elif tipo == 'COMENTARIO':
                    resultado_tokens.append([num_linha, lexema, tipo])
                    previous_meaningful_token_type = None 
                    last_meaningful_token_lexema = None
                elif tipo == 'MISMATCH':
                    resultado_tokens.append([num_linha, lexema, 'ERRO LÉXICO'])
                    previous_meaningful_token_type = None 
                    last_meaningful_token_lexema = None
                elif tipo == 'ASPAS_NAO_FECHADA':
                    resultado_tokens.append([num_linha, lexema, 'ERRO LÉXICO - ASPAS NÃO FECHADAS'])
                    previous_meaningful_token_type = None 
                    last_meaningful_token_lexema = None
                elif tipo == 'CARACTERE_SOLTO_PARENTESES':
                    resultado_tokens.append([num_linha, lexema, 'ERRO LÉXICO - CARACTERE INVÁLIDO'])
                    previous_meaningful_token_type = None 
                    last_meaningful_token_lexema = None
                else:
                    # Este é um token "válido" e significativo, então o adicionamos
                    resultado_tokens.append([num_linha, lexema, tipo])
                    
                    # --- Lógica de Validação MONSTRO ---
                    if tipo == 'ID' and previous_meaningful_token_type == 'VARIAVEL':
                        declared_variables.add(lexema) 
                    
                    if tipo == 'ID' and lexema not in declared_variables:
                        temp_pos = pos_coluna + len(lexema) 
                        next_is_assignment = False
                        while temp_pos < len(linha):
                            next_match = token_regex.match(linha, temp_pos)
                            if next_match:
                                next_tipo = next_match.lastgroup
                                if next_tipo == 'ATRIBUICAO':
                                    next_is_assignment = True
                                    break 
                                elif next_tipo not in ['SKIP', 'NEWLINE', 'COMENTARIO']:
                                    break 
                                temp_pos += len(next_match.group(next_tipo))
                            else:
                                break
                        
                        if next_is_assignment: 
                            erros_estrutura.append(f"Erro de Inicialização na linha {num_linha}: Variável '{lexema}' utilizada com atribuição ('TASAINDODAJAULA') sem declaração com 'MONSTRO'.")
                            declared_variables.add(lexema) 
                            
                    # --- Lógica de Detecção de Uso Incorreto de Palavras (tipo 'If', 'Else') ---
                    if tipo == 'ID' and lexema in POTENTIAL_KEYWORD_MISUSE:
                        erros_estrutura.append(f"Erro de Palavra-Chave na linha {num_linha}: Uso incorreto da palavra '{lexema}'. Utilize as palavras-chave BIRL! para controle de fluxo (ex: CONFERE_AI, OU_NAO).")
                    
                    # --- Lógica de Validação BORA/BIRL! (Apenas registra se o token foi encontrado) ---
                    if tipo == 'INICIO_PROGRAMA':
                        found_bora_token = True
                    elif tipo == 'FIM_PROGRAMA':
                        found_birl_token = True

                    # Lógica para verificação de balanceamento (usando a pilha)
                    # O lexema que vai para a pilha para PARENTESES_ABRE é 'Coloca anilha'
                    if tipo == 'PARENTESES_ABRE':
                        delimiters_stack.append((lexema, num_linha, tipo))
                    elif tipo == 'PARENTESES_FECHA': # O lexema que vem do match é 'Tira anilha'
                        if not delimiters_stack:
                            erros_estrutura.append(f"Erro de Balanceamento na linha {num_linha}: '{lexema}' encontrado sem delimitador de abertura correspondente.")
                        else:
                            last_open_delimiter_info = delimiters_stack.pop()
                            last_open_lexema = last_open_delimiter_info[0]
                            last_open_line = last_open_delimiter_info[1]
                            last_open_type = last_open_delimiter_info[2]
                            
                            # O delimiter_map agora vai procurar por 'Tira anilha' (o lexema de fechamento)
                            # e verificar se o tipo de abertura corresponde.
                            # O lexema de fechamento deve ser o que foi puxado para a pilha (last_open_lexema)
                            if delimiter_map.get(lexema) != last_open_type: # Aqui, 'lexema' é "Tira anilha"
                                erros_estrutura.append(f"Erro de Balanceamento na linha {num_linha}: '{lexema}' encontrado, mas esperava fechamento para '{last_open_lexema}' (linha {last_open_line}).")
                                        
                    # Atualiza o previous_meaningful_token_type e last_meaningful_token_lexema APÓS todas as checagens
                    previous_meaningful_token_type = tipo 
                    last_meaningful_token_lexema = lexema


                pos_coluna += len(lexema)
            else:
                # Se o regex não casar, adiciona como erro léxico e avança
                resultado_tokens.append([num_linha, linha[pos_coluna], 'ERRO LÉXICO'])
                previous_meaningful_token_type = None 
                last_meaningful_token_lexema = None
                pos_coluna += 1
        
    # --- Verificações Finais de Estrutura (Pós-Processamento) ---
    
    # 1. Validação de BORA e BIRL! (Mais precisa agora, com base na sequência de tokens significativos)
    meaningful_sequence = [
        t for t in resultado_tokens 
        if t[2] not in [
            'SKIP', 'NEWLINE', 'COMENTARIO', 'ERRO LÉXICO', 
            'ERRO LÉXICO - ASPAS NÃO FECHADAS', 'ERRO LÉXICO - CARACTERE INVÁLIDO'
        ]
    ]

    if not meaningful_sequence or meaningful_sequence[0][2] != 'INICIO_PROGRAMA':
        erros_estrutura.append("Erro de Estrutura: O programa deve começar com 'BORA'.")

    if not meaningful_sequence or meaningful_sequence[-1][2] != 'FIM_PROGRAMA':
        erros_estrutura.append("Erro de Estrutura: O programa deve terminar com 'BIRL!'.")

    # 2. Erros de Balanceamento de Delimitadores (qualquer coisa que sobrou na pilha)
    while delimiters_stack:
        unclosed_lexema, unclosed_line, _ = delimiters_stack.pop()
        erros_estrutura.append(f"Erro de Balanceamento na linha {unclosed_line}: Delimitador '{unclosed_lexema}' aberto e não fechado.")

    # Remove duplicidades nos erros de estrutura/balanceamento
    erros_estrutura = list(dict.fromkeys(erros_estrutura))

    return {'tokens': resultado_tokens, 'erros_estrutura': erros_estrutura}