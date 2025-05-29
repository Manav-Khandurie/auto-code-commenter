# app/utils/file_handler.py
import os

def walk_code_files(src_folder):
    for root, _, files in os.walk(src_folder):
        for file in files:
            if file.endswith(".py") or file.endswith(".sql"):
                yield os.path.join(root, file)

def read_code(filepath):
    with open(filepath, 'r') as f:
        return f.read()

def write_code(filepath, content):
    backup_path = filepath + ".bak"
    os.rename(filepath, backup_path)
    with open(filepath, 'w') as f:
        f.write(content)
