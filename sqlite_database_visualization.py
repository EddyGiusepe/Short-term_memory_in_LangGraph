#!/usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script visualizar_memoria.py
============================
Este script permite visualizar o conteúdo do banco de dados SQLite
que armazena a memória persistente do chatbot.

Run
---
uv run visualizar_memoria.py

uv run ver_historico_conversa.py --thread usuario_1 2>&1 | tail -80
"""
import sqlite3
import json
import pickle


def visualizar_estrutura_banco(db_path: str = "chatbot_memory.db"):
    """
    Mostra a estrutura do banco de dados (tabelas e colunas).
    """
    print("=" * 80)
    print("🗂️  ESTRUTURA DO BANCO DE DADOS")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lista todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        
        if not tabelas:
            print("\n⚠️  Banco de dados vazio ou não encontrado.")
            return
        
        for (tabela,) in tabelas:
            print(f"\n📋 Tabela: {tabela}")
            print("-" * 80)
            
            # Informações das colunas
            cursor.execute(f"PRAGMA table_info({tabela})")
            colunas = cursor.fetchall()
            
            print("Colunas:")
            for col in colunas:
                col_id, nome, tipo, notnull, default, pk = col
                pk_str = " [PRIMARY KEY]" if pk else ""
                notnull_str = " NOT NULL" if notnull else ""
                print(f"  • {nome} ({tipo}){pk_str}{notnull_str}")
            
            # Contagem de registros
            cursor.execute(f"SELECT COUNT(*) FROM {tabela}")
            count = cursor.fetchone()[0]
            print(f"\n📊 Total de registros: {count}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"\n❌ Erro ao acessar banco: {e}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


def visualizar_checkpoints(db_path: str = "chatbot_memory.db", limit: int = 10):
    """
    Visualiza os checkpoints armazenados.
    """
    print("\n" + "=" * 80)
    print("💾 CHECKPOINTS ARMAZENADOS")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Busca checkpoints
        query = """
        SELECT thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, 
               type, checkpoint
        FROM checkpoints 
        ORDER BY checkpoint_id DESC 
        LIMIT ?
        """
        
        cursor.execute(query, (limit,))
        checkpoints = cursor.fetchall()
        
        if not checkpoints:
            print("\n⚠️  Nenhum checkpoint encontrado.")
            conn.close()
            return
        
        for idx, cp in enumerate(checkpoints, 1):
            thread_id, ns, cp_id, parent_id, tipo, checkpoint_data = cp
            
            print(f"\n🔖 Checkpoint #{idx}")
            print("-" * 80)
            print(f"  Thread ID: {thread_id}")
            print(f"  Checkpoint ID: {cp_id}")
            print(f"  Parent ID: {parent_id if parent_id else 'None (primeiro)'}")
            print(f"  Namespace: {ns}")
            print(f"  Tipo: {tipo if tipo else 'N/A'}")
            
            # Tenta decodificar o checkpoint
            try:
                if checkpoint_data:
                    # O checkpoint está serializado, vamos apenas mostrar o tamanho
                    print(f"  Tamanho dos dados: {len(checkpoint_data)} bytes")
            except Exception:
                print("  Dados: [binário]")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"\n❌ Erro ao acessar banco: {e}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


def visualizar_writes(db_path: str = "chatbot_memory.db", limit: int = 20):
    """
    Visualiza as escritas (writes) que contêm as mensagens.
    """
    print("\n" + "=" * 80)
    print("✍️  HISTÓRICO DE ESCRITAS (MENSAGENS)")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Busca writes
        query = """
        SELECT thread_id, checkpoint_ns, checkpoint_id, task_id, idx, channel, type, value
        FROM writes 
        ORDER BY checkpoint_id, idx
        LIMIT ?
        """
        
        cursor.execute(query, (limit,))
        writes = cursor.fetchall()
        
        if not writes:
            print("\n⚠️  Nenhuma escrita encontrada.")
            conn.close()
            return
        
        current_checkpoint = None
        for write in writes:
            thread_id, ns, cp_id, task_id, idx, channel, tipo, value = write
            
            # Cabeçalho para novo checkpoint
            if cp_id != current_checkpoint:
                current_checkpoint = cp_id
                print(f"\n📝 Checkpoint: {cp_id} | Thread: {thread_id}")
                print("-" * 80)
            
            print(f"\n  [{idx}] Canal: {channel} | Tipo: {tipo}")
            
            # Tenta decodificar o valor (pode conter mensagens)
            try:
                if value:
                    # Tenta deserializar
                    try:
                        data = pickle.loads(value)
                        if isinstance(data, dict):
                            print(f"  Dados: {json.dumps(data, indent=4, ensure_ascii=False)}")
                        elif isinstance(data, list):
                            for item in data:
                                if hasattr(item, 'content'):
                                    # É uma mensagem LangChain
                                    role = type(item).__name__.replace('Message', '')
                                    print(f"  → {role}: {item.content[:100]}...")
                                else:
                                    print(f"  → {str(item)[:100]}")
                        else:
                            print(f"  Dados: {str(data)[:200]}")
                    except Exception:
                        print(f"  Tamanho: {len(value)} bytes [dados binários]")
            except Exception as e:
                print(f"  [Não foi possível decodificar: {e}]")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"\n❌ Erro ao acessar banco: {e}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


def visualizar_conversas_por_thread(db_path: str = "chatbot_memory.db"):
    """
    Mostra um resumo das conversas por thread.
    """
    print("\n" + "=" * 80)
    print("💬 RESUMO DE CONVERSAS POR THREAD")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Agrupa por thread_id
        query = """
        SELECT thread_id, COUNT(DISTINCT checkpoint_id) as num_checkpoints
        FROM checkpoints
        GROUP BY thread_id
        """
        
        cursor.execute(query)
        threads = cursor.fetchall()
        
        if not threads:
            print("\n⚠️  Nenhuma thread encontrada.")
            conn.close()
            return
        
        for thread_id, num_checkpoints in threads:
            print(f"\n🧵 Thread: {thread_id}")
            print(f"   📊 Checkpoints: {num_checkpoints}")
            
            # Conta mensagens
            query_writes = """
            SELECT COUNT(*) FROM writes
            WHERE thread_id = ?
            """
            cursor.execute(query_writes, (thread_id,))
            num_writes = cursor.fetchone()[0]
            print(f"   ✍️  Escritas: {num_writes}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"\n❌ Erro ao acessar banco: {e}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


def limpar_banco(db_path: str = "chatbot_memory.db"):
    """
    Apaga todos os dados do banco (com confirmação).
    """
    print("\n" + "=" * 80)
    print("🗑️  LIMPAR BANCO DE DADOS")
    print("=" * 80)
    
    resposta = input("\n⚠️  Tem certeza que deseja apagar TODOS os dados? (sim/não): ")
    
    if resposta.lower() not in ['sim', 's', 'yes', 'y']:
        print("\n❌ Operação cancelada.")
        return
    
    try:
        import os
        if os.path.exists(db_path):
            os.remove(db_path)
            print("\n✅ Banco de dados apagado com sucesso!")
            
            # Remove arquivos auxiliares
            for ext in ['-wal', '-shm']:
                aux_file = db_path + ext
                if os.path.exists(aux_file):
                    os.remove(aux_file)
                    print(f"✅ Arquivo {aux_file} removido.")
        else:
            print("\n⚠️  Arquivo não encontrado.")
    except Exception as e:
        print(f"\n❌ Erro ao apagar: {e}")


def menu_principal():
    """
    Menu interativo para visualizar o banco.
    """
    db_path = "chatbot_memory.db"
    
    while True:
        print("\n" + "=" * 80)
        print("🔍 VISUALIZADOR DE MEMÓRIA DO CHATBOT")
        print("=" * 80)
        print("\nOpções:")
        print("  1. Ver estrutura do banco")
        print("  2. Ver checkpoints")
        print("  3. Ver histórico de mensagens")
        print("  4. Ver resumo por thread")
        print("  5. Limpar banco de dados")
        print("  0. Sair")
        print("-" * 80)
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            visualizar_estrutura_banco(db_path)
        elif opcao == "2":
            visualizar_checkpoints(db_path)
        elif opcao == "3":
            visualizar_writes(db_path)
        elif opcao == "4":
            visualizar_conversas_por_thread(db_path)
        elif opcao == "5":
            limpar_banco(db_path)
        elif opcao == "0":
            print("\n👋 Até logo!")
            break
        else:
            print("\n⚠️  Opção inválida. Tente novamente.")
        
        input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    try:
        import os
        if not os.path.exists("chatbot_memory.db"):
            print("⚠️  Arquivo 'chatbot_memory.db' não encontrado.")
            print("Execute o chatbot primeiro para criar o banco de dados.")
        else:
            menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário. Até logo!")

