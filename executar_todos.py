import os
import subprocess
from datetime import datetime

# Diretório base (onde este script está localizado)
base_dir = os.path.dirname(os.path.abspath(__file__))

# Pastas configuradas
pasta_scripts = os.path.join(base_dir, "auto_execute")
log_dir = os.path.join(base_dir, "logs")

# Garante que as pastas existem
os.makedirs(log_dir, exist_ok=True)
os.makedirs(pasta_scripts, exist_ok=True)

# Arquivo de log fixo (sobrescreve a cada execução)
log_file = os.path.join(log_dir, "log_execucao.log")

with open(log_file, "w") as log:
    data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.write(f"📅 Data: {data_hora}\n")
    log.write(f"📁 Projeto: {base_dir}\n")
    log.write(f"{'='*60}\n")

    scripts = sorted([f for f in os.listdir(pasta_scripts) if f.endswith(".py")])

    if not scripts:
        log.write("⚠️ Nenhum script .py encontrado em auto_execute/\n")

    for script in scripts:
        caminho_script = os.path.join(pasta_scripts, script)
        log.write(f"\n🚀 Executando: {caminho_script}\n")

        try:
            result = subprocess.run(["python3", caminho_script], capture_output=True, text=True)
            log.write(f"📤 STDOUT:\n{result.stdout}\n")
            log.write(f"⚠️ STDERR:\n{result.stderr}\n")
        except Exception as e:
            log.write(f"❌ Erro ao executar {script}: {e}\n")

    log.write(f"{'='*60}\n")
    log.write("✅ Execução finalizada.\n")
