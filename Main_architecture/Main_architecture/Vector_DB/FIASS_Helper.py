# faiss_helper.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def store_queries_in_vector_db(query_list):
    """
    Takes a list of queries, stores them in a FAISS vector database, and returns the vector database.
    """
    # Generate embeddings for the query list
    query_embeddings = model.encode(query_list).astype('float32')

    # Create FAISS index (L2 distance for similarity)
    index = faiss.IndexFlatL2(query_embeddings.shape[1])  # L2 distance (Euclidean)
    index.add(query_embeddings)  # Add embeddings to the index

    return index

def get_most_relevant_query(vector_db, user_query, query_list):
    """
    Takes the FAISS vector database and a user query, performs similarity search,
    and returns the most relevant query along with its similarity score.
    """
    # Generate embedding for the user query
    user_query_embedding = model.encode([user_query]).astype('float32')

    # Perform similarity search (retrieve top 1 match)
    D, I = vector_db.search(user_query_embedding, k=1)  # D: distances, I: indices

    # Retrieve the most relevant query and similarity score
    most_similar_query = query_list[I[0][0]]
    similarity_score = D[0][0]

    return most_similar_query, similarity_score
