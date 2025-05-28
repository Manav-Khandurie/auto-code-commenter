from app.agents.comment_agent import CodeCommentAgent
from app.utils.file_handler import walk_py_files, read_code, write_code
from app.core.models import OllamaModel

def run_commenting_pipeline(model_name: str = "codagemma:2b", src_folder: str = "./src"):
    model = OllamaModel(model_name)
    agent = CodeCommentAgent(model)

    for filepath in walk_py_files(src_folder):
        print(f"[...] Commenting: {filepath}")
        original = read_code(filepath)
        updated = agent.generate_comment(original)
        write_code(filepath, updated)
        print(f"[✔] Updated: {filepath}")
