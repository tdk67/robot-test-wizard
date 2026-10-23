"""
dump_libdocs.py
Utility script to dump Robot Framework library documentation into Markdown format
for AI Skill references and human developer documentation.

Generates:
1. Full detailed Markdown documentation per library (<LibName>.md)
2. A consolidated quick-reference index (KEYWORDS_QUICKREF.md) with keyword signatures and shortdocs.
3. Automatically populates AI agent skill references under .agents/skills/
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Workspace root
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

# Libraries to document
LIBRARIES = [
    # Standard Core Libraries
    {"name": "BuiltIn", "target": "BuiltIn"},
    {"name": "Collections", "target": "Collections"},
    {"name": "String", "target": "String"},
    {"name": "OperatingSystem", "target": "OperatingSystem"},
    {"name": "DateTime", "target": "DateTime"},
    {"name": "Process", "target": "Process"},
    {"name": "XML", "target": "XML"},
    
    # Installed Third-party Libraries
    {"name": "RequestsLibrary", "target": "RequestsLibrary"},
    {"name": "Browser", "target": "Browser"},
    
    # Project Custom Libraries
    {
        "name": "PdfValidator",
        "target": str(WORKSPACE_ROOT / "resources" / "keywords" / "custom-libs" / "PdfValidator.py")
    },
    {
        "name": "DataLoader", 
        "target": str(WORKSPACE_ROOT / "resources" / "keywords" / "custom-libs" / "DataLoader.py")
    }
]

# Output directories
OUTPUT_DIRS = [
    WORKSPACE_ROOT / "docs" / "robot-libraries",
    WORKSPACE_ROOT / ".agents" / "skills" / "robotframework-architect" / "references"
]

SKILL_DIR = WORKSPACE_ROOT / ".agents" / "skills" / "robotframework-architect"

def ensure_dirs():
    for d in OUTPUT_DIRS:
        d.mkdir(parents=True, exist_ok=True)
    SKILL_DIR.mkdir(parents=True, exist_ok=True)

def dump_library_markdown(python_exe: str, lib_target: str, out_file: Path) -> bool:
    """Invokes robot.libdoc to dump a single library to Markdown."""
    cmd = [python_exe, "-m", "robot.libdoc", lib_target, str(out_file)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[WARN] Failed to dump {lib_target}: {res.stderr.strip()}", file=sys.stderr)
        return False
    print(f"[OK] Dumped Markdown: {out_file.name}")
    return True

def get_library_json_spec(python_exe: str, lib_target: str, temp_json: Path) -> dict:
    """Generates JSON spec using libdoc to extract keyword signatures and shortdocs."""
    cmd = [python_exe, "-m", "robot.libdoc", "--format", "JSON", lib_target, str(temp_json)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not temp_json.exists():
        return {}
    try:
        with open(temp_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    finally:
        if temp_json.exists():
            temp_json.unlink()

def build_quick_reference(all_specs: list, out_file: Path):
    """Generates a compact markdown quick reference table."""
    lines = [
        "# Robot Framework Keywords Quick Reference",
        "",
        "Quick signature and description index for Robot Framework standard, installed, and custom libraries.",
        "",
        "| Library | Keyword | Arguments | Description |",
        "| :--- | :--- | :--- | :--- |"
    ]
    
    for spec in all_specs:
        lib_name = spec.get("name", "Unknown")
        keywords = spec.get("keywords", [])
        for kw in sorted(keywords, key=lambda k: k.get("name", "")):
            name = kw.get("name", "")
            args_list = []
            for a in kw.get("args", []):
                arg_repr = a.get("repr") or a.get("name")
                args_list.append(f"`{arg_repr}`")
            args_str = ", ".join(args_list) if args_list else "*None*"
            
            # Clean shortdoc to single line
            shortdoc = kw.get("shortdoc", "").replace("\n", " ").strip()
            # Escape pipes for markdown table
            shortdoc = shortdoc.replace("|", "\\|")
            
            lines.append(f"| **{lib_name}** | `{name}` | {args_str} | {shortdoc} |")
    
    content = "\n".join(lines) + "\n"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Created Quick Reference: {out_file.name}")

def ensure_skill_definition():
    """Ensures .agents/skills/robotframework-architect/SKILL.md exists with relative links."""
    skill_file = SKILL_DIR / "SKILL.md"
    content = """---
name: robotframework-architect
description: Author, refactor, and execute modern Robot Framework 7.x test suites following the data-driven LEGO architecture (separation of code and YAML data, pre-run modifier hooks, and keyword lookups).
---

# Robot Framework Architect Skill

This skill provides guidelines, modern syntax standards, architectural patterns, and library references for generating and running Robot Framework 7.x tests natively.

---

## 1. Core Architectural Tenet: The "LEGO" Pattern

Every test suite must strictly decouple **Code (Logic)** from **Data (Values)**:
1. **Test Code (`.robot`)**: Contains *only* high-level reusable workflows and keyword contracts.
   - **Rule**: Never hardcode customer names, email addresses, phone numbers, product IDs, or base URLs into `.robot` test files.
