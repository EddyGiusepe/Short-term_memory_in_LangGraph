#!/usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script viewing_conversation_history.py
======================================
Visualiza o histórico de conversas usando a API do LangGraph.

Run
---
uv run viewing_conversation_history.py
"""
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver


def ver_historico_thread(
    thread_id: str = "usuario_1", db_path: str = "chatbot_memory.db"
):
    """
    Visualiza o histórico completo de uma thread usando a API do LangGraph.
    """
    print("=" * 40)
    print(f"💬 HISTÓRICO DA CONVERSA - Thread: {thread_id}")
    print("=" * 40)

    try:
        # Conecta ao banco usando SqliteSaver
        conn = sqlite3.connect(db_path, check_same_thread=False)
        checkpointer = SqliteSaver(conn)

        # Configuração da thread
        config = {"configurable": {"thread_id": thread_id}}

        # Lista todos os checkpoints desta thread
        checkpoints = list(checkpointer.list(config))

        if not checkpoints:
            print(f"\n⚠️  Nenhum checkpoint encontrado para thread '{thread_id}'")
            conn.close()
            return

        print(f"\n📊 Total de checkpoints: {len(checkpoints)}")
        print("-" * 80)

        # Pega o último checkpoint (mais recente)
        ultimo_checkpoint = checkpoints[0]

        # Extrai o estado
        state = ultimo_checkpoint.checkpoint

        # Acessa as mensagens
        if "channel_values" in state:
            messages = state["channel_values"].get("messages", [])
        else:
            messages = []

        if not messages:
            print("\n⚠️  Nenhuma mensagem encontrada.")
            conn.close()
            return

        print(f"\n💬 Total de mensagens: {len(messages)}\n")
        print("=" * 80)

        # Exibe cada mensagem
        for idx, msg in enumerate(messages, 1):
            # Determina o tipo
            msg_type = type(msg).__name__

            # Identifica o papel
            if "Human" in msg_type or "user" in msg_type.lower():
                emoji = "👤"
                role = "USUÁRIO"
                color = "\033[94m"  # Azul
            elif "AI" in msg_type or "assistant" in msg_type.lower():
                emoji = "🤖"
                role = "ASSISTENTE"
                color = "\033[92m"  # Verde
            elif "System" in msg_type:
                emoji = "⚙️"
                role = "SISTEMA"
                color = "\033[93m"  # Amarelo
            else:
                emoji = "💬"
                role = msg_type.upper()
                color = "\033[0m"  # Normal

            reset = "\033[0m"

            # Pega o conteúdo
            content = getattr(msg, "content", str(msg))

            # Exibe
            print(f"\n{color}{emoji} {role} (Mensagem #{idx}){reset}")
            print("-" * 80)
            print(content)

        print("\n" + "=" * 35)
        print("✅ Fim do histórico")
        print("=" * 35)

        conn.close()

    except Exception as e:
        print(f"\n❌ Erro ao acessar histórico: {e}")
        import traceback

        traceback.print_exc()


def listar_threads_disponiveis(db_path: str = "chatbot_memory.db"):
    """
    Lista todas as threads disponíveis no banco.
    """
    print("=" * 80)
    print("🧵 THREADS DISPONÍVEIS")
    print("=" * 80)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Lista threads únicas
        cursor.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id")
        threads = cursor.fetchall()

        if not threads:
            print("\n⚠️  Nenhuma thread encontrada.")
            conn.close()
            return

        print(f"\n📊 Total de threads: {len(threads)}\n")

        for (thread_id,) in threads:
            # Conta checkpoints
            cursor.execute(
                "SELECT COUNT(*) FROM checkpoints WHERE thread_id = ?", (thread_id,)
            )
            num_checkpoints = cursor.fetchone()[0]

            print(f"  🔹 {thread_id}")
            print(f"      Checkpoints: {num_checkpoints}")

        conn.close()

    except Exception as e:
        print(f"\n❌ Erro: {e}")


def estatisticas_banco(db_path: str = "chatbot_memory.db"):
    """
    Mostra estatísticas gerais do banco.
    """
    print("=" * 80)
    print("📊 ESTATÍSTICAS DO BANCO DE DADOS")
    print("=" * 80)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Threads:
        cursor.execute("SELECT COUNT(DISTINCT thread_id) FROM checkpoints")
        num_threads = cursor.fetchone()[0]

        # Checkpoints:
        cursor.execute("SELECT COUNT(*) FROM checkpoints")
        num_checkpoints = cursor.fetchone()[0]

        # Writes:
        cursor.execute("SELECT COUNT(*) FROM writes")
        num_writes = cursor.fetchone()[0]

        # Tamanho do arquivo:
        import os

        tamanho = os.path.getsize(db_path) / 1024  # KB

        print(
            f"""
