from flask import Flask, request, jsonify
from groq import Groq
import requests

app = Flask(__name__)

# Configuration for Groq API (using LLaMA model)
GROQ_API_KEY = "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"
GROQ_MODEL = "llama3-8b-8192"

# Configuration for Google Gemini API
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=AIzaSyBZ_Q0qsj-ZGSYpkxqYoMfqUNwIHfwpzm8"

# Configuration for Anthropic Claude API
CLAUDE_API_URL = "https://api.anthropic.com/v1/claude-3.5/complete"
CLAUDE_API_KEY = "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"  # Replace with your actual Claude API key


def call_llama(prompt, history):
    client = Groq(api_key=GROQ_API_KEY)

    # Append the user prompt to the history
    history.append({"role": "user", "content": prompt})

    # Create the chat completion request with the entire history
    chat_completion = client.chat.completions.create(
        messages=history,
        model=GROQ_MODEL,
    )

    # Retrieve the assistant's response
    response = chat_completion.choices[0].message.content

    # Append the assistant's response to the history
    history.append({"role": "assistant", "content": response})

    return response, history


def call_gemini(prompt):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(GEMINI_API_URL, json=data, headers=headers)
    return response.json()


def call_claude(prompt, history):
    headers = {
        "Authorization": f"Bearer {CLAUDE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "model": "claude-3.5",  # Specify the Claude model you want to use
        "history": history  # Include history if needed
    }

    response = requests.post(CLAUDE_API_URL, json=data, headers=headers)

    if response.status_code == 200:
        return response.json().get("completion"), history  # Return the response content and updated history
    else:
        return None, history  # Handle error case


@app.route('/api', methods=['POST'])
def api_endpoint():
    req_data = request.json
    model = req_data.get('model')
    prompt = req_data.get('prompt')
    history = req_data.get('history', [{"role": "system", "content": ""}])

    if model == 'llama':
        response, updated_history = call_llama(prompt, history)
        return jsonify({"response": response, "history": updated_history})

    elif model == 'gemini':
        response = call_gemini(prompt)
        return jsonify(response)

    elif model == 'claude':
        response, updated_history = call_claude(prompt, history)
        return jsonify({"response": response, "history": updated_history})

    else:
        return jsonify({"error": "Invalid model specified"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
