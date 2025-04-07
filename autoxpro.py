import os
import json
import time
import re
import urllib.parse
from urllib.parse import urlparse, unquote, parse_qs
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup  # Necessário: pip install beautifulsoup4

# --- Configurações ---
# Caminho base onde serão armazenadas as pastas das disciplinas
base_folder = r"C:\Users\Ralfe\OneDrive - Universidade Aberta\24-25\Semestre 2"

# --- Carregar Credenciais ---
with open("credentials.json", "r") as f:
    credentials = json.load(f)
username = credentials.get("username")
password = credentials.get("password")

# --- Iniciar WebDriver (Chrome) ---
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 20)

# --- Login ---
driver.get("https://elearning.uab.pt/my/courses.php")
wait.until(EC.presence_of_element_located((By.ID, "login")))
driver.find_element(By.ID, "username").send_keys(username)
password_field = driver.find_element(By.ID, "password")
password_field.send_keys(password)
password_field.send_keys(Keys.ENTER)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.list-group")))
print("Login efetuado com sucesso!")
time.sleep(2)

# --- Coletar e Filtrar Disciplinas ---
discipline_elements = driver.find_elements(By.CSS_SELECTOR, "ul.list-group li.course-listitem a.aalink.coursename")
courses = [(elem.get_attribute("href"), elem.text.strip()) for elem in discipline_elements]
print(f"Foram encontradas {len(courses)} disciplinas.")

# Exemplo de filtro: ignorar "Linguagens e Computação"
filtered_out = [(url, name) for url, name in courses if "Linguagens e Computação" in name]
courses_to_process = [(url, name) for url, name in courses if "Linguagens e Computação" not in name]

if filtered_out:
    print("As seguintes disciplinas serão ignoradas (já concluídas):")
    for url, name in filtered_out:
        print(f" - {name}")

print(f"\nSerão processadas {len(courses_to_process)} disciplinas.")

# --- Sessão Requests para Downloads Autenticados ---
session = requests.Session()
for cookie in driver.get_cookies():
    session.cookies.set(cookie['name'], cookie['value'])

# Função para extrair o nome do arquivo via Content-Disposition
def get_filename_from_cd(cd):
    if not cd:
        return None
    fname = re.findall('filename="([^"]+)"', cd)
    if not fname:
        fname = re.findall(r'filename=([^;]+)', cd)
    return fname[0].strip() if fname else None

# Função para extrair o ID do recurso do Moodle
def get_moodle_id(url):
    """
    Retorna o valor de ?id=XXX se existir; caso contrário, retorna None.
    Isso ajuda a evitar downloads duplicados quando o mesmo recurso aparece em várias seções.
    """
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    return query_params.get("id", [None])[0]

# Conjunto para armazenar IDs de recursos já baixados
processed_ids = set()

