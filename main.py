import os

import requests

branch = "main"
repo = os.getenv("REPOSITORY")
token = os.getenv("GITHUB_TOKEN")
filename = 'version.txt'
headers = {"Authorization": f"token {token}"}


with open(filename, "r+") as f:
    next_version = str(int(f.read()) + 1)
    f.seek(0)
    f.write(next_version)

ref_url = f"https://api.github.com/repos/{repo}/git/refs/heads/{branch}"
ref = requests.get(ref_url, headers=headers).json()
latest_commit_sha = ref["object"]["sha"]

commit_url = f"https://api.github.com/repos/{repo}/git/commits/{latest_commit_sha}"
commit = requests.get(commit_url, headers=headers).json()
tree_sha = commit["tree"]["sha"]

# 2. Create blob with updated content
blob_url = f"https://api.github.com/repos/{repo}/git/blobs"
blob_data = {
    "content": next_version,
    "encoding": "utf-8"
}
blob = requests.post(blob_url, headers=headers, json=blob_data).json()
blob_sha = blob["sha"]

# 3. Create new tree
tree_url = f"https://api.github.com/repos/{repo}/git/trees"
tree_data = {
    "base_tree": tree_sha,
    "tree": [{
        "path": "version.txt",
        "mode": "100644",
        "type": "blob",
        "sha": blob_sha
    }]
}
new_tree = requests.post(tree_url, headers=headers, json=tree_data).json()
new_tree_sha = new_tree["sha"]

# 4. Create commit
commit_url = f"https://api.github.com/repos/{repo}/git/commits"
commit_data = {
    "message": "Update version.txt",
    "tree": new_tree_sha,
    "parents": [latest_commit_sha]
}
new_commit = requests.post(commit_url, headers=headers, json=commit_data).json()
new_commit_sha = new_commit["sha"]

# 5. Update branch reference
update_ref_url = f"https://api.github.com/repos/{repo}/git/refs/heads/{branch}"
update_data = {"sha": new_commit_sha}
requests.patch(update_ref_url, headers=headers, json=update_data)