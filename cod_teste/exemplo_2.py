# EX. 2: CALCULADORA DE IMC 

BORA # Início do programa
MONSTRO peso TASAINDODAJAULA 85.5 # Declaração de variável para o peso (com decimal); Atribuição de valor
MONSTRO altura TASAINDODAJAULA 1.75 # Declaração de variável para a altura (com decimal); Atribuição de valor

# Cálculo do IMC utilizando os novos tokens para parênteses
MONSTRO altura_quadrado TASAINDODAJAULA Coloca anilha altura * altura Tira anilha # Calcula altura ao quadrado
MONSTRO imc TASAINDODAJAULA peso / altura_quadrado # Divide o peso pela altura ao quadrado

GRITA "Seu IMC é: " # Imprime uma string literal
GRITA imc # Imprime o valor da variável 'imc'
BIRL! # Fim do programa