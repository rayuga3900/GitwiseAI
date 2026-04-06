# from gitwise.core import DataLoader,Chunker,Embedder,VectorStore,Retriever,ResponseGenerator,HybridRetriever,Reranker
# # from gitwise.utils.decorators import log_duration
# from gitwise.utils import *
# import uuid
# from qdrant_client import QdrantClient
# import os
# from dotenv import load_dotenv
# from huggingface_hub import InferenceClient
# import numpy as np
# import pickle
# from rank_bm25 import BM25Okapi
# from langchain_groq import ChatGroq
# from gitwise.config import *

# setup_logging()
# data_loader =  DataLoader(repo_url="https://github.com/rayuga3900/Power-Consumption-Predictor",repo_name="",clone_root='data',branch='main')
# files = data_loader.data_loading() 

# # chunking content
# chunker = Chunker(chunk_size=500, overlap=100)
# chunks = chunker.chunk_content(files=files)
 

# # chunks are dict and we want string for the embeddings
# texts = [c["content"] for c in chunks]


# # Prepare UUIDs and payloads
# uuids = [str(uuid.uuid4()) for _ in chunks]
# for i, chunk in enumerate(chunks):
#     chunk["id"] = uuids[i]
 
# payloads = [
#     {
     
#         "file_name": c["metadata"].get("path"),
#         "file_type": c["metadata"].get("file_type"),
#         "start_index": c["metadata"].get("start_index"),
#         "end_index": c["metadata"].get("end_index"),
#         "content": c["content"]
#     }
#     for c in chunks
# ]
# # payloads = chunks
# client = QdrantClient(url=QDRANT_URL)
 
 
# mini_store = VectorStore(client, collection_name=COLLECTION_NAME, vector_dim=384)
# # Always initialize the embedder
# CACHE_FILE = "embeddings_cache.pkl"
# mini_embedder = Embedder(model_name="all-MiniLM-L6-v2")

 
# if os.path.exists(CACHE_FILE):
#     with open(CACHE_FILE, "rb") as f:
#         cache = pickle.load(f)
#     uuids = cache["uuids"]
#     mini_embeddings = cache["embeddings"]
#     payloads = cache["payloads"]
# else:
#     # Only generate UUIDs here if cache doesn't exist
#     uuids = [str(uuid.uuid4()) for _ in chunks]
#     for i, chunk in enumerate(chunks):
#         chunk["id"] = uuids[i]
#     mini_embeddings = mini_embedder.embed_chunks(texts)
#     with open(CACHE_FILE, "wb") as f:
#         pickle.dump({"uuids": uuids, "embeddings": mini_embeddings, "payloads": payloads}, f)
 

# # mini_store = VectorStore(client, collection_name=COLLECTION_NAME, vector_dim=384)
 
# mini_store.create_collection()
# mini_store.insert_update_vector(uuids,embeddings=mini_embeddings,payloads=payloads,batch_size=200,delay=0.1)

# query = "how does the project handles the outliers, skewness and missing values?. Also give which file handles those??"


# #normal retriever
# # retriever = Retriever(vector_store=mini_store,embedder=mini_embedder,top_k=20)
# # results = retriever.retrieve(query=query)
# # for r in results:
# #     r_dict = {
# #         "id": r.id,
# #         "score": r.score,
# #         "file_name": r.payload.get("file_name"),
# #         "content_preview": r.payload.get("content", "")[:50]
# #     }
# # context_chunks = []
 
# # context_chunks =  [r.payload.get("content", "") for r in results]

# #hybrid retriever
# documents = [c["content"] for c in chunks]
# doc_ids = [c["id"] for c in chunks]

# tokenized_docs = [doc.split() for doc in documents]

# bm25 = BM25Okapi(tokenized_docs)
# bm25_data = {
#     "bm25": bm25,
#     "doc_ids": doc_ids,
#     "documents": documents,
#     "metadatas": [c["metadata"] for c in chunks]
# }
# hr = HybridRetriever(dense_store=mini_store,dense_embedder=mini_embedder,bm25_data=bm25_data,top_k_dense=20,top_k_sparse=20,top_k_final=10)
# hybrid_results = hr.retrieve(query)
# for r in hybrid_results:
#     print(r)

# context_chunks = []
 
# context_chunks =  [r["content"] for r in hybrid_results]

# # reranking
# # rr = Reranker(top_k=5)
# # top_docs = rr.rerank(query,context_chunks)


 
 
# load_dotenv(dotenv_path=".env") 
# groq_api_key = os.getenv("GROQ_API_KEY")
# llm = ChatGroq(groq_api_key=groq_api_key,model_name="llama3-70b-8192",temperature=0.1,max_tokens=1024)
# generator = ResponseGenerator(llm)



# # Now call your response generator
# response = generator .generate_response(query, context_chunks=context_chunks)


# print(response)



# # Tested the hugging face model 
# # load_dotenv(dotenv_path=".env") 
# # hf_token = os.getenv("HF_API_TOKEN")
# # client = InferenceClient(token=hf_token)
# # response_generator = ResponseGenerator(client,model_name="deepseek-ai/DeepSeek-R1")
# # print(response.choices[0].message["content"])


# #general vector store
# # embedder = Embedder()
# # embeddings = embedder.embed_chunks(texts)
# # vector_store = VectorStore(client=client)
# # vector_store.insert_update_vector(uuids,embeddings=embeddings,payloads=payloads)