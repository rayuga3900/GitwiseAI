import os 
import git
import logging
from gitwise.config import (
    SKIP_DIRS,
    SKIP_EXTENSIONS,
    LANG_MAP,
    MAX_FILE_SIZE,
    MAX_CHUNK_SIZE,
)

from gitwise.utils.helper import (
    extract_repo_info,
    normalize_repo_id,
)
class DataLoader:


    def __init__(self, repo_url: str, repo_name: str = "", clone_root: str = "../data", branch: str = "main"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.repo_url = repo_url
        self.owner, self.repo_name = extract_repo_info(self.repo_url)
        self.repo_id = normalize_repo_id(self.owner, self.repo_name)
        self.clone_root = clone_root
        self.branch = branch
    
    def _cleanup_skipped_files(self):
        """Remove skipped files from local clone after git operations."""
        for root, dirs, files in os.walk(self.repo_path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            
            for file in files:
                if (file.startswith(".") or 
                    os.path.splitext(file)[1].lower() in SKIP_EXTENSIONS):
                    skip_path = os.path.join(root, file)
                    os.remove(skip_path)
                    self.logger.info(f"Cleaned: {os.path.relpath(skip_path, self.repo_path)}")
                    
   # cloning the repository and storing it on disk[faster]
    def data_loading(self):

        """
            Clone a Git repository locally and read all relevant files.

            Parameters:
            - self.repo_url: URL of the Git repository
            - self.repo_name: Optional local name for the repo; derived from URL if not given
            - self.clone_root: Parent folder where all repos are stored

            Returns:
            - List of dictionaries containing file content and metadata:
            {repo, path, content, language}
        """

        # Deriving repository name from the URL if not provided
        if not self.repo_name:
            self.repo_name = self.repo_url.split("/")[-1].replace(".git", "")
 
        # Constructing local path for storing the repo
        self.repo_path = os.path.join(self.clone_root, self.repo_id)
        self.logger.info(f"repo_id: {self.repo_id }")
        self.logger.info(f"repo url: {self.repo_url }")
        self.logger.info(f"repo path: {self.repo_path }")
        self.logger.info(f"clone root on local: {self.clone_root }")

        # Ensuring  the parent directory for cloned repositories exists
        os.makedirs(self.clone_root, exist_ok=True)

        if not os.path.exists(self.repo_path):
            self.logger.info(f"Cloning {self.repo_url} into {self.repo_path}...")
            branch_info = self.branch if self.branch else "default"
            try:
                if self.branch:
                    self.logger.info(f"Using branch: {branch_info}")
                    git.Repo.clone_from(self.repo_url, self.repo_path, depth=1, branch=self.branch)# depth=1 to only get latest commit history else will get all
                else:
                    self.logger.info(f"Using branch: {branch_info}")
                    git.Repo.clone_from(self.repo_url, self.repo_path, depth=1)
            except Exception as e:
                self.logger.error(f"Failed to clone repo: {e}")
                return []
        else:
            # If exists, pull latest code from the branch
            self.logger.info(f"Repo {self.repo_name} already exists locally.")
            repo = git.Repo(self.repo_path)
            origin = repo.remotes.origin
            branch_info = self.branch if self.branch else "default"

            if self.branch:
                self.logger.info(f"Using branch: {branch_info}")
                repo.git.checkout(self.branch)#if branch doesnt exist locally
                origin.pull(self.branch)
            else:
                self.logger.info(f"Using branch: {branch_info}")
                origin.pull()
        repo = git.Repo(self.repo_path)
        commit_hash = repo.head.commit.hexsha
        self._cleanup_skipped_files()
        # read files from each repos
        files_data = []
        for root, dirs, files in os.walk(self.repo_path):
            # Skip hidden folders[no useful data{code}]
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for file in files:
                path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].strip().lower()
                language = LANG_MAP.get(ext, "text")
                print(f"[Debug] filename{file}")
               
                if file.startswith(".") or ext in SKIP_EXTENSIONS:
                    self.logger.info(f"Skipping file: {file} with extension: {ext}")
                    continue 

                # if file size is greater than 10 mb than we will process in chunks
                if os.path.getsize(path) > MAX_FILE_SIZE:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        while True:
                            content = f.read(MAX_CHUNK_SIZE)
                            if not content:
                                break
                            files_data.append({
                                "repo": self.repo_name,
                                "commit": commit_hash,
                                "path": os.path.relpath(path, self.repo_path),
                                "content": content,
                                "language": language
                            })
                    self.logger.debug(f"Reading file: {path} size={os.path.getsize(path)} bytes")
                else:
                    try:
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        files_data.append({
                            "repo": self.repo_name,
                            "commit": commit_hash,
                            "path": os.path.relpath(path, self.repo_path),
                            "content": content,
                            "language": language
                        })
                    except Exception as e:
                        self.logger.warning(f"Skipping {path}: {e}")
        return files_data

