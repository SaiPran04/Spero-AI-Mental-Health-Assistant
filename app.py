from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import sqlite3
from datetime import datetime
from gemini_llm import GeminiLLM
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Add a secret key for session management

# Set Gemini API key environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    # Try to get API key from a file
    try:
        with open('gemini_api_key.txt', 'r') as f:
            GEMINI_API_KEY = f.read().strip()
    except FileNotFoundError:
        print("Please set your Gemini API key in one of these ways:")
        print("1. Set the GEMINI_API_KEY environment variable")
        print("2. Create a file named 'gemini_api_key.txt' with your API key")
        raise ValueError("Gemini API key not found")

# Initialize GeminiLLM with error handling
try:
    llm = GeminiLLM(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Error initializing GeminiLLM: {str(e)}")
    llm = None

# Initialize chat history
chat_history = []

def init_db():
    conn = sqlite3.connect('chat_logs.db')
    c = conn.cursor()
    
    # Create users table if it doesn't exist
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    
    # Create chat logs table if it doesn't exist
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_message TEXT,
            ai_response TEXT,
            user_id INTEGER,
            conversation_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Add conversation_id column if it doesn't exist
    try:
        c.execute("ALTER TABLE chat_logs ADD COLUMN conversation_id TEXT")
    except sqlite3.OperationalError:
        # Column already exists
        pass
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

def store_chat_log(user_message, ai_response, user_id=None):
    conn = sqlite3.connect('chat_logs.db')
    c = conn.cursor()
    
    # Check if user_id column exists
    c.execute("PRAGMA table_info(chat_logs)")
    columns = [column[1] for column in c.fetchall()]
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if 'user_id' in columns:
        c.execute("INSERT INTO chat_logs (timestamp, user_message, ai_response, user_id) VALUES (?, ?, ?, ?)",
                  (timestamp, user_message, ai_response, user_id))
    else:
        c.execute("INSERT INTO chat_logs (timestamp, user_message, ai_response) VALUES (?, ?, ?)",
                  (timestamp, user_message, ai_response))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('chat_logs.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return redirect(url_for('option'))
        else:
            return render_template('login.html', error="Invalid email or password")
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect('chat_logs.db')
        c = conn.cursor()
        
        # Check if email already exists
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        if c.fetchone():
            conn.close()
            return render_template('user.html', error="Email already exists")
        
        # Insert new user
        c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        
        # Get the user ID for session
        c.execute("SELECT id FROM users WHERE email = ?", (email,))
        user_id = c.fetchone()[0]
        conn.close()
        
        session['user_id'] = user_id
        session['user_name'] = name
        return redirect(url_for('option'))
    
    return render_template('user.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('index'))

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/option')
def option():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('option.html')

@app.route('/index')
def home():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/redirect_to_user', methods=['POST'])
def redirect_to_user():
    return redirect(url_for('user'))

@app.route('/redirect_to_option', methods=['POST'])
def redirect_to_option():
    return redirect(url_for('option'))

@app.route('/redirect_to_index', methods=['POST'])
def redirect_to_index():
    return redirect(url_for('home'))

@app.route('/chat', methods=['POST'])
def chat():
    if 'user_id' not in session:
        return jsonify({'response': 'Please log in to use the chatbot'})
    
    user_message = request.json['message']
    
    if llm is None:
        return jsonify({'response': 'Sorry, the AI model is currently unavailable. Please try again later.'})
    
    try:
        print(f"Attempting to get response for message: {user_message[:50]}...")
        ai_response = llm.chat(user_message)
        store_chat_log(user_message, ai_response, session['user_id'])
        return jsonify({'response': ai_response})
    except Exception as e:
        error_message = f"Error generating response: {str(e)}"
        print(error_message)
        print("Full error details:")
        import traceback
        print(traceback.format_exc())
        # Return more detailed error in development mode
        if app.debug:
            return jsonify({'response': f'Debug error info: {error_message}'})
        else:
            return jsonify({'response': 'Sorry, there was an error processing your request. Please try again.'})

@app.route('/reset', methods=['POST'])
def reset():
    global chat_history
    
    # The chat history is already saved by the frontend before calling reset
    # We just need to clear the in-memory chat history
    chat_history = []
    return jsonify({'status': 'success'})

@app.route('/save_chat', methods=['POST'])
def save_chat():
    try:
        if 'user_id' not in session:
            print("User not logged in when saving chat")
            return jsonify({'error': 'Not logged in'})
        
        data = request.json
        messages = data.get('messages', [])
        
        if not messages:
            print("No messages to save")
            return jsonify({'status': 'error', 'message': 'No messages to save'})
        
        user_id = session['user_id']
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Saving {len(messages)} messages for user_id: {user_id} with timestamp: {timestamp}")
        
        conn = sqlite3.connect('chat_logs.db')
        c = conn.cursor()
        
        # Create a conversation_id using the exact timestamp
        conversation_id = timestamp
        
        # Save each message pair with the same conversation_id
        for msg in messages:
            user_message = msg.get('user', '')
            ai_response = msg.get('ai', '')
            
            c.execute("""
                INSERT INTO chat_logs (timestamp, user_message, ai_response, user_id, conversation_id)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, user_message, ai_response, user_id, conversation_id))
        
        conn.commit()
        conn.close()
        print("Chat saved successfully with conversation_id:", conversation_id)
        return jsonify({'status': 'success', 'message': 'Chat saved successfully'})
    except Exception as e:
        print(f"Error in save_chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_chat_history')
def get_chat_history():
    try:
        if 'user_id' not in session:
            print("User not logged in when requesting chat history")
            return jsonify({'error': 'Not logged in'})
        
        user_id = session['user_id']
        print(f"Fetching chat history for user_id: {user_id}")
        
        conn = sqlite3.connect('chat_logs.db')
        c = conn.cursor()
        
        # Get unique conversations based on conversation_id
        # We also select the conversation_id here
        c.execute("""
            SELECT 
                conversation_id,
                MIN(timestamp) as timestamp,
                MIN(id) as first_message_id,
                substr(user_message, 1, 30) as preview,
                COUNT(*) as message_count
            FROM chat_logs 
            WHERE user_id = ? AND user_message != 'Conversation Start'
            GROUP BY conversation_id
            ORDER BY timestamp DESC
        """, (user_id,))
        
        conversations = []
        for row in c.fetchall():
            # Format the timestamp to show date and time
            timestamp = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
            formatted_time = timestamp.strftime("%B %d, %Y at %I:%M %p")
            
            conversations.append({
                'id': row[0], # Use conversation_id here
                'date': formatted_time,
                'preview': row[3] + '...' if len(row[3]) >= 30 else row[3],
                'message_count': row[4]
            })
        
        print(f"Found {len(conversations)} conversations")
        conn.close()
        return jsonify({'conversations': conversations})
    except Exception as e:
        print(f"Error in get_chat_history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get_conversation/<conversation_id>')
def get_conversation(conversation_id):
    try:
        if 'user_id' not in session:
            print("User not logged in when loading conversation")
            return jsonify({'error': 'Not logged in'})
        
        user_id = session['user_id']
        print(f"Loading conversation for user_id: {user_id}, conversation_id: {conversation_id}")
        
        conn = sqlite3.connect('chat_logs.db')
        c = conn.cursor()
        
        # Get all messages for this conversation using the conversation_id
        c.execute("""
            SELECT user_message, ai_response
            FROM chat_logs 
            WHERE user_id = ? 
            AND conversation_id = ? 
            AND user_message != 'Conversation Start'
            ORDER BY id ASC
        """, (user_id, conversation_id))
        
        messages = []
        for row in c.fetchall():
            messages.append({
                'user': row[0],
                'ai': row[1]
            })
        
        print(f"Found {len(messages)} messages for conversation {conversation_id}")
        conn.close()
        return jsonify({'messages': messages})
    except Exception as e:
        print(f"Error in get_conversation: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
