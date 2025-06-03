import os
import subprocess
from datetime import datetime

# Diretório base (onde este script está localizado)
base_dir = os.path.dirname(os.path.abspath(__file__))

# Pastas configuradas
pasta_scripts = os.path.join(base_dir, "auto_execute")
log_dir = os.path.join(base_dir, "logs")

# Garante que ambas as pastas existem
os.makedirs(log_dir, exist_ok=True)
os.makedirs(pasta_scripts, exist_ok=True)

# Nome do arquivo de log com data e hora
log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

with open(log_file, "w") as log:
    scripts = [f for f in os.listdir(pasta_scripts) if f.endswith(".py")]
    
    if not scripts:
        log.write("⚠️ Nenhum script .py encontrado em auto_execute/\n")
    
    for script in sorted(scripts):
        caminho_script = os.path.join(pasta_scripts, script)
        log.write(f"\n🚀 Executando: {caminho_script}\n")
        try:
            result = subprocess.run(["python3", caminho_script], capture_output=True, text=True)
            log.write(result.stdout)
            log.write(result.stderr)
        except Exception as e:
            log.write(f"❌ Erro ao executar {script}: {e}\n")
