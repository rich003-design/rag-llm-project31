import requests
import json
import os
from app.utils.helper_functions import build_prompt, construct_messages_list

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENAI_EMBEDDING_MODEL = 'text-embedding-ada-002'
PROMPT_LIMIT = 3750
CHATGPT_MODEL = 'gpt-4-1106-preview'

def get_embedding(chunk):
    url = 'https://api.openai.com/v1/embeddings'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        'model': OPENAI_EMBEDDING_MODEL,
        'input': chunk
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    response_json = response.json()
    
    # Check if 'data' exists in the response
    if "data" not in response_json:
        # Get the error message if available, else a default message
        error_message = response_json.get("error", {}).get("message", "Unknown error")
        raise Exception(f"Error retrieving embedding: {error_message}")
    
    embedding = response_json["data"][0]["embedding"]
    return embedding

def construct_llm_payload(question, context_chunks, chat_history):
    # Build the prompt with the context chunks and user's query
    prompt = build_prompt(question, context_chunks)
    print("\n==== PROMPT ====\n")
    print(prompt)

    # Construct messages array to send to OpenAI
    messages = construct_messages_list(chat_history, prompt)

    # Construct headers including the API key
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f"Bearer {OPENAI_API_KEY}"
    }

    # Construct data payload
    data = {
        'model': CHATGPT_MODEL,
        'messages': messages,
        'temperature': 1,
        'max_tokens': 1000,
        'stream': True
    }

    return headers, data

def get_llm_answer(prompt):
    # Aggregate a messages array to send to the LLM
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    messages.append({"role": "user", "content": prompt})
    # Send the payload to the LLM to retrieve an answer
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        'model': CHATGPT_MODEL,
        'messages': messages,
        'temperature': 1,
        'max_tokens': 1000
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    # return the final answer
    response_json = response.json()
    completion = response_json["choices"][0]["message"]["content"]
    return completion
