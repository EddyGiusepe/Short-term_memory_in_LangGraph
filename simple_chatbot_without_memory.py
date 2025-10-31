#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script simple_chatbot_without_memory.py
=======================================
Este script cria um chatbot simples sem memória.

Observe como o bot esquece meu nome entre as duas interações.
Cada interação começa do zero, sem nenhuma lembrança das mensagens
anteriores. Isso funciona bem para respostas pontuais, mas é 
péssimo para uma conversa.

Run
---
uv run simple_chatbot_without_memory.py
"""
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from typing import Annotated, List
from typing_extensions import TypedDict

import os
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())  # read local .env file
GROQ_API_KEY = os.environ["GROQ_API_KEY"]

class State(TypedDict):
    messages:Annotated[List[AnyMessage],add_messages]

llm = ChatGroq(model="llama-3.3-70b-versatile",
               api_key=GROQ_API_KEY,
               temperature=0.0
               )

prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_message}"),
        MessagesPlaceholder("messages")
    ]
)

llm_model = prompt_template | llm

graph_builder=StateGraph(State)

def ChatNode(state:State)->State:
    system_message="""Você é um assistente de IA. Responda as perguntas do usuário
                      de forma clara,concisa e factual.
                   """
    state["messages"]=llm_model.invoke({"system_message":system_message,"messages":state["messages"]})
    return state

graph_builder.add_node("chatnode", ChatNode)
graph_builder.add_edge(START, "chatnode")
graph_builder.add_edge("chatnode", END)
graph = graph_builder.compile()

# First input:
input_state={"messages":["Meu nome é Eddy Giusepe Chirinos Isidro"]}
response_state=graph.invoke(input_state)

for message in response_state["messages"]:
    message.pretty_print()

# Second input:
input_state={"messages":["Quem sou eu?"]}
response_state=graph.invoke(input_state)

for message in response_state["messages"]:
    message.pretty_print()
