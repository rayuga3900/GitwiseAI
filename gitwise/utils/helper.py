# import os

from urllib.parse import urlparse

# def get_repo_name_from_url(repo_url: str) -> str:
#     """
#     Extract the repo name from a GitHub/remote URL.
#     e.g. "https://github.com/user/my-repo.git" -> "my-repo"
#     """
#     return os.path.splitext(repo_url.rstrip("/").split("/")[-1])[0]


import os
import json
import git
import time

def needs_reload(repo_url: str, clone_root="data/raw/"):
    owner, repo_name = extract_repo_info(repo_url)
    repo_id = normalize_repo_id(owner, repo_name)

    metadata_path = f"data/processed/{repo_id}/metadata.json"

    # Never ingested
    if not os.path.exists(metadata_path):
        return True

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    old_commit = metadata.get("last_commit")

    # avoid frequent git checks (5 min TTL)
    if time.time() - metadata.get("last_ingested_at", 0) < 300:
        return False

    repo_path = os.path.join(clone_root, repo_id)

    if not os.path.exists(repo_path):
        return True

    repo = git.Repo(repo_path)
    new_commit = repo.head.commit.hexsha

    return old_commit != new_commit

def extract_repo_info(repo_url: str):
    parsed = urlparse(repo_url)
    
    if "github.com" not in parsed.netloc:
        raise ValueError("Only GitHub URLs are supported")

    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        raise ValueError("Invalid GitHub repo URL")

    owner = parts[0]
    repo_name = parts[1].replace(".git", "")

    return owner, repo_name

# repo_id = f"{owner}/{repo_name}"
def normalize_repo_id(owner: str, repo: str):
    return f"{owner.strip().lower()}__{repo.strip().lower()}"