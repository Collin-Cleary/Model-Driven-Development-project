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
from github import Github, Auth

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
    from github import Auth
    auth = Auth.Token(token)
    client = Github(auth=auth)
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
        message = comm.commit.message.split("\n")[0]

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


def fetch_issues(repo_name: str, state: str = "all", max_issues: int = None) -> pd.DataFrame:
    """
    Fetch up to 'max_issues' from the specified Github repository (issues only).
    Returns a DataFrame  with columns: id, number, title, user, state created_at, closed_ad, comments.
    """
    # 1) Read GitHub token
    token = os.environ.get("GITHUB_TOKEN")
    if token is None:
        raise RuntimeError("GITHUB_TOKEN environment variable not set")

    # 2) Initialize client and get the repo
    from github import Auth
    auth = Auth.Token(token)
    client = Github(auth=auth)
    repo =  client.get_repo(repo_name)

    # 3) Fetch issues, filtered by state ('all', 'open', 'closed')
    issues = []
    issues = repo.get_issues(state=state)

    # 4) Normalize each issue (skip PRs)
    records = []
    for idx, issue in enumerate(issues):
        if max_issues and idx >= max_issues:
            break
        if issue.pull_request is not None and hasattr(issue, "pull_request"):
            continue
        closed = False
        created = False
        local_created_at = None
        local_closed_at = None
        if issue.closed_at:
            local_closed_at = issue.closed_at.isoformat()
            closed = True
        if issue.created_at: 
            local_created_at = issue.created_at.isoformat()
            created = True
        duration = None
        if created and closed:
            duration = (issue.closed_at - issue.created_at).days

        # Append records
        records.append({
            "id": issue.id,
            "number": issue.number,
            "title": issue.title,
            "user": issue.user.login if issue.user else None,
            "state": issue.state,
            "created_at": local_created_at,
            "closed_at": local_closed_at,
            "comments": issue.comments,
            "open_duration_days": duration,
            "is_pr": issue.pull_request is not None,
            "duration_days": duration      
        })

    # 5) Build DataFrame
    return pd.DataFrame(records)
    

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

    # Sub-command: fetch-issues
    c2 = subparsers.add_parser("fetch-issues", help="Fetch issues and save to CSV")
    c2.add_argument("--repo",  required=True, help="Repository in owner/repo format")
    c2.add_argument("--state", choices=["all", "open", "closed"], default="all",
                    help="Filter issues by State")
    c2.add_argument("--max", type=int, dest="max_issues",
                    help="Max number of issues to fetch")
    c2.add_argument("--out", required=True, help="Path to output issues CSV")

    args = parser.parse_args()

    # Dispatch based on selected command
    if args.command == "fetch-commits":
        df = fetch_commits(args.repo, args.max_commits)
        df.to_csv(args.out, index=False)
        print(f"Saved {len(df)} commits to {args.out}")

    elif args.command == "fetch-issues":
        df = fetch_issues(args.repo, args.state, args.max_issues)
        df.to_csv(args.out, index=False)
        print(f"Saved {len(df)} issues to {args.out}")

if __name__ == "__main__":
    main()
