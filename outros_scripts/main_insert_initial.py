from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from io import StringIO
import requests
import time


def coletar_dados_inmet(estacao_id="A511", data_inicio="01/01/2025", data_fim="01/05/2025"):
    # Configurar o navegador (sem diretório de download porque não vamos baixar nada)
    options = Options()
    #options.add_argument("--start-maximized")
    # options.add_argument("--headless=new")  # evita que o Chrome mande cabeçalho "webdriver"
    #options.add_argument("--headless")  # não abre janela
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--window-size=1920,1080")  # simula tela "grande" invisível
    
    driver = webdriver.Chrome(options=options)
    

    try:
        # Acesse a página do INMET para dados da estação
        driver.get(f"https://tempo.inmet.gov.br/tabela/mapa/{estacao_id}/2025-05-20")
        time.sleep(3)

        # Preenche as datas nos inputs
        inputs = driver.find_elements(By.TAG_NAME, "input")
        if len(inputs) >= 2:
            inputs[0].clear()
            inputs[0].send_keys(data_inicio)
            inputs[1].clear()
            inputs[1].send_keys(data_fim)


        time.sleep(5)

        # Clica no botão "Gerar Tabela"
        buttons = driver.find_elements(By.TAG_NAME, "button")

        # for btn in buttons:
        #     if "Gerar Tabela" in btn.text:
        #         btn.click()
        #         break

        # time.sleep(5)

        # Procura o link "Baixar CSV"
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            if "Baixar CSV" in link.text:
                csv_url = link.get_attribute("href")
                print("📎 Link do CSV encontrado:", csv_url)

                if csv_url.startswith("blob:"):
                    print("⚠️ Este link é um BLOB URL, que só pode ser acessado dentro do navegador.")
                    print("   Use a abordagem de download com Selenium para capturar esse arquivo.")
                else:
                    print("✅ URL direta para CSV. Você pode usar requests ou pandas.read_csv com isso.")
                break



        # 3. Clica em "Gerar Tabela"
        for btn in driver.find_elements(By.TAG_NAME, "button"):
            if "Gerar Tabela" in btn.text:
                btn.click()
                break



        # 4. Aguarda aparecer o botão "Baixar CSV"
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Baixar CSV')]"))
        )

        # 5. Captura o link do blob
        blob_link = driver.find_element(By.XPATH, "//a[contains(text(), 'Baixar CSV')]")
        blob_url = blob_link.get_attribute("href")
        print("📎 blob URL:", blob_url)

        # 6. Executa um script assíncrono para ler o conteúdo do blob
        script = """
            const url = arguments[0];
            const callback = arguments[1];
            fetch(url)
                .then(res => res.text())
                .then(data => callback(data))
                .catch(err => callback("ERRO: " + err));
        """
        csv_content = driver.execute_async_script(script, blob_url)

        if csv_content.startswith("ERRO:"):
            raise Exception(csv_content)
        
        time.sleep(5)

        # 7. Converte para DataFrame e tratar os dados
        df = pd.read_csv(StringIO(csv_content), sep=";")

        colunas_desejadas = [
            'Data',
            'Hora (UTC)',
            'Temp. Max. (C)',
            'Temp. Min. (C)',
            'Pto Orvalho Max. (C)',
            'Pto Orvalho Min. (C)'
        ]

        df = df[colunas_desejadas]

       

        # ✅ Renomear colunas para formato SYS_
        renomear = {
            'Temp. Max. (C)': 'SYS_TEMPERATURA_MAX',
            'Temp. Min. (C)': 'SYS_TEMPERATURA_MIN',
            'Pto Orvalho Max. (C)': 'SYS_PONTO_ORVALHO_MAX',
            'Pto Orvalho Min. (C)': 'SYS_PONTO_ORVALHO_MIN',
            'Data': 'Data',
            'Hora (UTC)': 'Hora (UTC)'
        }

        df = df.rename(columns=renomear)  

        df = df[list(renomear.values())]
        # Renomear colunas



        def converter_para_hora_utc(hora_str):
            hora_str = str(hora_str).zfill(4)  # Garante 4 dígitos: ex: 0 -> 0000, 100 -> 0100
            return f"{hora_str[:2]}:{hora_str[2:]}:00"

        # Cria a coluna de datetime combinada
        df["Timestamp"] = pd.to_datetime(
            df["Data"] + " " + df["Hora (UTC)"].apply(converter_para_hora_utc),
            format="%d/%m/%Y %H:%M:%S"
        )

        # Converte para formato ISO 8601 com Z (UTC)
        df["Timestamp"] = df["Timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        return df
    finally:
        driver.quit()

# ----------- Função para obter WebId -----------
def get_webid_by_path(base_url: str, path: str) -> str:
    url = f"{base_url}/points?path={path}"
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        return response.json()["WebId"]
    except Exception as e:
        print(f"Erro ao obter WebId para {path}: {e}")
        return ""

# ----------- Função para enviar valores -----------
def send_recorded_values(base_url: str, webid: str, values: list) -> bool:
    url = f"{base_url}/streams/{webid}/recorded"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, json=values, verify=False)
        response.raise_for_status()
        print(f"Enviado com sucesso para WebId: {webid}")
        return True
    except Exception as e:
        print(f"Erro ao enviar para {webid}: {e}")
        print(response.text if response else "sem resposta")
        return False


