# app/pipeline.py
from app.agents.comment_agent import CodeCommentAgent
from app.utils.file_handler import walk_code_files, read_code, write_code
from app.core.models import DeepSeekModel

def run_commenting_pipeline(model_name: str = "deepseek-chat", src_folder: str = "./src"):
    model = DeepSeekModel(model_name)
    agent = CodeCommentAgent(model)

    for filepath in walk_code_files(src_folder):
        print(f"[...] Commenting: {filepath}")
        original = read_code(filepath)
        if not original.strip():
            print(f"⚠️  {filepath} is empty, skipping.")
            continue

        # DEBUG: print a snippet so you know it’s loaded
        print("----- begin original snippet -----")
        print(original[:200])
        print("-----  end original snippet  ------")

        # Check file extension and generate comments accordingly
        if filepath.endswith(".py"):
            updated = agent.generate_comment_for_python(original)
        elif filepath.endswith(".sql"):
            updated = agent.generate_comment_for_sql(original)
        
        # DEBUG: inspect what the model returns
        print("----- begin updated snippet -----")
        print(updated[:200])
        print("-----  end updated snippet  ------")

        write_code(filepath, updated)
        print(f"[✔] Updated: {filepath}")
