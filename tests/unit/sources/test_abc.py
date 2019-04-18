from config_composer.core import Config, Spec
from config_composer.sources.abc import (
    AbstractSourceDescriptor,
    ValueSource,
    DocumentSource,
)


class TestValueSource:
    def assert_descriptor_value(self, descriptor, expected_value):
        class MockClass(object):
            pass

        value = descriptor.__get__(None, MockClass)
        assert value == expected_value

    def test_gets_value_using_value_property(self, random_string):
        class MySource(ValueSource, AbstractSourceDescriptor):
            @property
            def _name(self):
                return "static name"

            @property
            def _key(self):
                class_name = type(self).__name__
                return (class_name,)

            @property
            def _value(self):
                return random_string

        source = MySource()

        self.assert_descriptor_value(source, random_string)

    def test_adds_each_new_value_to_cache(self, random_string):
        class MySource(ValueSource, AbstractSourceDescriptor):
            def __init__(self, path):
                self._path = path

            @property
            def _name(self):
                return self._path

            @property
            def _key(self):
                class_name = type(self).__name__
                return (class_name,)

            @property
            def _value(self):
                return random_string

        class ConfigSpec(Spec):
            foo: str
            bar: str

        class SourceSpec:
            foo = MySource("foo")
            bar = MySource("bar")

        config = Config(config_spec=ConfigSpec, source_spec=SourceSpec)

        # call to config.foo fetches value and stores is in cache
        assert config.foo == random_string
        root_cache = getattr(
            config.__dict__["_Config__source_spec"], "__source_cache__"
        )
        assert root_cache == {("MySource",): {"foo": random_string}}

        # call to config.bar fetches value and stores is in cache
        assert config.bar == random_string
        assert root_cache == {
            ("MySource",): {"foo": random_string, "bar": random_string}
        }


class TestDocumentSource:
    def assert_descriptor_value(self, descriptor, expected_value):
        class MockClass(object):
            pass

        value = descriptor.__get__(None, MockClass)
        assert value == expected_value

    def test_gets_value_using_value_property(self, random_string):
        class MySource(DocumentSource, AbstractSourceDescriptor):
            @property
            def _name(self):
                return "foo"

            @property
            def _key(self):
                class_name = type(self).__name__
                return (class_name,)

            @property
            def _doc(self):
                return {"foo": random_string}

        source = MySource()

        self.assert_descriptor_value(source, random_string)

    def test_adds_entire_doc_to_cache(self, random_string):
        class MySource(DocumentSource, AbstractSourceDescriptor):
            def __init__(self, path):
                self._path = path

            @property
            def _name(self):
                return self._path

            @property
            def _key(self):
                class_name = type(self).__name__
                return (class_name,)

            @property
            def _doc(self):
                return {
                    "foo": random_string,
                    "bar": random_string,
                    "baz": random_string,
                }

        class ConfigSpec(Spec):
            foo: str
            bar: str

        class SourceSpec:
            foo = MySource("foo")
            bar = MySource("bar")

        config = Config(config_spec=ConfigSpec, source_spec=SourceSpec)

        # call to config.foo fetches doc and stores is in cache
        assert config.foo == random_string
        root_cache = getattr(
            config.__dict__["_Config__source_spec"], "__source_cache__"
        )
        assert root_cache == {
            ("MySource",): {
                "foo": random_string,
                "bar": random_string,
                "baz": random_string,
            }
        }

        assert config.bar == random_string
