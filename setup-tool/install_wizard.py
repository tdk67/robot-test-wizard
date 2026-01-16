import streamlit as st
import os
import re
from dotenv import load_dotenv

# --- 1. CONFIGURATION ---
# The wizard now looks for docs in the sibling directory "../docs"
FILES_CONFIG = {
    "overview": "Requirements.md",
    "environment": "Environment.md", # Ensure you created this in docs/
    "install": "Install.md",
    "start_git": "StartFromGit.md",  # [NEW] Added based on your tree
    "context": ["PLAN.md"]           # Files to feed the AI
}

# Define where to look for the 'docs' folder relative to this script
# We look in:
# 1. "../docs" (Standard sibling structure)
# 2. "docs" (If running from root)
DOCS_DIRS = [
    os.path.join(os.path.dirname(__file__), "../docs"), # Sibling folder
    "docs",                                             # Local folder
    "../docs"                                           # Fallback
]

# --- 2. FILE & PARSING LOGIC ---

def find_file(filename):
    """Searches for a file in the defined docs directories."""
    for path in DOCS_DIRS:
        full_path = os.path.join(path, filename)
        if os.path.exists(full_path):
            return full_path
    return None

def load_file_content(filename):
    """Reads file content."""
    path = find_file(filename)
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

def parse_markdown_steps(md_content):
    """Splits Install.md into interactive steps."""
    if not md_content: return []
    
    # Split by '## Step' headers
    pattern = r"(## Step \d+.*)"
    parts = re.split(pattern, md_content)
    
    steps = []
    start_index = 0
    for i, part in enumerate(parts):
        if part.strip().startswith("## Step"):
            start_index = i
            break
            
    for i in range(start_index, len(parts), 2):
        if i + 1 < len(parts):
            header = parts[i].strip().replace("#", "").strip()
            content = parts[i+1].strip()
            steps.append({"title": header, "content": content})
    return steps

# --- 3. UI SETUP ---
st.set_page_config(page_title="Setup Wizard", page_icon="🧙‍♂️", layout="wide")
try: load_dotenv()
except: pass

# --- 4. DATA LOADING ---
if "knowledge_base" not in st.session_state:
    kb = {}
    
    # Load Main Docs
    for key, filename in FILES_CONFIG.items():
        if key == "context": continue
        kb[key] = load_file_content(filename)
    
    # Parse Steps
    kb["steps"] = parse_markdown_steps(kb.get("install", ""))
    
    # Load AI Context
    kb["extras"] = ""
    for f in FILES_CONFIG["context"]:
        content = load_file_content(f)
        if content: kb["extras"] += f"\n--- {f} ---\n{content}\n"
            
    st.session_state.knowledge_base = kb

kb = st.session_state.knowledge_base

# --- 5. MAIN UI ---

with st.sidebar:
    st.title("🧙‍♂️ Setup Wizard")
    
    # Navigation
    mode = st.radio("Navigation:", [
        "Project Overview", 
        "Execution Environment",
        "Installation Guide",
        "Start from Git" # [NEW]
    ])
    
    st.divider()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = st.text_input("OpenAI API Key:", type="password")
        if api_key: os.environ["OPENAI_API_KEY"] = api_key

# PAGE RENDERERS
if mode == "Project Overview":
    st.header("📂 Project Requirements")
    st.markdown(kb.get("overview") or "File not found.")

elif mode == "Execution Environment":
    st.header("🏗️ Architecture")
    st.markdown(kb.get("environment") or "File not found.")

elif mode == "Start from Git":
    st.header("🚀 Quick Start")
    st.markdown(kb.get("start_git") or "File not found.")

elif mode == "Installation Guide":
    if not kb.get("steps"):
        st.error(f"Could not parse steps from `{FILES_CONFIG['install']}`.")
    else:
        if "step_idx" not in st.session_state: st.session_state.step_idx = 0
        
        steps = kb["steps"]
        idx = st.session_state.step_idx
        
        st.progress((idx + 1) / len(steps))
        st.caption(f"Step {idx + 1} of {len(steps)}")
        
        st.subheader(steps[idx]["title"])
        st.markdown(steps[idx]["content"])
        
        st.divider()
        col1, col2 = st.columns([0.8, 0.2])
        with col2:
            if idx < len(steps) - 1:
                if st.button("Next Step ➡️"):
                    st.session_state.step_idx += 1
                    st.rerun()
            else:
                st.success("Done!")
                if st.button("Restart"):
                    st.session_state.step_idx = 0
                    st.rerun()

# --- 6. AI ASSISTANT ---
st.divider()
st.subheader("💬 Setup Helper")

if "chat" not in st.session_state: st.session_state.chat = []
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Ask about setup..."):
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    if api_key:
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage, SystemMessage
            llm = ChatOpenAI(api_key=api_key, model="gpt-4o", temperature=0)
            
            context = "\n".join([f"{k.upper()}:\n{v}" for k,v in kb.items() if isinstance(v, str)])
            sys_msg = f"You are a DevOps expert. Answer using this context:\n{context}"
            
            res = llm.invoke([SystemMessage(content=sys_msg), HumanMessage(content=prompt)])
            with st.chat_message("assistant"):
                st.markdown(res.content)
                st.session_state.chat.append({"role": "assistant", "content": res.content})
        except Exception as e:
            st.error(f"Error: {e}")