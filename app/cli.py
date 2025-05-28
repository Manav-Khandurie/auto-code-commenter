import argparse
from app.pipeline import run_commenting_pipeline

def main():
    parser = argparse.ArgumentParser(description="Auto-comment code using LLMs")
    parser.add_argument("--model", default="deepseek-chat", help="LLM model name (Ollama)")
    parser.add_argument("--src", default="./src", help="Source code folder")
    args = parser.parse_args()

    run_commenting_pipeline(model_name=args.model, src_folder=args.src)


if __name__ == "__main__":
    main()