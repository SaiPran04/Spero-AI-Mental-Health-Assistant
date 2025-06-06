import google.generativeai as genai
import time
import traceback

class GeminiLLM:
    def __init__(self, api_key: str, model_name: str = "gemma-3-27b-it", max_retries: int = 3):
        self.model_name = model_name
        self.max_retries = max_retries
        try:
            genai.configure(api_key=api_key)
            # List available models
            print("Available models:")
            for m in genai.list_models():
                print(f"- {m.name}")
            
            # Use the specified model
            self.model = genai.GenerativeModel(model_name)
            print(f"Initialized GeminiLLM with model: {self.model_name}")
        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            print("Full traceback:")
            print(traceback.format_exc())
            raise

    def chat(self, user_input: str) -> str:
        system_message = "You are a supportive AI assistant focused on mental health and well-being."

        for attempt in range(self.max_retries):
            try:
                print(f"Attempt {attempt + 1}: Starting chat with Gemini...")
                chat = self.model.start_chat(history=[])
                print("Chat session started, sending message...")
                response = chat.send_message(f"{system_message}\n\nUser: {user_input}")
                print("Successfully received response from Gemini")
                return response.text
            except Exception as e:
                print(f"Error connecting to Gemini (attempt {attempt + 1}/{self.max_retries}):")
                print(f"Error type: {type(e).__name__}")
                print(f"Error message: {str(e)}")
                print("Full traceback:")
                print(traceback.format_exc())
                
                if attempt < self.max_retries - 1:
                    print(f"Waiting 2 seconds before retry {attempt + 2}...")
                    time.sleep(2)
                else:
                    raise Exception(f"Failed to connect to Gemini after {self.max_retries} attempts. Last error: {str(e)}") 