from config_composer.sources import vault
from config_composer.consts import NOTHING


class TestVaultSecret:
    def assert_descriptor_value(self, descriptor, expected_value):
        class MockClass(object):
            pass

        value = descriptor.__get__(None, MockClass)
        assert value == expected_value

    def test_default_behaviour(self, vault_secret_fixtures):
        random_string = vault_secret_fixtures

        field = vault.Secret(path="/foo/bar/baz", field="my-secret")

        self.assert_descriptor_value(field, random_string)

    def test_non_existant_secret(self, vault_secret_fixtures):
        field = vault.Secret(path="/im/not/here", field="missing")

        self.assert_descriptor_value(field, NOTHING)

    def test_non_existant_path(self, vault_secret_fixtures):
        field = vault.Secret(path="/im/not/here", field="not-here")

        self.assert_descriptor_value(field, NOTHING)