2. **Test Data (`.yaml`)**: Contains concrete data instances and scenario permutations (`TestScenarios`, `ScenarioVars`, `RunSettings`).
3. **Pre-Run Hook (`DataLoader` / `SuiteVisitor`)**:
   - Uses Robot Framework's `--prerunmodifier` mechanism.
   - Before suite execution, it reads the matching YAML data file, clones the template test case for each scenario, and injects the variables.

---

## 2. Modern Robot Framework 7.x Syntax Guidelines

Always generate modern Robot Framework 7.x syntax. Avoid obsolete 3.x/4.x idioms.

### Variable Assignment (`VAR` syntax)
Use native `VAR` syntax (introduced in RF 7.0) instead of legacy assignment:
```robotframework
*** Test Cases ***
Example Variable Usage
    VAR    ${status}        ACTIVE
    VAR    ${timeout}       10
    VAR    @{items}         apple    banana    cherry
    VAR    &{user}          name=Alice    role=ADMIN
    VAR    ${suite_var}     123    scope=SUITE
```

### Flow Control (Native Block Syntax)
Never use legacy `Run Keyword If` or `Run Keyword And Return`. Always use native blocks:
```robotframework
    # IF / ELSE
    IF    $status == 'ACTIVE'
        Log To Console    User is active
    ELSE IF    $status == 'PENDING'
        Log To Console    User is pending
    ELSE
        Fail    Unexpected status: ${status}
    END

    # FOR LOOP
    FOR    ${item}    IN    @{items}
        Log To Console    Processing ${item}
    END

    # ERROR HANDLING
    TRY
        Some Risky Keyword
    EXCEPT    *Timeout*
        Log    Recovering from timeout
    FINALLY
        Cleanup Keyword
    END
```

---

## 3. Pre-Run Hook (`DataLoader`) Usage

To run a data-driven test with the YAML data driver:
```powershell
python -m robot --outputdir results --prerunmodifier resources/keywords/custom-libs/DataLoader.py:<ENV> testcases/<path_to_test>.robot
```

---

## 4. Library References & Exact Keyword Signatures

When writing keywords, look up exact arguments and signatures in:
- [KEYWORDS_QUICKREF.md](references/KEYWORDS_QUICKREF.md): Compact index of all keyword signatures and shortdocs across BuiltIn, Collections, RequestsLibrary, Browser, OperatingSystem, Process, DateTime, String, XML, and custom libraries.
- Detailed library markdown documentation:
  - [Browser.md](references/Browser.md) (Playwright-backed browser automation: `New Page`, `Click`, `Fill Text`, `Wait For Elements State`, assertions)
  - [BuiltIn.md](references/BuiltIn.md)
  - [Collections.md](references/Collections.md)
  - [RequestsLibrary.md](references/RequestsLibrary.md)
  - [OperatingSystem.md](references/OperatingSystem.md)
  - [String.md](references/String.md)
  - [DateTime.md](references/DateTime.md)
  - [Process.md](references/Process.md)
  - [XML.md](references/XML.md)
  - [PdfValidator.md](references/PdfValidator.md)
  - [DataLoader.md](references/DataLoader.md)

---

## 5. Lightweight Verification & Dry-Run (No Bloat)

Before running full tests, validate syntax and keyword availability directly via CLI:
```powershell
python -m robot --dryrun --outputdir results testcases/<path_to_test>.robot
```
To re-generate or update library documentation after installing a new package:
```powershell
python tools/dump_libdocs.py
```
"""
    skill_file.write_text(content.strip() + "\n", encoding="utf-8")
    print(f"[OK] Generated skill definition: {skill_file.relative_to(WORKSPACE_ROOT)}")

def main():
    python_exe = sys.executable
    print(f"Using Python: {python_exe}")
    ensure_dirs()
    ensure_skill_definition()
    
    all_specs = []
    temp_json = WORKSPACE_ROOT / "temp_spec.json"
    
    primary_dir = OUTPUT_DIRS[0]
    
    for lib in LIBRARIES:
        lib_name = lib["name"]
        lib_target = lib["target"]
        
        md_file = primary_dir / f"{lib_name}.md"
        success = dump_library_markdown(python_exe, lib_target, md_file)
        if success:
            spec = get_library_json_spec(python_exe, lib_target, temp_json)
            if spec:
                all_specs.append(spec)
    
    # Generate Quick Reference
    quickref_file = primary_dir / "KEYWORDS_QUICKREF.md"
    build_quick_reference(all_specs, quickref_file)
    
    # Mirror generated files to secondary directories (e.g. .agents/skills)
    for secondary_dir in OUTPUT_DIRS[1:]:
        for f in primary_dir.glob("*.md"):
            dest = secondary_dir / f.name
            dest.write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"[OK] Mirrored reference files to: {secondary_dir.relative_to(WORKSPACE_ROOT)}")

    print("\nAll library documentation and AI agent skills generated successfully.")

if __name__ == "__main__":
    main()
