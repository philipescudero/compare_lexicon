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
    # ALTERADO AQUI: Agora, PARENTESES_ABRE e FECHA são apenas as palavras-chave
    ('PARENTESES_ABRE', r'\bColoca anilha\b'), # Apenas a palavra-chave
    ('PARENTESES_FECHA', r'\bTira anilha\b'),   # Apenas a palavra-chave
    ('VIRGULA', r','),
    ('DOIS_PONTOS', r':'),

    # Literais
    ('NUM_DECIMAL', r'\b\d+\.\d+\b'),
    ('NUM', r'\b\d+\b'),
    ('STRING', r'"[^"\n]*"'),

    # Comentário: Deve vir antes de ID para não confundir com palavras-chave ou IDs
    ('COMENTARIO', r'#[^\n]*'),

    ('ID', r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'),

    # Ignorados
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),

    # Erro
    ('MISMATCH', r'.'), # O '.' agora capturará '(' e ')' como MISMATCH
]

token_regex = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC))

def analisar_codigo(codigo: str) -> dict:
    """
    Realiza a análise léxica de um código-fonte BIRL e verifica a estrutura básica.

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

    found_bora_struct = False
    found_birl_struct = False

    for num_linha, linha in enumerate(linhas_codigo, start=1):
        pos_coluna = 0
        while pos_coluna < len(linha):
            match = token_regex.match(linha, pos_coluna)

            if match:
                tipo = match.lastgroup
                lexema = match.group(tipo)

                if tipo == 'SKIP' or tipo == 'NEWLINE':
                    # Ignorar espaços em branco e novas linhas na saída
                    pass
                elif tipo == 'COMENTARIO':
                    # Incluir comentários na saída
                    resultado_tokens.append([num_linha, lexema, tipo])
                elif tipo == 'MISMATCH':
                    resultado_tokens.append([num_linha, lexema, 'ERRO LÉXICO'])
                else:
                    # Adicionar todos os outros tokens, incluindo BORA e BIRL!
                    resultado_tokens.append([num_linha, lexema, tipo])

                    # Lógica para verificação de estrutura (agora separada da adição do token)
                    if tipo == 'INICIO_PROGRAMA' and not found_bora_struct:
                        meaningful_tokens_so_far = [t for t in resultado_tokens if t[2] not in ['SKIP', 'NEWLINE', 'COMENTARIO']]
                        if meaningful_tokens_so_far and meaningful_tokens_so_far[0][1] == lexema:
                            found_bora_struct = True
                        else:
                            erros_estrutura.append(f"Erro na linha {num_linha}: 'BORA' deve ser o primeiro comando do programa. Lexema: '{lexema}'")

                    elif tipo == 'FIM_PROGRAMA':
                        found_birl_struct = True

                pos_coluna += len(lexema)
            else:
                # Trata caracteres que não casam com nenhum token.
                resultado_tokens.append([num_linha, linha[pos_coluna], 'ERRO LÉXICO'])
                pos_coluna += 1

    # Verificação da estrutura final (BORA e BIRL!)
    if not found_bora_struct:
        erros_estrutura.append("Erro de Estrutura: O programa deve começar com 'BORA'.")

    if not found_birl_struct:
        erros_estrutura.append("Erro de Estrutura: O programa deve terminar com 'BIRL!'.")
    elif found_birl_struct:
        meaningful_tokens_all = [t for t in resultado_tokens if t[2] not in ['SKIP', 'NEWLINE', 'COMENTARIO', 'ERRO LÉXICO']]
        
        if not meaningful_tokens_all or meaningful_tokens_all[-1][1] != "BIRL!":
            erros_estrutura.append("Erro de Estrutura: 'BIRL!' deve ser o último comando significativo do programa.")
            
    # Remove duplicidades nos erros de estrutura
    erros_estrutura = list(dict.fromkeys(erros_estrutura))

    return {'tokens': resultado_tokens, 'erros_estrutura': erros_estrutura}