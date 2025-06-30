====================================================================================================
1. Introdução
====================================================================================================

Bem-vindo ao Analisador Léxico da Linguagem BIRL!

Este projeto é um analisador léxico para a linguagem de programação BIRL!, inspirada na cultura
"maromba" brasileira. Ele foi desenvolvido como parte da disciplina de Compiladores e serve para
quebrar o código-fonte BIRL! em uma sequência de tokens (as menores unidades significativas do código),
identificando palavras-chave, identificadores, operadores, literais e comentários.

Além da análise léxica, o sistema verifica a estrutura básica do programa, exigindo que ele comece
com "BORA" e termine com "BIRL!".

O projeto é uma aplicação web simples, construída com Flask (Python), permitindo que o usuário
insira código diretamente ou faça upload de um arquivo, visualize os tokens resultantes e consulte
uma tabela completa de tokens da linguagem.

====================================================================================================
2. Pré-requisitos
====================================================================================================

Para rodar este projeto, você precisará ter o Python e o pip (gerenciador de pacotes do Python)
instalados em seu sistema.

* **Python:** Versão 3.6 ou superior (recomendado Python 3.9+)
    Você pode baixar o Python em: https://www.python.org/downloads/

* **pip:** Geralmente vem instalado com o Python. Para verificar, abra seu terminal/prompt
    de comando e digite: `pip --version`

====================================================================================================
3. IDE Utilizada (Recomendado)
====================================================================================================

Para o desenvolvimento e execução deste projeto, a IDE Visual Studio Code (VS Code) foi utilizada
e é altamente recomendada.

O VS Code oferece um ambiente leve, mas poderoso, com excelentes extensões para desenvolvimento
Python e web (HTML, CSS, JavaScript), como realce de sintaxe, depuração e um terminal integrado
que facilitam bastante o fluxo de trabalho.

* **Download VS Code:** https://code.visualstudio.com/download

Após instalar o VS Code, é útil instalar as seguintes extensões (pesquise por elas no painel de
extensões dentro do VS Code):

* **Python (Microsoft):** Essencial para recursos de Python.

====================================================================================================
4. Como Rodar o Projeto
====================================================================================================

Siga os passos abaixo para configurar e executar o Analisador Léxico BIRL!:

**Passo 1: Clone ou Baixe o Projeto**

Se você estiver usando Git, clone o repositório:
```bash
git clone <URL_DO_SEU_REPOSITORIO>

**Passo 2: Inicialização

pip install requirements.txt

python app.py 