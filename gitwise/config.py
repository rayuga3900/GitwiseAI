from dotenv import load_dotenv
import os

load_dotenv()
SKIP_DIRS = { ".git","node_modules","dist","build",".venv","__pycache__"}

SKIP_EXTENSIONS = {
".png",".jpg",".jpeg",".gif",".bmp",
".mp4",".mp3",".avi",
".zip",".tar",".gz",".7z",
".exe",".dll",".so",".pdf",".pkl",".lock", ".log", ".csv"
}
SKIP_FILENAMES = {".dockerignore", ".gitignore"}  
LANG_MAP = {
".py": "python",
".js": "javascript",
".ts": "typescript",
".java": "java",
".cpp": "cpp",
".c": "c",
".go": "go",
".rs": "rust",
".php": "php",
".rb": "ruby",
".md": "markdown"
}
CHUNK_SIZE = 700                  # 700 tokens/chars per chunk
CHUNK_OVERLAP = 200
MAX_FILE_SIZE = 10 * 1024 * 1024 #10mb
MAX_CHUNK_SIZE = 2 * 1024 * 1024  # 2MB per chunk


QDRANT_URL = os.getenv("QDRANT_URL" )

BASE_URL = os.getenv("BASE_URL" )