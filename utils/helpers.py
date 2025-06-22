import re

def clean_code(raw_output: str) -> str:
    """Extract Python code from Markdown-style code blocks"""
    pattern = r'```python(.*?)```'
    matches = re.findall(pattern, raw_output, re.DOTALL)
    if matches:
        return matches[0].strip()
    return raw_output.strip()

def secure_execution(code: str) -> str:
    """Remove dangerous constructs from code"""
    blacklist = [
        "os.system", "subprocess", "shutil", "rm ", "del ",
        "import os", "import sys", "import subprocess"
    ]
    for pattern in blacklist:
        if pattern in code:
            code = code.replace(pattern, "# DISABLED: " + pattern)
    return code
