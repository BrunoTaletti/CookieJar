# 👻 CookieJar

![Version](https://img.shields.io/badge/version-auto--update-blue.svg)
![Python](https://img.shields.io/badge/Python-3.x-yellow.svg)
![Build](https://img.shields.io/badge/build-PyInstaller%20%7C%20InnoSetup-success.svg)
![License](https://img.shields.io/badge/license-Ghost_Core-black.svg)

O **CookieJar** é uma ferramenta de desktop focada em performance e usabilidade, desenvolvida para gerenciar, formatar e validar arrays de cookies em formato JSON. Com uma interface moderna, nativa em dark mode, ele elimina erros de sintaxe de forma automatizada e agiliza operações de infraestrutura.

---

## 🚀 Funcionalidades

- **🔄 Organização Inteligente:** Corrige automaticamente erros comuns de sintaxe (como junção de arrays soltos `] [` ou objetos `} {`) e indenta o JSON perfeitamente.
- **🔍 Validação Rigorosa:** Checa se o texto de entrada é de fato uma estrutura JSON válida (Dicionário ou Lista), evitando falsos positivos.
- **🗜️ Minify:** Comprime o JSON validado, removendo espaços e quebras de linha para economizar processamento e armazenamento em requisições.
- **📋 Exportação Rápida:** Copie o resultado diretamente para a área de transferência com um clique ou exporte nativamente para arquivos `.txt` ou `.json`.
- **🌐 Auto-Update em Background:** O sistema verifica atualizações silenciosamente através de um servidor remoto e notifica o usuário na interface sem travar a aplicação.
- **UI/UX Premium:** Interface minimalista construída com `customtkinter`, projetada para fluxos de trabalho intensos.

---

## 🛠️ Tecnologias Utilizadas

- **[Python](https://www.python.org/):** Core da aplicação.
- **[CustomTkinter](https://customtkinter.tomschimansky.com/):** Framework de interface gráfica moderna.
- **[Requests](https://pypi.org/project/requests/):** Gerenciamento de requisições web para o sistema de update.
- **[PyInstaller](https://pyinstaller.org/):** Empacotamento do script em um executável autossuficiente `.exe`.
- **[Inno Setup](https://jrsoftware.org/isinfo.php):** Criação do instalador profissional do Windows.

---

## ⚙️ Como Usar (Ambiente de Desenvolvimento)

1. Clone o repositório:
   ```bash
   git clone [https://github.com/SEU_USUARIO/SEU_REPO.git](https://github.com/SEU_USUARIO/SEU_REPO.git)

2. Instale as dependências:
    ```bash
    pip install -r requirements.txt

3. Execute o aplicativo:
    ```bash
    python main.py

---

## 📦 Build e Distribuição

O projeto conta com uma esteira de build automatizada para Windows. O script build.bat gerencia o versionamento, compila o executável e gera o instalador em um único fluxo.

**Passo a passo para gerar uma nova Release:**

1. Execute o arquivo ```build.bat``` na raiz do projeto.

2. O script irá:

    - Incrementar automaticamente a versão no arquivo version.txt.

    - Limpar builds temporários antigos.

    - Compilar o main.py junto com os ícones usando o PyInstaller.

    - Chamar o Inno Setup (installer.iss) para empacotar o .exe gerado em um instalador profissional.

3. O instalador finalizado estará disponível na pasta setup.    

_(Nota: Certifique-se de que o Inno Setup 6 está instalado na sua máquina no diretório padrão especificado no .bat)._

---

## 📡 Configurando o Auto-Update

Para que o auto-update funcione em produção:

1. Hospede o arquivo ```version.txt``` (gerado pelo seu .bat) em um repositório público ou servidor estático (ex: GitHub Raw).

2. Atualize a variável ```UPDATE_TXT_URL``` no ```main.py``` com o link direto para este arquivo de texto.

3. Atualize a variável ```RELEASE_URL``` no ```main.py``` com o link para a página onde o usuário baixará a nova versão do instalador.

---

<div align="center">
<p><b>Ghost ©</b> - Operações e Infraestrutura de Elite.</p>
</div>
