from config_composer.sources import aws
from config_composer.consts import NOTHING


class TestParameterSource:
    def assert_descriptor_value(self, descriptor, expected_value):
        class MockClass(object):
            pass

        value = descriptor.__get__(None, MockClass)
        assert value == expected_value

    def test_default_behaviour(self, aws_parameter_fixtures):
        random_string = aws_parameter_fixtures

        field = aws.Parameter(path="/foo/bar/baz")

        self.assert_descriptor_value(field, random_string)

    def test_non_existant_path(self, aws_parameter_fixtures):
        field = aws.Parameter(path="/im/not/here")

        self.assert_descriptor_value(field, NOTHING)
