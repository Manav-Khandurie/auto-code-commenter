# app/cli.py
import argparse
from app.pipeline import run_commenting_pipeline
from app.utils.config_loader import load_config

def main():
    parser = argparse.ArgumentParser(description="Auto-comment code using LLMs")
    parser.add_argument("--config", help="YAML config file path")
    parser.add_argument("--model", default=None, help="LLM model name fallback")
    parser.add_argument("--src", default="./src", help="Source code folder")
    args = parser.parse_args()

    config = None
    if args.config:
        config = load_config(args.config)
    
    run_commenting_pipeline(config=config, 
                           model_name=args.model, 
                           src_folder=args.src)

if __name__ == "__main__":
    main()
