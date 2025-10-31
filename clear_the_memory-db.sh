#!/bin/bash
# Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro
# Script para limpar a memória do chatbot
# Permissão de execução: chmod +x clear_the_memory-db.sh
# Run: bash clear_the_memory-db.sh   ou   sh clear_the_memory-db.sh   ou   ./clear_the_memory-db.sh


echo "🗑️  Limpando memória do chatbot..."

if [ -f "chatbot_memory.db" ]; then
    rm -f chatbot_memory.db
    echo "✅ chatbot_memory.db removido"
fi

if [ -f "chatbot_memory.db-wal" ]; then
    rm -f chatbot_memory.db-wal
    echo "✅ chatbot_memory.db-wal removido"
fi

if [ -f "chatbot_memory.db-shm" ]; then
    rm -f chatbot_memory.db-shm
    echo "✅ chatbot_memory.db-shm removido"
fi

echo ""
echo "✅ Memória limpa! Você pode reiniciar o chatbot agora."
echo ""
echo "Para executar o chatbot:"
echo "  uv run chatbot_with_memory_checkpoints.py"

