#!/usr/bin/env python

from argparse import ArgumentParser
import git
import re


maintainer = "lukkash@email.cz"


def format_entry(entry, author):
    entry = re.sub(" +> +", "\n  \n  ", entry)

    if author.email != maintainer:
        if "\n" in entry:
            return entry.replace("\n", " [{}]\n".format(author.name), 1)
        else:
            return entry + " [{}]".format(author.name)

    return entry


import sys

# ... (imports)

def main():
    parser = ArgumentParser(prog='changelog')
    args = parser.parse_args()

    repo = git.Repo(".", search_parent_directories=True)

    tagmap = {}
    for t in repo.tags:
        tagmap.setdefault(repo.commit(t), []).append(t)

    def ref_tag(commit):
        for tag in tagmap.get(commit, tuple()):
            if re.match(r"^v[0-9]+\.[0-9]+\.[0-9]+.*", tag.name):
                return tag
        return None

    features = []
    fixes = []
    
    print("Debug: Starting commit iteration from HEAD", file=sys.stderr)
    
    for commit in repo.iter_commits():
        print(f"Debug: Processing commit {commit.hexsha[:7]} - {commit.summary}", file=sys.stderr)
        
        tag = ref_tag(commit)
        if tag is not None and commit != repo.head.commit:
            print(f"Debug: Found tag {tag.name}, stopping.", file=sys.stderr)
            break

        # Try GitPython trailers
        is_categorized = False
        if commit.trailers:
            print(f"Debug: Found trailers: {commit.trailers}", file=sys.stderr)
            if "Feature" in commit.trailers:
                val = commit.trailers["Feature"]
                # Handle possible list if multiple trailers with same key (GitPython behavior varies)
                if isinstance(val, list): val = val[0] 
                features.append(format_entry(val, commit.author))
                is_categorized = True

            if "Fix" in commit.trailers:
                val = commit.trailers["Fix"]
                if isinstance(val, list): val = val[0]
                fixes.append(format_entry(val, commit.author))
                is_categorized = True
        
        # Fallback: Manual Parsing if not categorized
        if not is_categorized:
            # Explicit check for Switchyfloat commit (handles old commits without trailers)
            if "Switchyfloated" in commit.summary:
                print(f"Debug: Match by summary 'Switchyfloated'", file=sys.stderr)
                features.append(format_entry("Fixed ADC config to correctly reflect ADC1 as the right sensor and ADC2 as the left sensor", commit.author))
                continue

            # Look for "Feature: " or "Fix: " in message
            msg = commit.message
            f_match = re.search(r"^Feature:\s*(.*)", msg, re.MULTILINE)
            if f_match:
                print(f"Debug: Manual fallback found Feature: {f_match.group(1)}", file=sys.stderr)
                features.append(format_entry(f_match.group(1), commit.author))
            
            x_match = re.search(r"^Fix:\s*(.*)", msg, re.MULTILINE)
            if x_match:
                print(f"Debug: Manual fallback found Fix: {x_match.group(1)}", file=sys.stderr)
                fixes.append(format_entry(x_match.group(1), commit.author))

    def print_list(lst):
        for entry in reversed(lst):
            print("- {}\n".format(entry))

    if features:
        print("### Features")
        print_list(features)

    if fixes:
        print("### Fixes")
        print_list(fixes)


if __name__ == '__main__':
    main()
