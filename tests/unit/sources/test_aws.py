import os

import pytest

from config_composer.sources import AWS


class MockClass(object):
    pass


class TestParameterSource:

    def assert_descriptor_value(self, descriptor, expected_value):
        value = descriptor.__get__(None, MockClass)
        assert value == expected_value

    def test_default_behaviour(self, aws_parameter_fixtures):
        random_string = aws_parameter_fixtures
        client = aws_parameter_fixtures

        field = AWS.Parameter(path="/foo/bar/baz")

        self.assert_descriptor_value(field, random_string)
