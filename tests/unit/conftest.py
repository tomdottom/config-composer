import random
import string

import pytest


@pytest.fixture
def random_string():
    return "".join(
        random.choice(string.ascii_letters) for _ in range(random.randrange(20))
    )
