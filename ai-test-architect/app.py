import time
import os
import subprocess
import sys
import fcntl # Specific to Linux/WSL for non-blocking IO
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

# --- 1. SETUP & LOGGING ---
def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)
    return f"[{ts}] {msg}"

if "system_logs" not in st.session_state:
    st.session_state.system_logs = []

def ui_log(msg):
    entry = log(msg)
    st.session_state.system_logs.insert(0, entry)
    if len(st.session_state.system_logs) > 20:
        st.session_state.system_logs.pop()

st.set_page_config(page_title="AI Test Architect", layout="wide", page_icon="🐧")
st.title("🐧 AI Test Architect (Real-Time)")

# --- 2. PATH CONFIGURATION ---
SCRIPT_LOCATION = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = SCRIPT_LOCATION
TESTS_DIR = os.path.join(WORKSPACE_ROOT, "tests")
RESULTS_DIR = os.path.join(WORKSPACE_ROOT, "results")
PROJECT_INDEX_FILE = os.path.join(WORKSPACE_ROOT, "project.md")

os.makedirs(TESTS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# --- 3. IMPORTS ---
try:
    from dotenv import load_dotenv
    load_dotenv()
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage
except Exception as e:
    st.error(f"Startup Error: {e}")
    st.stop()

# --- 4. ENGINE FUNCTIONS ---

def scan_project():
    if not os.path.exists(TESTS_DIR): return []
    files = [f for f in os.listdir(TESTS_DIR) if f.endswith(".robot")]
    
    index_content = f"# Project Index\n\n**Location:** `{TESTS_DIR}`\n\n## Files:\n"
    for f in files:
        index_content += f"- **{f}**\n"
    
    with open(PROJECT_INDEX_FILE, "w") as f:
        f.write(index_content)
    return files

def write_file_and_verify(filename, content):
    full_path = os.path.join(TESTS_DIR, filename)
    ui_log(f"Writing to: {full_path}")
    try:
        with open(full_path, "w") as f: f.write(content)
        if os.path.exists(full_path):
            scan_project() 
            return f"✅ Saved to `{filename}`"
        return "❌ Error: Write failed"
    except Exception as e:
        return f"❌ Error: {e}"

def read_file(filename):
    path = os.path.join(TESTS_DIR, filename)
    if os.path.exists(path):
        return f"--- Content of {filename} ---\n" + open(path, "r").read()
    return "File not found."

# --- 5. REAL-TIME BACKGROUND RUNNER ---
if "active_process" not in st.session_state:
    st.session_state.active_process = None
    st.session_state.live_logs = "" # Stores the accumulating logs
    st.session_state.last_report_path = None

def set_non_blocking(file):
    """Makes a file object non-blocking (Linux/WSL only)."""
    fd = file.fileno()
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

def start_test_background(filename):
    test_path = os.path.join(TESTS_DIR, filename)
    if not os.path.exists(test_path):
        return f"Error: {filename} not found."

    # Removed "--console dotted" so we see actual text
    cmd = [
        "robot", 
        "--outputdir", RESULTS_DIR, 
        test_path
    ]
    
    try:
        # Start process with pipes
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Merge stderr into stdout
            text=True,
            cwd=WORKSPACE_ROOT,
            bufsize=1, # Line buffered
            start_new_session=True 
        )
        
        # KEY: Make output non-blocking so we can read "whatever is there" without hanging
        set_non_blocking(proc.stdout)
        
        st.session_state.active_process = proc
        st.session_state.active_test_name = filename
        st.session_state.live_logs = f"🚀 Starting {filename}...\n"
        st.session_state.last_report_path = None
        
        ui_log(f"Started: {' '.join(cmd)}")
        return f"🚀 Started {filename}..."
    except Exception as e:
        return f"Failed: {e}"

