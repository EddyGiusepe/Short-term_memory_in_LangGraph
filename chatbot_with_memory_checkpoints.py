#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script chatbot_with_memory_checkpoints.py
=========================================
Este script cria um chatbot com memória de conversa usando checkpoints.
O chatbot é capaz de manter o contexto da conversa e responder as
perguntas do usuário com base no histórico completo da conversa.


Run
---
uv run chatbot_with_memory_checkpoints.py
"""
from langgraph.checkpoint.sqlite import SqliteSaver  # Persistência em disco
from langgraph.graph.message import RemoveMessage
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from typing import Annotated, List
from typing_extensions import TypedDict
import sqlite3

import os
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())  # read local .env file
GROQ_API_KEY = os.environ["GROQ_API_KEY"]


class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0.0,
    timeout=30.0,  # Timeout de 30 segundos
    max_retries=2,  # Tenta até 2 vezes em caso de erro
)

prompt_template = ChatPromptTemplate.from_messages(
    [("system", "{system_message}"), MessagesPlaceholder("messages")]
)

llm_model = prompt_template | llm


def ChatNode(state: State) -> State:

    system_message = """Você é um assistente de IA com memória de conversa.

INSTRUÇÕES IMPORTANTES:
1. Você TEM acesso ao histórico completo desta conversa
2. Use as mensagens anteriores para manter contexto
3. Lembre-se de informações que o usuário compartilhou anteriormente
4. Se o usuário perguntar "você lembra?", consulte o histórico
5. Seja consistente com informações já compartilhadas
6. Não precisa falar sobre o histórico, apenas use-o para responder as perguntas do usuário.
Responda de forma clara, concisa e factual, SEMPRE considerando
o contexto completo da conversa."""

    try:
        result = llm_model.invoke(
            {"system_message": system_message, "messages": state["messages"]}
        )

        state["messages"] = result
        return state
    except Exception as e:
        print(f"[ERRO] ChatNode: {e}")
        raise


def filter_node(state: State) -> State:
    """
    Filtra o histórico para manter memória de curto prazo gerenciável.

    CONFIGURAÇÃO ATUAL:
      Mantém últimas 25 interações (50 mensagens)
    - Isso permite que o bot lembre de muito mais contexto
    - Mantém informações importantes por mais tempo
    - Previne que o histórico cresça infinitamente
    - Ajustável conforme necessidade

    Para mudar: Altere MAX_INTERACTIONS abaixo
    """
    MAX_INTERACTIONS = 25  # Ajustar para mais ou menos memória
    MAX_MESSAGES = (
        MAX_INTERACTIONS * 2
    )  # Cada interação tem 2 mensagens (user + assistant)

    messages = state["messages"]
    num_messages = len(messages)

    # Só filtra se houver mais mensagens que o limite (MAX_MESSAGES)
    if num_messages > MAX_MESSAGES:
        # Remove todas as mensagens antigas, mantendo apenas as últimas MAX_MESSAGES
        messages_to_remove = messages[:-MAX_MESSAGES]
        delete_messages = [RemoveMessage(id=m.id) for m in messages_to_remove]

        return {"messages": delete_messages}

    # Se estiver dentro do limite, não remove nada. Retorna o estado atual.
    return state


graph_builder = StateGraph(State)
graph_builder.add_node("filternode", filter_node)
graph_builder.add_node("chatnode", ChatNode)

# IMPORTANTE: O fluxo correto é START → filternode → chatnode → END
# Isso garante que o filtro seja aplicado ANTES de processar a nova mensagem
graph_builder.add_edge(START, "filternode")
graph_builder.add_edge("filternode", "chatnode")
graph_builder.add_edge("chatnode", END)

# SqliteSaver: Persiste checkpoints em disco (arquivo SQLite)
# A memória agora sobrevive entre execuções do script!
# O arquivo 'chatbot_memory.db' será criado automaticamente na primeira execução
# Criamos uma conexão SQLite persistente
conn = sqlite3.connect("chatbot_memory.db", check_same_thread=False)
memory = SqliteSaver(conn)
graph = graph_builder.compile(checkpointer=memory)

# Configuração da thread (cada usuário teria seu próprio thread_id)
# IMPORTANTE: Usar o mesmo thread_id em execuções diferentes mantém o histórico!
config = {"configurable": {"thread_id": "usuario_1"}}


def print_new_messages(old_count: int, new_state: dict) -> int:
    """
    Imprime apenas as mensagens novas para evitar duplicação.

    IMPORTANTE: Como usamos filtro que remove mensagens antigas,
    o old_count pode estar desatualizado. Sempre imprimimos as
    últimas 2 mensagens (user + assistant da interação atual).

    Args:
        old_count: Número de mensagens já impressas anteriormente
        new_state: Estado retornado pelo graph com todas as mensagens

    Returns:
        Número total de mensagens após a impressão
    """
    messages = new_state["messages"]
    total_messages = len(messages)

    # Se o filtro removeu mensagens, old_count pode ser maior que total
    # Nesse caso, imprimimos apenas as últimas 2 (user + assistant)
    if old_count >= total_messages:

        for message in messages[-2:]:
            message.pretty_print()
    else:
        # Caso normal: imprime mensagens novas
        new_messages = messages[old_count:]

        for message in new_messages:
            message.pretty_print()

    return total_messages


def chat_interativo():
    """
    Função principal para chat interativo com memória persistente.
    O usuário pode conversar continuamente e o bot mantém todo o contexto.
    """
    print("=" * 70)
    print("🤖 Chatbot com Memória Persistente (LangGraph + SQLite)")
    print("=" * 70)
    print("\nOlá! Sou seu assistente virtual com memória PERMANENTE!")
    print("✅ Lembro de toda nossa conversa")
    print("✅ Minha memória persiste entre execuções do programa")
    print("✅ Você pode fechar e reabrir o script - eu lembro de você!")
    print("\n💡 Dica: A memória está salva em 'chatbot_memory.db'")
    print("\nDigite 'sair', 'quit' ou 'exit' para encerrar.")
    print("Digite 'limpar' ou 'reset' para apagar minha memória.\n")
    print("=" * 70)

    # Contador para rastrear quantas mensagens já foram impressas
    message_count = 0

    # Verifica se há histórico prévio ao iniciar:
    try:
        state_snapshot = graph.get_state(config)
        if state_snapshot.values.get("messages"):
            print("\n📚 Histórico detectado! Continuando conversa anterior...")
            # Imprime o histórico existente:
            for msg in state_snapshot.values["messages"]:
                msg.pretty_print()
            message_count = len(state_snapshot.values["messages"])
    except Exception:
        print("\n🆕 Iniciando nova conversa...")

    while True:
        try:
            # Captura entrada do usuário:
            user_input = input("\n🤓 Você: ").strip()

            # Verifica se o usuário quer sair
            if user_input.lower() in ["sair", "quit", "exit", "tchau", "bye"]:
                print("\n👋 Até logo! Foi um prazer conversar com você!")
                print("💾 Sua conversa foi salva e continuará na próxima execução!")
                print("=" * 70)
                break

            # Comando para limpar a memória
            if user_input.lower() in ["limpar", "reset", "apagar"]:
                try:
                    # Fechar a conexão antes de deletar
                    conn.close()
                    import os

                    if os.path.exists("chatbot_memory.db"):
                        os.remove("chatbot_memory.db")
                        print("\n🗑️  Memória apagada com sucesso!")
                        print("⚠️  Reinicie o script para começar uma nova conversa.")
                        print("=" * 70)
                        break
                    else:
                        print("\n⚠️  Não há memória para apagar.")
                        continue
                except Exception as e:
                    print(f"\n❌ Erro ao apagar memória: {e}")
                    continue

            # Ignora entradas vazias
            if not user_input:
                print("⚠️  Por favor, digite algo ou 'sair' para encerrar.")
                continue

            # Prepara o estado de entrada com a mensagem do usuário:
            input_state = {"messages": [user_input]}

            # Indicador de processamento:
            print("\n⏳ Processando ...")

            try:

                # Invoca o graph com a configuração de thread
                # O checkpoint mantém todo o histórico automaticamente
                response_state = graph.invoke(input_state, config=config)

                # Imprime apenas as mensagens novas (evita duplicação):
                print("\n🤖 Assistente:")
                message_count = print_new_messages(message_count, response_state)

            except Exception as e:
                print(f"\n❌ Erro ao processar mensagem: {e}")
                print(f"Tipo de erro: {type(e).__name__}")

                # Debug detalhado
                import traceback

                print("\n🔍 Detalhes do erro:")
                traceback.print_exc()

                print("\n💡 Possíveis causas:")
                print("  • Rate limit da API (tente aguardar alguns segundos)")
                print("  • Erro de conexão com a API")
                print("  • Problema com o filtro de mensagens")
                print("\nTente novamente ou digite 'sair' para encerrar.")

        except KeyboardInterrupt:
            # Permite sair com Ctrl+C:
            print("\n\n👋 Interrompido pelo usuário. Até logo!")
            print("💾 Sua conversa foi salva!")
            print("=" * 70)
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            print("Tente novamente ou digite 'sair' para encerrar.")

    # Fecha a conexão ao terminar:
    try:
        conn.close()
    except Exception:
        pass


# Executa o chat interativo:
if __name__ == "__main__":
    chat_interativo()
