import streamlit as st
import requests
import re
import time
from gitwise.config import BASE_URL
 


st.set_page_config(page_title="GitWise AI", layout="wide")
st.title("📚 GitWise - Repo Chat + Evaluation")

 
# st.session_state  => streamlit in memory store for current session[data alive while user interacts,
#  It does not save it on refresh or between sessions.]
 
if "repo_url" not in st.session_state:
    st.session_state["repo_url"] = ""

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if not st.session_state["chat_history"]:
    st.info("No chat history yet. Ask a question!")

if "loading" not in st.session_state:
    st.session_state["loading"] = False

# Sidebar: Repo Ingestion
st.sidebar.header("🔗 Ingest Repository")

repo_input = st.sidebar.text_input(
    "Enter GitHub Repo URL",
    value=st.session_state["repo_url"]
)

if st.sidebar.button("Ingest Repo", disabled=st.session_state["loading"]):

    if not repo_input:
        st.sidebar.warning("Please enter a repo URL")

    elif not repo_input.startswith("https://github.com/"):
        st.sidebar.error("Invalid GitHub URL")

    else:
        st.session_state["loading"] = True

        with st.spinner("Ingesting repository..."):
            start = time.time()
            res = requests.post(
                f"{BASE_URL}/ingest/",
                json={"repo_url": repo_input}
            )
            end = time.time()

        st.session_state["loading"] = False

        if res.status_code == 200:
            st.session_state["repo_url"] = repo_input
            st.sidebar.success("✅ Repo ready for questions")
            st.sidebar.caption(f"⏱ {end - start:.2f}s")
        else:
            st.sidebar.error(f"❌ Failed: {res.text}")

# Clear Chat
if st.sidebar.button("🗑 Clear Chat"):
    st.session_state["chat_history"] = []
    st.session_state.pop("last_query", None)
    st.session_state.pop("last_response", None)
    st.session_state.pop("last_chunks", None)


# Query 
st.header("💬 Ask Questions")

query = st.text_input("Enter your question")
top_k = st.slider("Top K chunks", 1, 10, 5)

if st.button("Ask", disabled=st.session_state["loading"]):
    #checking if similar query is already present in the history
    existing = next(
        (chat for chat in st.session_state["chat_history"] if query.lower() in chat["query"].lower() or chat["query"].lower() in query.lower()),
        None
    )

    if existing:
        st.info("⚡Retrieved from memory (no API call)")

        st.subheader("🤖 Answer")
        st.markdown(existing["response"])

        st.subheader("📄 Retrieved Context")
        for i, chunk in enumerate(existing["chunks"]):
            preview = chunk[:300] + "..." if len(chunk) > 300 else chunk
            with st.expander(f"Chunk {i+1}"):
                st.write(preview)
                st.caption(chunk)

        # also update last state for evaluation
        st.session_state["last_query"] = existing["query"]
        st.session_state["last_response"] = existing["response"]
        st.session_state["last_chunks"] = existing["chunks"]

        st.stop()
    if not st.session_state["repo_url"]:
        st.warning("Please ingest a repo first")
        st.stop()

    if not query:
        st.warning("Enter a question")
        st.stop()

    st.session_state["loading"] = True

    with st.spinner("Thinking..."):
        start = time.time()
        res = requests.post(
            f"{BASE_URL}/query/",
            json={
                "query": query,
                "repo_url": st.session_state["repo_url"],
                "top_k": top_k
            }
        )
        end = time.time()

    st.session_state["loading"] = False

    if res.status_code == 200:
        data = res.json()
        response = data["response"]
        chunks = data["retrieved_chunks"]

        st.caption(f"⏱ {end - start:.2f}s")

        st.subheader("🤖 Answer")
        st.markdown(response)

        st.subheader("📄 Retrieved Context")
        for i, chunk in enumerate(chunks):
            preview = chunk[:300] + "..." if len(chunk) > 300 else chunk
            with st.expander(f"Chunk {i+1}"):
                st.write(preview)
                st.caption(chunk)

        # Save state
        st.session_state["last_query"] = query
        st.session_state["last_response"] = response
        st.session_state["last_chunks"] = chunks

        st.session_state["chat_history"].append({
            "query": query,
            "response": response,
            "chunks": chunks
        })

    else:
        st.error(f"❌ Query failed: {res.text}")

# -------------------------------
# Chat History
# -------------------------------
st.header("💬 Chat History")

for i, chat in enumerate(reversed(st.session_state["chat_history"])):
    is_latest = (i == 0)

    with st.expander(f"🧑 {chat['query']}", expanded=is_latest):
        st.markdown(f"### 🤖 Answer:\n{chat['response']}")

        for j, chunk in enumerate(chat["chunks"]):
            preview = chunk[:200] + "..." if len(chunk) > 200 else chunk
            with st.expander(f"📄 Chunk {j+1}", expanded=False):
                st.write(preview)
                st.caption(chunk)

# -------------------------------
# Evaluation Section
# -------------------------------
st.header("🧠 Evaluate Answer")

if st.button("Evaluate Response", disabled=st.session_state["loading"]):

    if "last_query" not in st.session_state:
        st.warning("Ask a question first")
        st.stop()

    st.session_state["loading"] = True

    clean_response = re.sub(r"[*_]", "", st.session_state["last_response"])
    clean_response = clean_response.replace("-", "-")
    clean_response = clean_response[:1000]

    payload = {
        "query": st.session_state["last_query"].strip(),
        "repo_url": st.session_state["repo_url"],
        "response": clean_response,
        "context_chunks": st.session_state["last_chunks"]
    }

    with st.spinner("Evaluating..."):
        start = time.time()
        res = requests.post(
            f"{BASE_URL}/judge/",
            json=payload
        )
        end = time.time()

    st.session_state["loading"] = False

    if res.status_code == 200:
        result = res.json()

        st.caption(f"⏱ {end - start:.2f}s")

        st.subheader("📊 Evaluation Breakdown")
        st.json(result)

        score = result.get("score", 0)
        st.success(f"LLM Evaluation Score: {score:.2f}")
        st.progress(score)

    else:
        st.error(f"❌ Evaluation failed: {res.text}")