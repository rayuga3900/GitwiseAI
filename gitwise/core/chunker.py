from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging
from gitwise.config import *
class Chunker:

    def __init__(self, chunk_size=None, overlap=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.chunk_size = chunk_size or CHUNK_SIZE
        self.overlap = overlap or CHUNK_OVERLAP


    def chunk_code(self, content, file_name, file_type, commit):

        chunks = []
        start = 0

        while start < len(content):

            end = start + self.chunk_size

            chunks.append({
                "content": content[start:end],
                "metadata": {
                    "file_name": file_name,
                    "file_type": file_type,
                    "start_index": start,
                    "end_index": end,
                    "commit": commit
                }
            })

            start += self.chunk_size - self.overlap
        
        return chunks


    def chunk_content(self, files):

        all_chunks = []

        for file in files:

            file_content = file["content"]
            file_name = file["path"]
            file_type = file["language"]
            commit = file["commit"]
            if file_type == "markdown":

                self.logger.debug(f"Markdown chunking: {file_name}")

                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.chunk_size * 2, #bigger chunks for documentation.[double size]
                    chunk_overlap=self.overlap * 2,
                    separators=["\n\n", "\n", " "]
                )

                chunks = [
                    {
                        "content": t,
                        "metadata": {
                            "file_name": file_name,
                            "file_type": file_type,
                            "commit": commit
                        }
                    }
                    for t in splitter.split_text(file_content)
                ]

            else:
                
                self.logger.debug(f"Code chunking: {file_name}")
                chunks = self.chunk_code(file_content, file_name, file_type, commit)

            all_chunks.extend(chunks)

        self.logger.info(f"Total chunks created: {len(all_chunks)}")

        return all_chunks