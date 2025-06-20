#!/bin/bash

# Nome do script principal
NOME_PROJETO="executar_todos.py"

# Procura o PID do processo rodando esse script
PID=$(ps aux | grep "$NOME_PROJETO" | grep -v grep | awk '{print $2}')

if [ -z "$PID" ]; then
    echo "ℹ️ Nenhum processo encontrado rodando $NOME_PROJETO."
else
    echo "🛑 Finalizando processo $NOME_PROJETO com PID(s): $PID"
    kill $PID
    echo "✅ Processo finalizado."
fi
