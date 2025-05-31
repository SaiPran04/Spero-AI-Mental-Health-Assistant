const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const path = require('path');
const { LocalLLM } = require('./local_llm');

const app = express();
const port = 3000; 

// Set up middleware
app.use(bodyParser.json());
app.use(express.static('public'));
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'templates'));

// Set Ollama host environment variable
process.env.OLLAMA_HOST = 'http://localhost:11434';

// Initialize LocalLLM with error handling
let llm = null;
try {
    llm = new LocalLLM();
} catch (e) {
    console.error(`Error initializing LocalLLM: ${e.message}`);
}

// Initialize chat history
let chatHistory = [];

// Function to store chat logs
function storeChatLog(userMessage, aiResponse) {
    const db = new sqlite3.Database('chat_logs.db');
    
    // Ensure table structure
    db.run(`
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_message TEXT,
            ai_response TEXT
        )
    `);
    
    const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
    db.run(
        "INSERT INTO chat_logs (timestamp, user_message, ai_response) VALUES (?, ?, ?)",
        [timestamp, userMessage, aiResponse],
        function(err) {
            if (err) {
                console.error('Error storing chat log:', err.message);
            }
        }
    );
    
    db.close();
}

// Routes
app.get('/', (req, res) => {
    res.render('login');
});

app.get('/user', (req, res) => {
    res.render('user');
});

app.get('/option', (req, res) => {
    res.render('option');
});

app.get('/index', (req, res) => {
    res.render('index');
});

app.post('/redirect_to_user', (req, res) => {
    res.render('user');
});

app.post('/redirect_to_option', (req, res) => {
    res.redirect('/option');
});

app.post('/redirect_to_index', (req, res) => {
    res.redirect('/index');
});

app.post('/chat', async (req, res) => {
    const userMessage = req.body.message;
    
    if (!llm) {
        return res.json({
            response: 'Sorry, the AI model is currently unavailable. Please try again later.'
        });
    }
    
    try {
        const aiResponse = await llm.chat(userMessage);
        storeChatLog(userMessage, aiResponse);
        return res.json({ response: aiResponse });
    } catch (e) {
        console.error(`Error generating response: ${e.message}`);
        return res.json({
            response: 'Sorry, there was an error processing your request. Please try again.'
        });
    }
});

app.post('/reset', (req, res) => {
    chatHistory = [];
    res.json({ status: 'success' });
});

// Start server
app.listen(port, '0.0.0.0', () => {
    console.log(`Server running http://localhost:${port}`);
});


