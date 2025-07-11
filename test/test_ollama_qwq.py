from litellm import completion

response = completion(
    model="ollama/qwq",
    messages=[{"content": "respond in 20 words. who are you?", "role": "user"}],
    api_base="http://localhost:11434"
)

print(response)