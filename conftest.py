# Root conftest: loads the shared fixtures package as a pytest plugin.
#
# Importing this file makes pytest put the repo root on sys.path, so
# `fixtures` and `pages` resolve no matter how the suite is invoked
# (`pytest` or `python -m pytest`). Loading fixtures.conftest via
# `-p` in pytest.ini addopts instead breaks under bare `pytest`,
# because plugin imports happen before the root is on sys.path.
pytest_plugins = ["fixtures.conftest"]