# --- 6. SIDEBAR & MONITOR ---
with st.sidebar:
    st.header("📂 Explorer")
    if st.button("🔄 Refresh"):
        scan_project()
        st.rerun()

    files = scan_project()
    if files:
        for f in files: st.markdown(f"📄 `{f}`")
    else:
        st.caption("No tests found.")

    st.divider()
    st.header("⚙️ Live Runner")
    
    if st.session_state.active_process:
        proc = st.session_state.active_process
        
        # 1. READ NEW LOGS (Non-Blocking)
        try:
            # Read everything currently in the buffer
            new_data = proc.stdout.read()
            if new_data:
                st.session_state.live_logs += new_data
        except Exception:
            pass # No data available right now
            
        # 2. CHECK STATUS
        ret_code = proc.poll()
        
        if ret_code is None:
            # --- STILL RUNNING ---
            st.info(f"🏃 Running: {st.session_state.active_test_name}")
            
            # Show live logs in a scrollable box
            st.text_area("Console Output", st.session_state.live_logs, height=300)
            
            if st.button("🛑 Abort"):
                proc.terminate()
                st.session_state.active_process = None
                st.session_state.live_logs += "\n[ABORTED BY USER]"
                st.rerun()
            
            # REFRESH THE UI AUTOMATICALLY
            time.sleep(0.5) 
            st.rerun()
            
        else:
            # --- FINISHED ---
            status = "✅ PASS" if ret_code == 0 else "❌ FAIL"
            st.write(f"**Result:** {status}")
            
            # Show final complete logs
            st.text_area("Final Output", st.session_state.live_logs, height=300)
            
            # Check for report
            report_file = os.path.join(RESULTS_DIR, "report.html")
            if os.path.exists(report_file):
                st.session_state.last_report_path = report_file
                if "Report Generated" not in st.session_state.live_logs:
                     st.success("Report Ready!")
            
            if st.button("Clear Status"):
                st.session_state.active_process = None
                st.rerun()

# --- 7. REPORT VIEWER ---
if st.session_state.last_report_path:
    st.divider()
    st.subheader("📊 Test Report")
    with open(st.session_state.last_report_path, "r", encoding="utf-8") as f:
        report_html = f.read()
    
    st.download_button("📥 Download HTML", report_html, "report.html", "text/html")
    components.html(report_html, height=600, scrolling=True)
    st.divider()

# --- 8. CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ex: Run hello_world.robot"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Context Loading
    project_index_content = ""
    if os.path.exists(PROJECT_INDEX_FILE):
         with open(PROJECT_INDEX_FILE, "r") as f: project_index_content = f.read()

    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
        system_prompt = f"""
        You are a QA Architect.
        WORKSPACE ROOT: {WORKSPACE_ROOT}
        PROJECT CONTEXT: {project_index_content}
        
        TOOLS:
        1. WRITE: Output a ```robot code block. Put "File: <name>" on the line before.
        2. RUN: "ACTION: RUN <filename>"
        3. READ: "ACTION: READ <filename>"
        """
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                msgs = [SystemMessage(content=system_prompt)] + \
                       [HumanMessage(content=m["content"]) for m in st.session_state.messages]
                
                response = llm.invoke(msgs)
                content = response.content
                
                if "```robot" in content:
                    code = content.split("```robot")[1].split("```")[0].strip()
                    filename = "generated.robot"
                    for line in content.split('\n'):
                        if "File:" in line: 
                            parts = line.split("File:")[1].strip().split()
                            if parts: filename = parts[0]
                    if "hello" in prompt.lower(): filename = "hello_world.robot"
                    res = write_file_and_verify(filename, code)
                    st.success(res)

                if "ACTION: RUN" in content:
                    f = content.split("ACTION: RUN")[1].strip()
                    res = start_test_background(f)
                    st.info(res)
                    # Trigger the refresh loop
                    st.rerun() 
                
                if "ACTION: READ" in content:
                    f = content.split("ACTION: READ")[1].strip()
                    st.text(read_file(f))

                st.markdown(content)
                st.session_state.messages.append({"role": "assistant", "content": content})

    except Exception as e:
        st.error(f"Error: {e}")