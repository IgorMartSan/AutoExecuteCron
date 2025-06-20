from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import tempfile
import time

def testar_firefox():
    with tempfile.TemporaryDirectory() as temp_dir:
        options = FirefoxOptions()
        # options.headless = True  # Ative se quiser sem janela

        # ⚠️ Se precisar especificar o caminho do Firefox:
        # options.binary_location = "/usr/bin/firefox"  # Linux
        # options.binary_location = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"  # Windows

        # Exemplo de preferência: salvar arquivos no diretório temporário
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.dir", temp_dir)

        driver = webdriver.Firefox(options=options)
        driver.get("https://www.google.com")
        print("Página carregada:", driver.title)
        time.sleep(3)
        driver.quit()


testar_firefox()