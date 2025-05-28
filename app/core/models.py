import ollama

response = ollama.chat(
    model='codagemma:2b',
    messages=[
        {
            'role': 'user',
            'content': 'Add Python docstring and inline comments to the following code:\n\n<your_code_here>'
        }
    ]
)

print(response['message']['content'])