# ------------------ Coleta de dados mês a mês ------------------
def main():
    from datetime import datetime, timedelta
    from calendar import monthrange

    dados = []

    ano_inicio = 2025
    hoje = datetime.utcnow().date()
    ano_atual = hoje.year
    mes_atual = hoje.month
    dia_atual = hoje.day

    for ano in range(ano_inicio, ano_atual + 1):
        mes_final = 12
        if ano == ano_atual:
            mes_final = mes_atual

        for mes in range(1, mes_final + 1):
            data_inicio = f"{mes:02d}/01/{ano}"

            # Caso seja o mês atual e o ano atual, vai até ontem
            if ano == ano_atual and mes == mes_atual:
                dia_fim = (hoje - timedelta(days=1)).day
            else:
                dia_fim = monthrange(ano, mes)[1]

            data_fim = f"{mes:02d}/{dia_fim:02d}/{ano}"

            print(f"📅 Coletando de {data_inicio} até {data_fim}...")

            try:
                df_mensal = coletar_dados_inmet(estacao_id="A511", data_inicio=data_inicio, data_fim=data_fim)
                df_mensal = df_mensal.dropna()
                if not df_mensal.empty:
                    dados.append(df_mensal)
                    print(f"✅ Coletado: {len(df_mensal)} linhas.")
                else:
                    print("⚠️ Nenhum dado encontrado.")
            except Exception as e:
                print(f"❌ Falha ao coletar {mes:02d}/{ano}: {e}")

        df = df_mensal.dropna()

        # Substitui vírgula por ponto e converte para float
        for col in ["SYS_TEMPERATURA_MAX", "SYS_TEMPERATURA_MIN", "SYS_PONTO_ORVALHO_MAX", "SYS_PONTO_ORVALHO_MIN"]:
            df[col] = df[col].str.replace(",", ".").astype(float)

        # ----------- Configurações -----------
        base_url = "http://10.247.224.39/piwebapi"
        pims_prefix = "\\\\pims\\"

        # ----------- Obter WebIds -----------
        webid_map = {
            "SYS_TEMPERATURA_MAX": get_webid_by_path(base_url, f"{pims_prefix}SYS_TEMPERATURA_MAX"),
            "SYS_TEMPERATURA_MIN": get_webid_by_path(base_url, f"{pims_prefix}SYS_TEMPERATURA_MIN"),
            "SYS_PONTO_ORVALHO_MAX": get_webid_by_path(base_url, f"{pims_prefix}SYS_PONTO_ORVALHO_MAX"),
            "SYS_PONTO_ORVALHO_MIN": get_webid_by_path(base_url, f"{pims_prefix}SYS_PONTO_ORVALHO_MIN"),
        }


        # ----------- Enviar dados para cada tag -----------
        for tag, webid in webid_map.items():
            if not webid:
                continue  # pula se o WebId falhar

            valores_para_enviar = [
                {"Timestamp": row["Timestamp"], "Value": row[tag]}
                for _, row in df.iterrows()
                if pd.notnull(row[tag])
            ]

            send_recorded_values(base_url, webid, valores_para_enviar)





main()



