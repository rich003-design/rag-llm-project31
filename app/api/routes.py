from . import api_blueprint
import os
import logging
from flask import request, jsonify, Response, stream_with_context, json
import requests
import sseclient
from app.services import openai_service, pinecone_service, scraping_service
from app.utils.helper_functions import chunk_text, build_prompt, construct_messages_list

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

PINECONE_INDEX_NAME = 'index237'

@api_blueprint.route('/handle-query', methods=['POST'])
def handle_query():
    try:
        logger.info("Received /handle-query request")
        data = request.get_json()
        question = data.get('question', '')
        chat_history = data.get('chatHistory', [])
        
        # Get the most similar chunks from Pinecone
        logger.debug("Querying Pinecone for similar chunks")
        context_chunks = pinecone_service.get_most_similar_chunks_for_query(question, PINECONE_INDEX_NAME)
        logger.debug(f"Context chunks received: {context_chunks}")
        
        # Build the payload to send to OpenAI
        headers, payload = openai_service.construct_llm_payload(question, context_chunks, chat_history)
        logger.debug("Constructed payload for OpenAI")
        
        # Define generator to stream response from OpenAI's API
        def generate():
            try:
                url = 'https://api.openai.com/v1/chat/completions'
                logger.info("Sending request to OpenAI API")
                response = requests.post(url, headers=headers, data=json.dumps(payload), stream=True)
                response.raise_for_status()
                client = sseclient.SSEClient(response)
                for event in client.events():
                    if event.data != '[DONE]':
                        try:
                            data = json.loads(event.data)
                            text = data['choices'][0]['delta'].get('content', '')
                            yield text
                        except Exception as e:
                            logger.error("Error processing event data: %s", e)
                            yield ''
            except Exception as e:
                logger.error("Error during streaming from OpenAI: %s", e)
                yield 'Error retrieving response from OpenAI.'
        
        return Response(stream_with_context(generate()))
    except Exception as e:
        logger.exception("Error in /handle-query endpoint")
        return jsonify({"error": "Something went wrong in handling the query."}), 500

@api_blueprint.route('/embed-and-store', methods=['POST'])
def embed_and_store():
    try:
        logger.info("Received /embed-and-store request")
        data = request.get_json()
        url = data.get('url', '')
        logger.debug(f"Scraping website: {url}")
        
        # Set custom headers to mimic Chrome version 133.0
        custom_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' +
                          'AppleWebKit/537.36 (KHTML, like Gecko) ' +
                          'Chrome/133.0.0.0 Safari/537.36'
        }
        
        # Pass headers to the scraping service
        url_text = scraping_service.scrape_website(url, headers=custom_headers)
        logger.debug("Chunking text from website")
        chunks = chunk_text(url_text)
        logger.info("Embedding chunks and uploading to Pinecone")
        pinecone_service.embed_chunks_and_upload_to_pinecone(chunks, PINECONE_INDEX_NAME)
        return jsonify({"message": "Chunks embedded and stored successfully"})
    except Exception as e:
        logger.exception("Error in /embed-and-store endpoint")
        return jsonify({"error": "Something went wrong while embedding and storing."}), 500

@api_blueprint.route('/delete-index', methods=['POST'])
def delete_index():
    try:
        logger.info("Received /delete-index request")
        pinecone_service.delete_index(PINECONE_INDEX_NAME)
        return jsonify({"message": f"Index {PINECONE_INDEX_NAME} deleted successfully"})
    except Exception as e:
        logger.exception("Error in /delete-index endpoint")
        return jsonify({"error": "Something went wrong while deleting the index."}), 500
    
@api_blueprint.route('/embed-and-store-test', methods=['GET'])
def embed_and_store_test():
    return jsonify({"message": "This is a test route. Please use POST for /embed-and-store."})
