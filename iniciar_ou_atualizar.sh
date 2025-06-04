#!/bin/bash

# ========== VARIÁVEIS DE CONFIGURAÇÃO ==========
NOME_PROJETO="executar_todos.py"
DIRETORIO_SCRIPT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # Caminho absoluto
SCRIPT_PATH="$DIRETORIO_SCRIPT/$NOME_PROJETO"
DELAY_BOOT=200                 # segundos de delay após reboot
HORAS_INTERVALO=8             # intervalo entre execuções regulares
# ===============================================

PYTHON_PATH=$(which python3)

# Gera as linhas do cron desejadas
CRON_REGULAR="0 */$HORAS_INTERVALO * * * $PYTHON_PATH $SCRIPT_PATH"
CRON_REBOOT="@reboot sleep $DELAY_BOOT && $PYTHON_PATH $SCRIPT_PATH"

# Função auxiliar para garantir linha no crontab
adicionar_ou_atualizar_cron() {
    NOVA_LINHA="$1"
    PADRAO="$2"
    (crontab -l 2>/dev/null | grep -v "$PADRAO"; echo "$NOVA_LINHA") | sort -u | crontab -
}

# Atualiza/insere as linhas no crontab
adicionar_ou_atualizar_cron "$CRON_REGULAR" "$SCRIPT_PATH"
adicionar_ou_atualizar_cron "$CRON_REBOOT" "@reboot.*$SCRIPT_PATH"

# Confirmação
echo "✅ Agendamento configurado:"
echo "   - A cada $HORAS_INTERVALO horas"
echo "   - Ao reiniciar com delay de $DELAY_BOOT segundos"
echo "📍 Script: $SCRIPT_PATH"

echo "🚀 Executando imediatamente para teste inicial..."
$PYTHON_PATH $SCRIPT_PATH
