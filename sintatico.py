# sintatico.py

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.errors = [] # Agora vai armazenar tuplas: [linha, mensagem_limpa]

    def current_token(self):
        # Retorna o token atual, ou None se chegamos ao fim dos tokens
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None # Representa o End Of File (EOF) ou fim dos tokens

    def advance(self):
        # Avança para o próximo token
        self.current_token_index += 1
        return self.current_token()

    def add_error(self, message, line=None):
  
        error_line = line 
        if error_line is None: 
            if self.current_token(): 
                error_line = self.current_token()[0]
            elif self.tokens: 
                error_line = self.tokens[-1][0]
            else: 
                error_line = "N/A"

        
        error_entry = (error_line, message)
        
        
        if not self.errors or self.errors[-1] != error_entry:
            self.errors.append(error_entry)

    def match(self, expected_type):
   
        token = self.current_token()
        if token and token[2] == expected_type:
            self.advance()
            return True
        
       
        if token:
            self.add_error(f"Token inesperado '{token[1]}'. Esperava '{expected_type}'.", token[0]) # Passa a linha do token real
        else:
            self.add_error(f"Fim de arquivo inesperado. Esperava '{expected_type}'.") # add_error vai pegar a linha "N/A" ou do último token
        return False


    def parse_program(self):
        
        if self.match('INICIO_PROGRAMA'): # Espera o token 'BORA'
            self.parse_command_list() # Tenta analisar a lista de comandos
            if not self.match('FIM_PROGRAMA'): # Espera o token 'BIRL!'
                self.add_error("Comando 'BIRL!' ausente ou mal posicionado no final do programa.")
        else:
            self.add_error("Comando 'BORA' ausente ou mal posicionado no início do programa.")
        
        # Verifica se há tokens restantes após o programa ser parseado (indicando lixo no código)
        if self.current_token():
            self.add_error(f"Tokens extras após 'BIRL!': '{self.current_token()[1]}'.", self.current_token()[0])


    def parse_command_list(self):
       
        stop_tokens = ['FIM_PROGRAMA', 'ELIF', 'ELSE', 'PARENTESES_FECHA'] 

        while self.current_token() and self.current_token()[2] not in stop_tokens:
            start_index_before_command = self.current_token_index # Guarda a posição para detectar se o parser avançou

            if not self.parse_command(): 
               
                if self.current_token_index == start_index_before_command and self.current_token():
                    # Adiciona um erro genérico para o comando não processado e força o avanço
                    self.add_error(f"Erro: Não foi possível processar o comando '{self.current_token()[1]}'. Tentando sincronizar.", self.current_token()[0])
                    self.advance() # Força o avanço para evitar loop infinito
                elif not self.current_token(): # Se não há mais tokens, sai do loop
                    break
            # Se parse_command() foi bem-sucedido, ele já avançou o token, o loop recomeça para o próximo.


    def parse_command(self):
        # Regra: <Comando> ::= <DeclaracaoVar> | <Atribuicao> | <Impressao> | <Condicional> | <Loop> | <DeclaracaoFuncao> | <ChamadaFuncao>
        token = self.current_token()
        if not token: return False # Se não há token, não há comando para parsear

        # Tenta casar com cada tipo de comando pelo seu token inicial
        if token[2] == 'VARIAVEL': # MONSTRO
            return self.parse_declaration_var()
        elif token[2] == 'PRINT': # GRITA
            return self.parse_print()
        elif token[2] == 'IF': # CONFERE_AI
            return self.parse_conditional()
        elif token[2] == 'WHILE': # TREINA ATÉ
            return self.parse_loop()
        elif token[2] == 'FUNC': # FICA GRANDE
            return self.parse_declaration_function()
        elif token[2] == 'CALL': # CHAMA
            return self.parse_call_function()
        elif token[2] == 'ID': # Pode ser início de Atribuição
            if self.current_token_index + 1 < len(self.tokens):
                next_token_info = self.tokens[self.current_token_index + 1] 
                if next_token_info[2] in ['ATRIBUICAO', 'OP_ATRIBUICAO_COMPOSTA']:
                    return self.parse_assignment()
            
            self.add_error(f"Comando inválido. Esperava 'MONSTRO', 'GRITA', 'CONFERE_AI', 'TREINA ATÉ', 'FICA GRANDE', 'CHAMA' ou uma atribuição. Encontrou: '{token[1]}'", token[0])
            self.advance() # Consome o token para tentar continuar e evitar loops
            return False
        
        else: # Nenhum comando conhecido inicia com este token
            self.add_error(f"Comando não reconhecido ou mal formado: '{token[1]}'", token[0])
            self.advance() # Força o avanço para evitar loops
            return False

    def parse_declaration_var(self):
        # Regra: <DeclaracaoVar> ::= VARIAVEL ID ATRIBUICAO <Expressao>
        if self.match('VARIAVEL'): # Espera 'MONSTRO'
            if self.match('ID'): # Espera o nome da variável
                if self.match('ATRIBUICAO'): # Espera 'TASAINDODAJAULA'
                    return self.parse_expression() # Espera o valor/expressão a ser atribuído
        return False # Retorna False se qualquer match falhar (match já adiciona o erro)

    def parse_assignment(self):
        # Regra: <Atribuicao> ::= ID (ATRIBUICAO | OP_ATRIBUICAO_COMPOSTA) <Expressao>
        if self.match('ID'): # Espera o nome da variável a ser atribuída
            if self.current_token() and self.current_token()[2] in ['ATRIBUICAO', 'OP_ATRIBUICAO_COMPOSTA']:
                self.advance() # Consome o operador de atribuição
                return self.parse_expression() # Espera a expressão do valor
        return False

    def parse_print(self):
        # Regra: <Impressao> ::= PRINT PARENTESES_ABRE <ListaExpressoes> PARENTESES_FECHA
        if self.match('PRINT'): # Espera 'GRITA'
            if self.match('PARENTESES_ABRE'): # Espera 'Coloca anilha'
                # Tenta analisar a lista de expressões dentro dos parênteses
                if self.parse_expression_list(): 
                    # Espera 'Tira anilha' para fechar
                    if self.match('PARENTESES_FECHA'): 
                        return True # GRITA parseado com sucesso
                    else: # Erro: Faltou 'Tira anilha'
                        self.add_error(f"Delimitador 'Tira anilha' ausente após lista de impressão.", self.current_token()[0] if self.current_token() else "N/A")
                else: # Erro: Expressão inválida/ausente dentro do GRITA(...)
                    self.add_error(f"Expressão ou lista de expressões inválida dentro de GRITA Coloca anilha ... Tira anilha.", self.current_token()[0] if self.current_token() else "N/A")
                    return False
            else: # Erro: Faltou 'Coloca anilha' após GRITA
                self.add_error(f"Delimitador 'Coloca anilha' ausente após 'GRITA'.", self.current_token()[0] if self.current_token() else "N/A")
                return False
        return False 


    def parse_expression_list(self):
        
        if not self.parse_expression(): # Espera a primeira expressão
            # Erro já é adicionado em parse_expression(). Aqui, apenas indicamos que falhou.
            return False
        
        while self.current_token() and self.current_token()[2] == 'VIRGULA':
            self.advance() # Consome a vírgula
            if not self.parse_expression(): # Espera outra expressão após a vírgula
                self.add_error(f"Expressão ausente ou mal formada após vírgula na lista de expressões.", self.current_token()[0] if self.current_token() else "N/A")
                return False
        return True # Retorna True mesmo se não houver mais vírgulas (lista pode ter apenas 1 item)

    def parse_expression(self):
        # Regra: <Expressao> ::= <Termo> (<Operador> <Termo>)*
        if not self.parse_term(): # Uma expressão deve começar com um termo
            return False
        
        
        while self.current_token() and \
              self.current_token()[2] in ['OP_ARITMETICO', 'OP_LOGICO', 'OP_RELACIONAL_OU_IGUALDADE']:
            self.advance() # Consome o operador
            if not self.parse_term(): # Espera outro termo após o operador
                self.add_error(f"Expressão incompleta. Esperava um termo após o operador '{self.tokens[self.current_token_index-1][1]}'.", self.current_token()[0] if self.current_token() else "N/A")
                return False 
        
    
        EXPRESSION_END_DELIMITERS = [
            'DOIS_PONTOS',       # Fim de condição IF/WHILE/FUNC
            'PARENTESES_FECHA',  # Fim de (expressão) ou (arg1, arg2)
            'VIRGULA',           # Separador em lista de expressões/argumentos
            'FIM_PROGRAMA',      # Fim do programa
            'ELIF',              # Início de ELIF
            'ELSE',              # Início de ELSE
            'VARIAVEL',          # Início de MONSTRO
            'PRINT',             # Início de GRITA
            'IF',                # Início de CONFERE_AI
            'WHILE',             # Início de TREINA ATÉ
            'FUNC',              # Início de FICA GRANDE
            'CALL',              # Início de CHAMA
            'ID',                # Início de ID (que pode ser atribuição)
            None                 # Fim do arquivo (EOF)
        ]
        
     
        if self.current_token() and \
           self.current_token()[2] not in EXPRESSION_END_DELIMITERS:
            
            # Se o token atual é outro TERMO (NUM, ID, STRING, etc.) significa que o operador está faltando entre dois termos
            if self.current_token()[2] in ['NUM', 'NUM_DECIMAL', 'STRING', 'BOOLEAN_VERDADEIRO', 'BOOLEAN_FALSO', 'ID', 'PARENTESES_ABRE']:
                 self.add_error(f"Expressão mal formada: Operador ausente entre '{self.tokens[self.current_token_index-1][1]}' e '{self.current_token()[1]}'.", self.current_token()[0])
                 self.advance() # Avança o token para tentar sincronizar
                 return False 
            else:
                 # Outro tipo de token inesperado no meio da expressão
                 self.add_error(f"Expressão mal formada: Token inesperado '{self.current_token()[1]}' após '{self.tokens[self.current_token_index-1][1]}'.", self.current_token()[0])
                 self.advance()
                 return False
        return True # Se a expressão foi analisada sem erros nesse ponto, retorna True


    def parse_term(self):
        
        token = self.current_token()
        if not token: 
            self.add_error("Termo inesperado: fim de arquivo ou token inválido.", "N/A")
            return False

        if token[2] in ['NUM', 'NUM_DECIMAL', 'STRING', 'BOOLEAN_VERDADEIRO', 'BOOLEAN_FALSO', 'ID']:
            self.advance()
            return True
        elif token[2] == 'PARENTESES_ABRE': # Coloca anilha
            self.advance() # Consome PARENTESES_ABRE
            if not self.parse_expression():
                self.add_error(f"Expressão incompleta dentro de parênteses.", token[0])
                return False
            if not self.match('PARENTESES_FECHA'): # Tira anilha
                return False 
            return True
        else:
            self.add_error(f"Termo inesperado na expressão: '{token[1]}'", token[0])
            self.advance()
            return False


    def parse_conditional(self):
        # <Condicional> ::= IF <Expressao> DOIS_PONTOS <ListaComandos> <ElifOpcional> <ElseOpcional>
        if self.match('IF'): # CONFERE_AI
            if self.parse_expression(): # Condição
                if self.match('DOIS_PONTOS'): # Dois pontos após a condição
                    self.parse_command_list() # Comandos dentro do IF
                    self.parse_elif_optional() # Partes opcionais
                    self.parse_else_optional() # Partes opcionais
                    return True
                else: 
                    self.add_error(f"Dois pontos ':' ausente após condição 'CONFERE_AI'.", self.current_token()[0] if self.current_token() else "N/A")
            return False 
        return False

    def parse_elif_optional(self):
       
        while self.current_token() and self.current_token()[2] == 'ELIF': # CONFERE_MAIS
            self.advance() # Consome ELIF
            if self.parse_expression(): # Condição do ELIF
                if self.match('DOIS_PONTOS'): # Dois pontos
                    self.parse_command_list() # Comandos do ELIF
                else:
                    self.add_error(f"Dois pontos ':' ausente após condição 'CONFERE_MAIS'.", self.current_token()[0] if self.current_token() else "N/A")
                    return False
            else:
                self.add_error(f"Expressão de condição ausente ou inválida após 'CONFERE_MAIS'.", self.current_token()[0] if self.current_token() else "N/A")
                return False
        return True

    def parse_else_optional(self):
       
        if self.current_token() and self.current_token()[2] == 'ELSE': # OU_NAO
            self.advance() # Consome ELSE
            if self.match('DOIS_PONTOS'): # Dois pontos
                self.parse_command_list() # Comandos do ELSE
            else:
                self.add_error(f"Dois pontos ':' ausente após 'OU_NAO'.", self.current_token()[0] if self.current_token() else "N/A")
                return False
        return True

    def parse_loop(self):
       
        if self.match('WHILE'): # TREINA ATÉ
            if self.parse_expression(): # Condição do loop
                if self.match('DOIS_PONTOS'): # Dois pontos
                    self.parse_command_list() # Comandos do loop
                    return True
                else: # Erro: DOIS_PONTOS faltando
                    self.add_error(f"Dois pontos ':' ausente após condição 'TREINA ATÉ'.", self.current_token()[0] if self.current_token() else "N/A")
            return False
        return False

    def parse_declaration_function(self):
        
        if self.match('FUNC'): # FICA GRANDE
            if self.match('ID'): # Nome da função
                if self.match('PARENTESES_ABRE'): # Coloca anilha
                    self.parse_parameters_optional() # Parâmetros opcionais
                    if self.match('PARENTESES_FECHA'): # Tira anilha
                        if self.match('DOIS_PONTOS'): # Dois pontos
                            self.parse_command_list() # Comandos da função
                            return True
                        else: # Erro: DOIS_PONTOS faltando
                            self.add_error(f"Dois pontos ':' ausente após declaração da função.", self.current_token()[0] if self.current_token() else "N/A")
                    return False
                return False
            return False
        return False

    def parse_parameters_optional(self):
        # <ListaParametrosOpcional> ::= <ListaParametros> | ε
        # <ListaParametros> ::= ID | ID VIRGULA <ListaParametros>
        if self.current_token() and self.current_token()[2] == 'ID':
            self.match('ID') # Consome o primeiro parâmetro
            while self.current_token() and self.current_token()[2] == 'VIRGULA':
                self.advance() # Consome a vírgula
                if not self.match('ID'): # Espera outro ID
                    self.add_error(f"Identificador ausente após vírgula na lista de parâmetros.", self.current_token()[0] if self.current_token() else "N/A")
                    return False
        return True

    def parse_call_function(self):
        # <ChamadaFuncao> ::= CALL ID PARENTESES_ABRE <ListaArgumentosOpcional> PARENTESES_FECHA
        if self.match('CALL'): # CHAMA
            if self.match('ID'): # Nome da função
                if self.match('PARENTESES_ABRE'): # Coloca anilha
                    self.parse_arguments_optional() # Argumentos opcionais
                    if self.match('PARENTESES_FECHA'): # Tira anilha
                        return True
        return False

    def parse_arguments_optional(self):
        # <ListaArgumentosOpcional> ::= <ListaArgumentos> | ε
        # <ListaArgumentos> ::= <Expressao> | <Expressao> VIRGULA <ListaArgumentos>
        if self.current_token() and self.current_token()[2] != 'PARENTESES_FECHA':
            if not self.parse_expression(): # Espera a primeira expressão
                self.add_error(f"Expressão de argumento ausente ou mal formada.", self.current_token()[0] if self.current_token() else "N/A")
                return False
            while self.current_token() and self.current_token()[2] == 'VIRGULA':
                self.advance() # Consome a vírgula
                if not self.parse_expression(): # Espera outra expressão
                    self.add_error(f"Expressão de argumento ausente ou mal formada após vírgula.", self.current_token()[0] if self.current_token() else "N/A")
                    return False
        return True


    def parse(self):
        self.parse_program()
        return self.errors