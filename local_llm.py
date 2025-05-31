import ollama
import time

class LocalLLM:
    def __init__(self, model_name: str = "llama3.2:3b", max_retries: int = 3):
        self.model_name = model_name
        self.max_retries = max_retries
        print(f"Initialized LocalLLM with model: {self.model_name}")

    def chat(self, user_input: str) -> str:
        system_message = "You are a supportive AI assistant focused on mental health and well-being."

        for attempt in range(self.max_retries):
            try:
                response = ollama.chat(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_input}
                    ]
                )
                return response['message']['content']
            except Exception as e:
                print(f"Error connecting to Ollama (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)  # Wait for 2 seconds before retrying
                else:
                    raise Exception("Failed to connect to Ollama after multiple attempts")
