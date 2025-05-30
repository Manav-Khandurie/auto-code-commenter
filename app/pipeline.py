# app/pipeline.py
from app.agents.comment_agent import CodeCommentAgent
from app.utils.file_handler import walk_code_files, read_code, write_code
from app.core.models import get_model_instance  # new factory method

def run_commenting_pipeline(config=None, model_name: str = "deepseek-chat", src_folder: str = "./src"):
    # If config provided, use model info & project scan config from it
    if config:
        project_cfg = config.get("project", {})
        include = project_cfg.get("include", [])
        exclude = project_cfg.get("exclude", [])
        file_types = project_cfg.get("file_types", [".py", ".sql"])
        model_cfg = config.get("model", {})
        model = get_model_instance(model_cfg)
        # src_folder override if project/include specified?
        if include:
            # For simplicity, use first include dir for scanning (or customize further)
            src_folder = include[0]
    else:
        model = get_model_instance({
            "provider": {"type": "deepseek"},
            "model_name": model_name,
        })

    agent = CodeCommentAgent(model)

    # Walk files respecting include/exclude and file_types logic
    for filepath in walk_code_files(src_folder):
        if file_types and not any(filepath.endswith(ext) for ext in file_types):
            continue
        # Implement exclude logic (paths, globs) if needed here or in walk_code_files

        print(f"[...] Commenting: {filepath}")
        original = read_code(filepath)
        if not original.strip():
            print(f"⚠️  {filepath} is empty, skipping.")
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
