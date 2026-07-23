#!/usr/bin/env python3
import os
import sys
import subprocess
import threading
import time

BASE_DIR = '/home/sword/Documents/BayazidxMarin'
TOOLS_DIR = os.path.join(BASE_DIR, 'tools')

def test_import(tool_name):
    """Try to import the tool module and see if there are import errors."""
    path = os.path.join(TOOLS_DIR, tool_name)
    mod_name = tool_name[:-3]  # remove .py
    # Add BASE_DIR to sys.path so that imports inside the tool work
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)
    try:
        # Execute the module in a new namespace
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
        # We'll exec the code but prevent the main block from running by setting __name__ to something else
        # However, exec will still run the whole module. To avoid side effects, we can try to import it as a module.
        # Since we added BASE_DIR to sys.path, we can try to import it.
        # But if the tool does relative imports, it might fail. We'll just exec and hope for no side effects.
        # We'll set __name__ to '__notmain__' to avoid the main block.
        globals_dict = {'__name__': '__notmain__', '__file__': path}
        exec(code, globals_dict)
        return True, "Import successful"
    except Exception as e:
        return False, f"Import error: {e}"

def test_run_with_timeout(tool_name, timeout=2):
    """Run the tool with a timeout, closing stdin immediately to avoid waiting for input."""
    path = os.path.join(TOOLS_DIR, tool_name)
    try:
        # We'll use Popen with stdin, stdout, stderr as pipes.
        # We'll close stdin immediately after starting (or set it to empty).
        proc = subprocess.Popen(
            [sys.executable, path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Close stdin to send EOF immediately
        proc.stdin.close()
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            return True, f"Exited with code {proc.returncode}", stdout, stderr
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
            return False, f"Timed out after {timeout}s", stdout, stderr
    except Exception as e:
        return False, f"Error running: {e}", "", ""

# Test the four tools
tools = ['news_harvester.py', 'bangla.py', 'tictactoe.py', 'wordgame.py']
print("=== Testing Import ===")
for tool in tools:
    ok, msg = test_import(tool)
    print(f"{tool}: {'OK' if ok else 'FAIL'} - {msg}")

print("\n=== Testing Run (with stdin closed) ===")
for tool in tools:
    ok, msg, stdout, stderr = test_run_with_timeout(tool, timeout=2)
    print(f"{tool}: {'OK' if ok else 'FAIL'} - {msg}")
    if not ok and stdout:
        # Truncate output
        if len(stdout) > 200:
            stdout = stdout[:200] + '...'
        print(f"  STDOUT: {stdout}")
    if not ok and stderr:
        if len(stderr) > 200:
            stderr = stderr[:200] + '...'
        print(f"  STDERR: {stderr}")
