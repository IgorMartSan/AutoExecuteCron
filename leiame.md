# 🧩 Gerenciador de Execução Automática com `cron`

Este projeto gerencia a execução de scripts Python de forma automática e controlada com agendamento via `cron` no linux.

## 📦 Scripts disponíveis

- `iniciar_ou_atualizar.sh` – Agenda a execução automática
- `parar_execucao.sh` – Remove os agendamentos do crontab
- `finalizar_processo.sh` – Encerra o processo atual em execução do script principal

---

## ▶️ Iniciar o Processo

Este comando agenda o script `executar_todos.py` para:

- Rodar a cada X horas (`HORAS_INTERVALO`)
- Rodar automaticamente após reinício com delay de Y segundos (`DELAY_BOOT`)

# Iniciar a Execução Automática (bash)

sudo chmod +x iniciar_ou_atualizar.sh
./iniciar_ou_atualizar.sh

# Parar a Execução Automática (bash)

chmod +x parar_execucao.sh
./parar_execucao.sh

# Verificar o conteúdo atual do crontab

crontab -l