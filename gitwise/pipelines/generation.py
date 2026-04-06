import os
from dotenv import load_dotenv
from gitwise.core import ResponseGenerator
from langchain_groq import ChatGroq
import time
import logging
from gitwise.utils import *

setup_logging()
load_dotenv(dotenv_path=".env")
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PREFERRED_MODELS = [
    "groq/compound",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]
# Lazy generator variable
generator = None

 
def get_working_model(preferred_models, api_key):
    for model_name in preferred_models:
        try:
            llm = ChatGroq(
                groq_api_key=api_key,
                model_name=model_name,
                temperature=0.1,
                max_tokens=1024
            )
            logging.info(f"Using model: {model_name}")
            return llm, model_name
        except Exception as e:
            logging.warning(f"Model {model_name} failed: {e}")
    raise RuntimeError("No working Groq model found.")
# llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama-3.1-70b-versatile", temperature=0.1, max_tokens=1024)

# llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name="llama-3.1-8b-instant", temperature=0.1, max_tokens=1024)
if __name__ == "__main__":
    llm, model_name = get_working_model(PREFERRED_MODELS, GROQ_API_KEY)
    generator = ResponseGenerator(llm)
def get_generator():
    """
    Returns a ResponseGenerator instance, initializing it only once (lazy loading).
    """
    global generator
    if generator is None:
        llm, model_name = get_working_model(PREFERRED_MODELS, GROQ_API_KEY)
        generator = ResponseGenerator(llm)
    return generator

def run_generation(query: str, context_chunks: list):
        start_time = time.time()
        logger.info(f"Generating response for query: {query}")
        logger.info(f"Number of context chunks: {len(context_chunks) if context_chunks else 0}")
        time.sleep(1)  # rate limit safety [Groq  has requests per minute limits.]
        if context_chunks is None:
            context_chunks = []
        try:
            time.sleep(1)  # rate limit spacing
            # Lazy initialize generator
            gen = get_generator()
            response = gen.generate_response(query, context_chunks=context_chunks)
            logger.info(f"Response generation completed in {time.time() - start_time:.2f}s")
            return response or ""
        except Exception as e:
            logging.warning(f"Generation failed: {e}")
            return f"Generation failed: {str(e)}"