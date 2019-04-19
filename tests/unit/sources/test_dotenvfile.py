import os
from textwrap import dedent
from tempfile import NamedTemporaryFile

import pytest

from config_composer.sources.files import DotEnvFile


class TestDotEnvFileSource:
    def assert_descriptor_value(self, descriptor, expected_value, MockClass):
        value = descriptor.__get__(None, MockClass)
        assert value == expected_value

    def test_default_behaviour(self, random_string, random_integer):
        class MockClass(object):
            pass

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

        self.assert_descriptor_value(foo_field, random_string, MockClass)
        self.assert_descriptor_value(bar_field, str(random_integer), MockClass)

    def test_reloads_changed_file(self, random_string, random_integer):
        control = {"time": 0.0}

        class MockClass(object):
            pass

        def mock_time():
            return control["time"]

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

        foo_field = DotEnvFile(
            path="FOO", dotenv_path=tempfile.name, _get_time=mock_time
        )
        bar_field = DotEnvFile(
            path="bar", dotenv_path=tempfile.name, _get_time=mock_time
        )

        self.assert_descriptor_value(foo_field, random_string, MockClass)
        self.assert_descriptor_value(bar_field, str(random_integer), MockClass)

        # Update file
        with open(tempfile.name, "w") as fh:
            fh.write(
                dedent(
                    f"""
            # a comment and that will be ignored.
            FOO={random_integer}
            foo=Fail baby fail
            BAR=Fail baby fail
            bar={random_string}
            """
                )
            )

        # ttl has not expired and hence cache is used
        foo_field = DotEnvFile(
            path="FOO", dotenv_path=tempfile.name, _get_time=mock_time
        )
        bar_field = DotEnvFile(
            path="bar", dotenv_path=tempfile.name, _get_time=mock_time
        )

        # time passes ttl
        control["time"] = 60.0

        # ttl expired and hence doc is reloaded
        self.assert_descriptor_value(foo_field, str(random_integer), MockClass)
        self.assert_descriptor_value(bar_field, random_string, MockClass)
