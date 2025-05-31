const fetch = require('node-fetch');

class LocalLLM {
    constructor(modelName = "llama3.2:3b", maxRetries = 3) {
        this.modelName = modelName;
        this.maxRetries = maxRetries;
        console.log(`Initialized LocalLLM with model: ${this.modelName}`);
    }

    async chat(userInput) {
        const systemMessage = "You are a supportive AI assistant focused on mental health and well-being.";

        for (let attempt = 0; attempt < this.maxRetries; attempt++) {
            try {
                console.log(`Attempt ${attempt + 1}: Sending request to Ollama...`);
                
                const response = await fetch(`${process.env.OLLAMA_HOST}/api/chat`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        model: this.modelName,
                        messages: [
                            { role: "system", content: systemMessage },
                            { role: "user", content: userInput }
                        ],
                        stream: false // Explicitly disable streaming
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                // Get the raw text
                const rawText = await response.text();
                
                // Fix for multiple JSON objects: take only the first valid JSON object
                let jsonText = rawText;
                if (rawText.indexOf('}{') > 0) {
                    jsonText = rawText.substring(0, rawText.indexOf('}{') + 1);
                    console.log("Found multiple JSON objects, using only the first one");
                }
                
                // Try to parse the JSON
                let data;
                try {
                    data = JSON.parse(jsonText);
                } catch (jsonError) {
                    // Try an alternative approach - split by newlines and parse the first line
                    const lines = rawText.split('\n');
                    if (lines.length > 0) {
                        try {
                            data = JSON.parse(lines[0]);
                            console.log("Successfully parsed first line of response");
                        } catch (lineError) {
                            console.error("JSON parsing error on first line:", lineError.message);
                            throw new Error(`Failed to parse JSON response: ${jsonError.message}`);
                        }
                    } else {
                        throw new Error(`Failed to parse JSON response: ${jsonError.message}`);
                    }
                }
                
                if (!data.message || !data.message.content) {
                    console.error("Unexpected response structure:", data);
                    return "I'm sorry, I received an unexpected response format. Please try again.";
                }
                
                return data.message.content;
            } catch (e) {
                console.error(`Error connecting to Ollama (attempt ${attempt + 1}/${this.maxRetries}): ${e.message}`);
                if (attempt < this.maxRetries - 1) {
                    // Wait for 2 seconds before retrying
                    await new Promise(resolve => setTimeout(resolve, 2000));
                } else {
                    throw new Error("Failed to connect to Ollama after multiple attempts");
                }
            }
        }
    }
}

module.exports = { LocalLLM };