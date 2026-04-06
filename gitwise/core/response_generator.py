from huggingface_hub import InferenceClient
import os
import logging
from dotenv import load_dotenv
 
class ResponseGenerator :
    def __init__(self, llm):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.llm = llm
    
    def generate_response(self, query, context_chunks, max_tokens=512, temperature=0.0):
        """
        Generates a response using Groq LLM.

        Args:
            query (str): user question
            context_chunks (List[str]): retrieved chunks from vector DB
        """

        # Combine retrieved chunks
        context = "\n".join([str(c.get("content", "")) for c in context_chunks])

        # for dynamic evaluation we wont send context
        if context_chunks is None:
            context_chunks = []

        prompt = f"""
            Use the following context to answer the question concisely.

            Context:
            {context}

            Question:
            {query}

            Answer:
            """

        response = self.llm.invoke(prompt)

        return response.content
# class  :
#     def __init__(self, client, model_name: str = "deepseek-ai/DeepSeek-R1"):
#         self.logger = logging.getLogger(self.__class__.__name__)
#         self.client = client
#         self.model_name = model_name
    
#     def generate_response(self, query, context_chunks, max_tokens=512, temperature=0.0):
#         """
#         Generates a response based on the query and retrieved context.

#         Args:
#             query (str): user question
#             context_chunks (List[str]): list of retrieved chunks from vector DB
#             max_tokens (int): maximum tokens to generate
#             temperature (float): randomness in generation
#         """
#         # Combine context chunks into a single string
#         context = "\n".join(context_chunks)

#         prompt = f"Use the following context to answer the question:\n\n{context}\n\nQuestion: {query}\nAnswer:"
#         response = llm.invoke([prompt.format(context=context_chunks,query=query)])
#         # Call the HuggingFace Inference API
#         # response = self.client.text_generation(
#         #     model=self.model_name,
#         #     prompt=prompt,
#         #     max_new_tokens=max_tokens
#         #     # temperature=temperature
#         # )

#         # The response returned by HF client
#         return response
    
    # def generate_response(self, query, context_chunks, max_tokens=512, temperature=0.0):
    #     """
    #     Generates a response based on the query and retrieved context.

    #     Args:
    #         query (str): user question
    #         context_chunks (List[str]): list of retrieved chunks from vector DB
    #         max_tokens (int): maximum tokens to generate
    #         temperature (float): randomness in generation
    #     """
    #     # Combine context chunks into a single string
    #     context = "\n".join(context_chunks)

    #     # prompt = f"Use the following context to answer the question:\n\n{context}\n\nQuestion: {query}\nAnswer:"
    #     messages = [
    #         {"role": "system", "content": "You are a knowledgeable coding assistant."},
    #         {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{query}"}
    #     ]
    #     # Call the HuggingFace Inference API
    #     response = self.client.chat_completion(
    #         model=self.model_name,
    #         messages=messages,
    #         max_tokens=max_tokens
    #         # temperature=temperature
    #     )

    #     # The response returned by HF client
    #     return response