import logging
import os
import random
import string

import pytest


logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def random_string():
    return "".join(
        random.choice(string.ascii_letters) for _ in range(random.randrange(10, 20))
    )


@pytest.fixture
def random_integer():
    return random.randint(1, 99999)


@pytest.fixture
def environ():
    class Environ:
        def __init__(self):
            self._og_keys = set(os.environ.keys())
            self._keys = set()

        def __getitem__(self, name):
            return os.environ[name]

        def __setitem__(self, name, value):
            self._keys.add(name)
            os.environ[name] = value

        def __delitem__(self, name):
            self._keys.discard(name)
            del os.environ[name]

        def clean_up(self):
            for key in self._keys - self._og_keys:
                del os.environ[key]

    environ = Environ()

    yield Environ()

    environ.clean_up()
