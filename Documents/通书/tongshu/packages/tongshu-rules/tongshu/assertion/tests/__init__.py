import sys
import os

# Add packages to path
repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(repo_root, "packages", "tongshu-rules"))
sys.path.insert(0, repo_root)
