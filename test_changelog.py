import git
import re

repo = git.Repo(".")
tagmap = {}
for t in repo.tags:
    # Resolve commit for tag (handles annotated tags)
    tagmap.setdefault(repo.commit(t), []).append(t)

print(f"HEAD commit: {repo.head.commit.hexsha}")
head_tags = tagmap.get(repo.head.commit, [])
print(f"HEAD tags: {[t.name for t in head_tags]}")

for commit in repo.iter_commits(max_count=2):
    print(f"Checking commit {commit.hexsha}")
    tags = tagmap.get(commit, [])
    print(f"  Tags: {[t.name for t in tags]}")
    match = False
    for t in tags:
         if re.match(r"^v[0-9]+\.[0-9]+\.[0-9]+.*", t.name):
             print(f"  Matches regex: {t.name}")
             match = True
    
    if match and commit != repo.head.commit:
        print("  WOULD BREAK HERE")
    else:
        print("  CONTINUING")
