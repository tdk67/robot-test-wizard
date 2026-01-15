from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import glob
from typing import List
from .agent import ask_agent

app = FastAPI()

# --- CONFIG ---
BASE_DIR = os.getcwd() # /workspaces/ai-test-architect
TESTS_DIR = os.path.join(BASE_DIR, "tests")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(TESTS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# --- GLOBAL STATE (MVP) ---
runner_state = {
    "process": None,
    "logs": "",
    "active_file": None,
    "status": "idle" # idle, running, finished
}

class ChatRequest(BaseModel):
    messages: List[dict]

class FileWriteRequest(BaseModel):
    filename: str
    content: str

# --- ROUTES ---

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/files")
def list_files():
    files = [os.path.basename(f) for f in glob.glob(os.path.join(TESTS_DIR, "*.robot"))]
    return {"files": sorted(files)}

@app.post("/chat")
def chat(req: ChatRequest):
    files = list_files()["files"]
    response = ask_agent(req.messages, f"Files: {files}")
    return {"content": response}

@app.post("/files")
def save_file(req: FileWriteRequest):
    path = os.path.join(TESTS_DIR, req.filename)
    with open(path, "w") as f:
        f.write(req.content)
    return {"status": "saved", "path": path}

# --- EXECUTION ENGINE ---

@app.post("/run/{filename}")
def run_test(filename: str):
    path = os.path.join(TESTS_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(404, "File not found")
    
    # Reset State
    runner_state["logs"] = f"🚀 Starting {filename}...\n"
    runner_state["active_file"] = filename
    runner_state["status"] = "running"
    
    cmd = ["robot", "--outputdir", RESULTS_DIR, path]
    
    # Start Async
    runner_state["process"] = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=BASE_DIR
    )
    return {"status": "started"}

@app.get("/status")
def get_status():
    proc = runner_state["process"]
    
    if proc:
        # 1. Read new logs
        try:
            # Set non-blocking read
            import fcntl
            fd = proc.stdout.fileno()
            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
            
            chunk = proc.stdout.read()
            if chunk: runner_state["logs"] += chunk
        except: pass
        
        # 2. Check finish
        ret = proc.poll()
        if ret is not None:
            runner_state["status"] = "finished"
            runner_state["process"] = None
            status_text = "PASS" if ret == 0 else "FAIL"
            runner_state["logs"] += f"\n[Process Finished: {status_text}]"
            
    return {
        "status": runner_state["status"],
        "logs": runner_state["logs"],
        "file": runner_state["active_file"]
    }