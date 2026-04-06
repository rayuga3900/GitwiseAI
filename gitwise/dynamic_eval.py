import logging
from gitwise.pipelines.generation import run_generation
from gitwise.utils import * 
from gitwise.config import *
from gitwise.core import ResponseGenerator
from langchain_groq import ChatGroq
import os
import re
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

 
scoring_llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant",
    temperature=0.0,      # deterministic for scoring
    max_tokens=128        # enough for 0-1 score
)
# Setup logging
setup_logging()



def judge_answer(query, response, context_chunks, scoring_generator=None):
    """
    LLM-based judge using a separate scoring model.
    Returns a float score 0-1.
    """
    logging.info(f"--- Inside the Dynamic Evaluation Pipeline ---")
    if scoring_generator is None:
        raise ValueError("scoring_generator must be provided")
    context_chunks = [{"content": c} if isinstance(c, str) else c for c in context_chunks]
    context_text = "\n".join([c["content"] for c in context_chunks])
#     Faithfulness score → uses context
#     Correctness score → ignores context
    prompt = f"""
    You are a strict grader.

    Score the answer from 0 to 1 based on:

    1. Faithfulness: Is the answer supported by the context?
    2. Relevance: Does it answer the question?
    3. Correctness: Is it logically correct?

    Rules:
    - If answer is not supported by context → score < 0.5
    - If answer contradicts context → score = 0
    - If fully correct and grounded → score close to 1

    Return ONLY a number between 0 and 1.

    Question: {query}
    Answer: {response}
    Context: {context_text}
    """

    score_text = scoring_generator.generate_response(prompt, context_chunks=[])
    try:
        score = float(score_text.strip())
    except:
        match = re.search(r"\d*\.?\d+", score_text or "")
        score = float(match.group(0)) if match else 0.0 
    score = max(0.0, min(1.0, score))
    print(f"score_text:{score_text}")
    return score


scoring_generator = ResponseGenerator(scoring_llm)
if __name__ == "__main__":
    # testing 
    query = "How is the project handling missing values?"

    
    response = "Missing values are handled using imputation techniques such as mean or median depending on the feature type."

    
    context_chunks = [
        {"content": " num_preprocess = Pipeline([\n    (\"imputer\", SimpleImputer(strategy=\"median\"))\n])\n\npreprocessor = ColumnTransformer([\n    (\"num\", num_preprocess, num"}
    ]

    logging.info(f"Dynamic evaluation using model: {scoring_llm.model_name}")
    score = judge_answer(query,response,context_chunks,scoring_generator=scoring_generator)

    logging.info(f"Score: {score}")