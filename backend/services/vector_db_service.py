import os
import chromadb
from sentence_transformers import SentenceTransformer
import textwrap
from services.config_service import load_config # Imports the function to load our app's configuration

# Load the configuration to get the user-defined data storage path
config = load_config()
DATA_STORAGE_PATH = config.get("data_storage_path", ".")

# The ChromaDB vector database will now be stored inside the configured data storage path
CHROMA_DB_PATH = os.path.join(DATA_STORAGE_PATH, "chroma_db")

# --- INITIALIZATION ---
print("Initializing ChromaDB client...")
# This creates a persistent client that saves data to the specified path
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

print("Loading Sentence Transformer model...")
# Load a pre-trained model for creating embeddings. 'all-MiniLM-L6-v2' is a good, fast starting model.
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Sentence Transformer model loaded.")

# Get or create a collection in ChromaDB to store our transcripts
collection = client.get_or_create_collection(name="transcripts")
print("ChromaDB collection 'transcripts' ready.")


# --- HELPER FUNCTIONS ---

def chunk_text(text, chunk_size=500, overlap=50):
    """
    Splits a long plain text into smaller, overlapping chunks.
    This is used by the summarization endpoint.
    """
    wrapper = textwrap.TextWrapper(width=chunk_size, break_long_words=False)
    chunks = wrapper.wrap(text)
    
    overlapped_chunks = []
    for i in range(len(chunks)):
        if i == 0:
            overlapped_chunks.append(chunks[i])
        else:
            prev_chunk_end = chunks[i-1][-overlap:]
            overlapped_chunks.append(prev_chunk_end + chunks[i])
    return overlapped_chunks

def create_chunks_from_segments(segments: list, max_chunk_size: int = 1000):
    """
    Groups Whisper's timed segments into larger chunks with associated start and end times.
    This is used for creating embeddings for vector search.
    """
    chunks = []
    current_chunk_text = ""
    current_chunk_start_time = 0.0
    
    for i, segment in enumerate(segments):
        if not current_chunk_text:
            current_chunk_start_time = segment.get('start', 0.0)

        # Add segment text to the current chunk
        current_chunk_text += segment.get('text', '') + " "

        # If the chunk is large enough or it's the last segment, finalize the chunk
        if len(current_chunk_text) >= max_chunk_size or i == len(segments) - 1:
            chunks.append({
                "text": current_chunk_text.strip(),
                "start_time": current_chunk_start_time,
                "end_time": segment.get('end', 0.0)
            })
            # Reset for the next chunk
            current_chunk_text = ""
    
    return chunks


# --- CORE FUNCTIONS ---

def add_transcript_to_db(source_id: int, result: dict):
    """
    Chunks a transcript's segments, creates embeddings, and stores them with timestamps in ChromaDB.
    """
    print(f"Adding transcript for source_id {source_id} to vector DB.")
    segments = result.get('segments', [])
    if not segments:
        print("No segments found in transcription result.")
        return

    # 1. Group segments into chunks with timestamps
    chunks = create_chunks_from_segments(segments)
    text_chunks = [chunk['text'] for chunk in chunks]

    # 2. Generate embeddings for each chunk
    print(f"Generating embeddings for {len(text_chunks)} chunks...")
    embeddings = embedding_model.encode(text_chunks).tolist()

    # 3. Create unique IDs for each chunk
    chunk_ids = [f"{source_id}_{i}" for i in range(len(text_chunks))]
    
    # 4. Create metadata to store the original text, source_id, and timestamps
    metadatas = [
        {
            "source_id": source_id,
            "text": chunk['text'],
            "start_time": chunk['start_time'],
            "end_time": chunk['end_time']
        } 
        for chunk in chunks
    ]

    # 5. Add the data to the ChromaDB collection
    collection.add(
        ids=chunk_ids,
        embeddings=embeddings,
        documents=text_chunks,
        metadatas=metadatas
    )
    print("Transcript with timestamps successfully added to vector DB.")

def query_db(query_text: str, source_id: int, n_results: int = 3) -> list[dict]:
    """
    Queries the vector database and returns the full metadata of relevant chunks (including text and timestamps).
    """
    print(f"Querying vector DB for source_id {source_id} with query: '{query_text}'")
    
    # Generate an embedding for the user's query
    query_embedding = embedding_model.encode(query_text).tolist()

    # Query the collection, filtering by the specific source document
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={"source_id": source_id}
    )
    
    # Return the list of metadata dictionaries for the found chunks
    retrieved_metadatas = results['metadatas'][0] if results.get('metadatas') else []
    print(f"Found {len(retrieved_metadatas)} relevant chunks.")
    return retrieved_metadatas