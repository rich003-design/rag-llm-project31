import os
from pinecone import Pinecone, ServerlessSpec
from app.services.openai_service import get_embedding

# Initialize Pinecone instance using your API key
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
pc = Pinecone(api_key=PINECONE_API_KEY)

EMBEDDING_DIMENSION = 1536

def embed_chunks_and_upload_to_pinecone(chunks, index_name):
    # Check if the index exists; if it does, delete it.
    existing_indexes = [index.name for index in pc.list_indexes()]
    if index_name in existing_indexes:
        print("\nIndex already exists. Deleting index ...")
        pc.delete_index(index_name)
    
    print("\nCreating a new index:", index_name)
    # Create a new index using AWS settings (e.g., region us-east-1)
    pc.create_index(
        name=index_name,
        dimension=EMBEDDING_DIMENSION,
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )

    # Get the index instance
    index = pc.Index(index_name)

    # Embed each chunk using OpenAI and prepare vectors for upload
    print("\nEmbedding chunks using OpenAI ...")
    embeddings_with_ids = []
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        embeddings_with_ids.append((str(i), embedding, chunk))

    # Prepare and upsert vectors into Pinecone
    print("\nUploading chunks to Pinecone ...")
    upserts = [(id, vec, {"chunk_text": text}) for id, vec, text in embeddings_with_ids]
    index.upsert(vectors=upserts)

    print(f"\nUploaded {len(chunks)} chunks to Pinecone index '{index_name}'.")


def get_most_similar_chunks_for_query(query, index_name):
    print("\nEmbedding query using OpenAI ...")
    question_embedding = get_embedding(query)

    print("\nQuerying Pinecone index ...")
    index = pc.Index(index_name)
    query_results = index.query(question_embedding, top_k=3, include_metadata=True)
    context_chunks = [match['metadata']['chunk_text'] for match in query_results['matches']]
    return context_chunks   


def delete_index(index_name):
    existing_indexes = [index.name for index in pc.list_indexes()]
    if index_name in existing_indexes:
        print("\nDeleting index ...")
        pc.delete_index(index_name)
        print(f"Index '{index_name}' deleted successfully.")
    else:
        print("\nNo index to delete!")
