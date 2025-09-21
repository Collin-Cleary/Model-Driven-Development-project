#!/usr/bin/env python3
"""
repo_miner.py

A command-line tool to:
  1) Fetch and normalize commit data from GitHub

Sub-commands:
  - fetch-commits
"""

import os
import argparse
import pandas as pd
from github import Github

def fetch_commits(repo_name: str, max_commits: int = None) -> pd.DataFrame:
    """
    Fetch up to `max_commits` from the specified GitHub repository.
    Returns a DataFrame with columns: sha, author, email, date, message.
    """
    # 1) Read GitHub token from environment
    token = os.environ.get("GITHUB_TOKEN")
    if token is None:
        raise RuntimeError("GITHUB_TOKEN environment variable not set")

    # 2) Initialize GitHub client and get the repo
    client = Github(token)
    repo =  client.get_repo(repo_name)

    # 3) Fetch commit objects (paginated by PyGitHub)
    commits = []
    comms = repo.get_commits()
    for i, comm in enumerate(comms):
        commits.append(comm)
        if max_commits is not None and i+1 >= max_commits:
            break

    # 4) Normalize each commit into a record dict
    commits_dict = []

    for comm in commits:
        sha = comm.sha
        author = comm.commit.author.name
        email = comm.commit.author.email
        date = comm.commit.author.date
        message = comm.commit.message

        commits_dict.append({
            "sha": sha,
            "author": author,
            "email": email,
            "date": date,
            "message": message
        })

    # 5) Build DataFrame from records
    Dataframe = pd.DataFrame(commits_dict)
    return Dataframe
    

def main():
    """
    Parse command-line arguments and dispatch to sub-commands.
    """
    parser = argparse.ArgumentParser(
        prog="repo_miner",
        description="Fetch GitHub commits/issues and summarize them"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sub-command: fetch-commits
    c1 = subparsers.add_parser("fetch-commits", help="Fetch commits and save to CSV")
    c1.add_argument("--repo", required=True, help="Repository in owner/repo format")
    c1.add_argument("--max",  type=int, dest="max_commits",
                    help="Max number of commits to fetch")
    c1.add_argument("--out",  required=True, help="Path to output commits CSV")

    args = parser.parse_args()

    # Dispatch based on selected command
    if args.command == "fetch-commits":
        df = fetch_commits(args.repo, args.max_commits)
        df.to_csv(args.out, index=False)
        print(f"Saved {len(df)} commits to {args.out}")

if __name__ == "__main__":
    main()
