from config_composer.sources import Default


class TestDefaultSource:
    def assert_descriptor_value(self, descriptor, expected_value):
        class MockClass(object):
            pass

        value = descriptor.__get__(None, MockClass)
        assert value == expected_value

    def test_default_behaviour(self, random_string, random_integer):
        field_1 = Default(random_string)
        field_2 = Default(value=random_string)
        field_3 = Default(value=random_integer)

        self.assert_descriptor_value(field_1, random_string)
        self.assert_descriptor_value(field_2, random_string)
        self.assert_descriptor_value(field_3, random_integer)
