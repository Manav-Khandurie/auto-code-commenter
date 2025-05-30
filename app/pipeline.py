# app/pipeline.py

from app.agents.comment_agent import CodeCommentAgent
from app.utils.file_handler import walk_code_files, read_code, write_code
from app.core.models import get_model_instance
import nbformat
import os

def extract_code_from_ipynb(filepath: str) -> str:
    """Extract code from code cells in a Jupyter notebook."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        code_cells = [cell for cell in nb.cells if cell.cell_type == 'code']
        code_str = "\n".join(cell.source for cell in code_cells)
        return code_str
    except Exception as e:
        print(f"❌ Error reading notebook {filepath}: {e}")
        return ""

def load_notebook(filepath: str):
    """Loads a notebook and returns the nbformat.NotebookNode object."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return nbformat.read(f, as_version=4)
    except Exception as e:
        print(f"❌ Failed to load notebook {filepath}: {e}")
        return None

def write_notebook(filepath: str, notebook_node):
    """Writes a notebook node back to file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            nbformat.write(notebook_node, f)
    except Exception as e:
        print(f"❌ Failed to write notebook {filepath}: {e}")

def run_commenting_pipeline(config=None, model_name: str = "deepseek-chat", src_folder: str = "./src"):
    if config:
        project_cfg = config.get("project", {})
        include = project_cfg.get("include", [])
        exclude = project_cfg.get("exclude", [])
        file_types = project_cfg.get("file_types", [".py", ".sql", ".ipynb"])
        model_cfg = config.get("model", {})
        model = get_model_instance(model_cfg)
        if include:
            src_folder = include[0]
    else:
        model = get_model_instance({
            "provider": {"type": "deepseek"},
            "model_name": model_name,
        })

    agent = CodeCommentAgent(model)

    for filepath in walk_code_files(src_folder):
        if file_types and not any(filepath.endswith(ext) for ext in file_types):
            continue

        print(f"[...] Commenting: {filepath}")

        if filepath.endswith(".ipynb"):
            nb_node = load_notebook(filepath)
            if not nb_node:
                print(f"⚠️  Could not load notebook {filepath}, skipping.")
                continue
            updated_nb = agent.generate_comment_for_ipynb(nb_node)
            write_notebook(filepath, updated_nb)
            print(f"[✔] Updated: {filepath}")
            continue  # Skip rest of loop

        original = read_code(filepath)
        if not original.strip():
            print(f"⚠️  {filepath} is empty or could not be read, skipping.")
            continue

        if filepath.endswith(".py"):
            updated = agent.generate_comment_for_python(original)
        elif filepath.endswith(".sql"):
            updated = agent.generate_comment_for_sql(original)
        else:
            print(f"⚠️  Skipping unsupported file {filepath}")
            continue

        print("----- begin updated snippet -----")
        print(updated[:200])
        print("-----  end updated snippet  ------")

        write_code(filepath, updated)
        print(f"[✔] Updated: {filepath}")
