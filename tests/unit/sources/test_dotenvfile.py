import os
from textwrap import dedent
from tempfile import NamedTemporaryFile

import pytest

from config_composer.sources.files import DotEnvFile


class TestDotEnvFileSource:
    def assert_descriptor_value(self, descriptor, expected_value):
        class MockClass(object):
            pass

        value = descriptor.__get__(None, MockClass)
        assert value == expected_value

    def test_default_behaviour(self, random_string, random_integer):
        tempfile = NamedTemporaryFile(prefix=".env")
        with open(tempfile.name, "w") as fh:
            fh.write(
                dedent(
                    f"""
            # a comment and that will be ignored.
            FOO={random_string}
            foo=Fail baby fail
            BAR=Fail baby fail
            bar={random_integer}
            """
                )
            )

        foo_field = DotEnvFile(path="FOO", dotenv_path=tempfile.name)
        bar_field = DotEnvFile(path="bar", dotenv_path=tempfile.name)

        self.assert_descriptor_value(foo_field, random_string)
        self.assert_descriptor_value(bar_field, str(random_integer))


#     def test_adds_prefix(self, random_string):
#         os.environ["TEST_FOO"] = random_string

#         field = Env(path="foo", prefix="TEST_")

#         self.assert_descriptor_value(field, random_string)
