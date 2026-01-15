import streamlit as st
import requests
import time

# Connect to the Backend running on port 8000
API_URL = "http://localhost:8000"

st.set_page_config(page_title="AI Test Architect", layout="wide", page_icon="🐧")
st.title("🐧 AI Test Architect (Modular)")

# --- API HELPER FUNCTIONS ---
def get(endpoint):
    try: 
        response = requests.get(f"{API_URL}/{endpoint}")
        if response.status_code == 200:
            return response.json()
    except Exception: 
        return None
    return None

def post(endpoint, data):
    try: 
        response = requests.post(f"{API_URL}/{endpoint}", json=data)
        if response.status_code == 200:
            return response.json()
    except Exception: 
        return None
    return None

# --- SIDEBAR (CONTROLS) ---
with st.sidebar:
    st.header("📂 Test Files")
    if st.button("🔄 Refresh"): st.rerun()
    
    # 1. Fetch file list from Backend
    data = get("files")
    if data:
        for f in data.get("files", []):
            col1, col2 = st.columns([0.8, 0.2])
            col1.code(f, language="text")
            # 2. Button triggers a run on the Backend
            if col2.button("▶️", key=f):
                post(f"run/{f}", {})
                st.toast(f"Request sent: {f}")

    st.divider()
    st.header("⚙️ Console")
    
    # 3. Poll Backend for Status
    state = get("status")
    if state:
        logs = state.get("logs", "")
        status = state.get("status", "idle")
        
        st.text_area("Live Output", logs, height=300)
        
        if status == "running":
            st.info("Test Running...")
            time.sleep(1) # Wait 1s
            st.rerun()    # Refresh UI automatically
        elif status == "finished":
            st.success("Finished!")

# --- MAIN CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ex: Write a login test"):
    # 1. Show User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("Backend Processing..."):
        # 2. Send Message to Backend
        res = post("chat", {"messages": st.session_state.messages})
        
        if res:
            content = res.get("content", "Error: No content from backend")
            
            # 3. Handle Commands (Client-side actions)
            if "```robot" in content:
                # Extract code and save via API
                try:
                    code = content.split("```robot")[1].split("```")[0].strip()
                    filename = "generated.robot"
                    for line in content.split('\n'):
                        if "File:" in line: filename = line.split("File:")[1].strip()
                    
                    post("files", {"filename": filename, "content": code})
                    st.success(f"Saved {filename} to Backend")
                except:
                    pass

            if "ACTION: RUN" in content:
                f = content.split("ACTION: RUN")[1].strip()
                post(f"run/{f}", {})
                st.rerun()

            st.markdown(content)
            st.session_state.messages.append({"role": "assistant", "content": content})
        else:
            st.error("❌ Could not connect to Backend (is it running on port 8000?)")