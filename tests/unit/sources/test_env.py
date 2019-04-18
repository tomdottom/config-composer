import os

import pytest

from config_composer.sources import Env


class TestEnvSource:
    def assert_descriptor_value(self, descriptor, expected_value):
        class MockClass(object):
            pass

        value = descriptor.__get__(None, MockClass)
        assert value == expected_value

    def test_default_behaviour(self, random_string):
        os.environ["FOO"] = random_string

        field = Env(path="FOO")

        self.assert_descriptor_value(field, random_string)

    def test_adds_prefix(self, random_string):
        os.environ["TEST_FOO"] = random_string

        field = Env(path="FOO", prefix="TEST_")

        self.assert_descriptor_value(field, random_string)
