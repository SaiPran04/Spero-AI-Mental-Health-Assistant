# Mental Health App AI Chatbot

This is a locally hosted AI chatbot designed for mental health support, built using Flask and Node.js backends with SQLite for data storage. The chatbot utilizes the Ollama LLaMA 3.2 3B model running on a local machine.

It features user authentication, persistent chat history, and a user-friendly interface that allows individuals to interact securely and privately with an AI chatbot.

## Features
- **User Authentication**: Users must sign up or log in before accessing the chatbot.
- **Chat Storage**: Stores conversations in `chat_logs.db` associated with each user.
- **Chat History Sidebar**: Displays previous chats for logged-in users.
- **Locally Hosted AI**: Uses **Ollama LLaMA 3 3B** to generate responses.
- **Logout Option**: Users can log out to end their session.
- **Multiple Backend Options**: Available in both Flask (Python) and Node.js (JavaScript).


## Installation & Setup

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Node.js and npm (for Node.js backend)
- Flask (`pip install flask`)
- SQLite (included with Python)
- Ollama (`ollama` must be installed and running locally)
- LLaMA 3 3B model downloaded (`ollama pull llama3:3b`)

### Steps to Run
1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd ai-chatbot
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the Ollama LLaMA 3B model:
   ```bash
   ollama run llama3:3b
   ```
4. Run the Flask application or Run the Nodejs application:
   ```bash
   python app.py
   npm start
   ```
5. Open your browser and go to:
   ```
   http://127.0.0.1:5000/
   or
   http://localhost:3000/
   ```

## File Structure
- `app.py` - Main Flask backend handling user authentication, chat history, and AI response generation.
- `app.js` - Node.js backend
- `local_llm.py` - Python Ollama API interface for Flask
- `local_llm.ls` - JavaScript Ollama API interface
- `chat_logs.db` - SQLite database storing user credentials and chat history.
- `templates/`
  - `index.html` - Chatbot UI with chat history.
  - `index.ejs` - Node.js chat UI
  - `login.html` - Login page.
  - `login.ejs` - Node.js login page UI
  - `user.html` - Signup page.
  - `user.ejs` - Node.js Signup page UI
- `static/` - Contains CSS/JS files if needed.
- `package.json` - Node.js config
- `README.md` - Project documentation
  
## How It Works
- When a user accesses the chatbot, they are prompted to **Sign Up** or **Login**.
- After logging in, their **previous chats are loaded from SQLite**.
- New chat messages are **sent to the Ollama LLaMA 3B model** for response generation.
- Conversations are stored and can be accessed later.
   
   ## Notes
   - The chatbot runs **entirely locally**; no external API calls are required.
   - Ensure **Ollama is running** before starting the Flask app or Nodejs.
- The SQLite database is lightweight and stores user authentication and chat data.

## Future Improvements
- Add support for multiple AI models.
- Improve UI/UX with a more dynamic frontend.
- Implement a feedback mechanism for AI responses.

---
This chatbot is a great example of running **AI models locally** for personal or enterprise use without cloud dependency.
it facilitates an insightful conversation between AI and user.


Group: Penguin
Rishabh, Pratosh, Harshal, Praneeth
for query mail : 2022A3PS0485H
