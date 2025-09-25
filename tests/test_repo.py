import sys, os
import pandas as pd
import pytest
from datetime import datetime, timedelta

# --- Ensure src on sys.path ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.repo_miner import fetch_commits
import vcr

# --- Dummy GitHub objects for offline tests ---
class DummyAuthor:
    def __init__(self, name, email, date):
        self.name = name
        self.email = email
        self.date = date

class DummyCommitCommit:
    def __init__(self, author, message):
        self.author = author
        self.message = message

class DummyCommit:
    def __init__(self, sha, author, email, date, message):
        self.sha = sha
        self.commit = DummyCommitCommit(DummyAuthor(author, email, date), message)

class DummyRepo:
    def __init__(self, commits, issues):
        self._commits = commits
        self._issues = issues

    def get_commits(self):
        return self._commits

# Minimal DummyGithub
class DummyGithub:
    def __init__(self, token):
        assert token == "fake-token"
    def get_repo(self, repo_name):
        return self._repo

# Global dummy instance
gh_instance = DummyGithub("fake-token")

@pytest.fixture
def dummy_github(monkeypatch):
    """Patch Github and env for offline tests."""
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")
    monkeypatch.setattr("src.repo_miner.Github", lambda auth=None: gh_instance)
    return gh_instance

# --- VCR instance for live test ---
this_vcr = vcr.VCR(
    cassette_library_dir='tests/cassettes',
    record_mode='once',
    match_on=['uri', 'method']
)

# ---------------- OFFLINE TESTS ----------------
def test_fetch_commits_basic(dummy_github):
    now = datetime.now()
    commits = [
        DummyCommit("sha1", "Alice", "a@example.com", now, "Initial commit\nDetails"),
        DummyCommit("sha2", "Bob", "b@example.com", now - timedelta(days=1), "Bug fix")
    ]
    gh_instance._repo = DummyRepo(commits, [])
    df = fetch_commits("any/repo")
    assert list(df.columns) == ["sha", "author", "email", "date", "message"]
    assert len(df) == 2
    assert df.iloc[0]["message"] == "Initial commit"

def test_fetch_commits_limit(dummy_github):
    now = datetime.now()
    commits = [
        DummyCommit("sha1", "Alice", "a@example.com", now, "Commit1"),
        DummyCommit("sha2", "Bob", "b@example.com", now, "Commit2"),
        DummyCommit("sha3", "Carol", "c@example.com", now, "Commit3")
    ]
    gh_instance._repo = DummyRepo(commits, [])
    df = fetch_commits("any/repo", max_commits=2)
    assert len(df) == 2

def test_fetch_commits_empty(dummy_github):
    gh_instance._repo = DummyRepo([], [])
    df = fetch_commits("any/repo")
    assert df.empty

# ---------------- LIVE TEST (with real GitHub + VCR) ----------------
def test_fetch_commits_octocat():
    token = os.environ.get("GITHUB_TOKEN")
    print("PYTEST sees token:", repr(token))
    if not token:
        pytest.skip("No real GitHub token available")
    with this_vcr.use_cassette('octocat_hello_world_basic.yaml'):
        df = fetch_commits("octocat/Hello-World", max_commits=5)
    assert isinstance(df, pd.DataFrame)
    assert len(df) <= 5

def test_octocat_commit_messages_and_columns():
    token = os.environ.get("GITHUB_TOKEN")
    print("PYTEST sees token:", repr(token))
    if not token:
        pytest.skip("No real GitHub token available")
    with this_vcr.use_cassette('octocat_hello_world_all.yaml', record_mode='once'):
        df = fetch_commits("octocat/Hello-World", max_commits=10)
    expected_columns = {"sha", "author", "email", "date", "message"}
    assert set(df.columns) == expected_columns
    assert all(isinstance(msg, str) and msg for msg in df["message"])
    assert any("commit" in msg.lower() or "readme" in msg.lower() for msg in df["message"])
    assert all(isinstance(a, str) and a for a in df["author"])
