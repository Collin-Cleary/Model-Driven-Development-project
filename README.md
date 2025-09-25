# Model-Driven-Development-project


## Project Structure

### src/
Contains the main source code for the project.

- `repo_miner.py`: Command-line tool and module for fetching and normalizing commit data from GitHub repositories.

### tests/
Contains test code and supporting files for automated testing.

- `test_repo.py`: Pytest test suite for validating the functionality of `repo_miner.py` and related code.
- `cassettes/`: Directory for VCR.py cassette files, which store recorded HTTP interactions for offline and reproducible testing.
	- `octocat_hello_world_all.yaml`: Cassette for tests involving multiple commits from the `octocat/Hello-World` repository.
	- `octocat_hello_world_basic.yaml`: Cassette for basic commit fetch tests from the `octocat/Hello-World` repository.

