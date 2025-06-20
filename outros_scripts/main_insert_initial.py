def coletar_dados_inmet(estacao_id="A511", data_inicio="01/01/2025", data_fim="01/05/2025"):
    # Configurar o navegador (sem diretório de download porque não vamos baixar nada)
    options = Options()
    options.add_argument("--profile-directory=Profile 2")  # ou "Default"
    # options.add_argument("--start-maximized")
    # options.add_argument("--headless=new")  # evita que o Chrome mande cabeçalho "webdriver"
    # options.add_argument("--headless")  # não abre janela
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--window-size=1920,1080")  # simula tela "grande" invisível