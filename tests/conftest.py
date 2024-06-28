import os

import pytest


@pytest.fixture()
def read_file():
    def _read_file(name: str) -> str:
        with open(
            os.path.join(os.path.dirname(__file__), "files", name), "rb"
        ) as f:
            return f.read().decode("utf8")

    return _read_file
