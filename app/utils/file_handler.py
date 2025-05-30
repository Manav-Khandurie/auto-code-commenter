# app/utils/file_handler.py
import os
import json
def walk_code_files(src_folder):
    for root, _, files in os.walk(src_folder):
        for file in files:
            if file.endswith(".py") or file.endswith(".sql") or file.endswith(".ipynb"):
                yield os.path.join(root, file)

def read_code(filepath):
    if filepath.endswith(".ipynb"):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        with open(filepath, 'r') as f:
            return f.read()

def write_code(filepath, content):
    backup_path = filepath + ".bak"
    os.rename(filepath, backup_path)
    if filepath.endswith(".ipynb"):
        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2)
    with open(filepath, 'w') as f:
        f.write(content)
