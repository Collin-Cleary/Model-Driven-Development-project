# Model-Driven-Development-project

## Project Structure

### src/
Contains the main source code for the project.

- `repo_miner.py`: Command-line tool and module for fetching and normalizing commit and issue data from GitHub repositories.  
  - **Commits**: Fetches commits with columns `sha`, `author`, `email`, `date`, `message`.  
  - **Issues**: Fetches issues with columns `id`, `number`, `title`, `user`, `state`, `created_at`, `closed_at`, `comments`, `open_duration_days`, `duration_days`, and `is_pr`. Supports filtering by state (`all`, `open`, `closed`) and limiting the number of issues returned with `max_issues`.

### tests/
Contains test code and supporting files for automated testing.

- `test_repo.py`: Pytest test suite for validating the functionality of `repo_miner.py` and related code.  
  - Tests now include **issue-fetching functionality** with VCR-based offline tests.  
  - Validates columns, commit and issue data, exclusion of pull requests, date formatting, and issue durations.  
- `cassettes/`: Directory for VCR.py cassette files, which store recorded HTTP interactions for offline and reproducible testing.
  - `octocat_hello_world_all.yaml`: Cassette for tests involving multiple commits from the `octocat/Hello-World` repository.
  - `octocat_hello_world_basic.yaml`: Cassette for basic commit fetch tests from the `octocat/Hello-World` repository.
  - `octocat_issues_excludes_prs.yaml`: Cassette for tests verifying that pull requests are excluded from issue results.
  - `octocat_issues_dates_are_iso.yaml`: Cassette for tests verifying that issue dates are formatted as ISO 8601 strings.
  - `octocat_issues_duration_days.yaml`: Cassette for tests verifying calculation of issue durations (`open_duration_days` / `duration_days`).
