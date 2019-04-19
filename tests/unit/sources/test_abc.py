from config_composer.core import Config, Spec
from config_composer.sources.abc import (
    AbstractSourceDescriptor,
    ValueSource,
    DocumentSource,
    DocumentSourceTTL,
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


class TestDocumentSourceTTL:
    def assert_descriptor_value(self, descriptor, expected_value, MockClass):
        value = descriptor.__get__(None, MockClass)
        assert value == expected_value

    def test_can_expire_document_cache(self, random_string, random_integer):
        class MockClass(object):
            pass

        control = {"expired": True}

        class MySource(DocumentSource, DocumentSourceTTL, AbstractSourceDescriptor):
            def __init__(self):
                self._value = random_string
                self._is_expired = False

            @property
            def _name(self):
                return "foo"

            @property
            def _key(self):
                class_name = type(self).__name__
                return (class_name,)

            @property
            def _doc(self):
                return {"foo": self._value}

            def _expired(self, ttl_data):
                if not isinstance(ttl_data, dict):
                    ttl_data = control

                if ttl_data["expired"] == True:
                    expired = True
                    ttl_data.update({"expired": False})
                else:
                    expired = False

                return expired, ttl_data

        source = MySource()

        # Calling multiple times uses same doc
        self.assert_descriptor_value(source, random_string, MockClass)
        self.assert_descriptor_value(source, random_string, MockClass)
        self.assert_descriptor_value(source, random_string, MockClass)

        # Change returned doc
        source._value = str(random_integer)

        # and expire current doc
        control["expired"] = True

        self.assert_descriptor_value(source, str(random_integer), MockClass)
        # Change returned doc
        source._value = "This should not be read"
        # Carry on using cached doc until expired
        self.assert_descriptor_value(source, str(random_integer), MockClass)
        self.assert_descriptor_value(source, str(random_integer), MockClass)

    def test_adds_entire_doc_to_cache(self, random_string):

        control = {"expired": True}

        class MySource(DocumentSource, DocumentSourceTTL, AbstractSourceDescriptor):
            def __init__(self, path):
                self._path = path
                self._count = 0

            @property
            def _name(self):
                return self._path

            @property
            def _key(self):
                class_name = type(self).__name__
                return (class_name,)

            @property
            def _doc(self):
                self._count += 1
                return {
                    "foo": f"foo - {random_string} - {self._count}",
                    "bar": f"bar - {random_string} - {self._count}",
                    "baz": f"baz - {random_string} - {self._count}",
                }

            def _expired(self, ttl_data):
                if not isinstance(ttl_data, dict):
                    ttl_data = control

                if ttl_data["expired"] == True:
                    expired = True
                    ttl_data.update({"expired": False})
                else:
                    expired = False

                return expired, ttl_data

        class ConfigSpec(Spec):
            foo: str
            bar: str

        class SourceSpec:
            foo = MySource("foo")
            bar = MySource("bar")

        config = Config(config_spec=ConfigSpec, source_spec=SourceSpec)

        # call to config.foo fetches doc and stores is in cache
        assert config.foo == f"foo - {random_string} - 1"
        assert config.bar == f"bar - {random_string} - 1"
        root_cache = getattr(
            config.__dict__["_Config__source_spec"], "__source_cache__"
        )
        assert root_cache == {
            ("MySource",): {
                "foo": f"foo - {random_string} - 1",
                "bar": f"bar - {random_string} - 1",
                "baz": f"baz - {random_string} - 1",
            }
        }

        # call to config.foo fetches doc and stores is in cache
        source_spec = config.__dict__["_Config__source_spec"]
        control["expired"] = True

        assert config.foo == f"foo - {random_string} - 2"
        assert config.bar == f"bar - {random_string} - 2"
        root_cache = getattr(source_spec, "__source_cache__")
        assert root_cache == {
            ("MySource",): {
                "foo": f"foo - {random_string} - 2",
                "bar": f"bar - {random_string} - 2",
                "baz": f"baz - {random_string} - 2",
            }
        }
