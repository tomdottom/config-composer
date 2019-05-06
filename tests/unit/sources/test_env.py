import os

from config_composer.sources.env import Env, Env2


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


class TestEnv2Source:
    def assert_descriptor_value(self, descriptor, expected_value):
        class MockClass(object):
            pass

        value = descriptor.__get__(None, MockClass)
        assert value == expected_value

    def test_default_behaviour(self, random_string):
        os.environ["FOO"] = random_string
        cache = {}

        parameter = Env2(path="FOO")

        parameter.fetch(cache=cache)
        value = parameter.get(name=None, cache=cache)

        assert value == random_string

    def test_adds_prefix(self, random_string):
        os.environ["TEST_FOO"] = random_string
        cache = {}

        parameter = Env2(path="FOO", prefix="TEST_")

        parameter.fetch(cache=cache)
        value = parameter.get(name=None, cache=cache)

        assert value == random_string
