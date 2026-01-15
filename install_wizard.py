import streamlit as st
import os
import requests
from dotenv import load_dotenv

# --- 1. SETUP & CONFIG ---
st.set_page_config(page_title="Installation Wizard 🧙‍♂️", page_icon="🧙‍♂️", layout="wide")

# Try loading from .env, otherwise ask user
load_dotenv()
if "OPENAI_API_KEY" not in st.session_state:
    st.session_state["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# --- 2. CONTENT & STEPS ---
REPO_URL = "https://github.com/tdk67/robot-test-wizard.git"

STEPS = {
    1: {
        "title": "Prerequisites Check",
        "content": """
        Before we begin, we need to make sure your Windows machine is ready.
        
        **We need 3 things:**
        1. **WSL 2** (Windows Subsystem for Linux)
        2. **Docker Engine** (Inside Ubuntu)
        3. **VS Code** (With 'Dev Containers' extension)
        """,
        "action": "Check if you have these installed.",
        "verify": "Open PowerShell and type `wsl --list`. Do you see Ubuntu?"
    },
    2: {
        "title": "Clone the Repository",
        "content": f"""
        Now, let's get the code onto your machine.
        
        **Command:**
        ```bash
        git clone {REPO_URL}
        cd robot-test-wizard/ai-test-architect
        ```
        
        *Note: Do this inside your WSL terminal (Ubuntu), NOT standard PowerShell.*
        """,
        "action": "Run the git clone command.",
        "verify": "Type `ls` in that folder. Do you see `app.py` and `Dockerfile`?"
    },
    3: {
        "title": "Build the Environment",
        "content": """
        We will use VS Code to build the Docker container automatically.
        
        1. Open VS Code in that folder: `code .`
        2. Look for the pop-up: *"Folder contains a Dev Container configuration..."*
        3. Click **Reopen in Container**.
        
        *(Alternative: Press F1 -> 'Dev Containers: Reopen in Container')*
        """,
        "action": "Open VS Code and start the container build.",
        "verify": "Does your VS Code terminal say `root@...` instead of your Windows user?"
    },
    4: {
        "title": "Configuration Secrets",
        "content": """
        The AI needs a brain! We need to set your OpenAI API Key.
        
        1. Create a file named `.env` in the root folder.
        2. Paste your key inside:
        ```ini
        OPENAI_API_KEY=sk-proj-....
        ```
        """,
        "action": "Create the .env file.",
        "verify": "Run `cat .env` in the terminal. Does it show your key?"
    },
    5: {
        "title": "Launch!",
        "content": """
        Everything is ready. Let's start the engine.
        
        **Run this command:**
        ```bash
        ./start.sh
        ```
        """,
        "action": "Run the start script.",
        "verify": "Open http://localhost:8501. Do you see the Penguin?"
    }
}

# --- 3. UI LAYOUT ---

# Sidebar: Global Config & Progress
with st.sidebar:
    st.title("🧙‍♂️ Install Wizard")
    
    # API Key Handling
    if not st.session_state["OPENAI_API_KEY"]:
        st.warning("⚠️ No API Key found!")
        key_input = st.text_input("Enter OpenAI Key:", type="password")
        if key_input:
            st.session_state["OPENAI_API_KEY"] = key_input
            st.success("Key saved!")
            st.rerun()
    else:
        st.success("🔑 API Key Active")

    st.divider()
    
    # Progress Tracking
    if "current_step" not in st.session_state:
        st.session_state.current_step = 1

    st.write(f"**Step {st.session_state.current_step} of {len(STEPS)}**")
    progress_val = st.session_state.current_step / len(STEPS)
    st.progress(progress_val)

# Main Area
step_data = STEPS[st.session_state.current_step]

st.header(f"Step {st.session_state.current_step}: {step_data['title']}")
st.markdown(step_data['content'])

st.info(f"👉 **Action:** {step_data['action']}")

# Verification & Navigation
with st.expander("✅ Verification Checklist (Open to Confirm)", expanded=True):
    st.write(step_data['verify'])
    chk = st.checkbox("I have completed this step successfully.")

    if chk:
        if st.session_state.current_step < len(STEPS):
            if st.button("Next Step ➡️"):
                st.session_state.current_step += 1
                st.rerun()
        else:
            st.success("🎉 INSTALLATION COMPLETE! You are ready to automate.")
            st.balloons()

st.divider()

# --- 4. AI TROUBLESHOOTER (Chat) ---
st.subheader("🤖 Troubleshooting Assistant")
st.caption("Stuck? Ask me anything about WSL, Docker, or Python errors.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ex: 'My docker permission is denied'"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not st.session_state["OPENAI_API_KEY"]:
        st.error("Please enter an API Key in the sidebar to use the Assistant.")
    else:
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage, SystemMessage

            llm = ChatOpenAI(api_key=st.session_state["OPENAI_API_KEY"], model="gpt-4o")
            
            # Context-Aware System Prompt
            system_prompt = f"""
            You are an Expert DevOps Engineer helping a user install the 'AI Test Architect'.
            Current Step: {step_data['title']}
            Context: {step_data['content']}
            
            Common Issues:
            - WSL 2 not enabled (BIOS virtualization).
            - Docker permission denied (needs `sudo usermod -aG docker $USER`).
            - VS Code not connecting to WSL.
            
            Provide short, actionable CLI commands to fix errors.
            """
            
            msgs = [SystemMessage(content=system_prompt)] + \
                   [HumanMessage(content=m["content"]) for m in st.session_state.messages]
            
            with st.chat_message("assistant"):
                response = llm.invoke(msgs)
                st.markdown(response.content)
                st.session_state.messages.append({"role": "assistant", "content": response.content})
        
        except Exception as e:
            st.error(f"AI Error: {e}")