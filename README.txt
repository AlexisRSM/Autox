# Script de Download Automático do Moodle (PlataformAbERTA)

Este script realiza login no Moodle da Universidade Aberta (PlataformAbERTA), identifica as disciplinas e baixa automaticamente materiais de estudo (PDFs, links, páginas, etc.).

## Requisitos

- **Python 3.7+**  
- **Bibliotecas**:  
  - `selenium`  
  - `requests`  
  - `beautifulsoup4` (para extrair texto das páginas HTML)  

- **Driver do Chrome** compatível com a versão instalada do Google Chrome ([ChromeDriver](https://chromedriver.chromium.org/)).  

## Instalação

1. Clone ou baixe este repositório.
2. Crie (ou use) um ambiente virtual do Python:  
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate.bat # Windows
Instale as dependências:

bash
Copy
Edit
pip install -r requirements.txt
Se não tiver um requirements.txt, instale manualmente:

bash
Copy
Edit
pip install selenium requests beautifulsoup4
Baixe o ChromeDriver para sua versão do Google Chrome e coloque o executável no PATH ou na mesma pasta do script.

Configuração
Crie um arquivo credentials.json na mesma pasta do script, com o formato:

json
Copy
Edit
{
    "username": "SEU_USUARIO_MOODLE",
    "password": "SUA_SENHA_MOODLE"
}
No script, há uma variável base_folder apontando para o local onde os arquivos serão salvos. Ajuste conforme necessário:

python
Copy
Edit
base_folder = r"C:\Users\SEU_USUARIO\OneDrive - Universidade Aberta\24-25\Semestre 2"
Uso
Com o ambiente virtual ativo, execute:

bash
Copy
Edit
python autox.py
(Ou o nome que você deu ao arquivo.)

O script:

Faz login no Moodle usando as credenciais de credentials.json.

Coleta a lista de disciplinas e filtra algumas (ex.: “Linguagens e Computação”).

Para cada disciplina:

Cria pastas para “Geral” e “Turma”.

Baixa arquivos (ex. PDFs) em /mod/resource/.

Em /mod/page/, extrai o texto em um arquivo .txt.

Evita duplicar downloads usando o id do recurso no Moodle.

Lista o que foi baixado na pasta Turma ao final de cada disciplina.

No final, o navegador é fechado e o script encerra.

Personalizações
Ajuste o trecho de filtro de disciplinas no final do script se desejar incluir ou excluir outras disciplinas específicas.

Você pode comentar ou remover o trecho if "/mod/page/" in file_url: se não quiser extrair o texto de páginas.

Para armazenar HTML em vez de texto, basta trocar .txt por .html e salvar resp.text completo (ou algo intermediário com BeautifulSoup).

Licença