from sklearn.metrics.pairwise import cosine_similarity

#  Retrieval Metrics 
def precision_at_k(retrieved_ids, relevant_ids, k=5):
    top_k = retrieved_ids[:k]
    return len(set(top_k) & set(relevant_ids)) / k

def recall_at_k(retrieved_ids, relevant_ids, k=5):
    top_k = retrieved_ids[:k]
    return len(set(top_k) & set(relevant_ids)) / len(relevant_ids)

#  Generation Metrics 
def embedding_similarity(generated_embedding, reference_embedding):
    """Cosine similarity between generated and reference embeddings"""
    return cosine_similarity([generated_embedding], [reference_embedding])[0][0]