#!/usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script checking_connection_with_groq_api.py
===========================================
Este script testa se a API Groq está respondendo corretamente.

Run
---
uv run checking_connection_with_groq_api.py
"""
import os
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
import time

_ = load_dotenv(find_dotenv())
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

print("=" * 70)
print("🧪 TESTE DA API GROQ")
print("=" * 70)

print("\n1️⃣ Testando conexão básica...")

try:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY,
        temperature=0.0,
        timeout=10.0
    )
    
    print("✅ Cliente ChatGroq criado com sucesso")
    
    print("\n2️⃣ Enviando mensagem de teste...")
    start_time = time.time()
    
    response = llm.invoke("Responda apenas: Sou o modelo tal ....")
    
    end_time = time.time()
    tempo = end_time - start_time
    
    print(f"✅ Resposta recebida em {tempo:.2f} segundos")
    print(f"\n📝 Resposta: {response.content}")
    
    print("\n" + "=" * 70)
    print("✅ API GROQ ESTÁ FUNCIONANDO NORMALMENTE")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    print(f"Tipo: {type(e).__name__}")
    
    import traceback
    print("\n🔍 Detalhes:")
    traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("❌ PROBLEMA COM A API GROQ")
    print("=" * 70)
    
    # Identifica o tipo de erro
    error_str = str(e).lower()
    
    if "rate limit" in error_str or "429" in error_str:
        print("\n⚠️  RATE LIMIT DETECTADO")
        print("Você atingiu o limite de requisições da API Groq.")
        print("\n💡 Soluções:")
        print("  1. Aguarde 5-10 minutos e tente novamente")
        print("  2. Use um plano pago da Groq para limites maiores")
        print("  3. Use outra API key (se tiver)")
        
    elif "timeout" in error_str or "timed out" in error_str:
        print("\n⚠️  TIMEOUT DETECTADO")
        print("A API está demorando muito para responder.")
        print("\n💡 Soluções:")
        print("  1. Tente novamente (pode ser temporário)")
        print("  2. Verifique sua conexão com internet")
        print("  3. Tente mais tarde")
        
    elif "401" in error_str or "unauthorized" in error_str:
        print("\n⚠️  API KEY INVÁLIDA")
        print("Sua chave de API está incorreta ou expirada.")
        print("\n💡 Soluções:")
        print("  1. Verifique o arquivo .env")
        print("  2. Regenere a API key no Groq Console")
        
    elif "connection" in error_str or "network" in error_str:
        print("\n⚠️  PROBLEMA DE CONEXÃO")
        print("Não foi possível conectar à API Groq.")
        print("\n💡 Soluções:")
        print("  1. Verifique sua internet")
        print("  2. Verifique se https://api.groq.com está acessível")
        print("  3. Tente desativar VPN/proxy temporariamente")
    
    else:
        print("\n⚠️  ERRO DESCONHECIDO")
        print("Verifique os detalhes acima.")

