import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Carregar credenciais do arquivo credentials.json
with open("credentials.json", "r") as f:
    credentials = json.load(f)

username = credentials.get("username")
password = credentials.get("password")

# Iniciar o WebDriver (Chrome, por exemplo)
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 20)

# Acessar a página de login
driver.get("https://elearning.uab.pt/my/courses.php")
wait.until(EC.presence_of_element_located((By.ID, "login")))

# Preencher os campos de login
driver.find_element(By.ID, "username").send_keys(username)
password_field = driver.find_element(By.ID, "password")
password_field.send_keys(password)
password_field.send_keys(Keys.ENTER)

# Aguardar a lista de cursos aparecer
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.list-group")))
print("Login efetuado com sucesso!")
time.sleep(2)

# Obter os URLs das disciplinas
discipline_elements = driver.find_elements(By.CSS_SELECTOR, "ul.list-group li.course-listitem a.aalink.coursename")
discipline_urls = [elem.get_attribute("href") for elem in discipline_elements]
print(f"Foram encontradas {len(discipline_urls)} disciplinas.")

input("Pressione Enter para começar a abrir cada disciplina...")

# Iterar sobre cada disciplina usando os URLs extraídos
for index, url in enumerate(discipline_urls, start=1):
    try:
        print(f"\nAbrindo disciplina {index}: {url}")
        driver.get(url)
        # Aguarda que a página carregue (usamos o <body> como referência)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Tempo fixo de espera para teste (7 segundos)
        wait_time = 7
        print(f"Aguardando {wait_time} segundos na disciplina {index}...")
        time.sleep(wait_time)
        
        # Retorna à página de cursos e aguarda que a lista seja recarregada
        driver.get("https://elearning.uab.pt/my/courses.php")
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.list-group")))
    except Exception as e:
        print(f"Erro ao processar a disciplina {index}: {e}")

print("\nProcessamento concluído, fechando o navegador.")
driver.quit()
