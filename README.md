# 📚 GitWise AI - Repo Chat + Evaluation

GitWise AI(https://gitwiseai.streamlit.app/) is an intelligent tool that allows you to:

- Ingest GitHub repositories
- Ask questions about the code and receive contextual answers using LLMs
- Evaluate answers based on your repository content
-  Maintain chat history for the current session until refresh





<img width="959" height="439" alt="image" src="https://github.com/user-attachments/assets/c36b541c-9bb5-4b76-ad54-f5747ef3f416" />

---

## 🔹 Features

- **Repository Ingestion:** Load GitHub repos into the system for querying.  
- **Interactive Querying:** Ask questions about the repository and get answers from embedded code context.  
- **Chat History:** Keep track of all your queries and answers in a session.  
- **LLM Evaluation:** Automatically score and /breakdown answers for correctness.  
- **Frontend:** Built using **Streamlit** for interactive experience.  
- **Backend:** Built using **FastAPI** for serving API endpoints.  
- **Vector Storage:** Uses **Qdrant** for storing embeddings of code chunks.  

---

## 🔹 Project Structure
```bash
backend/ # FastAPI backend service 
data/ # Raw, processed, and evaluation data 
gitwise/ # Core pipelines, utils, config, and dynamic evaluation
notebooks/ # Jupyter notebooks for experimentation
qdrant_storage/ # Persistent vector database storage
test_data/ # Sample repositories and tests
ui/ # Streamlit frontend
tests/ # Unit tests
docker-compose.yml # Compose file for Qdrant
.env # Environment variables
```
---

## 🔹 Requirements

Python 3.11 and the following dependencies:  
```bash
fastapi==0.135.2
GitPython==3.1.46
huggingface_hub==1.6.0
langchain_groq==1.1.2
langchain_text_splitters==1.1.1
pydantic==2.12.5
pytest==9.0.2
python-dotenv==1.2.2
qdrant_client==1.17.1
requests==2.33.1
sentence-transformers==5.2.3
streamlit==1.55.0
torch==2.2.2
rank_bm25==0.2.2
```
---

## 🔹 Quick Start (Local / Live Demo)

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/gitwise-ai.git
cd gitwise-ai
```
2️⃣ Set environment variables
```bash
Create a .env file at the project root:  
QDRANT_URL=http://localhost:6333
BASE_URL=http://localhost:8000

Note: For live server on same machine, localhost works. If deployed on separate server, replace with public backend URL.
```
3️⃣ Start Qdrant
```bash
docker-compose up -d

This will start Qdrant vector database for storing embeddings. No backend or frontend Docker is needed — run them directly for faster startup.
```
4️⃣ Run Backend (FastAPI)
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
5️⃣ Run Frontend (Streamlit)
```bash
cd ui
streamlit run app.py

Open http://localhost:8501
 in your /browser.
```
🔹 Usage

- Enter GitHub repo URL in the sidebar and click Ingest Repo.
- Ask questions about the code using the query box.
- View retrieved code chunks and the LLM-generated answer.
- Evaluate answers using the Evaluation section.

🔹 Notes

- No Docker build for backend/frontend: Backend and frontend are run directly for faster iteration.
- Persistent Qdrant storage: Stored in qdrant_storage/ (local bind mount).
- Chat session state: Stored in Streamlit session memory; will reset on page refresh.
