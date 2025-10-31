import json
import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from datetime import timedelta
from logger import logger

class SemanticSearcher:

    def __init__(self):
        self.model = None

    def load_transcript_data(self, video_id: str, ):
        """Loads the JSON transcript file and returns the list of snippets."""
        logger.info('Transcriptions logger started')
        filename = f'{video_id}.json'
        data_dir: str = "transcription_db"
        full_path = os.path.join(data_dir, filename)
        
        with open(full_path, 'r', encoding='utf-8') as f:
            # Load the list of dictionaries
            transcript_data = json.load(f)
            
        return transcript_data 
    
    # Define a function to convert seconds to HH:MM:SS format
    def seconds_to_timestamp(self, seconds: float) -> str:
        """Converts a floating-point time in seconds to the format HH:MM:SS."""
        return str(timedelta(seconds=int(seconds)))

    def embed_and_store_faiss(self, video_id: str):
        logger.info('embed and store started')
        """Loads data, creates embeddings, and initializes a FAISS index."""
        
        # 1. Load Data and Model
        transcript_data = self.load_transcript_data(video_id)
        # Use a high-quality, efficient model
        if self.model is None:
            self.model = SentenceTransformer('all-MiniLM-L6-v2') 
            logger.info('all-MiniLM-L6-v2 initialized')
        # 2. Prepare Data for Embedding
        # Create a list of just the text for the model
        texts = [item['text'] for item in transcript_data]
        
        # 3. Generate Embeddings
        print("Generating embeddings...")
        embeddings = self.model.encode(texts)
        logger.info("embeddings done")
        
        # 4. Create FAISS Index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings) # Add the vectors to the index
        
        # 5. Store Metadata (Crucial for lookup)
        # We store the original snippet data along with the index object
        vector_store = {
            'index': index,
            'metadata': transcript_data,
            'model': self.model 
        }
        
        print(f"Index created with {index.ntotal} vectors.")
        return vector_store

    def semantic_search_and_time(self, video_id: str,  vector_store: dict, query: str, k: int = 1):
        """Performs semantic search and returns the text and timestamp of the top result."""
        logger.info("semantic search started")
        # 1. Access the components
        index = vector_store['index']
        metadata = vector_store['metadata']
        model = vector_store['model']
        
        # 2. Embed the query
        query_embedding = model.encode([query])
        logger.info("query embeddings done")
        # 3. Search the FAISS index (D=distances, I=indices)
        distances, indices = index.search(query_embedding, k)
        
        # 4. Retrieve the best match metadata
        best_match_index = indices[0][0]
        best_match = metadata[best_match_index]
        
        # 5. Format the output to meet your goal
        timestamp_start = self.seconds_to_timestamp(best_match['start'])
        timestamp_end = self.seconds_to_timestamp(best_match['start'] + best_match['duration'])

        return {
            "video_id": video_id, # Assuming video_id is available in the scope or passed
            "timestamp_start": timestamp_start,
            "timestamp_end": timestamp_end,
            "matched_text": best_match['text']
        }