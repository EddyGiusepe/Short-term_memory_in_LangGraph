# <h1 align="center"><font color="red">Short-term memory in LangGraph</font></h1>

<font color="pink">Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro </font>


![](https://cdn.prod.website-files.com/66841c2a95405226a60d332e/67372ce594995c3cfec35531_AI_20_retried.webp)


A memória de curto prazo é fundamental para manter as conversas fluindo naturalmente, e o ``LangGraph`` facilita sua implementação. Neste repositório, exploraremos como o ``LangGraph`` lida com a memória de curto prazo usando ``checkpoints`` com escopo de ``thread`` (linha de execução ou sessão de conversa única) e mostrarei exemplos práticos para demonstrar isso na prática.


## <font color="gree">O que é memória de curto prazo no LangGraph?</font>

O LangGraph gerencia a memória de curto prazo como parte do estado de um agente, persistindo-a por meio de pontos de verificação com escopo de thread. Esse estado normalmente inclui o histórico da conversa — entradas humanas e respostas da IA ​​— juntamente com quaisquer outros dados relevantes, como arquivos enviados ou saídas geradas. Ao armazenar esse estado no grafo, o agente pode manter o contexto completo dentro de uma única thread de conversa, mantendo as diferentes threads isoladas umas das outras.


## <font color="gree">Adicionando Memória de Curto Prazo com Checkpoints</font>

Para fornecer memória ao nosso ``chatbot``, usaremos ``checkpointers`` do ``LangGraph`` e um mecanismo ``thread_id`` para persistir o estado entre as invocações.

O bot lembrará do contexto da conversa! O ``checkpointer`` persiste o estado, e o ``thread_id`` garante que todas as interações permaneçam dentro da mesma thread de conversa. Cada nova entrada é adicionada ao histórico de mensagens existente, fornecendo ao ``LLM`` o contexto completo.

### <font color="orange">Tipos de Checkpointers</font>

#### 1. **MemorySaver** (Memória Volátil - RAM)
```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)
```

**Características:**
- ✅ Muito rápido
- ✅ Ideal para desenvolvimento e testes
- ❌ **Memória perdida ao fechar o script**
- ❌ Não persiste entre execuções

#### 2. **SqliteSaver** (Memória Persistente - Disco)
```python
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

conn = sqlite3.connect("chatbot_memory.db", check_same_thread=False)
memory = SqliteSaver(conn)
graph = graph_builder.compile(checkpointer=memory)
```

**Características:**
- ✅ Rápido
- ✅ **Memória persiste entre execuções**
- ✅ Ideal para produção
- ✅ Histórico ilimitado


## <font color="gree">Gerenciando conversas longas</font>

À medida que as conversas se desenvolvem, o histórico de mensagens pode ultrapassar os limites do contexto de um ``LLM`` (Language Learning Model), causando erros. O ``LangGraph`` oferece duas estratégias principais para lidar com isso: ``truncar mensagens`` e ``resumir conversas``.

![](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*rcwh5AJZKUKz53abp1RuMg.png)



## <font color="gree">Recortando mensagens</font>

 Vamos recortar a lista de mensagens para manter apenas as últimas entradas. Você pode usar uma função de redução personalizada para filtrar mensagens com base na informação do estado ou você pode usar ``RemoveMessage`` para remover a mensagem do estado quando usando ``add_messages`` como o reducer.




## <font color="gree">Memória Persistente no LangGraph</font>

## O que Aconteceu?

Quando você parou e reiniciou o script, a memória foi perdida porque estava usando `MemorySaver()`, que armazena dados apenas em **RAM (memória volátil)**.

## 📊 Comparação: ``MemorySaver`` vs ``SqliteSaver``

| Característica | ``MemorySaver`` | ``SqliteSaver`` |
|---------------|-------------|-------------|
| **Armazenamento** | RAM (memória volátil) | Disco (arquivo SQLite) |
| **Persistência** | ❌ Perdida ao fechar | ✅ Mantida entre execuções |
| **Performance** | ⚡ Muito rápida | ⚡ Rápida |
| **Uso de disco** | Zero | Mínimo (~KB) |
| **Caso de uso** | Testes, desenvolvimento | Produção, aplicações reais |
| **Threads múltiplas** | ✅ Suportado | ✅ Suportado |
| **Histórico longo** | Limitado pela RAM | Ilimitado |

## 🔄 Mudanças Implementadas

### ``Antes`` (MemorySaver - Volátil)
```python
from langgraph.checkpoint.memory import MemorySaver

graph = graph_builder.compile(checkpointer=MemorySaver())
```

**Resultado:**
- ✅ Memória funciona durante a execução
- ❌ Tudo é perdido ao fechar o script
- ❌ Nova execução = nova conversa

### ``Depois`` (SqliteSaver - Persistente)
```python
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3

# Criar conexão SQLite
conn = sqlite3.connect("chatbot_memory.db", check_same_thread=False)
memory = SqliteSaver(conn)
graph = graph_builder.compile(checkpointer=memory)
```

**Resultado:**
- ✅ Memória funciona durante a execução
- ✅ Memória persiste ao fechar o script
- ✅ Nova execução = continua conversa anterior

## 🗂️ Arquivo de Banco de Dados

O SQLite cria um arquivo chamado `chatbot_memory.db` que contém:

- ``Checkpoint``: Snapshots do estado completo
- ``Histórico de mensagens``: Todas as conversas
- ``Metadados``: Thread IDs, timestamps, etc.

### Estrutura
```
chatbot_memory.db
├── checkpoints (tabela principal)
├── checkpoint_blobs (dados binários)
└── checkpoint_writes (histórico de escritas)
```

## <font color="gree">Como Usar</font>

### 1. Instalação da Dependência
```bash
uv add langgraph-checkpoint-sqlite
```

### 2. Conversar com Memória Persistente
```bash
uv run chatbot_with_memory_checkpoints.py
```

### 3. Teste de Persistência
```bash
# Primeira execução
👤 Você: Meu nome é Eddy
🤖 Assistente: Prazer, Eddy!

# Fechar o script (Ctrl+C ou 'sair')

# Segunda execução (nova janela de terminal)
👤 Você: Qual é o meu nome?
🤖 Assistente: Seu nome é Eddy!  # ✅ LEMBROU!
```

## 🗑️ Limpando a Memória

### Opção 1: Comando Interno
Durante a conversa, digite:
```
👤 Você: limpar
```

### Opção 2: Deletar Arquivo Manualmente
```bash
rm chatbot_memory.db
```

### Opção 3: Programaticamente
```python
import os
if os.path.exists("chatbot_memory.db"):
    os.remove("chatbot_memory.db")
```

## 🔐 Gerenciamento de Threads

### Thread Única (Um Usuário)
```python
config = {"configurable": {"thread_id": "usuario_1"}}
```

### Múltiplas Threads (Vários Usuários)
```python
# Usuário A
config_a = {"configurable": {"thread_id": "user_123"}}
graph.invoke(input, config=config_a)

# Usuário B (conversa separada)
config_b = {"configurable": {"thread_id": "user_456"}}
graph.invoke(input, config=config_b)
```

**Resultado:** Cada usuário tem seu próprio histórico isolado!

## 🚀 Funcionalidades Novas

### 1. Detecção Automática de Histórico
Ao iniciar o script, ele verifica se há histórico prévio:
```python
state_snapshot = graph.get_state(config)
if state_snapshot.values.get("messages"):
    print("📚 Histórico detectado! Continuando conversa anterior...")
```

### 2. Continuidade Automática
Se houver histórico, ele é automaticamente carregado e exibido.

### 3. Comandos Especiais
- `sair`, `quit`, `exit` → Encerra (salvando memória)
- `limpar`, `reset`, `apagar` → Apaga toda a memória

## 💡 Melhores Práticas

### ✅ Faça
- Use `SqliteSaver` para aplicações em produção
- Use ``thread_id`` único por usuário
- Implemente limpeza periódica de conversas antigas
- Faça backup do arquivo .db em produção

### ❌ Evite
- Usar `MemorySaver` em produção
- Compartilhar thread_id entre usuários diferentes
- Deletar o arquivo .db sem aviso ao usuário
- Armazenar dados sensíveis sem criptografia

## 🔍 Debugging e Inspeção

### Ver Estado Atual
```python
state = graph.get_state(config)
print(state.values["messages"])
```

### Listar Todos os Checkpoints
```python
checkpoints = list(memory.list(config))
for checkpoint in checkpoints:
    print(f"Checkpoint ID: {checkpoint.id}")
```

### Voltar a um Checkpoint Anterior
```python
# Não implementado neste exemplo, mas é possível!
state = graph.get_state(config, checkpoint_id="...")
```


## 🎓 Conceitos-Chave

### ``Checkpoint``
Snapshot completo do estado da aplicação em um momento específico.

### ``Thread``
Sessão de conversa isolada com seu próprio histórico.

### ``Persistência``
Capacidade de manter dados após o término da execução do programa.

### ``Checkpointer``
Componente responsável por salvar e recuperar checkpoints.



## 📚 Links de estudo:

- [Medium: Understanding Short-Term Memory in LangGraph: A Hands-On Guide](https://medium.com/@sajith_k/understanding-short-term-memory-in-langgraph-a-hands-on-guide-5536f39d0cb3)
- [Documentação LangGraph - Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [LangGraph Checkpoints](https://langchain-ai.github.io/langgraph/concepts/low_level/#checkpoints)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