📈 Resumo:
  • Threads (conversas): {num_threads}
  • Checkpoints: {num_checkpoints}
  • Writes: {num_writes}
  • Tamanho do arquivo: {tamanho:.2f} KB
        """
        )

        # Threads com mais atividade
        cursor.execute(
            """
            SELECT thread_id, COUNT(*) as num 
            FROM checkpoints 
            GROUP BY thread_id 
            ORDER BY num DESC 
            LIMIT 5
        """
        )
        top_threads = cursor.fetchall()

        if top_threads:
            print("\n🏆 Top 5 threads mais ativas:")
            for thread_id, num in top_threads:
                print(f"  • {thread_id}: {num} checkpoints")

        conn.close()

    except Exception as e:
        print(f"\n❌ Erro: {e}")


def menu_interativo():
    """
    Menu interativo para visualização.
    """
    import os

    db_path = "chatbot_memory.db"

    if not os.path.exists(db_path):
        print("⚠️  Arquivo 'chatbot_memory.db' não encontrado.")
        print("Execute o chatbot primeiro para criar o banco de dados.")
        return

    while True:
        print("\n" + "=" * 42)
        print("🔍 VISUALIZADOR DE HISTÓRICO DE CONVERSAS")
        print("=" * 42)
        print("\nOpções:")
        print("  1. Ver histórico de uma thread")
        print("  2. Listar threads disponíveis")
        print("  3. Ver estatísticas do banco")
        print("  0. Sair")
        print("-" * 42)

        try:
            opcao = input("\nEscolha uma opção: ").strip()

            if opcao == "1":
                thread_id = input(
                    "Digite o thread_id (ou ENTER para 'usuario_1'): "
                ).strip()
                if not thread_id:
                    thread_id = "usuario_1"
                ver_historico_thread(thread_id, db_path)

            elif opcao == "2":
                listar_threads_disponiveis(db_path)

            elif opcao == "3":
                estatisticas_banco(db_path)

            elif opcao == "0":
                print("\n👋 Até logo!")
                break

            else:
                print("\n⚠️  Opção inválida. Tente novamente.")

            input("\n↵ Pressione ENTER para continuar...")

        except KeyboardInterrupt:
            print("\n\n👋 Interrompido pelo usuário. Até logo!")
            break
        except EOFError:
            print("\n👋 Até logo!")
            break


if __name__ == "__main__":
    import sys
    import os

    if not os.path.exists("chatbot_memory.db"):
        print("⚠️  Arquivo 'chatbot_memory.db' não encontrado.")
        print("Execute o chatbot primeiro para criar o banco de dados.")
        sys.exit(1)

    # Se não tem argumentos, modo interativo
    if len(sys.argv) == 1:
        menu_interativo()
    # Se tem argumentos
    elif sys.argv[1] == "--thread" and len(sys.argv) > 2:
        ver_historico_thread(sys.argv[2])
    elif sys.argv[1] == "--list":
        listar_threads_disponiveis()
    elif sys.argv[1] == "--stats":
        estatisticas_banco()
    else:
        print("Uso:")
        print("  uv run ver_historico_conversa.py              # Modo interativo")
        print("  uv run ver_historico_conversa.py --thread ID  # Ver thread específica")
        print("  uv run ver_historico_conversa.py --list       # Listar threads")
        print("  uv run ver_historico_conversa.py --stats      # Estatísticas")
