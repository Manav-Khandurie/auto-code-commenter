# app/agents/comment_agent.py
class CodeCommentAgent:
    def __init__(self, llm):
        self.llm = llm

    def generate_comment_for_python(self, code: str) -> str:
        prompt = f"""
            You are a Python expert. Your task is to insert or update docstrings for all functions, classes, and modules, and add helpful inline comments **only where necessary**—for logic that may be non-obvious or where explanation adds clarity.

            Do not comment trivial or self-explanatory lines.
            Do not modify any of the code's logic or structure.
            Preserve all original code and formatting.

            Return the entire updated Python file as **raw code only**, with:
            - Proper docstrings for all relevant functions, classes, and modules
            - Helpful, non-redundant inline comments only where it adds value
            - No extra explanations
            - No markdown formatting (e.g. no triple backticks)
            - No surrounding text — just the complete updated code

            Here is the code:

            {code}

            Return the updated code now — as plain Python source code only.
        """

        response = self.llm.generate(prompt)
        print("----- begin original response -----")
        print(response)
        print("-----  end original response  ------")
        return response

    def generate_comment_for_sql(self, code: str) -> str:
        prompt = f"""
            You are an expert in SQL. Your task is to add comments to the SQL query provided. The comments should explain the purpose of complex queries, joins, subqueries, and any logic that might not be immediately clear. Keep comments concise but informative. 

            Do not comment trivial or self-explanatory SQL statements.

            Return the updated SQL query with comments. The comments should be inline with the code, right next to the relevant parts of the query. Do **not** add any extra explanations.

            Here is the SQL query:

            {code}

            Return the updated SQL now — as plain SQL source code only.
        """
        
        response = self.llm.generate(prompt)
        print("----- begin original response -----")
        print(response)
        print("-----  end original response  ------")
        return response
