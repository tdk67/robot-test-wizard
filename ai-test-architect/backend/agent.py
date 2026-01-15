from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
import os

load_dotenv()

try:
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
except:
    llm = None

def ask_agent(messages, context):
    if not llm:
        return "Error: OpenAI Key missing."
    
    system_prompt = f"""
    You are a QA Architect.
    PROJECT CONTEXT: {context}
    
    TOOLS:
    1. WRITE: Output a ```robot code block. Put "File: <name>" on the line before.
    2. RUN: "ACTION: RUN <filename>"
    """
    
    # Convert incoming dicts to LangChain objects
    lc_messages = [SystemMessage(content=system_prompt)]
    for m in messages:
        if m['role'] == 'user':
            lc_messages.append(HumanMessage(content=m['content']))
        elif m['role'] == 'assistant':
            # Skip system messages to prevent confusion
            pass
            
    response = llm.invoke(lc_messages)
    return response.content