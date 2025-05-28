class CodeCommentAgent:
    def __init__(self, llm):
        self.llm = llm

    def generate_comment(self, code: str) -> str:
        prompt = (
            "Add Python docstring and inline comments to the following code. "
            "Only return the updated version:\n\n"
            f"{code}"
        )
        return self.llm.generate(prompt)