# --- Processar cada disciplina ---
for index, (course_url, course_name) in enumerate(courses_to_process, start=1):
    try:
        print(f"\nProcessando disciplina {index}: {course_name}")
        driver.get(course_url)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(5)

        # Obter título da página ou usar o nome da disciplina
        try:
            page_title = driver.find_element(By.TAG_NAME, "h1").text.strip()
            course_display_name = page_title if page_title else course_name
        except Exception:
            course_display_name = course_name

        # Criar pasta da disciplina
        safe_name = "".join([c if c.isalnum() or c in " ._-" else "_" for c in course_display_name])
        discipline_folder = os.path.join(base_folder, safe_name)
        os.makedirs(discipline_folder, exist_ok=True)
        print(f"Pasta da disciplina: {discipline_folder}")

        # Subpastas: Geral e Turma
        geral_folder = os.path.join(discipline_folder, "Geral")
        turma_folder = os.path.join(discipline_folder, "Turma")
        os.makedirs(geral_folder, exist_ok=True)
        os.makedirs(turma_folder, exist_ok=True)

        # Coletar links de resource, url e page
        file_links = driver.find_elements(
            By.XPATH,
            "//a[contains(@href, '/mod/resource/') or contains(@href, '/mod/url/') or contains(@href, '/mod/page/')]"
        )
        print(f"Foram encontrados {len(file_links)} links de material na disciplina '{course_display_name}'.")

        for file_link in file_links:
            file_url = file_link.get_attribute("href")
            # Tentar obter o ID do recurso para evitar duplicados
            moodle_id = get_moodle_id(file_url)
            if not moodle_id:
                moodle_id = f"NOID-{file_url}"

            if moodle_id in processed_ids:
                print(f" - Pulando recurso duplicado (id={moodle_id}): {file_url}")
                continue
            processed_ids.add(moodle_id)

            # Tentar obter um nome base a partir do texto do link
            base_file_name = file_link.text.strip() or os.path.basename(urlparse(file_url).path)
            base_file_name = unquote(base_file_name)

            # Fazer HEAD para tentar extrair Content-Disposition
            try:
                head_resp = session.head(file_url, allow_redirects=True)
                cd = head_resp.headers.get("Content-Disposition")
                header_filename = get_filename_from_cd(cd)
            except Exception as e:
                print(f"   Erro ao fazer HEAD: {e}")
                header_filename = None

            final_file_name = header_filename if header_filename else base_file_name

            # Se não houver extensão, adicionar .pdf ou .html, etc.
            if not os.path.splitext(final_file_name)[1]:
                if "/mod/resource/" in file_url:
                    ext = os.path.splitext(urlparse(file_url).path)[1] or ".pdf"
                else:
                    ext = ".html"
                final_file_name += ext

            # Escolhe a subpasta
            if "turma" in final_file_name.lower() or "turma" in file_url.lower():
                target_folder = turma_folder
            else:
                target_folder = geral_folder

            file_path = os.path.join(target_folder, final_file_name)
            counter = 1
            while os.path.exists(file_path):
                name_part, ext = os.path.splitext(final_file_name)
                file_path = os.path.join(target_folder, f"{name_part}_{counter}{ext}")
                counter += 1

            # Se for "mod/page/", extrair conteúdo textual e salvar .txt (exemplo)
            if "/mod/page/" in file_url:
                print(f" - (Página) Salvando conteúdo texto de {file_url} como .txt")
                try:
                    resp = session.get(file_url, allow_redirects=True)
                    if resp.status_code == 200:
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(resp.text, "html.parser")

                        # Remover scripts, styles etc.
                        for s in soup(["script", "style"]):
                            s.decompose()

                        page_text = soup.get_text(separator="\n").strip()

                        txt_file_name = os.path.splitext(os.path.basename(file_path))[0] + ".txt"
                        txt_path = os.path.join(target_folder, txt_file_name)

                        with open(txt_path, "w", encoding="utf-8") as txtfile:
                            txtfile.write(page_text)

                        print(f"   Texto extraído: {txt_file_name}")
                    else:
                        print(f"   Falha ao obter HTML (HTTP {resp.status_code}): {file_url}")
                except Exception as e:
                    print(f"   Erro ao extrair texto da página: {e}")

            else:
                # Download normal (PDF, DOC, etc.)
                print(f" - Baixando arquivo: {final_file_name} para {target_folder}")
                try:
                    download_resp = session.get(file_url, stream=True)
                    if download_resp.status_code == 200:
                        with open(file_path, "wb") as f:
                            for chunk in download_resp.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        print(f"   Download completo: {os.path.basename(file_path)}")
                    else:
                        print(f"   Falha no download (HTTP {download_resp.status_code}): {final_file_name}")
                except Exception as e:
                    print(f"   Erro ao baixar {final_file_name}: {e}")

        # Listar arquivos da pasta "Turma"
        turma_files = os.listdir(turma_folder)
        print("Conteúdo da pasta 'Turma':")
        if turma_files:
            for f in turma_files:
                print(f" - {f}")
        else:
            print(" - Pasta 'Turma' vazia.")

        time.sleep(2)

    except Exception as e:
        print(f"Erro ao processar disciplina {index} ({course_name}): {e}")

print("\nProcessamento de downloads concluído, fechando o navegador.")
driver.quit()
