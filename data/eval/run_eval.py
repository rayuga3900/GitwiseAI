import os
import json
import logging
import numpy as np
from gitwise.core import Embedder, VectorStore
from metrics import *
from gitwise.utils import *
from gitwise.pipelines.retrieval import run_retrieval
from gitwise.pipelines.generation import run_generation
from qdrant_client import QdrantClient
from gitwise.config import *
from gitwise.utils.helper import * 
# Setup logging
setup_logging()
logger = logging.getLogger(__name__)
logging.info("--- Inside the Static Evaluation Pipeline ---")

# Config
repo_url = "https://github.com/rayuga3900/Power-Consumption-Predictor"
owner, repo_name = extract_repo_info(repo_url)
repo_id = normalize_repo_id(owner, repo_name)
CHUNKS_FILE = f"data/processed/{repo_id}/chunks.json"
EVAL_FILE = f"data/eval/{repo_id}/eval.json"
 
REF_EMBED_FILE = f"data/processed/{repo_id}/ref_embeddings.npy"
GEN_EMBED_FILE = f"data/processed/{repo_id}/gen_embeddings.npy"
TOP_K = 20

 
if not os.path.exists(CHUNKS_FILE):
    raise FileNotFoundError(f"Chunks file not found: {CHUNKS_FILE}")
with open(CHUNKS_FILE, "r") as f:
    chunks = json.load(f)
 
with open(EVAL_FILE, "r") as f:
    eval_dataset = json.load(f)

 
embedder = Embedder(model_name="all-MiniLM-L6-v2")

 
 

if os.path.exists(GEN_EMBED_FILE):
    logger.info("Loading cached generated embeddings...")
    gen_embeddings_cache = np.load(GEN_EMBED_FILE, allow_pickle=True).item()
else:
    gen_embeddings_cache = {}

if os.path.exists(REF_EMBED_FILE):
    logger.info("Loading cached reference embeddings...")
    ref_embeddings = np.load(REF_EMBED_FILE, allow_pickle=True).item()
else:
    logger.info("Computing reference embeddings...")
    ref_embeddings = {item['query']: embedder.embed_chunks([item['reference_answer']])[0] for item in eval_dataset}
    os.makedirs(os.path.dirname(REF_EMBED_FILE), exist_ok=True)
    np.save(REF_EMBED_FILE, ref_embeddings)

 
client = QdrantClient(url=QDRANT_URL)

vector_store = VectorStore(client, f"{repo_id.lower()}_chunks")

all_metrics = []

 
for item in eval_dataset:
    query = item["query"]
    reference = item["reference_answer"]
    ground_truth_ids = item["ground_truth_chunk_ids"]

    logger.info(f"Evaluating query: {query}")

    # Retrieve context chunks using cached embeddings
    context_chunks = run_retrieval(
        query=query,
        chunks=chunks,
        vector_store=vector_store,
        embedder=embedder,
        rerank_top_k=TOP_K,
 
    )

    logger.info(f"Context chunks count: {len(context_chunks)}")
    if not context_chunks:
        logger.warning("No context retrieved!")

    retrieved_ids = [c["id"] for c in context_chunks]

 
    # retrieval metrics
    prec = precision_at_k(retrieved_ids, ground_truth_ids, k=TOP_K)
    rec = recall_at_k(retrieved_ids, ground_truth_ids, k=TOP_K)

 
    # response = run_generation(query=query, context_chunks=context_chunks)
    if query in gen_embeddings_cache:
            gen_emb = gen_embeddings_cache[query]
            
    else:
        response = run_generation(query=query, context_chunks=context_chunks)
        if response:
            gen_emb = embedder.embed_chunks([response])[0]
        else:
            gen_emb = np.zeros(embedder.embedding_dim)  # fallback
        gen_embeddings_cache[query] = gen_emb  # save in cache

    ref_emb = ref_embeddings[query]
    sim = embedding_similarity(gen_emb, ref_emb)
 
    logger.info(f"Query completed: {query}")
    logger.info(f"Precision@{TOP_K}: {prec:.3f}, Recall@{TOP_K}: {rec:.3f}, Embedding sim: {sim:.3f}")
    logger.info(f"Response snippet: {response[:100]}")

 
    all_metrics.append({
        "query": query,
        "precision": prec,
        "recall": rec,
        "embedding_similarity": sim
    })

# Saving evaluation metrics
metrics_file = f"data/eval/{repo_id}/metrics.json"

os.makedirs(os.path.dirname(metrics_file), exist_ok=True)
with open(metrics_file, "w") as f:
    json.dump(all_metrics, f, indent=2)
logger.info(f"Saved evaluation metrics to {metrics_file}")
np.save(GEN_EMBED_FILE, gen_embeddings_cache)
logger.info(f"Saved generated embeddings cache to {GEN_EMBED_FILE}")